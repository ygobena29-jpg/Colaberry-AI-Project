from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Resolved once at import time so lru_cache key is stable
_PRIVATE_KEY_PATH = os.getenv("JWT_PRIVATE_KEY_PATH", "/run/secrets/jwt_private_key")
_PUBLIC_KEY_PATH = os.getenv("JWT_PUBLIC_KEY_PATH", "/run/secrets/jwt_public_key")

# Local dev fallback paths (relative to this file's location: backend/app/security/)
_LOCAL_PRIVATE = Path(__file__).resolve().parents[3] / "secrets" / "jwt_private_key.pem"
_LOCAL_PUBLIC  = Path(__file__).resolve().parents[3] / "secrets" / "jwt_public_key.pem"


@lru_cache(maxsize=1)
def load_rsa_keys():
    """
    Loads RS256 keypair.

    Resolution order:
    1. Docker secret paths (production / docker-compose)
    2. Local secrets/ folder (local dev with real keys)
    3. Generated in-memory ephemeral keys (local dev, no key files)
    """
    priv_p = Path(_PRIVATE_KEY_PATH)
    pub_p  = Path(_PUBLIC_KEY_PATH)

    # 1. Docker secrets path
    if priv_p.exists() and pub_p.exists():
        private_key = serialization.load_pem_private_key(priv_p.read_bytes(), password=None)
        public_key  = serialization.load_pem_public_key(pub_p.read_bytes())
        return private_key, public_key

    # 2. Local secrets/ folder
    if _LOCAL_PRIVATE.exists() and _LOCAL_PUBLIC.exists():
        private_key = serialization.load_pem_private_key(_LOCAL_PRIVATE.read_bytes(), password=None)
        public_key  = serialization.load_pem_public_key(_LOCAL_PUBLIC.read_bytes())
        return private_key, public_key

    # 3. Ephemeral in-memory keys (local dev only — tokens won't survive restarts)
    print("WARNING: No JWT key files found. Generating ephemeral RSA keys for local dev.")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key  = private_key.public_key()
    return private_key, public_key
