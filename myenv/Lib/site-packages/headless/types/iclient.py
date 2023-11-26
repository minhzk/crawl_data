# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import inspect
import logging
import urllib.parse
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import Generic
from typing import Generator
from typing import NoReturn
from typing import TypeVar

import pydantic

from .headers import Headers
from .hints import RequestContent
from .ibackoff import IBackoff
from .icredential import ICredential
from .ratelimited import RateLimited
from .iresource import IResource
from .iresponse import IResponse
from .irequest import IRequest
from .nullbackoff import NullBackoff
from .nullcredential import NullCredential
from .optionsresponse import OptionsResponse


Request = TypeVar('Request')
Response = TypeVar('Response')
M = TypeVar('M', bound=IResource)
T = TypeVar('T', bound='IClient[Any, Any]')


class IClient(Generic[Request, Response]):
    """Specifies the interface for all API client implementations."""
    __module__: str = 'headless.types'
    backoff: IBackoff = NullBackoff()
    base_url: str
    credential: ICredential = NullCredential()
    request_class: type[IRequest[Request]]
    response_class: type[IResponse[Request, Response]]
    logger: logging.Logger = logging.getLogger('headless.client')
    user_agent: str = 'Headless'

    @property
    def cookies(self) -> Any:
        raise NotImplementedError

    @property
    def issuer(self) -> str:
        return self.get_issuer()

    def check_json(self, headers: Headers):
        # TODO: Abstract this to a separate class.
        content_type = headers.get('Content-Type') or ''
        if not str.startswith(content_type, 'application/json'):
            raise TypeError(
                'Invalid response content type: '
                f'{headers.get("Content-Type")}'
            )

    def get_issuer(self) -> str:
        p = urllib.parse.urlparse(self.base_url)
        return f'{p.scheme}://{p.netloc}'

    def in_context(self) -> bool:
        """Return a boolean indicating if the client is current used as a
        context manager.
        """
        raise NotImplementedError

    async def delete(self, **kwargs: Any) -> IResponse[Request, Response]:
        return await self.request(method='DELETE', **kwargs)

    async def get(self, **kwargs: Any) -> IResponse[Request, Response]:
        return await self.request(method='GET', **kwargs)

    async def post(self, **kwargs: Any) -> IResponse[Request, Response]:
        return await self.request(method='POST', **kwargs)

    async def options(self, **kwargs: Any) -> OptionsResponse:
        response = await self.request(method='OPTIONS', **kwargs)
        return OptionsResponse.parse_response(response)

    async def persist(
        self,
        model: type[M],
        instance: M
    ) -> M:
        response = await self.request(
            method=model._meta.persist_method,
            url=instance.get_persist_url(),
            json=instance.dict()
        )
        response.raise_for_status()
        return instance

    async def request(
        self,
        method: str,
        url: str,
        credential: ICredential | None = None,
        json: list[Any] | dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        allow_none: bool = False,
        cookies: dict[str, str] | None = None,
        content: RequestContent | None = None
    ) -> IResponse[Request, Response]:
        headers: dict[str, str] = headers or {}
        headers.setdefault('User-Agent', self.user_agent)
        if json is not None:
            headers['Content-Type'] = 'application/json'
        request = await self._request_factory(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params,
            cookies=cookies,
            content=content
        )
        await (credential or self.credential).add_to_request(request)
        try:
            response = await self.send(request)
        except Exception as exc:
            response = await request.on_failure(exc, self)
            if response is None:
                raise
        if response.status_code == 429:
            response = await self.on_rate_limited(response)
        elif response.status_code == 404 and allow_none:
            pass
        elif 400 <= response.status_code < 500:
            response = await self.on_client_error(response)
        return response

    async def retrieve(self, model: type[M], resource_id: int | str | None = None) -> M:
        """Discover the API endpoint using the class configuration
        and retrieve a single instance using the HTTP GET verb.
        """
        meta = model.get_meta()
        response = await self.get(
            url=model.get_retrieve_url(resource_id),
            headers=meta.headers
        )
        response.raise_for_status()
        self.check_json(response.headers)
        data = self.process_response('retrieve', await response.json())
        return self.resource_factory(model, 'retrieve', data)

    async def on_client_error(
        self,
        response: IResponse[Any, Any]
    ) -> NoReturn | IResponse[Any, Any]:
        return response

    async def on_rate_limited(
        self,
        response: IResponse[Any, Any]
    ) -> NoReturn | IResponse[Any, Any]:
        """Invoked when the endpoint returns a ``429`` status code, indicating that
        it is rate limited. The default implementation raises an exception, but
        subclasses may override this method to return a response object.
        """
        response = await self.backoff.retry(self, response.request, response)
        if response.status_code == 429:
            self.logger.critical(
                "Unable to recover from rate limit (request: %s, resource: %s)",
                response.request.id, response.request.url
            )
            raise RateLimited(request=response.request, response=response)
        return response

    def process_response(
        self,
        action: str,
        data: dict[str, Any] | list[Any]
    ) -> dict[str, Any]:
        """Hook to transform response data."""
        return data

    def resource_factory(self, model: type[M], action: str, data: dict[str, Any]) -> M:
        resource = model.parse_obj(model.process_response(action, data))
        self._inject_client(resource)
        return resource

    async def request_factory(
        self,
        method: str,
        url: str,
        json: list[Any] | dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        cookies: dict[str, str] | None = None,
        content: RequestContent | None = None,
    ) -> Request:
        raise NotImplementedError

    async def send(self, request: IRequest[Request]) -> IResponse[Request, Response]:
        raise NotImplementedError

    async def __aenter__(self: T) -> T:
        raise NotImplementedError

    async def __aexit__(self, cls: type[BaseException] | None, *args: Any) -> bool | None:
        raise NotImplementedError

    def _inject_client(self, resource: pydantic.BaseModel):
        # Traverse the object hierarchy and add the client to each implementation
        # of IResource.
        resource._client = self
        for attname, field in resource.__fields__.items():
            if not inspect.isclass(field.type_)\
            or not issubclass(field.type_, IResource):
                continue
            value = getattr(resource, attname)
            if isinstance(value, Iterable):
                if isinstance(value, Mapping):
                    value = list(value.values())
                for subresource in value:
                    self._inject_client(subresource)

    async def _request_factory(self, *args: Any, **kwargs: Any) -> IRequest[Request]:
        request = await self.request_factory(
            *args,
            **(await self.credential.preprocess_request(**kwargs))
        )
        return self.request_class.fromimpl(request)

    async def listall(
        self,
        model: type[M],
        *params: Any,
        url: str | None = None
    ) -> Generator[M, None, None]:
        """Like :meth:`list()`, but returns all entities."""
        meta = model.get_meta()
        response = await self.request(
            method='GET',
            url=url or model.get_list_url(*params),
            headers=meta.headers
        )
        response.raise_for_status()
        self.check_json(response.headers)
        data = self.process_response('list', await response.json())
        data = model.process_response('list', data)
        resources = [
            self.resource_factory(model, None, x)
            for x in data
        ]
        n = 0
        while resources:
            n =+ 1
            yield resources.pop(0)
        try:
            url = model.get_next_url(response, n)
        except StopIteration:
            url = None
        if url is None:
            return
        async for resource in self.listall(model, *params, url=url):
            yield resource

    async def list(self, model: type[M]) -> Generator[M, None, None]:
        """Discover the API endpoint using the class configuration
        and retrieve a list of instances using the HTTP GET verb.
        """
        meta = model.get_meta()
        response = await self.request(
            method='GET',
            url=model.get_list_url(),
            headers=meta.headers
        )
        response.raise_for_status()
        self.check_json(response.headers)
        data = self.process_response('list', await response.json())
        if inspect.isawaitable(data): data = await data
        data = model.process_response('list', data)
        resources = [
            self.resource_factory(model, None, x)
            for x in data
        ]
        for resource in resources:
            yield resource