"""
Agent Demo - CLI Interface for Agent Authentication and Configuration

This module provides a command-line interface for:
- Generating Ed25519 keypairs
- Registering agents with challenge-response flow
- Authenticating with DPoP proof
- Querying agent information
- Managing sessions

Usage:
    python agent_demo.py generate-keys
    python agent_demo.py register --name "My Agent" --description "A demo agent"
    python agent_demo.py login
    python agent_demo.py info
    python agent_demo.py logout
    python agent_demo.py config
"""

import argparse
import sys
from typing import Optional

import base64
import json
import os
import time
import uuid
import hashlib
import urllib.request
import urllib.error
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
    "private_key": "AGENT_PRIVATE_KEY",
    "public_key": "AGENT_PUBLIC_KEY",
    "agent_id": "AGENT_ID",
    "session_id": "AGENT_SESSION_ID",
}


def load_config(env_file: str = ENV_FILE) -> dict:
    """
    Load configuration from .env file.

    Args:
        env_file: Path to .env file (default: .env)

    Returns:
        Dict with keys: backend_url, private_key, public_key, agent_id, session_id
        Values are None if not set in the file.
    """
    load_dotenv(env_file)
    return {
        "backend_url": os.getenv("BACKEND_URL"),
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
        env_file: Path to .env file (default: .env)
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


# =============================================================================
# Agent Registration (Challenge-Response Flow)
# =============================================================================


class RegistrationError(Exception):
    """Exception raised for registration failures."""

    pass


def register_agent_initiate(
    backend_url: str, name: str, public_key: str, description: Optional[str] = None
) -> dict:
    """
    Initiate agent registration with name and public key.

    Sends a POST request to /v1/agents/register/initiate with the agent's
    name and Ed25519 public key. Returns challenge data that must be signed
    to complete registration.

    Args:
        backend_url: Base URL of the backend API
        name: Agent name
        public_key: Base64url-encoded Ed25519 public key
        description: Optional agent description

    Returns:
        Dict with keys:
        - challenge_id: UUID string for the challenge
        - expires_at: ISO timestamp when challenge expires
        - challenge_data: Canonicalized JSON string to sign

    Raises:
        RegistrationError: If registration initiate fails
    """
    # Build request body
    body = {"name": name, "public_key": public_key}
    if description:
        body["description"] = description

    # Make POST request
    url = f"{backend_url}/v1/agents/register/initiate"
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            error_msg = error_body.get("error", str(e))
        except (json.JSONDecodeError, Exception):
            error_msg = str(e)
        raise RegistrationError(f"Registration initiate failed: {error_msg}")
    except urllib.error.URLError as e:
        raise RegistrationError(f"Network error: {e.reason}")


def register_agent_complete(
    backend_url: str, challenge_id: str, private_key: SigningKey, challenge_data: str
) -> dict:
    """
    Complete agent registration by signing challenge data.

    Signs the challenge_data with the agent's Ed25519 private key and
    sends it to the backend to complete registration.

    Args:
        backend_url: Base URL of the backend API
        challenge_id: Challenge ID from initiate response
        private_key: Ed25519 private key (SigningKey)
        challenge_data: Challenge string from initiate response

    Returns:
        Dict with keys:
        - agent: Agent object with id, name, public_key, etc.
        - session_id: Session token for authenticated requests

    Raises:
        RegistrationError: If registration complete fails
    """
    # Sign challenge_data directly (already canonicalized by backend)
    signed = private_key.sign(challenge_data.encode("utf-8"))
    signature_b64url = base64url_encode(signed.signature)

    # Make POST request
    url = f"{backend_url}/v1/agents/register/complete/{challenge_id}"
    body = {"signature": signature_b64url}
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            error_msg = error_body.get("error", str(e))
        except (json.JSONDecodeError, Exception):
            error_msg = str(e)
        raise RegistrationError(f"Registration complete failed: {error_msg}")
    except urllib.error.URLError as e:
        raise RegistrationError(f"Network error: {e.reason}")


def register_agent(
    backend_url: str,
    name: str,
    private_key: SigningKey,
    description: Optional[str] = None,
) -> dict:
    """
    Complete two-step agent registration in one call.

    Convenience function that combines initiate and complete steps.
    Generates public key from private key, initiates registration,
    signs challenge, and completes registration.

    Args:
        backend_url: Base URL of the backend API
        name: Agent name
        private_key: Ed25519 private key (SigningKey)
        description: Optional agent description

    Returns:
        Dict with keys:
        - agent: Agent object with id, name, public_key, etc.
        - session_id: Session token for authenticated requests

    Raises:
        RegistrationError: If registration fails at any step
    """
    # Derive public key from private key
    public_key_b64url = base64url_encode(bytes(private_key.verify_key))

    # Step 1: Initiate registration
    initiate_result = register_agent_initiate(
        backend_url=backend_url,
        name=name,
        public_key=public_key_b64url,
        description=description,
    )

    challenge_id = initiate_result["challenge_id"]
    challenge_data = initiate_result["challenge_data"]

    # Step 2: Complete registration with signature
    result = register_agent_complete(
        backend_url=backend_url,
        challenge_id=challenge_id,
        private_key=private_key,
        challenge_data=challenge_data,
    )

    return result


# =============================================================================
# Agent Authentication (Login, Logout, Info)
# =============================================================================


class AuthenticationError(Exception):
    """Exception raised for authentication failures."""

    pass


def login_agent(backend_url: str, agent_id: str, private_key: SigningKey) -> dict:
    """
    Login with DPoP proof authentication.

    Creates a DPoP proof JWT and POSTs to /v1/agents/login to establish
    a session. The DPoP proof binds the session to the agent's private key.

    Args:
        backend_url: Base URL of the backend API
        agent_id: Agent ID to authenticate
        private_key: Ed25519 private key (SigningKey)

    Returns:
        Dict with keys:
        - session_id: Session token for authenticated requests
        - expires_in: Session lifetime in seconds (typically 1800)

    Raises:
        AuthenticationError: If login fails
    """
    # Build login URL
    login_url = f"{backend_url}/v1/agents/login"

    # Normalize URL for DPoP HTU (no query params, no trailing slash)
    parsed = urlparse(login_url)
    normalized_htu = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Create DPoP proof
    dpop_proof = create_dpop_proof(private_key, "POST", normalized_htu)

    # Build request
    body = {"agent_id": agent_id}
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        login_url,
        data=data,
        headers={"Content-Type": "application/json", "DPoP": dpop_proof},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            error_msg = error_body.get("error", str(e))
        except (json.JSONDecodeError, Exception):
            error_msg = str(e)
        raise AuthenticationError(f"Login failed: {error_msg}")
    except urllib.error.URLError as e:
        raise AuthenticationError(f"Network error: {e.reason}")


def logout_agent(backend_url: str, session_id: str) -> bool:
    """
    Logout and revoke session.

    POSTs to /v1/agents/logout with Bearer token authentication
    to revoke the session.

    Args:
        backend_url: Base URL of the backend API
        session_id: Session token to revoke

    Returns:
        True if logout successful, False otherwise

    Raises:
        AuthenticationError: If logout request fails due to network error
    """
    logout_url = f"{backend_url}/v1/agents/logout"

    req = urllib.request.Request(
        logout_url,
        headers={"Authorization": f"Bearer {session_id}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("success", False)
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            error_msg = error_body.get("error", str(e))
        except (json.JSONDecodeError, Exception):
            error_msg = str(e)
        raise AuthenticationError(f"Logout failed: {error_msg}")
    except urllib.error.URLError as e:
        raise AuthenticationError(f"Network error: {e.reason}")


def get_agent_info(backend_url: str, session_id: str) -> dict:
    """
    Get current agent information.

    GETs /v1/agents/me with Bearer token authentication to retrieve
    the authenticated agent's information.

    Args:
        backend_url: Base URL of the backend API
        session_id: Session token for authentication

    Returns:
        Dict with keys:
        - agent: Agent object with id, name, description, created_at, etc.

    Raises:
        AuthenticationError: If request fails
    """
    info_url = f"{backend_url}/v1/agents/me"

    req = urllib.request.Request(
        info_url,
        headers={"Authorization": f"Bearer {session_id}"},
        method="GET",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read().decode("utf-8"))
            error_msg = error_body.get("error", str(e))
        except (json.JSONDecodeError, Exception):
            error_msg = str(e)
        raise AuthenticationError(f"Get agent info failed: {error_msg}")
    except urllib.error.URLError as e:
        raise AuthenticationError(f"Network error: {e.reason}")


# =============================================================================
# Fail-Fast HTTP Wrapper
# =============================================================================


def make_request(
    url: str, headers: dict, data: Optional[bytes] = None, method: Optional[str] = None
) -> str:
    """
    Unified fail-fast HTTP wrapper.

    Executes an HTTP request using urllib.request.urlopen. On HTTPError,
    prints the raw unadulterated response body to stderr and immediately
    exits via sys.exit(1).

    Args:
        url: Full URL to request
        headers: Dict of HTTP headers
        data: Optional request body bytes
        method: HTTP method (GET, POST, etc.). Auto-detected if None.

    Returns:
        Response body as string
    """
    if method is None:
        method = "POST" if data is not None else "GET"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def print_output(response_string: str) -> None:
    """
    Parse response string into a Python dict and pretty-print as JSON.

    Outputs the full response without pagination or truncation.

    Args:
        response_string: Raw JSON response string from API
    """
    obj = json.loads(response_string)
    print(json.dumps(obj, indent=2))


# =============================================================================
# CLI Interface
# =============================================================================


def cmd_generate_keys(args) -> int:
    """Generate new Ed25519 keypair and optionally save to config."""
    try:
        private_b64url, public_b64url = generate_keypair()

        if getattr(args, "save", False):
            config = load_config()
            config["private_key"] = private_b64url
            config["public_key"] = public_b64url
            save_config(config)
            print("Keys generated and saved successfully!")
            print(f"Public key: {public_b64url}")
            print("Private key: [saved to .env]")
        else:
            print("Keys generated successfully!")
            print(f"Public key: {public_b64url}")
            print(f"Private key: {private_b64url}")
            print("\nNote: Keys were NOT saved. Use --save to save them to .env")
        return 0
    except Exception as e:
        print(f"Error generating keys: {e}", file=sys.stderr)
        return 1


def cmd_register(args) -> int:
    """Register a new agent with the backend."""
    try:
        # Load and validate config
        config = load_config()
        is_valid, msg = validate_config(config)
        if not is_valid:
            print(f"Config validation failed: {msg}", file=sys.stderr)
            print("Run 'python agent_demo.py generate-keys' first.", file=sys.stderr)
            return 1

        # Load private key
        private_key = load_private_key(config["private_key"])

        # Register agent
        print(f"Registering agent: {args.name}...")
        result = register_agent(
            backend_url=config["backend_url"],
            name=args.name,
            private_key=private_key,
            description=args.description,
        )

        # Save agent_id and session_id
        agent_id = result["agent"]["id"]
        session_id = result["session_id"]

        config["agent_id"] = agent_id
        config["session_id"] = session_id
        save_config(config)

        print("Agent registered successfully!")
        print(json.dumps(result, indent=2))
        return 0
    except RegistrationError as e:
        print(f"Registration failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_login(args) -> int:
    """Login with DPoP authentication."""
    try:
        # Load and validate config
        config = load_config()
        is_valid, msg = validate_config(config)
        if not is_valid:
            print(f"Config validation failed: {msg}", file=sys.stderr)
            return 1

        if not config.get("agent_id"):
            print(
                "No agent_id found. Run 'python agent_demo.py register' first.",
                file=sys.stderr,
            )
            return 1

        # Load private key
        private_key = load_private_key(config["private_key"])

        # Login
        print("Logging in...")
        result = login_agent(
            backend_url=config["backend_url"],
            agent_id=config["agent_id"],
            private_key=private_key,
        )

        # Save session_id
        session_id = result["session_id"]
        config["session_id"] = session_id
        save_config(config)

        expires_in = result.get("expires_in", 1800)
        expires_minutes = expires_in // 60

        print("Login successful!")
        print(f"Session ID: {session_id}")
        print(f"Expires in: {expires_minutes} minutes")
        return 0
    except AuthenticationError as e:
        print(f"Login failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_logout(args) -> int:
    """Logout and revoke session."""
    try:
        # Load config
        config = load_config()

        if not config.get("session_id"):
            print("No active session. Nothing to logout.", file=sys.stderr)
            return 1

        if not config.get("backend_url"):
            print("No backend_url configured.", file=sys.stderr)
            return 1

        # Logout
        print("Logging out...")
        success = logout_agent(
            backend_url=config["backend_url"],
            session_id=config["session_id"],
        )

        if success:
            # Clear session_id from config
            config["session_id"] = None
            save_config(config)
            print("Logout successful!")
            return 0
        else:
            print("Logout failed.", file=sys.stderr)
            return 1
    except AuthenticationError as e:
        print(f"Logout failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """Get and display agent information."""
    try:
        # Load config
        config = load_config()

        if not config.get("session_id"):
            print(
                "No active session. Run 'python agent_demo.py login' first.",
                file=sys.stderr,
            )
            return 1

        if not config.get("backend_url"):
            print("No backend_url configured.", file=sys.stderr)
            return 1

        # Get agent info
        result = get_agent_info(
            backend_url=config["backend_url"],
            session_id=config["session_id"],
        )

        agent = result.get("agent", {})
        print("Agent Information:")
        print(f"  ID:          {agent.get('id', 'N/A')}")
        print(f"  Name:        {agent.get('name', 'N/A')}")
        print(f"  Description: {agent.get('description', 'N/A')}")
        print(f"  Created at:  {agent.get('created_at', 'N/A')}")
        if agent.get("public_key"):
            print(f"  Public key:  {agent.get('public_key', 'N/A')[:32]}...")
        return 0
    except AuthenticationError as e:
        print(f"Failed to get info: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_query(args) -> int:
    """Query OAuth history or overseer information."""
    try:
        # Load config
        config = load_config()

        if not config.get("session_id"):
            print(
                "No active session. Run 'python agent-demo.py login' first.",
                file=sys.stderr,
            )
            return 1

        if not config.get("backend_url"):
            print("No backend_url configured.", file=sys.stderr)
            return 1

        backend_url = config["backend_url"]
        session_id = config["session_id"]
        headers = {"Authorization": f"Bearer {session_id}"}

        if args.target == "history":
            url = f"{backend_url}/v1/agents/me/oauth-history"
        else:  # overseers
            url = f"{backend_url}/v1/agents/me/overseer"

        response = make_request(url, headers)
        print_output(response)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_claim(args) -> int:
    """Complete a claim challenge to accept oversight."""
    config = load_config()

    if not config.get("backend_url"):
        print("No backend_url configured.", file=sys.stderr)
        return 1

    has_session = bool(config.get("session_id"))
    has_keys = bool(config.get("private_key") and config.get("public_key"))

    if not has_session and not has_keys:
        print(
            "Authentication required: set session_id or private_key + public_key in .env.",
            file=sys.stderr,
        )
        return 1

    backend_url = config["backend_url"]
    url = f"{backend_url}/v1/agents/claim/complete/{args.challenge_id}"
    body = {"overseer_id": args.overseer_id}
    encoded_body = json.dumps(body).encode("utf-8")

    headers = {"Content-Type": "application/json"}

    if has_session:
        headers["Authorization"] = f"Bearer {config['session_id']}"
    else:
        private_key = load_private_key(config["private_key"])
        dpop_proof = create_dpop_proof(private_key, "POST", url)
        headers["DPoP"] = dpop_proof

    response = make_request(url, headers, data=encoded_body, method="POST")
    print_output(response)
    return 0


def cmd_revoke_overseer(args) -> int:
    """Revoke current overseer relationship immediately."""
    config = load_config()

    if not config.get("backend_url"):
        print("No backend_url configured.", file=sys.stderr)
        return 1

    if not config.get("session_id"):
        print(
            "No active session. Run 'python agent-demo.py login' first.",
            file=sys.stderr,
        )
        return 1

    backend_url = config["backend_url"]
    session_id = config["session_id"]
    url = f"{backend_url}/v1/agents/revoke-overseer"
    headers = {"Authorization": f"Bearer {session_id}"}

    response = make_request(url, headers, method="POST")
    print_output(response)
    return 0


def cmd_config(args) -> int:
    """Configure the agent demo or display current configuration."""
    try:
        config = load_config()

        # Check if we should update config
        update_made = False

        if getattr(args, "backend_url", None):
            config["backend_url"] = args.backend_url
            update_made = True

        if getattr(args, "private_key", None) and getattr(args, "public_key", None):
            config["private_key"] = args.private_key
            config["public_key"] = args.public_key
            update_made = True
        elif getattr(args, "private_key", None) or getattr(args, "public_key", None):
            print(
                "Error: Both --private-key and --public-key must be provided together.",
                file=sys.stderr,
            )
            return 1

        if update_made:
            # Validate before saving if we have keys
            if config.get("private_key") and config.get("public_key"):
                is_valid, msg = validate_keys_match(
                    config["private_key"], config["public_key"]
                )
                if not is_valid:
                    print(f"Error: Invalid keys provided - {msg}", file=sys.stderr)
                    return 1

            save_config(config)
            print("Configuration updated successfully.\n")

        print("Current Configuration:")
        print(f"  Backend URL:  {config.get('backend_url') or '(not set)'}")
        print(f"  Agent ID:     {config.get('agent_id') or '(not set)'}")
        print(f"  Session ID:   {config.get('session_id') or '(not set)'}")

        private_key = config.get("private_key")
        public_key = config.get("public_key")

        if private_key:
            print(f"  Private key: {private_key[:16]}...{private_key[-8:]}")
        else:
            print(f"  Private key: (not set)")

        if public_key:
            print(f"  Public key:  {public_key}")
        else:
            print(f"  Public key:  (not set)")

        # Validate and report status
        if private_key and public_key:
            is_valid, msg = validate_keys_match(private_key, public_key)
            if is_valid:
                print("\n  Status: VALID (keys match)")
            else:
                print(f"\n  Status: INVALID - {msg}")
        else:
            print("\n  Status: INCOMPLETE")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agent-ID Demo Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent_demo.py generate-keys
  python agent_demo.py register --name "My Agent"
  python agent_demo.py login
  python agent_demo.py info
  python agent_demo.py logout
  python agent_demo.py config
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate-keys command
    parser_generate = subparsers.add_parser(
        "generate-keys",
        help="Generate new Ed25519 keypair and optionally save to .env",
    )
    parser_generate.add_argument(
        "--save",
        action="store_true",
        help="Save generated keys to .env file",
    )

    # register command
    parser_register = subparsers.add_parser(
        "register",
        help="Register a new agent with the backend",
    )
    parser_register.add_argument(
        "--name",
        required=True,
        help="Agent name",
    )
    parser_register.add_argument(
        "--description",
        help="Optional agent description",
    )

    # login command
    parser_login = subparsers.add_parser(
        "login",
        help="Authenticate with DPoP proof and create session",
    )

    # logout command
    parser_logout = subparsers.add_parser(
        "logout",
        help="Logout and revoke current session",
    )

    # info command
    parser_info = subparsers.add_parser(
        "info",
        help="Get and display agent information",
    )

    # config command
    parser_config = subparsers.add_parser(
        "configure",
        help="Configure the agent demo or display current configuration",
    )
    parser_config.add_argument(
        "--backend-url",
        help="The URL of the backend API",
    )
    parser_config.add_argument(
        "--private-key",
        help="The base64url-encoded Ed25519 private key",
    )
    parser_config.add_argument(
        "--public-key",
        help="The base64url-encoded Ed25519 public key",
    )

    # claim command
    parser_claim = subparsers.add_parser(
        "claim",
        help="Complete a claim challenge to accept oversight",
    )
    parser_claim.add_argument(
        "--challenge-id",
        required=True,
        help="The claim challenge ID to complete",
    )
    parser_claim.add_argument(
        "--overseer-id",
        required=True,
        help="The overseer ID initiating the claim",
    )

    # revoke-overseer command
    parser_revoke = subparsers.add_parser(
        "revoke-overseer",
        help="Revoke current overseer relationship immediately",
    )

    # query command
    parser_query = subparsers.add_parser(
        "query",
        help="Query OAuth history or overseer information",
    )
    parser_query.add_argument(
        "target",
        choices=["history", "overseers"],
        help="What to query: history (OAuth history) or overseers (overseer info)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Dispatch to command handlers
    if args.command is None:
        parser.print_help()
        return 0

    command_handlers = {
        "generate-keys": cmd_generate_keys,
        "register": cmd_register,
        "login": cmd_login,
        "logout": cmd_logout,
        "info": cmd_info,
        "configure": cmd_config,
        "query": cmd_query,
        "claim": cmd_claim,
        "revoke-overseer": cmd_revoke_overseer,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
