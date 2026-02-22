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
from nacl.signing import SigningKey, VerifyKey

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
