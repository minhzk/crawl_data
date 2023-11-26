# pylint: skip-file
import base64
import binascii
import datetime
import json
import hashlib
from typing import Any

from cryptography.hazmat.primitives.asymmetric import utils


def b64encode_json(obj: dict[str, Any]) -> bytes:
    return b64encode(json.dumps(obj, sort_keys=True), 'utf-8')


def b64encode(buf: bytes | str, encoding: str = 'utf-8') -> bytes: # pragma: no cover
    if isinstance(buf, str):
        buf = str.encode(buf, encoding=encoding)
    return base64.urlsafe_b64encode(buf).replace(b"=", b"")


def b64encode_sha1(value: bytes) -> bytes:
    return b64encode(hashlib.sha1(value).digest())


def b64encode_sha256(value: bytes) -> bytes:
    return b64encode(hashlib.sha256(value).digest())


def b64encode_str(*args: Any, **kwargs: Any) -> str:
    return bytes.decode(b64encode(*args, **kwargs), 'ascii')


def b64encode_int(value: int) -> bytes: # pragma: no cover
    return b64encode(int.to_bytes(value, (value.bit_length() + 7) // 8, 'big'))


def b64decode(buf: bytes | str) -> bytes: # pragma: no cover
    if isinstance(buf, str):
        buf = buf.encode("ascii")
    rem = len(buf) % 4
    if rem > 0:
        buf += b"=" * (4 - rem)
    return base64.urlsafe_b64decode(buf)


def b64decode_json(
    buf: bytes | str,
    encoding: str = 'utf-8',
    on_failure: BaseException | None = None,
    require: type[list[Any]] | type[dict[str, Any]] | None = None
) -> dict[str, Any] | list[Any]:
    """Deserialize a Base64-encoded string or byte-sequence as JSON."""
    try:
        result = json.loads(bytes.decode(b64decode(buf), encoding))
        if not isinstance(result, (require,) if require else (dict, list)):
            raise ValueError 
    except ValueError as exception:
        raise (on_failure or exception)
    return result


def b64decode_int(value: bytes | str) -> int:
    return bytes_to_number(b64decode(value))


def current_timestamp() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def number_to_bytes(value: int, l: int) -> bytes: # pragma: no cover
    padded = str.encode("%0*x" % (2 * l, value), "ascii")
    return binascii.a2b_hex(padded)


def bytes_to_number(value: bytes) -> int: # pragma: no cover
    return int(binascii.b2a_hex(value), 16)


def normalize_ec_signature(l: int, sig: bytes): # pragma: no cover
    r, s = utils.decode_dss_signature(sig)
    return number_to_bytes(r, l) + number_to_bytes(s, l)


def certificate_chain(pem: bytes) -> list[bytes]:
    """Split a PEM-encoded certificate chain into a list of
    individual certificates.
    """
    linesep = b'\n'
    start_line = b'-----BEGIN CERTIFICATE-----' + linesep
    cleaned_data = bytes.join(linesep, [
        x for x in bytes.split(pem, linesep)
        if not x.startswith(b'#')
    ])
    return [
        (start_line + x)
        for x in bytes.split(cleaned_data, start_line) if x
    ]