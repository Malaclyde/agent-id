# Phase 36: Client Demo - Core - Research

**Researched:** 2026-02-22
**Domain:** OAuth2 client authentication, PKCE, HTTP callback servers, Ed25519 JWT signing
**Confidence:** HIGH

## Summary

This phase implements a client demo CLI script that handles OAuth2 authorization_code flow with PKCE and private key JWT client authentication. The key components are: (1) PKCE verifier/challenge generation using SHA256+S256, (2) blocking HTTP callback server for receiving OAuth tokens, (3) Ed25519-signed JWT client assertions for authentication, and (4) token exchange with the backend's `/v1/oauth/token` endpoint.

**Primary recommendation:** Reuse existing patterns from agent-demo.py (base64url encoding, Ed25519 signing, HTTP wrapper, dotenv config). Build new components for PKCE generation and HTTP callback server using Python standard library.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyNaCl | latest | Ed25519 key generation and signing | Matches backend @noble/ed25519 |
| python-dotenv | latest | .env file loading and saving | Already used in agent-demo.py |
| argparse | stdlib | CLI subcommand parsing | Already used in agent-demo.py |
| http.server | stdlib | Blocking HTTP callback server | Python standard library |

### No New Dependencies
- `hashlib` (stdlib) - SHA256 for PKCE S256
- `secrets` (stdlib) - Cryptographically secure random bytes
- `urllib.request` (stdlib) - HTTP requests (already used)
- `json`, `base64`, `time`, `uuid` (stdlib) - JWT construction

## Architecture Patterns

### Recommended Project Structure
```
demo/client/
├── client-demo.py          # Main CLI entry point
└── ...                     # Reuse modules from agent-demo.py or create shared utils
```

### Pattern 1: PKCE Verifier/Challenge Generation (S256)

**What:** Generate cryptographically secure code verifier and derive S256 code challenge
**When to use:** Before initiating OAuth authorization flow
**Implementation:**
```python
import secrets
import hashlib
import base64

def generate_pkce_pair():
    """
    Generate PKCE code verifier and S256 challenge pair.
    
    Per RFC 7636:
    - code_verifier: 43-128 characters, cryptographically random
    - code_challenge: BASE64URL(SHA256(code_verifier))
    """
    # Generate 32-byte random verifier, base64url encode without padding
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # SHA256 hash of verifier, then base64url encode without padding
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge
```

**Key points:**
- Verifier length: 43-128 characters (32 bytes → ~43 chars base64url)
- S256 is mandatory in 2025 OAuth specs (RFC 9700)
- Always strip `=` padding for base64url

### Pattern 2: Blocking HTTP Callback Server

**What:** Start HTTP server, block until callback received, extract tokens, stop server
**When to use:** OAuth2 authorization_code flow waiting for redirect with tokens
**Implementation:**
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class CallbackHandler(BaseHTTPRequestHandler):
    """Handler that captures callback request and signals completion."""
    
    tokens = None  # Class variable to store captured tokens
    
    def do_GET(self):
        """Handle GET callback - extract tokens from query params."""
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        # Store tokens (access_token, refresh_token in query or body)
        CallbackHandler.tokens = {
            'access_token': query.get('access_token', [None])[0],
            'refresh_token': query.get('refresh_token', [None])[0],
        }
        
        # Send success response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Authorization successful! You can close this window.')
    
    def do_POST(self):
        """Handle POST callback - extract tokens from body."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length)
        
        # Parse JSON body
        try:
            data = json.loads(post_body.decode('utf-8'))
            CallbackHandler.tokens = {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
            }
        except json.JSONDecodeError:
            CallbackHandler.tokens = None
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass  # Or use: print(f"[Callback] {format % args}")

def start_callback_server(hostname: str, port: int) -> dict:
    """
    Start blocking HTTP server and wait for callback.
    
    Args:
        hostname: Server hostname (e.g., 'localhost')
        port: Server port (e.g., 8790)
    
    Returns:
        Dict with access_token and refresh_token, or None if timeout/error
    """
    server_address = (hostname, port)
    httpd = HTTPServer(server_address, CallbackHandler)
    
    print(f"Waiting for callback at http://{hostname}:{port}/callback...")
    print("Press Ctrl+C to cancel.")
    
    # Block until callback received
    httpd.handle_request()  # Handle only one request, then stop
    
    httpd.server_close()
    return CallbackHandler.tokens
```

**Key points:**
- Use `handle_request()` to process only one request then exit
- Support both GET (query params) and POST (JSON body) callbacks
- Store tokens in class variable for cross-request access
- Need to handle case where backend sends POST to callback URL

### Pattern 3: Client Assertion JWT

**What:** Create JWT signed with Ed25519 private key for client authentication
**When to use:** Token exchange request with private_key_jwt client authentication
**Difference from DPoP proof:**
| Aspect | DPoP Proof | Client Assertion JWT |
|--------|-------------|---------------------|
| Header | `typ: dpop+jwt`, `jwk` with public key | `typ: JWT`, no jwk |
| Claims | `htm`, `htu`, `jti`, `ath` (optional) | `iss`, `sub`, `aud`, `exp`, `iat`, `jti` |
| Purpose | Bind token to HTTP request | Authenticate client identity |
| Audience | Target API URL | Token endpoint URL |

**Implementation:**
```python
import json
import time
import uuid
from nacl.signing import SigningKey
from .encoding import base64url_encode, base64url_encode_json

def create_client_assertion(
    private_key: SigningKey,
    client_id: str,
    token_endpoint: str
) -> str:
    """
    Create JWT client assertion for token exchange.
    
    Args:
        private_key: Ed25519 private key for signing
        client_id: OAuth client ID
        token_endpoint: Full URL of token endpoint (audience)
    
    Returns:
        JWT string (header.payload.signature)
    """
    # JWT Header
    header = {
        "alg": "EdDSA",
        "typ": "JWT"
    }
    
    # JWT Payload
    now = int(time.time())
    payload = {
        "iss": client_id,           # Issuer = client_id
        "sub": client_id,           # Subject = client_id
        "aud": token_endpoint,      # Audience = token endpoint URL
        "iat": now,                 # Issued at
        "exp": now + 60,           # Expire (short-lived, 60 seconds)
        "jti": str(uuid.uuid4())    # Unique JWT ID
    }
    
    # Build signing input: base64url(header).base64url(payload)
    encoded_header = base64url_encode_json(header)
    encoded_payload = base64url_encode_json(payload)
    signing_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    
    # Sign with Ed25519
    signed = private_key.sign(signing_input)
    signature = signed.signature
    encoded_signature = base64url_encode(signature)
    
    # Return complete JWT
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"
```

### Pattern 4: Token Exchange Request

**What:** Exchange authorization code for tokens using POST to `/v1/oauth/token`
**When to use:** After receiving authorization code from OAuth flow
**Backend expects (from oauth.ts analysis):**
```python
def exchange_token(
    backend_url: str,
    code: str,
    code_verifier: str,
    redirect_uri: str,
    client_id: str,
    client_assertion: str
) -> dict:
    """
    Exchange authorization code for access/refresh tokens.
    
    Request body (application/x-www-form-urlencoded):
        grant_type: authorization_code
        code: <authorization code>
        redirect_uri: <callback URL>
        client_id: <client ID>
        client_assertion: <JWT signed with Ed25519>
        client_assertion_type: urn:ietf:params:oauth:client-assertion-type:jwt-bearer
        code_verifier: <PKCE verifier>
    """
    import urllib.request
    import urllib.parse
    
    url = f"{backend_url}/v1/oauth/token"
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_assertion": client_assertion,
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "code_verifier": code_verifier,
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))
```

**Backend response:**
```json
{
  "access_token": "...",
  "token_type": "DPoP",
  "expires_in": 300,
  "refresh_token": "...",
  "scope": "..."
}
```

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Base64url encoding | Custom encode/decode | agent-demo.py `base64url_encode`, `base64url_decode` | Handles padding correctly |
| Ed25519 signing | Custom JWT signing | agent-demo.py patterns with PyNaCl | Correct canonicalization, signature encoding |
| .env loading | Custom file parsing | python-dotenv `load_dotenv`, `set_key` | Handles quotes, comments, escaping |
| HTTP requests | Custom urllib wrapper | agent-demo.py `make_request` | Already has fail-fast error handling |
| Key validation | Custom derive/verify | agent-demo.py `validate_keys_match` | Uses PyNaCl correctly |

## Common Pitfalls

### Pitfall 1: PKCE S256 Encoding Errors
**What goes wrong:** Code challenge doesn't match, token exchange fails with "PKCE validation failed"
**Why it happens:** 
- Forgetting to strip `=` padding from base64url
- Using standard base64 instead of base64url
- Wrong hash algorithm (must be SHA256)
**How to avoid:**
```python
# CORRECT: base64url without padding
code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')

# WRONG: base64 with padding
code_challenge = base64.b64encode(sha256_hash).decode('utf-8')  # Has +/ and =
```
**Warning signs:** Backend returns "PKCE validation failed"

### Pitfall 2: Client Assertion JWT Claims
**What goes wrong:** "JWT iss/sub must match client_id" or "JWT aud must match token endpoint"
**Why it happens:** 
- Using wrong audience (not the token endpoint URL)
- Not setting iss/sub to client_id
- Using DPoP proof structure instead of client assertion
**How to avoid:**
```python
# Build token endpoint URL dynamically
token_endpoint = f"{backend_url}/v1/oauth/token"

payload = {
    "iss": client_id,           # Must be client_id
    "sub": client_id,           # Must be client_id
    "aud": token_endpoint,      # Must be token endpoint URL
    ...
}
```
**Warning signs:** Backend returns 401 with "invalid_client" error

### Pitfall 3: HTTP Server Not Blocking
**What goes wrong:** Server starts but doesn't wait for callback
**Why it happens:** Using non-blocking server or calling serve_forever() incorrectly
**How to avoid:** Use `httpd.handle_request()` which processes one request then returns
**Warning signs:** Function returns immediately before tokens received

### Pitfall 4: Callback URL Mismatch
**What goes wrong:** "Redirect URI mismatch" error
**Why it happens:** Callback URL constructed differently between client and backend
**How to avoid:** 
- Use exact same construction: `http://{CLIENT_URL}:{CLIENT_PORT}/callback`
- Read from .env consistently
**Warning signs:** Backend returns "Redirect URI mismatch"

## Code Examples

### Subcommand 1: generate-verifier
```python
def cmd_generate_verifier(args) -> int:
    """Generate PKCE verifier/challenge pair."""
    code_verifier, code_challenge = generate_pkce_pair()
    
    result = {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    print_output(json.dumps(result))
    return 0
```

### Subcommand 2: generate-keys (client)
```python
def cmd_generate_keys(args) -> int:
    """Generate Ed25519 keypair for client auth."""
    private_b64url, public_b64url = generate_keypair()
    
    if getattr(args, 'save', False):
        # Save to .env under CLIENT_* namespace
        set_key(ENV_FILE, 'CLIENT_PRIVATE_KEY', private_b64url)
        set_key(ENV_FILE, 'CLIENT_PUBLIC_KEY', public_b64url)
        print("Keys generated and saved!")
    else:
        print(json.dumps({
            "private_key": private_b64url,
            "public_key": public_b64url
        }, indent=2))
    return 0
```

### Subcommand 3: token-exchange
```python
def cmd_token_exchange(args) -> int:
    """Exchange authorization code for tokens via callback server."""
    # Load config
    config = load_config()
    
    # Extract values
    backend_url = config['backend_url']
    client_id = config['client_id']
    client_private_key = load_private_key(config['client_private_key'])
    
    # Build callback URL
    client_url = config.get('CLIENT_URL', 'localhost')
    client_port = int(config.get('CLIENT_PORT', 8790))
    redirect_uri = f"http://{client_url}:{client_port}/callback"
    
    # Build token endpoint for client assertion aud
    token_endpoint = f"{backend_url}/v1/oauth/token"
    
    # Create client assertion JWT
    client_assertion = create_client_assertion(
        client_private_key,
        client_id,
        token_endpoint
    )
    
    # Start callback server in background thread (or process)
    callback_tokens = start_callback_server(client_url, client_port)
    
    # Make token exchange request (backend will POST to callback)
    result = exchange_token(
        backend_url=backend_url,
        code=args.token,
        code_verifier=args.code_verifier,
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_assertion=client_assertion
    )
    
    # After successful exchange, server receives tokens
    # Save tokens to .env
    agent_id = args.agent_id  # or extract from token response
    set_key(ENV_FILE, f'AGENT_{agent_id}_ACCESS_TOKEN', result['access_token'])
    set_key(ENV_FILE, f'AGENT_{agent_id}_REFRESH_TOKEN', result['refresh_token'])
    
    print_output(json.dumps(result))
    return 0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Plain PKCE | S256 mandatory | RFC 9700 (2025) | All new implementations must use S256 |
| Client secrets | Private key JWT | Modern OAuth | Ed25519 keys replace shared secrets |
| Blocking polling | HTTP callback | Standard practice | More reliable token capture |

**Deprecated/outdated:**
- `plain` code_challenge_method: Deprecated, S256 required
- Client secrets: Replaced by private key JWT authentication

## Open Questions

1. **Callback HTTP method:** Does backend send GET (query params) or POST (body)?
   - What we know: Both agent-demo authorize and CONTEXT.md mention redirect with tokens
   - What's unclear: Need to verify backend implementation
   - Recommendation: Implement both GET and POST handlers

2. **Agent ID in tokens:** How is agent_id associated with tokens for storage?
   - What we know: Tokens stored as `AGENT_<agent-id>_ACCESS_TOKEN`
   - What's unclear: Is agent_id in the token response or passed separately?
   - Recommendation: Pass via --agent-id flag for now

## Sources

### Primary (HIGH confidence)
- Python `http.server` documentation - Official stdlib docs
- RFC 7636 (PKCE) - IETF standard for code challenge generation
- Backend oauth.ts - Verified token endpoint expectations

### Secondary (MEDIUM confidence)
- Web search: "PKCE S256 Python hashlib base64url" - Multiple tutorials confirm pattern
- Web search: "OAuth2 client assertion JWT EdDSA" - Pattern matches RFC 7523

### Tertiary (LOW confidence)
- General OAuth2 patterns - Need to verify backend behavior

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified (PyNaCl, python-dotenv, stdlib)
- Architecture: HIGH - Patterns from agent-demo.py plus verified stdlib patterns
- Pitfalls: HIGH - Common OAuth2 mistakes verified against RFC and backend code

**Research date:** 2026-02-22
**Valid until:** 2026-03-22 (30 days - stable domain)
