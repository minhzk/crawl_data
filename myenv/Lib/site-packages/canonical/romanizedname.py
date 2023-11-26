# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import re

from .symbolicname import SymbolicName


pattern: str = r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{1,}$"


class RomanizedName(SymbolicName[2, 20, pattern]):
    """A string that contains a romanized personal name. A personal name is
    defined as follows:
    
    - Is at least 2 characters.
    - Begins with a word character, but not a number.
    - Contains at least one uppercase character for each space, dot
      or hyphen in the name, or consists of all uppercase characters.

    Automatic sanitation and transformation is performed on:

    - Stripping non-word characters from the beginning and the end of the
      name.
    - Normalizing whitespace, dots or hyphens to one character.
    - If the name does not contain a space, dot or hyphen, then the first
      character is capitalized.
    """

    @classmethod
    def validate(cls, v: str) -> str:
        v = re.sub(r'[^\w]+$', '', v)
        v = re.sub(r'^[^\w]+', '', v)
        v = re.sub(r'\s+', ' ', v)
        v = re.sub(r'\.+', '.', v)
        v = re.sub(r'\-+', '-', v)
        if str.isnumeric(v[0]):
            raise ValueError("Name cannot start with a number.")

        length: int = len(v)
        characters = list(v)
        for i, char in enumerate(characters):
            if (i + 1) == length:
                continue

            # If the character is a hyphen, then the next character
            # is capitalized.
            if char == '-':
                characters[i + 1] = str.upper(v[i + 1])

        v = ''.join(characters)
        if str.upper(v) != v:
            # If the name does not contain any spaces, hyphens or dots,
            # then it must start with a capital.
            if not re.findall(r'(\s|\-|\.)', v):
                characters[0] = str.upper(characters[0])

        return super().validate(str.join('', characters))

    def __repr__(self) -> str: # pragma: no cover
        return f'RomanizedName({self})'