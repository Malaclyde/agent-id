"""
Client Demo - CLI Interface for OAuth Client Operations

This module provides a command-line interface for:
- PKCE verifier and challenge generation
- Ed25519 keypair management for client authentication
- OAuth2 token exchange with blocking callback server
- Token refresh, revocation, and introspection
- Querying userinfo (DPoP-bound)

Usage:
    python client-demo.py generate-verifier
    python client-demo.py generate-keys
    python client-demo.py token-exchange --token <auth-code> --code-verifier <verifier>
"""

import base64
import json
import os
import sys
import argparse
from nacl.signing import SigningKey, VerifyKey
from dotenv import load_dotenv, set_key


# =============================================================================
# Base64url Encoding/Decoding
# =============================================================================


def base64url_encode(data: bytes) -> str:
    """Encode bytes to base64url WITHOUT padding (strip trailing '=')."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def base64url_decode(data: str) -> bytes:
    """Decode base64url to bytes, adding padding if needed."""
    padding = "=" * (4 - len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def base64url_encode_json(obj: dict) -> str:
    """JSON-encode dict with no whitespace, then base64url encode."""
    return base64url_encode(json.dumps(obj, separators=(",", ":")).encode("utf-8"))


# =============================================================================
# Ed25519 Key Management
# =============================================================================


def generate_keypair() -> tuple[str, str]:
    """
    Generate new Ed25519 keypair.

    Returns:
        Tuple of (private_key_b64url, public_key_b64url)
    """
    private_key = SigningKey.generate()
    public_key = private_key.verify_key

    private_b64url = base64url_encode(bytes(private_key))
    public_b64url = base64url_encode(bytes(public_key))

    return private_b64url, public_b64url


def load_private_key(private_b64url: str) -> SigningKey:
    """
    Load Ed25519 private key from base64url-encoded string.

    Args:
        private_b64url: Base64url-encoded 32-byte private key

    Returns:
        SigningKey instance

    Raises:
        ValueError: If key is not 32 bytes
    """
    private_bytes = base64url_decode(private_b64url)
    if len(private_bytes) != 32:
        raise ValueError(f"Private key must be 32 bytes, got {len(private_bytes)}")
    return SigningKey(private_bytes)


def load_public_key(public_b64url: str) -> VerifyKey:
    """
    Load Ed25519 public key from base64url-encoded string.

    Args:
        public_b64url: Base64url-encoded 32-byte public key

    Returns:
        VerifyKey instance

    Raises:
        ValueError: If key is not 32 bytes
    """
    public_bytes = base64url_decode(public_b64url)
    if len(public_bytes) != 32:
        raise ValueError(f"Public key must be 32 bytes, got {len(public_bytes)}")
    return VerifyKey(public_bytes)


def validate_keys_match(private_b64url: str, public_b64url: str) -> tuple[bool, str]:
    """
    Validate that public key derives from private key.

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        private_key = load_private_key(private_b64url)
        derived_public = base64url_encode(bytes(private_key.verify_key))
        if derived_public == public_b64url:
            return True, "OK"
        return False, "Public key does not match private key"
    except Exception as e:
        return False, f"Key validation failed: {str(e)}"


# =============================================================================
# Configuration Management (.env handling)
# =============================================================================


ENV_FILE = ".env"

# Mapping from internal config keys to environment variable names
ENV_KEYS = {
    "backend_url": "BACKEND_URL",
    "client_id": "CLIENT_ID",
    "private_key": "CLIENT_PRIVATE_KEY",
    "public_key": "CLIENT_PUBLIC_KEY",
    "client_url": "CLIENT_URL",
    "client_port": "CLIENT_PORT",
}


def load_config(env_file: str = ENV_FILE) -> dict:
    """
    Load configuration from .env file.

    Args:
        env_file: Path to .env file (default: .env)

    Returns:
        Dict with keys: backend_url, client_id, private_key, public_key, client_url, client_port
        Values are None if not set in the file.
    """
    load_dotenv(env_file)
    return {
        "backend_url": os.getenv("BACKEND_URL"),
        "client_id": os.getenv("CLIENT_ID"),
        "private_key": os.getenv("CLIENT_PRIVATE_KEY"),
        "public_key": os.getenv("CLIENT_PUBLIC_KEY"),
        "client_url": os.getenv("CLIENT_URL", "localhost"),
        "client_port": os.getenv("CLIENT_PORT", "8790"),
    }


def save_config(config: dict, env_file: str = ENV_FILE) -> None:
    """
    Save configuration to .env file.

    Args:
        config: Dict with internal config keys (not env var names)
        env_file: Path to .env file (default: .env)
    """
    for internal_key, value in config.items():
        if value is not None and internal_key in ENV_KEYS:
            env_var = ENV_KEYS[internal_key]
            set_key(env_file, env_var, str(value))


def validate_config(config: dict) -> tuple[bool, str]:
    """
    Validate configuration dictionary.

    Checks:
    - backend_url is set
    - client_id is set
    - Check private_key and public_key are both set (or neither)
    - If both keys present, validate they match using validate_keys_match

    Args:
        config: Configuration dict from load_config()

    Returns:
        Tuple of (is_valid, message)
    """
    if not config.get("backend_url"):
        return False, "backend_url is required"

    if not config.get("client_id"):
        return False, "client_id is required"

    private_key = config.get("private_key")
    public_key = config.get("public_key")

    if (private_key and not public_key) or (public_key and not private_key):
        return False, "Both private_key and public_key must be set (or neither)"

    if private_key and public_key:
        is_valid, msg = validate_keys_match(private_key, public_key)
        if not is_valid:
            return False, f"Keys do not match: {msg}"

    return True, "OK"


# =============================================================================
# CLI Interface
# =============================================================================


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Client Demo - CLI Interface for OAuth Client Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate-verifier command (placeholder)
    subparsers.add_parser(
        "generate-verifier",
        help="Generate PKCE verifier and challenge pair",
    )

    # generate-keys command (placeholder)
    subparsers.add_parser(
        "generate-keys",
        help="Generate new Ed25519 keypair",
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
