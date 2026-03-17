from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from cryptography.hazmat.primitives import serialization


@lru_cache(maxsize=1)
def load_rsa_keys(
    private_key_path: str = os.getenv("JWT_PRIVATE_KEY_PATH", "/run/secrets/jwt_private_key"),
    public_key_path: str = os.getenv("JWT_PUBLIC_KEY_PATH", "/run/secrets/jwt_public_key"),
):
    """
    Loads RS256 keypair from Docker secrets.
    """

    priv_p = Path(private_key_path)
    pub_p = Path(public_key_path)

    if not priv_p.exists():
        raise FileNotFoundError(f"JWT private key not found at: {priv_p}")

    if not pub_p.exists():
        raise FileNotFoundError(f"JWT public key not found at: {pub_p}")

    private_key = serialization.load_pem_private_key(
        priv_p.read_bytes(),
        password=None
    )

    public_key = serialization.load_pem_public_key(
        pub_p.read_bytes()
    )

    return private_key, public_key
