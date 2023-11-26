# Copyright (C) 2020-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""Declares :class:`ResponseType`."""
import enum


class ResponseType(str, enum.Enum):
    code = "code"
    code_id_token = "code id_token"
    code_id_token_token = "code id_token token"
    code_token = "code token"
    id_token = "id_token"
    id_token_token = "id_token token"
    none = "none"
    token = "token"