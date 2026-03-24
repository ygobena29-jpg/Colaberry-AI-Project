import os
from pathlib import Path

# Point JWT key loader at the local secrets directory when running outside Docker
_secrets_dir = Path(__file__).resolve().parents[2] / "secrets"
os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(_secrets_dir / "jwt_private_key.pem"))
os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(_secrets_dir / "jwt_public_key.pem"))
