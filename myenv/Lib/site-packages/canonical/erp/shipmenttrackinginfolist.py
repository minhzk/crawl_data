# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from ..collectionmixin import CollectionMixin
from .shipmenttrackinginfo import ShipmentTrackingInfo


class ShipmentTrackingInfoList(list[ShipmentTrackingInfo], CollectionMixin):

    def has(self, trackingcode: str) -> bool:
        """Return a boolean if the :class:`ShipmentTrackingInfoList`
        holds any shipment with the given tracking code.
        """
        return any([getattr(x.trace, 'number', None) is not None for x in self])