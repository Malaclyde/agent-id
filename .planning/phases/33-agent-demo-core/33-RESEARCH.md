# Phase 33: Agent Demo - Core - Research

**Researched:** 2026-02-22
**Domain:** Python CLI tool for agent authentication and configuration
**Confidence:** HIGH

## Summary

This phase involves creating a Python CLI demo script that demonstrates agent configuration, Ed25519 key management, registration with challenge-response flow, and DPoP-based authentication. The script interacts with a Cloudflare Workers backend that uses Ed25519 for all cryptographic operations.

The standard approach is to use `pynacl` (PyNaCl) for Ed25519 operations (compatible with backend's `@noble/ed25519`), `python-dotenv` for .env management, and Python's standard library for HTTP and CLI operations.

**Primary recommendation:** Use PyNaCl 1.6+ for Ed25519 cryptography, python-dotenv for .env handling, and argparse for CLI. All cryptographic operations must use base64url encoding for key/signature exchange with the backend.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pynacl | 1.6.2 | Ed25519 signing/key generation | Official Python binding to libsodium, compatible with @noble/ed25519 used by backend |
| python-dotenv | 1.2.1 | .env file read/write | Industry standard for .env handling, includes CLI support |
| argparse | stdlib | CLI argument parsing | Standard library, no external deps needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| urllib.request | stdlib | HTTP client | All API calls - avoid external deps per constraint |
| json | stdlib | JSON handling | API payloads, canonical JSON |
| uuid | stdlib | UUID generation | DPoP `jti` field |
| base64 | stdlib | Base64url encoding | Key/signature encoding |
| hashlib | stdlib | SHA-256 | Access token hash for DPoP `ath` field |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pynacl | cryptography library | cryptography requires more code for Ed25519 raw bytes; pynacl matches backend's @noble/ed25519 semantics |
| urllib | requests/httpx | Adds external dependency; urllib sufficient for simple REST calls |
| argparse | click | click adds dependency; argparse sufficient for demo script |

**Installation:**
```bash
pip install pynacl python-dotenv
```

## Architecture Patterns

### Recommended Project Structure
```
demos/
├── agent_demo.py          # Main CLI script
├── .env.agent             # Configuration file (gitignored)
└── requirements.txt       # pynacl, python-dotenv
```

### Pattern 1: Ed25519 Key Generation
**What:** Generate Ed25519 keypair and encode as base64url
**When to use:** ACONF-02 (keypair generation)
**Example:**
```python
# Source: PyNaCl docs + backend crypto.ts
from nacl.signing import SigningKey
import base64

def generate_keypair():
    # Generate new Ed25519 keypair
    private_key = SigningKey.generate()
    public_key = private_key.verify_key
    
    # Encode as base64url (no padding)
    private_b64url = base64.urlsafe_b64encode(bytes(private_key)).rstrip(b'=').decode('ascii')
    public_b64url = base64.urlsafe_b64encode(bytes(public_key)).rstrip(b'=').decode('ascii')
    
    return private_b64url, public_b64url

def load_private_key(private_b64url: str) -> SigningKey:
    # Decode base64url to bytes
    padding = '=' * (4 - len(private_b64url) % 4)
    private_bytes = base64.urlsafe_b64decode(private_b64url + padding)
    return SigningKey(private_bytes)
```

### Pattern 2: Canonical JSON for Signatures
**What:** Deterministic JSON serialization for challenge signing
**When to use:** AAUTH-01 (registration challenge signing)
**Example:**
```python
# Source: backend/src/utils/helpers.ts canonicalize()
def canonicalize(obj: dict) -> str:
    """Canonical JSON per RFC 8785 principles - sort keys, no whitespace."""
    def sort_and_serialize(o):
        if isinstance(o, dict):
            # Sort keys alphabetically
            items = [f'"{k}":{sort_and_serialize(v)}' for k, v in sorted(o.items())]
            return '{' + ','.join(items) + '}'
        elif isinstance(o, str):
            # Escape special characters
            escaped = o.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{escaped}"'
        elif isinstance(o, bool):
            return 'true' if o else 'false'
        elif o is None:
            return 'null'
        elif isinstance(o, (int, float)):
            return str(o)
        elif isinstance(o, list):
            return '[' + ','.join(sort_and_serialize(i) for i in o) + ']'
        return str(o)
    
    return sort_and_serialize(obj)
```

### Pattern 3: DPoP Proof Construction
**What:** Build JWT proof for DPoP authentication
**When to use:** AAUTH-02 (agent login)
**Example:**
```python
# Source: backend/src/services/dpop.ts
import json
import time
import uuid
import base64
import hashlib
from nacl.signing import SigningKey

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def base64url_encode_json(obj: dict) -> str:
    return base64url_encode(json.dumps(obj, separators=(',', ':')).encode('utf-8'))

def hash_access_token(token: str) -> str:
    """SHA-256 hash of access token, base64url encoded."""
    digest = hashlib.sha256(token.encode('utf-8')).digest()
    return base64url_encode(digest)

def create_dpop_proof(private_key: SigningKey, method: str, uri: str, access_token: str = None) -> str:
    """Create DPoP proof JWT for authentication."""
    public_key = private_key.verify_key
    public_b64url = base64url_encode(bytes(public_key))
    
    # JWT Header
    header = {
        'typ': 'dpop+jwt',
        'alg': 'EdDSA',
        'jwk': {
            'kty': 'OKP',
            'crv': 'Ed25519',
            'x': public_b64url
        }
    }
    
    # JWT Payload
    payload = {
        'jti': str(uuid.uuid4()),
        'htm': method,
        'htu': uri,
        'iat': int(time.time())
    }
    
    if access_token:
        payload['ath'] = hash_access_token(access_token)
    
    # Build signing input
    encoded_header = base64url_encode_json(header)
    encoded_payload = base64url_encode_json(payload)
    signing_input = f'{encoded_header}.{encoded_payload}'.encode('utf-8')
    
    # Sign with Ed25519
    signed = private_key.sign(signing_input)
    signature = signed.signature
    encoded_signature = base64url_encode(signature)
    
    return f'{encoded_header}.{encoded_payload}.{encoded_signature}'
```

### Pattern 4: Registration Challenge Flow
**What:** Two-step registration with Ed25519 signature
**When to use:** AAUTH-01 (agent registration)
**Example:**
```python
# Source: backend/src/routes/agents.ts
import urllib.request
import json

def register_agent(backend_url: str, name: str, private_key: SigningKey, description: str = None):
    public_key = private_key.verify_key
    public_b64url = base64url_encode(bytes(public_key))
    
    # Step 1: Initiate registration
    initiate_body = {'name': name, 'public_key': public_b64url}
    if description:
        initiate_body['description'] = description
    
    req = urllib.request.Request(
        f'{backend_url}/api/agents/register/initiate',
        data=json.dumps(initiate_body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    challenge_id = result['challenge_id']
    challenge_data = result['challenge_data']  # Already canonicalized by backend
    
    # Step 2: Sign challenge and complete
    signed = private_key.sign(challenge_data.encode('utf-8'))
    signature_b64url = base64url_encode(signed.signature)
    
    complete_req = urllib.request.Request(
        f'{backend_url}/api/agents/register/complete/{challenge_id}',
        data=json.dumps({'signature': signature_b64url}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(complete_req) as resp:
        final_result = json.loads(resp.read().decode('utf-8'))
    
    return final_result  # {agent: {...}, session_id: "..."}
```

### Pattern 5: .env File Management
**What:** Read/write configuration to .env file
**When to use:** ACONF-01, ACONF-02 (configuration)
**Example:**
```python
# Source: python-dotenv docs
from dotenv import load_dotenv, set_key, get_key, unset_key
import os

def load_config(env_file: str = '.env.agent'):
    """Load configuration from .env file."""
    load_dotenv(env_file)
    return {
        'backend_url': os.getenv('AGENT_BACKEND_URL'),
        'private_key': os.getenv('AGENT_PRIVATE_KEY'),
        'public_key': os.getenv('AGENT_PUBLIC_KEY'),
        'agent_id': os.getenv('AGENT_ID'),
        'session_id': os.getenv('AGENT_SESSION_ID')
    }

def save_config(env_file: str, config: dict):
    """Save configuration to .env file."""
    for key, value in config.items():
        if value is not None:
            set_key(env_file, key, value)

def validate_keys_match(private_b64url: str, public_b64url: str) -> bool:
    """ACONF-03: Verify public key derives from private key."""
    private_key = load_private_key(private_b64url)
    derived_public = base64url_encode(bytes(private_key.verify_key))
    return derived_public == public_b64url
```

### Anti-Patterns to Avoid
- **Using standard JSON serialization for challenge signing:** Must use canonical JSON with sorted keys
- **Including padding in base64url:** Backend uses unpadded base64url; strip `=` characters
- **Using 64-byte private key format:** PyNaCl uses 32-byte seed format; backend uses same via @noble/ed25519
- **Normalizing URL with query params in DPoP htu:** Backend normalizes to `protocol//host/pathname` only

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| .env file parsing | Custom key=value parser | python-dotenv | Handles quoting, escaping, comments, multiline |
| Ed25519 cryptography | Manual curve operations | PyNaCl | Correct implementation, constant-time, tested |
| Base64url encoding | base64 module + manual padding | Helper function | Consistent padding handling across all calls |
| Canonical JSON | json.dumps(sort_keys=True) | Custom canonicalize function | Backend uses specific RFC 8785-style serialization |

**Key insight:** The canonical JSON format must match the backend's implementation exactly. Using `json.dumps(sort_keys=True)` is NOT sufficient because it includes spaces after separators.

## Common Pitfalls

### Pitfall 1: Base64url Padding Mismatch
**What goes wrong:** Keys/signatures fail verification due to padding differences
**Why it happens:** Standard base64 includes `=` padding; base64url typically omits it
**How to avoid:** Always strip padding when encoding; always add padding before decoding
**Warning signs:** `Invalid signature` errors, `Invalid Ed25519 public key format` errors

### Pitfall 2: Challenge Data Canonicalization
**What goes wrong:** Signature fails because signed data doesn't match challenge_data
**Why it happens:** Python's `json.dumps()` produces different output than backend's `canonicalize()`
**How to avoid:** Sign the `challenge_data` string directly from backend response; don't re-serialize
**Warning signs:** `Invalid signature` error on registration complete

### Pitfall 3: DPoP HTU Normalization
**What goes wrong:** DPoP proof rejected with `htu mismatch`
**Why it happens:** Backend normalizes URL to `protocol//host/pathname` (no query params, no trailing slash)
**How to avoid:** Normalize URL before constructing DPoP proof: `f'{url.scheme}://{url.netloc}{url.path}'`
**Warning signs:** `DPoP htu mismatch` error on login

### Pitfall 4: Private Key Size Confusion
**What goes wrong:** Key import fails or derived public key doesn't match
**Why it happens:** Ed25519 private keys can be 32-byte seed or 64-byte expanded form
**How to avoid:** PyNaCl `SigningKey` uses 32-byte seed; backend's `@noble/ed25519` also uses seed format
**Warning signs:** `ValueError: ... is not 32 bytes` or public key mismatch

### Pitfall 5: Session vs DPoP Authentication
**What goes wrong:** Using DPoP when session auth expected, or vice versa
**Why it happens:** Different endpoints require different auth methods
**How to avoid:**
- `/agents/login`: Requires DPoP header
- `/agents/logout`, `/agents/me`: Requires `Authorization: Bearer <session_id>`
**Warning signs:** `Not authenticated` or `DPoP proof required` errors

## Code Examples

### Complete Login Flow
```python
# Source: backend/src/routes/agents.ts + dpop.ts
def login_agent(backend_url: str, agent_id: str, private_key: SigningKey) -> dict:
    """Login with DPoP proof, return session info."""
    login_url = f'{backend_url}/api/agents/login'
    
    # Normalize URL for DPoP htu
    from urllib.parse import urlparse
    parsed = urlparse(login_url)
    normalized_htu = f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
    
    # Create DPoP proof
    dpop_proof = create_dpop_proof(private_key, 'POST', normalized_htu)
    
    # Make login request
    req = urllib.request.Request(
        login_url,
        data=json.dumps({'agent_id': agent_id}).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'DPoP': dpop_proof
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    return result  # {session_id: "...", expires_in: 1800}
```

### Agent Info Query
```python
# Source: backend/src/routes/agents.ts
def get_agent_info(backend_url: str, session_id: str) -> dict:
    """Get current agent info using session auth."""
    req = urllib.request.Request(
        f'{backend_url}/api/agents/me',
        headers={'Authorization': f'Bearer {session_id}'},
        method='GET'
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    return result  # {agent: {id, name, description, created_at}}
```

### Logout
```python
# Source: backend/src/routes/agents.ts
def logout_agent(backend_url: str, session_id: str) -> bool:
    """Revoke session."""
    req = urllib.request.Request(
        f'{backend_url}/api/agents/logout',
        headers={'Authorization': f'Bearer {session_id}'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    return result.get('success', False)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| RSA signatures | Ed25519 signatures | ~2017+ | Smaller keys, faster signing, simpler implementation |
| Session-only auth | DPoP + Session auth | OAuth 2.1 era | DPoP provides proof-of-possession for login |

**Deprecated/outdated:**
- Ed448: Not needed; Ed25519 is standard for agent auth
- JWT RS256: Backend uses EdDSA exclusively for agent flows

## API Reference

### Registration Flow
| Endpoint | Method | Auth | Body | Response |
|----------|--------|------|------|----------|
| `/api/agents/register/initiate` | POST | None | `{name, public_key, description?}` | `{challenge_id, expires_at, challenge_data}` |
| `/api/agents/register/complete/:challengeId` | POST | None | `{signature}` | `{agent, session_id}` |

### Authentication Flow
| Endpoint | Method | Auth | Body | Response |
|----------|--------|------|------|----------|
| `/api/agents/login` | POST | DPoP header | `{agent_id}` | `{session_id, expires_in}` |
| `/api/agents/logout` | POST | Bearer token | None | `{success, message}` |
| `/api/agents/me` | GET | Bearer token | None | `{agent}` |

### Key Formats
| Key Type | Size | Encoding |
|----------|------|----------|
| Ed25519 private key | 32 bytes (seed) | base64url, no padding |
| Ed25519 public key | 32 bytes | base64url, no padding |
| Ed25519 signature | 64 bytes | base64url, no padding |

## Open Questions

1. **Error Handling Granularity**
   - What we know: Backend returns JSON with `success: false` and `error` field
   - What's unclear: Whether to surface raw errors or provide user-friendly messages
   - Recommendation: Surface raw errors for debugging; demo script users are developers

2. **Session Persistence**
   - What we know: Sessions expire in 30 minutes (1800 seconds)
   - What's unclear: Whether to auto-refresh sessions or require re-login
   - Recommendation: Simple approach - store session_id in .env, re-login when expired

## Sources

### Primary (HIGH confidence)
- `backend/src/routes/agents.ts` - Complete API endpoint implementations
- `backend/src/services/dpop.ts` - DPoP proof construction and validation
- `backend/src/utils/crypto.ts` - Ed25519 signature verification
- `backend/src/utils/helpers.ts` - Canonical JSON, UUID generation, expiration
- `https://pypi.org/project/PyNaCl/` - PyNaCl 1.6.2 documentation
- `https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/` - Ed25519 API reference
- `https://pypi.org/project/python-dotenv/` - python-dotenv 1.2.1 documentation

### Secondary (MEDIUM confidence)
- None required - all information from primary sources

### Tertiary (LOW confidence)
- None required

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyNaCl is the standard Python Ed25519 library, matches backend
- Architecture: HIGH - Directly derived from backend source code
- Pitfalls: HIGH - Identified from actual backend implementation details

**Research date:** 2026-02-22
**Valid until:** 30 days (stable cryptographic libraries)
