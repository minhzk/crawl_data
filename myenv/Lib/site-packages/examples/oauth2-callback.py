# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import urllib.parse
from typing import Any

import fastapi
import uvicorn

from headless.ext.oauth2 import Client
from headless.ext.oauth2.models import ClientAuthenticationMethod
from headless.ext.oauth2.models import AuthorizationEndpointResponse
from headless.ext.teamleader import CurrentUser
from headless.ext.teamleader import TeamleaderClient
from headless.ext.teamleader import CustomFieldDefinition
from headless.ext.teamleader import Product
from headless.ext.teamleader import User


app: fastapi.FastAPI = fastapi.FastAPI()


client: Client = Client(
    client_id='95426b7f8f3878a21468201b165a2371',
    client_auth=ClientAuthenticationMethod.client_secret_post,
    client_secret='af5fd177321185f9ba36c78fb0a72cd5',
    authorization_endpoint='https://focus.teamleader.eu/oauth2/authorize',
    token_endpoint='https://focus.teamleader.eu/oauth2/access_token',
    token_endpoint_auth_methods_supported=[
        ClientAuthenticationMethod.client_secret_post
    ]
)


@app.get('/oauth2/callback')
async def oauth2_callback(request: fastapi.Request):
    q = dict(urllib.parse.parse_qsl(request.url.query))
    obj = AuthorizationEndpointResponse.parse_obj(q)
    at = await obj.exchange(
        client.token,
        redirect_uri=f'https://{request.url.netloc}{request.url.path}'
    )

    api = TeamleaderClient(
        base_url='https://api.focus.teamleader.eu/',
        credential=at.access_token
    )
    current_user = await api.retrieve(CurrentUser)
    await api.retrieve(User, current_user.id)
    async for user in api.list(User):
        print(f'{user.first_name} {user.last_name}')

    async for product in api.list(Product):
        print(f'{product.name} {product.code}')

    async for definition in api.list(CustomFieldDefinition):
        print(f'{definition.label} {definition.required}')

if __name__ == '__main__':
    uvicorn.run('__main__:app', reload=True)