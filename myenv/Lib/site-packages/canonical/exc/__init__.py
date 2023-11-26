# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .canonicalexception import CanonicalException
from .missingshippingdestination import MissingShippingDestination
from .ratelimited import RateLimited
from .staleresource import StaleResource
from .upstreamservicefailure import UpstreamServiceFailure


__all__: list[str] = [
    'CanonicalException',
    'MissingShippingDestination',
    'RateLimited',
    'StaleResource',
    'UpstreamServiceFailure',
]