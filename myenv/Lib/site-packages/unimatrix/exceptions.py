"""Declares common exceptions for all Unimatrix packages."""
import uuid
from typing import Any
from typing import Callable

from .lib import timezone


__all__ = [
    'CanonicalException',
    'ImproperlyConfigured',
    'ProgrammingError',
]


class ImproperlyConfigured(RuntimeError):
    """Raised when an invalid or illegal configuration was detected."""
    pass


class ProgrammingError(Exception):
    """Raised when parts of the framework are implemented incorrectly."""
    pass


class CanonicalExceptionMetaclass(type):
    http_status_code: int

    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]):
        new_class = super().__new__(cls, name, bases, attrs)
        if new_class.http_status_code is not None\
        and new_class not in CanonicalException.registered:
            CanonicalException.registered.append(new_class)
        return new_class


class CanonicalException(Exception, metaclass=CanonicalExceptionMetaclass):
    """The base class for all exceptions."""
    __module__: str = 'unimatrix.exceptions'
    registered: list[CanonicalExceptionMetaclass] = []

    #: The HTTP default HTTP status code.
    http_status_code: int | None = None

    #: The default code for the exception.
    code: str = 'UNCAUGHT_EXCEPTION'

    #: The default message.
    message: str | None = None

    #: The default detail.
    detail: str | None = None

    #: The default hint
    hint: str | None = None

    #: The default log message. String formatting is applied.
    log_message: str = "Caught fatal {code} (id: {id})"

    #: The cooldown period enforced on the caller.
    backoff: dict[str, Any] | None = None

    @property
    def http_headers(self) -> dict[str, str]:
        """The HTTP headers when returning this exception to a client."""
        return self.get_http_headers()

    def __init__(
        self,
        id: str | None = None,
        code: str | None = None,
        message: str | None = None,
        detail: str | None = None,
        hint: str | None = None,
        http_status_code: int | None = None,
        **params: Any
    ):
        """Initialize a new :class:`CanonicalException`."""
        self.id = id or uuid.uuid4()
        self.code = code or self.code
        self.message = message or self.message
        self.detail = detail or self.detail
        self.hint = hint or self.hint
        self.http_status_code = http_status_code or self.http_status_code
        self.params = params
        self.backoff = None
        self.timestamp = timezone.now()

    def as_dict(self) -> dict[str, Any]:
        """Return a dictionary containing the exception properties."""
        return {
            'apiVersion': "v1",
            'kind': type(self).__name__,
            'type': "unimatrixone.io/error",
            'metadata': {
                'id': str(self.id),
                'timestamp': self.timestamp
            },
            'spec': {
                'code': self.code,
                'message': self.message,
                'detail': self.detail,
                'hint': self.hint,
                'fieldErrors': {},
            }
        }

    def get_http_headers(self) -> dict[str, str]:
        """Return a dictionary containing the HTTP headers to add to
        a client response.
        """
        return {
            'Cache-Control': "no-cache, no-store, must-revalidate",
            'Expires': "0",
            'Pragma': "no-cache",
            'X-Error-Code': self.code,
            'X-Canonical-Exception': type(self).__name__,
        }

    def log(
        self,
        func: Callable[..., Any],
        message: str | None = None
    ) -> None:
        """Use `logger` to log the exception as `level`."""
        pass

    def set_backoff(self,
        ttl: int,
        expires: int,
        attempts: int,
        timestamp: int
    ) -> None:
        """Set a backoff (cooldown) period that indicating how
        long the caller wait before retrying the request that
        caused the :class:`CanonicalException`.
        """
        self.backoff = {
            'ttl': ttl,
            'expires': expires,
            'attempts': attempts,
            'timestamp': timestamp
        }

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'<{type(self).__name__}: {self.code} (id: {self.id})>'


class UpstreamFailure(CanonicalException):
    code = 'UPSTREAM_FAILURE'
    http_status_code = 503
    message = "An upstream service caused a degradation of service quality."
