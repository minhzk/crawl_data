# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

.. _impl-picqer

======
Picqer
======


.. envvar: PICQER_API_DOMAIN

.. envvar: PICQER_API_EMAIL

.. envvar: PICQER_API_KEY
"""

from .client import Client
from .credential import PicqerCredential
from .defaultclient import DefaultClient
from .v1 import *


__all__: list[str] = [
    'DefaultClient',
    'Client',
    'PicqerCredential',
    'Order',
    'Picklist',
    'PicklistStatus',
    'Product',
    'PurchaseOrder',
    'Supplier',
    'User',
    'Warehouse',
    'Webhook',
]