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
