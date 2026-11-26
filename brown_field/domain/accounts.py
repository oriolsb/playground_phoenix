"""The password digest of an account (STORE-3, contested).

Every stored account depends on this exact format.
"""

import hashlib


def password_hash(password: str) -> str:
    # TODO: bcrypt (2023)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
