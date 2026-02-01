import base64
import hashlib
import platform
from cryptography.fernet import Fernet


def _derive_key() -> bytes:
    machine_id = f"{platform.node()}-{platform.machine()}-slide-alchemy"
    key_bytes = hashlib.sha256(machine_id.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


def get_fernet() -> Fernet:
    return Fernet(_derive_key())


def encrypt_value(value: str) -> str:
    f = get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted.encode()).decode()
