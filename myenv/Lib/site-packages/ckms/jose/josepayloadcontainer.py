"""Declares :class:`JOSEPayloadContainer`."""
import typing


class JOSEPayloadContainer:
    """Specifies the interface for objects that can contain a payload."""
    __module__: str = 'ckms.jose'
    content_type: str | None
    token_type: str | None

    @property
    def content_type(self) -> str | None:
        return self.header.cty

    def accept(
        self,
        token_type: set[str] | None = None,
        content_type: set[str] | None = None,
    ):
        # Only perform this validation if the payload is not nested.
        if str.lower(self.content_type or '') == 'jwt':
            return

    async def get_payload(
        self,
        codec: 'PayloadCodec'
    ) -> typing.Union[bytes, str, 'JOSEPayloadContainer']:
        """Get the payload of the container object."""
        raise NotImplementedError