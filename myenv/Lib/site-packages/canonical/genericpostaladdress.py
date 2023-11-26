# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from .genericdeliverypointspecification import GenericDeliveryPointSpecification


class GenericPostalAddress(GenericDeliveryPointSpecification):
    """A generic postal address. It is assumed that further validation
    is done upstream.
    """
    addressee: str = pydantic.Field(
        default=...,
        max_length=31,
        title='Address',
        description=(
            "The addressee line of the address. If the receiver is a person, "
            "this field contains its name. For organizations, the receiver may "
            "be further specified using the `contact_name` field."
        )
    )

    contact_name: str = pydantic.Field(
        default='',
        max_length=31,
        title='Contact name',
        alias='contactName',
        description=(
            "The name of the receiver. Use this field when sending, for example, "
            "to an organization with a specific person."
        )
    )

    class Config(GenericDeliveryPointSpecification.Config):
        allow_population_by_field_name: bool = True