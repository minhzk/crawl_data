# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
from .credential import PicqerCredential


class PicqerEnvironmentCredential(PicqerCredential):
    """A :class:`~headless.ext.picqer.PicqerCredential` implementation
    that is discovered from environment variables.
    """

    def __init__(self):
        super().__init__(
            api_email=os.environ['PICQER_API_EMAIL'],
            api_key=os.environ['PICQER_API_KEY']
        )