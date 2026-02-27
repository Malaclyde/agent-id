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
import time
import uuid
import argparse
import hashlib
import secrets
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
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
# PKCE Generation
# =============================================================================


def generate_pkce_pair() -> tuple[str, str]:
    """
    Generate PKCE code verifier and S256 challenge pair.

    Per RFC 7636:
    - code_verifier: 43-128 characters, cryptographically random
    - code_challenge: BASE64URL(SHA256(code_verifier))
    """
    # Generate 32 bytes of random data
    random_bytes = secrets.token_bytes(32)

    # Base64url encode without padding to create code_verifier
    code_verifier = base64url_encode(random_bytes)

    # SHA256 hash the verifier (as UTF-8 bytes)
    sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()

    # Base64url encode the hash without padding to create code_challenge
    code_challenge = base64url_encode(sha256_hash)

    return code_verifier, code_challenge


# =============================================================================
# Client Assertion JWT Construction
# =============================================================================


def create_client_assertion(
    private_key: SigningKey, client_id: str, token_endpoint: str
) -> str:
    """
    Create JWT client assertion for token endpoint authentication.

    Args:
        private_key: Ed25519 private key for signing
        client_id: OAuth client ID
        token_endpoint: Full URL of token endpoint (audience)

    Returns:
        JWT string (header.payload.signature)
    """
    # JWT Header
    header = {"alg": "EdDSA", "typ": "JWT"}

    # JWT Payload
    now = int(time.time())
    payload = {
        "iss": client_id,  # Issuer = client_id
        "sub": client_id,  # Subject = client_id
        "aud": token_endpoint,  # Audience = token endpoint URL
        "iat": now,  # Issued at
        "exp": now + 60,  # Expire (short-lived, 60 seconds)
        "jti": str(uuid.uuid4()),  # Unique JWT ID
    }

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
# DPoP Proof Construction
# =============================================================================


def hash_access_token(access_token: str) -> str:
    """
    Compute SHA-256 hash of access token, base64url encoded (no padding).
    Used for DPoP 'ath' claim per RFC 9449.
    """
    digest = hashlib.sha256(access_token.encode("utf-8")).digest()
    return base64url_encode(digest)


def create_dpop_proof(
    private_key: SigningKey,
    method: str,
    uri: str,
    access_token: Optional[str] = None,
) -> str:
    """
    Create DPoP proof JWT for resource access (userinfo endpoint).

    Different from create_client_assertion:
    - Header: typ='dpop+jwt' (not 'JWT'), NO jwk field
    - Payload: htm, htu, jti, iat (no iss/sub/aud/exp)
    - Optional ath claim (SHA-256 hash of access token)

    Args:
        private_key: Client's Ed25519 signing key
        method: HTTP method (e.g. 'GET')
        uri: Full request URI (e.g. 'https://api.example.com/v1/oauth/userinfo')
        access_token: Access token to bind via ath claim

    Returns:
        DPoP proof JWT string
    """
    header = {
        "typ": "dpop+jwt",
        "alg": "EdDSA",
        # NO jwk - validateDPoPProof gets key from client record
    }

    now = int(time.time())
    payload = {
        "jti": str(uuid.uuid4()),
        "htm": method,
        "htu": uri,
        "iat": now,
    }

    if access_token:
        payload["ath"] = hash_access_token(access_token)

    encoded_header = base64url_encode_json(header)
    encoded_payload = base64url_encode_json(payload)
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    signed = private_key.sign(signing_input)
    encoded_signature = base64url_encode(signed.signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


# =============================================================================
# HTTP Callback Server
# =============================================================================


class CallbackHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for OAuth callback.
    Captures tokens from GET or POST requests.
    """

    tokens = None

    def do_GET(self):
        """Handle GET callback (query parameters)."""
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # Extract tokens
        access_token = query.get("access_token", [None])[0]
        refresh_token = query.get("refresh_token", [None])[0]

        CallbackHandler.tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Success: tokens received. You can close this window.")

    def do_POST(self):
        """Handle POST callback (JSON body)."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
            CallbackHandler.tokens = {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_callback_server(hostname: str, port: int) -> Optional[dict]:
    """
    Start a blocking HTTP server to receive one callback request.
    """
    CallbackHandler.tokens = None
    server_address = (hostname, port)
    httpd = HTTPServer(server_address, CallbackHandler)

    print(f"Waiting for callback at http://{hostname}:{port}/callback...")
    print("Press Ctrl+C to cancel.")

    try:
        httpd.handle_request()  # Handle only one request
    except KeyboardInterrupt:
        print("\nCancelled.")
    finally:
        httpd.server_close()

    return CallbackHandler.tokens


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
# Command Handlers
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
            print(
                json.dumps(
                    {"private_key": private_b64url, "public_key": public_b64url},
                    indent=2,
                )
            )
            print("\nNote: Keys were NOT saved. Use --save to save them to .env")
        return 0
    except Exception as e:
        print(f"Error generating keys: {e}", file=sys.stderr)
        return 1


def cmd_generate_verifier(args) -> int:
    """Generate PKCE verifier/challenge pair."""
    try:
        code_verifier, code_challenge = generate_pkce_pair()

        result = {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        print_output(json.dumps(result))
        return 0
    except Exception as e:
        print(f"Error generating verifier: {e}", file=sys.stderr)
        return 1


def cmd_token_exchange(args) -> int:
    """Exchange authorization code for tokens."""
    try:
        # Load and validate config
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1
        if not config.get("client_id"):
            print("Error: client_id not configured", file=sys.stderr)
            return 1
        if not config.get("private_key"):
            print("Error: client private_key not configured", file=sys.stderr)
            return 1

        # Build callback URL (redirect_uri)
        client_url = config.get("client_url", "localhost")
        client_port = config.get("client_port", "8790")
        redirect_uri = f"http://{client_url}:{client_port}/callback"

        # Build token endpoint
        backend_url = config["backend_url"]
        token_endpoint = f"{backend_url}/v1/oauth/token"

        # Load private key and create client assertion
        private_key = load_private_key(config["private_key"])
        client_assertion = create_client_assertion(
            private_key, config["client_id"], token_endpoint
        )

        # Prepare request body
        body_fields = {
            "grant_type": "authorization_code",
            "code": args.token,
            "redirect_uri": redirect_uri,
            "client_id": config["client_id"],
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "code_verifier": args.code_verifier,
        }
        body_bytes = urllib.parse.urlencode(body_fields).encode("utf-8")

        # Make token exchange request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response_string = make_request(token_endpoint, headers, data=body_bytes)

        # Print output
        print_output(response_string)

        # Extract tokens and save to .env
        result = json.loads(response_string)
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")

        if access_token:
            set_key(ENV_FILE, f"AGENT_{args.agent_id}_ACCESS_TOKEN", access_token)
        if refresh_token:
            set_key(ENV_FILE, f"AGENT_{args.agent_id}_REFRESH_TOKEN", refresh_token)

        return 0
    except Exception as e:
        print(f"Error during token exchange: {e}", file=sys.stderr)
        return 1


def cmd_config(args) -> int:
    """Configure the client demo or display current configuration."""
    try:
        config = load_config()

        # Check if we should update config
        update_made = False

        if getattr(args, "backend_url", None):
            config["backend_url"] = args.backend_url
            update_made = True

        if getattr(args, "client_id", None):
            config["client_id"] = args.client_id
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

        if getattr(args, "client_url", None):
            config["client_url"] = args.client_url
            update_made = True

        if getattr(args, "client_port", None):
            config["client_port"] = args.client_port
            update_made = True

        if update_made:
            # Validate before saving
            is_valid, msg = validate_config(config)
            if not is_valid:
                print(f"Error: Invalid configuration - {msg}", file=sys.stderr)
                return 1

            save_config(config)
            print("Configuration updated successfully.\n")

        print("Current Configuration:")
        print(f"  Backend URL: {config.get('backend_url') or '(not set)'}")
        print(f"  Client ID:   {config.get('client_id') or '(not set)'}")
        print(f"  Client URL:  {config.get('client_url') or '(not set)'}")
        print(f"  Client Port: {config.get('client_port') or '(not set)'}")

        private_key = config.get("private_key")
        public_key = config.get("public_key")

        if private_key:
            print(f"  Private key: {private_key[:4]}***{private_key[-4:]}")
        else:
            print(f"  Private key: (not set)")

        if public_key:
            print(f"  Public key:  {public_key}")
        else:
            print(f"  Public key:  (not set)")

        # Validate and report status
        is_valid, msg = validate_config(config)
        if is_valid:
            print("\n  Status: VALID")
        else:
            print(f"\n  Status: INVALID - {msg}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_refresh(args) -> int:
    """Refresh access token using refresh token grant."""
    try:
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1
        if not config.get("client_id"):
            print("Error: client_id not configured", file=sys.stderr)
            return 1
        if not config.get("private_key"):
            print("Error: client private_key not configured", file=sys.stderr)
            return 1

        # Build token endpoint (MUST use /v1/ prefix — NOT from well-known)
        backend_url = config["backend_url"]
        client_id = config["client_id"]
        token_endpoint = f"{backend_url}/v1/oauth/token"

        # Load stored refresh token
        load_dotenv(ENV_FILE)
        refresh_token = os.getenv(f"AGENT_{args.agent_id}_REFRESH_TOKEN")
        if not refresh_token:
            print(
                f"Error: No refresh token found for agent {args.agent_id}",
                file=sys.stderr,
            )
            return 1

        # Create client assertion (aud = token endpoint)
        private_key = load_private_key(config["private_key"])
        client_assertion = create_client_assertion(
            private_key, client_id, token_endpoint
        )

        body_fields = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        }
        body_bytes = urllib.parse.urlencode(body_fields).encode("utf-8")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response_string = make_request(token_endpoint, headers, data=body_bytes)

        # Print full token JSON to stdout
        print_output(response_string)

        # Save new tokens (rotation: always overwrite both)
        result = json.loads(response_string)
        if result.get("access_token"):
            set_key(
                ENV_FILE,
                f"AGENT_{args.agent_id}_ACCESS_TOKEN",
                result["access_token"],
            )
        if result.get("refresh_token"):
            set_key(
                ENV_FILE,
                f"AGENT_{args.agent_id}_REFRESH_TOKEN",
                result["refresh_token"],
            )

        return 0
    except Exception as e:
        print(f"Error during token refresh: {e}", file=sys.stderr)
        return 1


def cmd_discover(args) -> int:
    """Fetch and display OpenID discovery document."""
    try:
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1

        backend_url = config["backend_url"]

        # Well-known URL DOES need /v1/ prefix (route mounted at /v1/oauth)
        well_known_url = f"{backend_url}/v1/oauth/.well-known/openid-configuration"

        # Simple GET, no auth required
        headers = {}
        response_string = make_request(well_known_url, headers)
        # Note: URLs in response lack /v1/ prefix (known backend bug) — display as-is
        print_output(response_string)
        return 0
    except Exception as e:
        print(f"Error during discovery: {e}", file=sys.stderr)
        return 1


def cmd_userinfo(args) -> int:
    """Query userinfo endpoint with DPoP-bound access token."""
    try:
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1
        if not config.get("client_id"):
            print("Error: client_id not configured", file=sys.stderr)
            return 1
        if not config.get("private_key"):
            print("Error: client private_key not configured", file=sys.stderr)
            return 1

        backend_url = config["backend_url"]

        # Load stored access token
        load_dotenv(ENV_FILE)
        access_token = os.getenv(f"AGENT_{args.agent_id}_ACCESS_TOKEN")
        if not access_token:
            print(
                f"Error: No access token found for agent {args.agent_id}",
                file=sys.stderr,
            )
            return 1

        # Build userinfo endpoint (MUST use /v1/ prefix)
        userinfo_endpoint = f"{backend_url}/v1/oauth/userinfo"

        # Generate DPoP proof (signed with CLIENT key, includes ath)
        private_key = load_private_key(config["private_key"])
        dpop_proof = create_dpop_proof(
            private_key, "GET", userinfo_endpoint, access_token
        )

        headers = {
            "Authorization": f"DPoP {access_token}",
            "DPoP": dpop_proof,
        }
        response_string = make_request(userinfo_endpoint, headers, method="GET")
        print_output(response_string)
        return 0
    except Exception as e:
        print(f"Error querying userinfo: {e}", file=sys.stderr)
        return 1


def cmd_revoke(args) -> int:
    """Revoke access or refresh token."""
    try:
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1
        if not config.get("client_id"):
            print("Error: client_id not configured", file=sys.stderr)
            return 1
        if not config.get("private_key"):
            print("Error: client private_key not configured", file=sys.stderr)
            return 1

        backend_url = config["backend_url"]
        client_id = config["client_id"]

        # Determine token to revoke from --access or --refresh flag
        load_dotenv(ENV_FILE)
        if args.access:
            token = os.getenv(f"AGENT_{args.agent_id}_ACCESS_TOKEN")
            token_type_hint = "access_token"
        else:
            token = os.getenv(f"AGENT_{args.agent_id}_REFRESH_TOKEN")
            token_type_hint = "refresh_token"

        if not token:
            print(
                f"Error: No {token_type_hint} found for agent {args.agent_id}",
                file=sys.stderr,
            )
            return 1

        # Build revoke endpoint (MUST use /v1/ prefix)
        revoke_endpoint = f"{backend_url}/v1/oauth/revoke"

        # Client assertion aud must match the revoke endpoint (NOT well-known URL)
        private_key = load_private_key(config["private_key"])
        client_assertion = create_client_assertion(
            private_key, client_id, revoke_endpoint
        )

        body_fields = {
            "token": token,
            "client_id": client_id,
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "token_type_hint": token_type_hint,  # Cosmetic: backend accepts but ignores
        }
        body_bytes = urllib.parse.urlencode(body_fields).encode("utf-8")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response_string = make_request(revoke_endpoint, headers, data=body_bytes)
        # No .env cleanup after revocation (per CONTEXT.md decision)
        print_output(response_string)
        return 0
    except Exception as e:
        print(f"Error during revocation: {e}", file=sys.stderr)
        return 1


def cmd_introspect(args) -> int:
    """Introspect token for status and metadata."""
    try:
        config = load_config()
        if not config.get("backend_url"):
            print("Error: backend_url not configured", file=sys.stderr)
            return 1
        if not config.get("client_id"):
            print("Error: client_id not configured", file=sys.stderr)
            return 1
        if not config.get("private_key"):
            print("Error: client private_key not configured", file=sys.stderr)
            return 1

        backend_url = config["backend_url"]
        client_id = config["client_id"]

        # Determine token to introspect from --access or --refresh flag
        load_dotenv(ENV_FILE)
        if args.access:
            token = os.getenv(f"AGENT_{args.agent_id}_ACCESS_TOKEN")
            token_type_hint = "access_token"
        else:
            token = os.getenv(f"AGENT_{args.agent_id}_REFRESH_TOKEN")
            token_type_hint = "refresh_token"

        if not token:
            print(
                f"Error: No {token_type_hint} found for agent {args.agent_id}",
                file=sys.stderr,
            )
            return 1

        # Build introspect endpoint (MUST use /v1/ prefix)
        introspect_endpoint = f"{backend_url}/v1/oauth/introspect"

        # Client assertion aud must match introspect endpoint
        private_key = load_private_key(config["private_key"])
        client_assertion = create_client_assertion(
            private_key, client_id, introspect_endpoint
        )

        body_fields = {
            "token": token,
            "client_id": client_id,
            "client_assertion": client_assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "token_type_hint": token_type_hint,  # Cosmetic: backend accepts but ignores
        }
        body_bytes = urllib.parse.urlencode(body_fields).encode("utf-8")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response_string = make_request(introspect_endpoint, headers, data=body_bytes)
        print_output(response_string)
        return 0
    except Exception as e:
        print(f"Error during introspection: {e}", file=sys.stderr)
        return 1


# =============================================================================
# CLI Interface
# =============================================================================


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Client-ID Demo Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate-keys command
    parser_generate_keys = subparsers.add_parser(
        "generate-keys",
        help="Generate new Ed25519 keypair and optionally save to .env",
    )
    parser_generate_keys.add_argument(
        "--save",
        action="store_true",
        help="Save generated keys to .env file",
    )

    # generate-verifier command
    subparsers.add_parser(
        "generate-verifier",
        help="Generate PKCE verifier and challenge pair",
    )

    # token-exchange command
    parser_token_exchange = subparsers.add_parser(
        "token-exchange",
        help="Exchange authorization code for tokens",
    )
    parser_token_exchange.add_argument(
        "--token", required=True, help="Authorization code"
    )
    parser_token_exchange.add_argument(
        "--code-verifier", required=True, help="PKCE code verifier"
    )
    parser_token_exchange.add_argument(
        "--agent-id", required=True, help="Agent ID for token storage"
    )

    # config command
    parser_config = subparsers.add_parser(
        "config",
        help="Configure the client demo or display current configuration",
    )
    parser_config.add_argument("--backend-url", help="Backend API URL")
    parser_config.add_argument("--client-id", help="OAuth client ID")
    parser_config.add_argument("--private-key", help="Client private key (base64url)")
    parser_config.add_argument("--public-key", help="Client public key (base64url)")
    parser_config.add_argument(
        "--client-url", help="Callback server URL (e.g. localhost)"
    )
    parser_config.add_argument("--client-port", help="Callback server port (e.g. 8790)")

    # refresh command
    parser_refresh = subparsers.add_parser(
        "refresh",
        help="Refresh access token using refresh token grant",
    )
    parser_refresh.add_argument(
        "--agent-id", required=True, help="Agent ID for token lookup/storage"
    )

    # discover command
    subparsers.add_parser(
        "discover",
        help="Query OpenID Connect discovery endpoint",
    )

    # userinfo command
    parser_userinfo = subparsers.add_parser(
        "userinfo",
        help="Query userinfo endpoint with DPoP-bound access token",
    )
    parser_userinfo.add_argument(
        "--agent-id", required=True, help="Agent ID for token lookup"
    )

    # revoke command
    parser_revoke = subparsers.add_parser(
        "revoke",
        help="Revoke an access or refresh token",
    )
    parser_revoke.add_argument(
        "--agent-id", required=True, help="Agent ID for token lookup"
    )
    revoke_token_type = parser_revoke.add_mutually_exclusive_group(required=True)
    revoke_token_type.add_argument(
        "--access", action="store_true", help="Revoke access token"
    )
    revoke_token_type.add_argument(
        "--refresh", action="store_true", help="Revoke refresh token"
    )

    # introspect command
    parser_introspect = subparsers.add_parser(
        "introspect",
        help="Introspect a token for status and metadata",
    )
    parser_introspect.add_argument(
        "--agent-id", required=True, help="Agent ID for token lookup"
    )
    introspect_token_type = parser_introspect.add_mutually_exclusive_group(
        required=True
    )
    introspect_token_type.add_argument(
        "--access", action="store_true", help="Introspect access token"
    )
    introspect_token_type.add_argument(
        "--refresh", action="store_true", help="Introspect refresh token"
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Dispatch to command handlers
    command_handlers = {
        "generate-keys": cmd_generate_keys,
        "generate-verifier": cmd_generate_verifier,
        "token-exchange": cmd_token_exchange,
        "config": cmd_config,
        "refresh": cmd_refresh,
        "discover": cmd_discover,
        "userinfo": cmd_userinfo,
        "revoke": cmd_revoke,
        "introspect": cmd_introspect,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
