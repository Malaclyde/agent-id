"""
Agent Demo - Core Crypto Utilities and Configuration Management

Provides base64url encoding/decoding, canonical JSON serialization,
Ed25519 key management, DPoP proof construction, and .env configuration.
"""

from typing import Optional

import base64
import json
import os
import time
import uuid
import hashlib
from nacl.signing import SigningKey, VerifyKey
from urllib.parse import urlparse
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
# Canonical JSON Serialization
# =============================================================================


def canonicalize(obj: dict) -> str:
    """
    Deterministic JSON serialization per RFC 8785 principles.

    - Sorts keys alphabetically
    - No whitespace between elements
    - Booleans as lowercase true/false
    - null as null
    - Escapes special characters in strings (\\, ", \\n, \\r, \\t)
    """

    def serialize_value(o):
        if isinstance(o, dict):
            items = [f'"{k}":{serialize_value(v)}' for k, v in sorted(o.items())]
            return "{" + ",".join(items) + "}"
        elif isinstance(o, str):
            escaped = (
                o.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
            )
            return f'"{escaped}"'
        elif isinstance(o, bool):
            return "true" if o else "false"
        elif o is None:
            return "null"
        elif isinstance(o, (int, float)):
            return str(o)
        elif isinstance(o, list):
            return "[" + ",".join(serialize_value(i) for i in o) + "]"
        else:
            return str(o)

    return serialize_value(obj)


# =============================================================================
# DPoP Proof Construction
# =============================================================================


def hash_access_token(token: str) -> str:
    """SHA-256 hash of access token, base64url encoded."""
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return base64url_encode(digest)


def create_dpop_proof(
    private_key: SigningKey, method: str, uri: str, access_token: Optional[str] = None
) -> str:
    """
    Create DPoP proof JWT for authentication.

    Args:
        private_key: Ed25519 private key for signing
        method: HTTP method (GET, POST, etc.)
        uri: Target URI (will be normalized to scheme://host:path)
        access_token: Optional access token for 'ath' claim

    Returns:
        DPoP proof JWT string
    """
    public_key = private_key.verify_key
    public_b64url = base64url_encode(bytes(public_key))

    # Normalize URL for DPoP htu (no query params, no trailing slash)
    parsed = urlparse(uri)
    normalized_htu = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # JWT Header per DPoP spec
    header = {
        "typ": "dpop+jwt",
        "alg": "EdDSA",
        "jwk": {"kty": "OKP", "crv": "Ed25519", "x": public_b64url},
    }

    # JWT Payload
    payload = {
        "jti": str(uuid.uuid4()),
        "htm": method.upper(),
        "htu": normalized_htu,
        "iat": int(time.time()),
    }

    if access_token:
        payload["ath"] = hash_access_token(access_token)

    # Build signing input (base64url-encoded header.payload)
    encoded_header = base64url_encode_json(header)
    encoded_payload = base64url_encode_json(payload)
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    # Sign with Ed25519
    signed = private_key.sign(signing_input)
    signature = signed.signature
    encoded_signature = base64url_encode(signature)

    # Return complete JWT
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


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


def validate_keys_match(private_b64url: str, public_b64url: str) -> bool:
    """
    Validate that public key derives from private key.

    Args:
        private_b64url: Base64url-encoded 32-byte private key
        public_b64url: Base64url-encoded 32-byte public key

    Returns:
        True if public key derives from private key, False otherwise
    """
    try:
        private_key = load_private_key(private_b64url)
        derived_public = base64url_encode(bytes(private_key.verify_key))
        return derived_public == public_b64url
    except (ValueError, Exception):
        return False


# =============================================================================
# Configuration Management (.env handling)
# =============================================================================


ENV_FILE = ".env.agent"

# Mapping from internal config keys to environment variable names
ENV_KEYS = {
    "backend_url": "AGENT_BACKEND_URL",
    "private_key": "AGENT_PRIVATE_KEY",
    "public_key": "AGENT_PUBLIC_KEY",
    "agent_id": "AGENT_ID",
    "session_id": "AGENT_SESSION_ID",
}


def load_config(env_file: str = ENV_FILE) -> dict:
    """
    Load configuration from .env file.

    Args:
        env_file: Path to .env file (default: .env.agent)

    Returns:
        Dict with keys: backend_url, private_key, public_key, agent_id, session_id
        Values are None if not set in the file.
    """
    load_dotenv(env_file)
    return {
        "backend_url": os.getenv("AGENT_BACKEND_URL"),
        "private_key": os.getenv("AGENT_PRIVATE_KEY"),
        "public_key": os.getenv("AGENT_PUBLIC_KEY"),
        "agent_id": os.getenv("AGENT_ID"),
        "session_id": os.getenv("AGENT_SESSION_ID"),
    }


def save_config(config: dict, env_file: str = ENV_FILE) -> None:
    """
    Save configuration to .env file.

    Args:
        config: Dict with internal config keys (not env var names)
        env_file: Path to .env file (default: .env.agent)
    """
    for internal_key, env_value in config.items():
        if env_value is not None and internal_key in ENV_KEYS:
            env_var = ENV_KEYS[internal_key]
            set_key(env_file, env_var, str(env_value))


def validate_config(config: dict) -> tuple[bool, str]:
    """
    Validate configuration dictionary.

    Checks:
    - backend_url is set
    - private_key is set
    - public_key is set
    - If both keys present, validates they match (ACONF-03)

    Args:
        config: Configuration dict from load_config()

    Returns:
        Tuple of (is_valid, message)
        - (True, "OK") if valid
        - (False, "error message") if invalid
    """
    # Check required fields
    if not config.get("backend_url"):
        return False, "backend_url is required"

    if not config.get("private_key"):
        return False, "private_key is required"

    if not config.get("public_key"):
        return False, "public_key is required"

    # Validate key match (ACONF-03)
    private_key = config.get("private_key")
    public_key = config.get("public_key")

    if private_key and public_key:
        if not validate_keys_match(private_key, public_key):
            return False, "public_key does not derive from private_key"

    return True, "OK"
