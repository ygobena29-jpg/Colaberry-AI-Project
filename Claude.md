# Project Control File

This project follows the Colaberry Internship Build System.

Rules:
- Human makes final decisions.
- One step at a time.
- All work happens inside VS Code.
- GitHub is the system of record.
- Claude Code assists but does not decide.
- Changes must be verified before commit.
Verification: Claude.md is the active control file for this repo.
Confirm Claude.md exists at the repository root.
Read it fully and summarize the rules you must follow in this repo.
Do not change any code.
Explicitly confirm you will follow those rules.
Hello

mkdir -p secrets

# Generate a 2048-bit RSA private key
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out secrets/jwt_private_key.pem

# Derive the public key from the private key
openssl rsa -pubout -in secrets/jwt_private_key.pem -out secrets/jwt_public_key.pem

# Lock down permissions (macOS/Linux)
chmod 600 secrets/jwt_private_key.pem
chmod 644 secrets/jwt_public_key.pem
"C:\Users\yubeh\Documents\Colaberry-AI-Project"
