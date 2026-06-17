"""Mã hóa dữ liệu nhạy cảm (YouTube session cookies)."""
import base64
import os
from cryptography.fernet import Fernet

# Key cố định (trong production nên lưu vào biến môi trường)
_KEY_FILE = os.path.join(os.path.dirname(__file__), 'data', '.secret_key')


def _get_or_create_key() -> bytes:
    os.makedirs(os.path.dirname(_KEY_FILE), exist_ok=True)
    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    with open(_KEY_FILE, 'wb') as f:
        f.write(key)
    return key


_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_or_create_key())
    return _fernet


def encrypt(text: str) -> str:
    """Mã hóa chuỗi, trả về chuỗi base64."""
    return _get_fernet().encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    """Giải mã chuỗi đã mã hóa."""
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except Exception:
        return ''
