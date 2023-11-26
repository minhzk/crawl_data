# pylint: disable=E0202,W0212
# Copyright © 2019, Encode OSS Ltd. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials
# provided with the distribution.
# 
# Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
from typing import Any
from typing import Iterator
from typing import ItemsView
from typing import KeysView
from typing import Mapping
from typing import MutableMapping
from typing import Sequence
from typing import Union
from typing import ValuesView


HeaderTypes = Union[
    "Headers",
    Mapping[str, str],
    Mapping[bytes, bytes],
    Sequence[tuple[str, str]],
    Sequence[tuple[bytes, bytes]],
]

class Headers(MutableMapping[str, str]):
    """
    HTTP headers, as a case-insensitive multi-dict.
    """

    @staticmethod
    def normalize_key(
        value: str | bytes,
        lower: bool,
        encoding: str | None = None,
    ) -> bytes:
        """
        Coerce str/bytes into a strictly byte-wise HTTP header key.
        """
        if isinstance(value, bytes):
            bytes_value = value
        else:
            bytes_value = value.encode(encoding or "ascii")

        return bytes_value.lower() if lower else bytes_value

    @staticmethod
    def normalize_value(
        value: str | bytes,
        encoding: str | None = None
    ) -> bytes:
        """
        Coerce str/bytes into a strictly byte-wise HTTP header value.
        """
        if isinstance(value, bytes):
            return value
        return value.encode(encoding or "ascii")

    def __init__(
        self,
        headers: HeaderTypes | None = None,
        encoding: str | None = None,
    ) -> None:
        if headers is None:
            self._list: list[tuple[bytes, bytes, bytes]] = []
        elif isinstance(headers, Headers):
            self._list = list(headers._list)
        elif isinstance(headers, Mapping):
            self._list = [
                (
                    Headers.normalize_key(k, lower=False, encoding=encoding),
                    Headers.normalize_key(k, lower=True, encoding=encoding),
                    Headers.normalize_value(v, encoding),
                )
                for k, v in headers.items()
            ]
        else:
            self._list = [
                (
                    Headers.normalize_key(k, lower=False, encoding=encoding),
                    Headers.normalize_key(k, lower=True, encoding=encoding),
                    Headers.normalize_value(v, encoding),
                )
                for k, v in headers
            ]

        self._encoding = encoding

    @property
    def encoding(self) -> str:
        """
        Header encoding is mandated as ascii, but we allow fallbacks to utf-8
        or iso-8859-1.
        """
        if self._encoding is None:
            for encoding in ["ascii", "utf-8"]:
                for key, value in self.raw:
                    try:
                        key.decode(encoding)
                        value.decode(encoding)
                    except UnicodeDecodeError:
                        break
                else:
                    # The else block runs if 'break' did not occur, meaning
                    # all values fitted the encoding.
                    self._encoding = encoding
                    break
            else:
                # The ISO-8859-1 encoding covers all 256 code points in a byte,
                # so will never raise decode errors.
                self._encoding = "iso-8859-1"
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        self._encoding = value

    @property
    def raw(self) -> list[tuple[bytes, bytes]]:
        """
        Returns a list of the raw header items, as byte pairs.
        """
        return [(raw_key, value) for raw_key, _, value in self._list]

    def keys(self) -> KeysView[str]:
        return {
            key.decode(self.encoding): None
            for _, key, value in self._list # type: ignore
        }.keys()

    def values(self) -> ValuesView[str]:
        values_dict: dict[str, str] = {}
        for _, key, value in self._list:
            str_key = key.decode(self.encoding)
            str_value = value.decode(self.encoding)
            if str_key in values_dict:
                values_dict[str_key] += f", {str_value}"
            else:
                values_dict[str_key] = str_value
        return values_dict.values()

    def items(self) -> ItemsView[str, str]:
        """
        Return `(key, value)` items of headers. Concatenate headers
        into a single comma separated value when a key occurs multiple times.
        """
        values_dict: dict[str, str] = {}
        for _, key, value in self._list:
            str_key = key.decode(self.encoding)
            str_value = value.decode(self.encoding)
            if str_key in values_dict:
                values_dict[str_key] += f", {str_value}"
            else:
                values_dict[str_key] = str_value
        return values_dict.items()

    def multi_items(self) -> list[tuple[str, str]]:
        """
        Return a list of `(key, value)` pairs of headers. Allow multiple
        occurrences of the same key without concatenating into a single
        comma separated value.
        """
        return [
            (key.decode(self.encoding), value.decode(self.encoding))
            for _, key, value in self._list
        ]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Return a header value. If multiple occurrences of the header occur
        then concatenate them together with commas.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_list(self, key: str, split_commas: bool = False) -> list[str]:
        """
        Return a list of all header values for a given key.
        If `split_commas=True` is passed, then any comma separated header
        values are split into multiple return strings.
        """
        get_header_key = key.lower().encode(self.encoding)

        values = [
            item_value.decode(self.encoding)
            for _, item_key, item_value in self._list
            if item_key.lower() == get_header_key
        ]

        if not split_commas:
            return values

        split_values: list[str] = []
        for value in values:
            split_values.extend([item.strip() for item in value.split(",")])
        return split_values

    def update(self, headers: HeaderTypes | None = None) -> None:  # type: ignore
        headers = Headers(headers)
        for key in headers.keys():
            if key in self:
                self.pop(key)
        self._list.extend(headers._list)

    def copy(self) -> "Headers":
        return Headers(self, encoding=self.encoding)

    def __getitem__(self, key: str) -> str:
        """
        Return a single header value.
        If there are multiple headers with the same key, then we concatenate
        them with commas. See: https://tools.ietf.org/html/rfc7230#section-3.2.2
        """
        normalized_key = key.lower().encode(self.encoding)

        items = [
            header_value.decode(self.encoding)
            for _, header_key, header_value in self._list
            if header_key == normalized_key
        ]

        if items:
            return ", ".join(items)

        raise KeyError(key)

    def __setitem__(self, key: str, value: str) -> None:
        """
        Set the header `key` to `value`, removing any duplicate entries.
        Retains insertion order.
        """
        set_key = key.encode(self._encoding or "utf-8")
        set_value = value.encode(self._encoding or "utf-8")
        lookup_key = set_key.lower()

        found_indexes = [
            idx
            for idx, (_, item_key, _) in enumerate(self._list)
            if item_key == lookup_key
        ]

        for idx in reversed(found_indexes[1:]):
            del self._list[idx]

        if found_indexes:
            idx = found_indexes[0]
            self._list[idx] = (set_key, lookup_key, set_value)
        else:
            self._list.append((set_key, lookup_key, set_value))

    def __delitem__(self, key: str) -> None:
        """
        Remove the header `key`.
        """
        del_key = key.lower().encode(self.encoding)

        pop_indexes = [
            idx
            for idx, (_, item_key, _) in enumerate(self._list)
            if item_key.lower() == del_key
        ]

        if not pop_indexes:
            raise KeyError(key)

        for idx in reversed(pop_indexes):
            del self._list[idx]

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator[tuple[str, str]]: # type: ignore
        return iter(self.multi_items())