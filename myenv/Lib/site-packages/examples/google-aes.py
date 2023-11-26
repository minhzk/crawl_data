import os

from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import GCM
from google.cloud import kms



algorithm = AES(b'0' * 32)



def encrypt_local(pt: bytes) -> tuple[bytes, bytes]:
    iv = os.urandom(12)
    cipher = Cipher(algorithm, GCM(iv))
    e = cipher.encryptor()
    ct = e.update(pt) + e.finalize()
    return (ct, iv)



if __name__ == '__main__':
    breakpoint()
