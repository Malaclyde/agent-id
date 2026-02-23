# Phase 37: Client Demo - OAuth Operations — Research

**Researched:** 2026-02-23
**Domain:** DPoP proof generation, token refresh/revoke/introspect, well-known endpoint URL mismatch
**Confidence:** HIGH — All findings sourced directly from backend TypeScript source code

## Summary

Phase 37 adds five new subcommands to `demo/client/client-demo.py`: `refresh`, `revoke`, `introspect`, `userinfo`, and `discover`. The foundational patterns (base64url encoding, Ed25519 signing, `make_request`, `print_output`, `create_client_assertion`) are already in place from Phase 36.

The three research directives are fully resolved: (1) DPoP proof for userinfo uses NO `jwk` in header and MUST include `ath`; (2) refresh grant DOES require `private_key_jwt` auth just like token exchange; (3) there is a **confirmed critical mismatch** between well-known endpoint URLs (missing `/v1/`) and actual backend routes (have `/v1/`). The demo script must hardcode `/v1/oauth/` paths — it CANNOT use the well-known URLs for either HTTP requests or JWT `aud` claims.

**Primary recommendation:** Hard-construct all endpoint URLs as `{backend_url}/v1/oauth/{endpoint}`. Do NOT use well-known discovery URLs for requests or `aud` claims. Only use `discover` subcommand to display the (buggy) well-known document as-is for informational purposes.

---

## Research Directive Answers

### Directive 1: DPoP Proof Claims for `validateDPoPProof`

**Source:** `backend/src/services/dpop.ts`, lines 17–91 (confirmed, read directly)

`validateDPoPProof` is called at userinfo with: `validateDPoPProof(dpopProof, client.public_key, 'GET', `${requestUrl.origin}${requestUrl.pathname}`, accessToken)`

**DPoP JWT Header (EXACTLY):**
```json
{"typ": "dpop+jwt", "alg": "EdDSA"}
```
- `typ` must be `"dpop+jwt"` — validated at line 42
- `alg` must be `"EdDSA"` — validated at line 46
- **NO `jwk` field** — `validateDPoPProof` does NOT look for `jwk`. That is only `validateDPoPForAuth` (used for agent login). Including `jwk` would not break validation but is incorrect.

**DPoP JWT Payload (EXACTLY):**
```json
{
  "jti": "<uuid>",
  "htm": "GET",
  "htu": "<userinfo_url>",
  "iat": <unix_timestamp>,
  "ath": "<sha256_base64url_of_access_token>"
}
```

| Claim | Required | Validation | Notes |
|-------|----------|------------|-------|
| `jti` | YES (part of interface) | NOT checked for replay in `validateDPoPProof` | Only `validateDPoPForAuth` checks replay via `isJtiReplayed` |
| `htm` | YES | Must equal `"GET"` (exact match, line 63) | Case-sensitive |
| `htu` | YES | Normalized and compared to request URI (line 67–72) | Normalized = `protocol//host/pathname`, no query/fragment |
| `iat` | YES | Must be within ±60 seconds (line 74–77) | Unix epoch integer |
| `ath` | Conditional | Checked only if BOTH `accessToken` provided AND `payload.ath` exists (line 79) | Backend always passes `accessToken` to this call, so include `ath` |

**`htu` value for userinfo:** `{backend_url}/v1/oauth/userinfo`  
The backend normalizes via `normalizeUri` → `${url.protocol}//${url.host}${url.pathname}`. No query string, no trailing slash.

**`ath` computation:**
```python
import hashlib
def hash_access_token(access_token: str) -> str:
    """SHA-256 hash of access token, base64url encoded (no padding)."""
    digest = hashlib.sha256(access_token.encode('utf-8')).digest()
    return base64url_encode(digest)
```
Verified matches `hashAccessToken` in dpop.ts (lines 134–149): SHA-256 → btoa → replace +/= → no padding.

**Signing:** Sign with the CLIENT's Ed25519 private key (same key used for `private_key_jwt` assertions). The backend retrieves `client.public_key` from the OAuth client record and passes it directly to `validateDPoPProof` — no public key embedding in JWT needed.

---

### Directive 2: Token Endpoint Refresh Grant Parameters

**Source:** `backend/src/routes/oauth.ts`, `handleRefreshTokenGrant` function, lines 306–398 (read directly)

**YES — refresh grant requires `private_key_jwt` client authentication.**

**Required body parameters (application/x-www-form-urlencoded):**
```
grant_type=refresh_token
refresh_token=<refresh_token>
client_id=<client_id>
client_assertion=<jwt_signed_with_ed25519>
```

**Optional:**
```
scope=<narrowed_scope>   # Can narrow scope from original grant; omit to keep original
```

**Client assertion `aud` for refresh:** `{backend_url}/v1/oauth/token` (line 339: `${new URL(c.req.url).origin}/v1/oauth/token`)

**Important difference from auth_code grant:** The refresh handler does NOT check `jwtPayload.exp` (no expiry check on the client_assertion JWT). Auth code grant checks exp (line 241). However, keep including `exp: now + 60` for correctness — the existing `create_client_assertion()` already does this.

**Response:**
```json
{
  "access_token": "<new_access_token>",
  "token_type": "DPoP",
  "expires_in": 300,
  "refresh_token": "<new_refresh_token>",
  "scope": "<granted_scope>"
}
```

**Refresh token rotation:** A new refresh token is ALWAYS issued (`generateRefreshToken` called unconditionally at line 384). Both `AGENT_{id}_ACCESS_TOKEN` and `AGENT_{id}_REFRESH_TOKEN` must be overwritten in `.env`.

---

### Directive 3: JWT `aud` Claim — `/v1/` Prefix and Well-Known Mismatch

**Source:** `backend/src/routes/oauth.ts` + `backend/src/index.ts` (read directly)

**CONFIRMED CRITICAL MISMATCH** — The well-known endpoint returns wrong URLs.

**Route mounting (`index.ts` line 54):**
```typescript
app.route('/v1/oauth', oauth);
```
All actual routes: `/v1/oauth/token`, `/v1/oauth/userinfo`, `/v1/oauth/revoke`, `/v1/oauth/introspect`, `/v1/oauth/.well-known/openid-configuration`

**Well-known response (`oauth.ts` lines 669–685):**
```typescript
token_endpoint: `${baseUrl}/oauth/token`,        // MISSING /v1/
userinfo_endpoint: `${baseUrl}/oauth/userinfo`,   // MISSING /v1/
revocation_endpoint: `${baseUrl}/oauth/revoke`,   // MISSING /v1/
introspection_endpoint: `${baseUrl}/oauth/introspect`, // MISSING /v1/
```

**JWT `aud` validation constructs from actual request URL** (which includes `/v1/`):
- Token: `${new URL(c.req.url).origin}/v1/oauth/token` (line 231, 339)
- Revoke: `${new URL(c.req.url).origin}/v1/oauth/revoke` (line 536)
- Introspect: `${new URL(c.req.url).origin}/v1/oauth/introspect` (line 605)

**Consequence for demo script:**

| Purpose | Wrong (well-known URL) | Correct (hardcoded) |
|---------|----------------------|---------------------|
| HTTP request to token | `{url}/oauth/token` → 404 | `{backend_url}/v1/oauth/token` |
| JWT `aud` for token | `{url}/oauth/token` → 401 | `{backend_url}/v1/oauth/token` |
| HTTP request to revoke | `{url}/oauth/revoke` → 404 | `{backend_url}/v1/oauth/revoke` |
| JWT `aud` for revoke | `{url}/oauth/revoke` → 401 | `{backend_url}/v1/oauth/revoke` |
| HTTP request to introspect | `{url}/oauth/introspect` → 404 | `{backend_url}/v1/oauth/introspect` |
| JWT `aud` for introspect | `{url}/oauth/introspect` → 401 | `{backend_url}/v1/oauth/introspect` |
| HTTP request to userinfo | `{url}/oauth/userinfo` → 404 | `{backend_url}/v1/oauth/userinfo` |
| DPoP `htu` for userinfo | `{url}/oauth/userinfo` → 401 | `{backend_url}/v1/oauth/userinfo` |

**Well-known fetch for `discover` subcommand:** `{backend_url}/v1/oauth/.well-known/openid-configuration` (must include `/v1/`).

**Decision: NEVER use well-known URLs for anything except the `discover` subcommand display.** Hardcode `/v1/oauth/` paths constructed from `config["backend_url"]`.

---

## Code Examples

### New Function: `create_dpop_proof()`

```python
def create_dpop_proof(
    private_key: SigningKey,
    method: str,
    uri: str,
    access_token: Optional[str] = None
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
        "alg": "EdDSA"
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
```

### New Function: `hash_access_token()`

```python
def hash_access_token(access_token: str) -> str:
    """
    Compute SHA-256 hash of access token, base64url encoded (no padding).
    Used for DPoP 'ath' claim per RFC 9449.
    """
    digest = hashlib.sha256(access_token.encode("utf-8")).digest()
    return base64url_encode(digest)
```

### `cmd_refresh` Subcommand

```python
def cmd_refresh(args) -> int:
    """Refresh access token using refresh token grant."""
    config = load_config()
    backend_url = config["backend_url"]
    client_id = config["client_id"]

    # Load stored refresh token
    load_dotenv(ENV_FILE)
    refresh_token = os.getenv(f"AGENT_{args.agent_id}_REFRESH_TOKEN")
    if not refresh_token:
        print(f"Error: No refresh token found for agent {args.agent_id}", file=sys.stderr)
        return 1

    # Build token endpoint (MUST use /v1/ prefix — NOT from well-known)
    token_endpoint = f"{backend_url}/v1/oauth/token"

    # Create client assertion (aud = token endpoint)
    private_key = load_private_key(config["private_key"])
    client_assertion = create_client_assertion(private_key, client_id, token_endpoint)

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

    # Save new tokens (rotation: always overwrite both)
    result = json.loads(response_string)
    if result.get("access_token"):
        set_key(ENV_FILE, f"AGENT_{args.agent_id}_ACCESS_TOKEN", result["access_token"])
    if result.get("refresh_token"):
        set_key(ENV_FILE, f"AGENT_{args.agent_id}_REFRESH_TOKEN", result["refresh_token"])

    # Print full token JSON to stdout
    print_output(response_string)
    return 0
```

### `cmd_userinfo` Subcommand

```python
def cmd_userinfo(args) -> int:
    """Query userinfo endpoint with DPoP-bound access token."""
    config = load_config()
    backend_url = config["backend_url"]

    # Load stored access token
    load_dotenv(ENV_FILE)
    access_token = os.getenv(f"AGENT_{args.agent_id}_ACCESS_TOKEN")
    if not access_token:
        print(f"Error: No access token found for agent {args.agent_id}", file=sys.stderr)
        return 1

    # Build userinfo endpoint (MUST use /v1/ prefix)
    userinfo_endpoint = f"{backend_url}/v1/oauth/userinfo"

    # Generate DPoP proof (signed with CLIENT key, includes ath)
    private_key = load_private_key(config["private_key"])
    dpop_proof = create_dpop_proof(private_key, "GET", userinfo_endpoint, access_token)

    headers = {
        "Authorization": f"DPoP {access_token}",
        "DPoP": dpop_proof,
    }
    response_string = make_request(userinfo_endpoint, headers)
    print_output(response_string)
    return 0
```

### `cmd_revoke` Subcommand

```python
def cmd_revoke(args) -> int:
    """Revoke access or refresh token."""
    config = load_config()
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
        print(f"Error: No token found for agent {args.agent_id}", file=sys.stderr)
        return 1

    # Build revoke endpoint (MUST use /v1/ prefix)
    revoke_endpoint = f"{backend_url}/v1/oauth/revoke"

    # Client assertion aud must match the revoke endpoint (NOT well-known URL)
    private_key = load_private_key(config["private_key"])
    client_assertion = create_client_assertion(private_key, client_id, revoke_endpoint)

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
```

### `cmd_introspect` Subcommand

```python
def cmd_introspect(args) -> int:
    """Introspect token for status and metadata."""
    config = load_config()
    backend_url = config["backend_url"]
    client_id = config["client_id"]

    load_dotenv(ENV_FILE)
    if args.access:
        token = os.getenv(f"AGENT_{args.agent_id}_ACCESS_TOKEN")
        token_type_hint = "access_token"
    else:
        token = os.getenv(f"AGENT_{args.agent_id}_REFRESH_TOKEN")
        token_type_hint = "refresh_token"

    if not token:
        print(f"Error: No token found for agent {args.agent_id}", file=sys.stderr)
        return 1

    # Build introspect endpoint (MUST use /v1/ prefix)
    introspect_endpoint = f"{backend_url}/v1/oauth/introspect"

    # Client assertion aud must match introspect endpoint
    private_key = load_private_key(config["private_key"])
    client_assertion = create_client_assertion(private_key, client_id, introspect_endpoint)

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
```

### `cmd_discover` Subcommand

```python
def cmd_discover(args) -> int:
    """Fetch and display OpenID discovery document."""
    config = load_config()
    backend_url = config["backend_url"]

    # Well-known URL DOES need /v1/ prefix (route mounted at /v1/oauth)
    well_known_url = f"{backend_url}/v1/oauth/.well-known/openid-configuration"

    headers = {}  # No auth required
    response_string = make_request(well_known_url, headers)
    # Note: URLs in response lack /v1/ prefix (known backend bug) — display as-is
    print_output(response_string)
    return 0
```

---

## Architecture: New Functions to Add

Two new helper functions must be added to the script before the command handlers section:

1. **`hash_access_token(access_token: str) -> str`** — SHA-256 + base64url for `ath` claim
2. **`create_dpop_proof(private_key, method, uri, access_token=None) -> str`** — DPoP JWT for userinfo

These differ from `create_client_assertion` in:
- Header `typ`: `"dpop+jwt"` vs `"JWT"`
- No `jwk` in header
- Payload has `htm`/`htu`/`jti`/`iat`/`ath` (NOT `iss`/`sub`/`aud`/`exp`)

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Access token hashing | Custom base64 logic | `hashlib.sha256` + existing `base64url_encode` | Already in script |
| DPoP JWT signing | Custom crypto | Same PyNaCl `SigningKey.sign()` pattern | Same as client assertion signing |
| Token storage after refresh | Custom .env writing | `set_key(ENV_FILE, key, value)` | Already used in `token-exchange` |
| Well-known endpoint discovery | Manual URL construction | Always fetch `/v1/oauth/.well-known/openid-configuration` | Fail-fast if unreachable |
| Well-known URLs for requests | Use as-is | Hardcode `/v1/oauth/` prefix | Well-known URLs are wrong (missing `/v1/`) |

---

## Common Pitfalls

### Pitfall 1: Using Well-Known URLs for Requests or JWT `aud`
**What goes wrong:** 404 on HTTP requests, or 401 "JWT aud must match" on revoke/introspect
**Why it happens:** Well-known returns `{base}/oauth/token` but actual route is `{base}/v1/oauth/token`
**How to avoid:** Always construct endpoint URLs from `config["backend_url"]` with `/v1/oauth/` prefix. NEVER use URLs from the well-known discovery document for anything other than `discover` display.
**Warning signs:** 404 responses, or 401 with "JWT aud must match" error

### Pitfall 2: Including `jwk` in DPoP Proof Header
**What goes wrong:** Doesn't cause validation failure (not checked by `validateDPoPProof`), but is semantically wrong
**Why it happens:** Confusion with agent-demo DPoP proofs which use `validateDPoPForAuth` (requires `jwk`)
**How to avoid:** DPoP for userinfo uses `validateDPoP`**Proof** (no jwk). DPoP for agent auth uses `validateDPoP`**ForAuth** (requires jwk). They are different functions.

### Pitfall 3: Missing `ath` Claim in DPoP Proof
**What goes wrong:** Technically passes validation (check is conditional on both `accessToken` AND `payload.ath` existing), but incorrect per RFC 9449
**Why it happens:** `ath` appears optional in the TypeScript interface (`ath?: string`)
**How to avoid:** Always include `ath` when `access_token` is available. The backend passes `accessToken` to `validateDPoPProof`, so the binding check will run when `ath` is present.

### Pitfall 4: Refresh Token Not Rotated in `.env`
**What goes wrong:** Old refresh token used again → invalid grant on next refresh
**Why it happens:** Only updating `ACCESS_TOKEN`, forgetting `REFRESH_TOKEN`
**How to avoid:** Always call `set_key` for BOTH `AGENT_{id}_ACCESS_TOKEN` AND `AGENT_{id}_REFRESH_TOKEN` after refresh. Backend always issues a new refresh token.

### Pitfall 5: Wrong `htu` in DPoP Proof
**What goes wrong:** 401 "DPoP htu mismatch"
**Why it happens:** Including query string in `htu`, or using wrong path
**How to avoid:** `htu` must be `{backend_url}/v1/oauth/userinfo` — no query string, no trailing slash. Backend normalizes via `${url.protocol}//${url.host}${url.pathname}`.

### Pitfall 6: `aud` in Revoke/Introspect Assertions Points to Token Endpoint
**What goes wrong:** 401 "JWT aud must match revocation endpoint" or introspection endpoint
**Why it happens:** Reusing token endpoint `aud` for all assertions, or calling `create_client_assertion` with token endpoint URL
**How to avoid:** Each endpoint needs its own assertion with the SPECIFIC endpoint as `aud`:
- Refresh: `aud = {backend_url}/v1/oauth/token`
- Revoke: `aud = {backend_url}/v1/oauth/revoke`
- Introspect: `aud = {backend_url}/v1/oauth/introspect`

---

## Backend Response Shapes

### Userinfo Response (scope-dependent)
```json
{
  "sub": "<agent_id>",
  "id": "<agent_id>",         // if 'id' scope
  "name": "<agent_name>",     // if 'name' scope
  "description": "<desc>",    // if 'description' scope
  "public_key": "<key>",      // if 'pub_key' scope
  "oauth_count": 5,           // if 'subscription' scope
  "billing_period_end": "..."  // if 'subscription' scope
}
```

### Revoke Response
```json
{}
```
Status 200, empty object. `print_output` will render as `{}`.

### Introspect Response (active token)
```json
{
  "active": true,
  "client_id": "<client_id>",
  "token_type": "access_token",
  "exp": 1234567890,
  "iat": 1234567890,
  "sub": "<agent_id>",
  "scope": "<scope>",
  "username": "<name>"  // only if 'name' scope in token
}
```

### Introspect Response (inactive/revoked)
```json
{"active": false}
```

---

## CLI Argument Patterns

### `refresh` subcommand
```
token-exchange --agent-id <id>     # NEW: already done per CONTEXT.md
refresh --agent-id <id>
```

### `userinfo` subcommand
```
userinfo --agent-id <id>
```

### `revoke` subcommand (mutually exclusive `--access`/`--refresh`)
```
revoke --agent-id <id> --access
revoke --agent-id <id> --refresh
```

### `introspect` subcommand (same pattern)
```
introspect --agent-id <id> --access
introspect --agent-id <id> --refresh
```

### `discover` subcommand
```
discover
```
No flags. Reads `backend_url` from `.env`.

**Argparse pattern for `--access`/`--refresh` (mutually exclusive):**
```python
group = parser_revoke.add_mutually_exclusive_group(required=True)
group.add_argument("--access", action="store_true", help="Revoke access token")
group.add_argument("--refresh", action="store_true", help="Revoke refresh token")
```

---

## Open Questions

None. All three research directives are fully resolved from backend source.

---

## Sources

### Primary (HIGH confidence)
- `backend/src/services/dpop.ts` — Read directly. Confirms DPoP header/payload requirements, `validateDPoPProof` vs `validateDPoPForAuth` distinction, `hashAccessToken` algorithm, `normalizeUri` behavior.
- `backend/src/routes/oauth.ts` — Read directly. Confirms refresh grant body params, `private_key_jwt` requirement, `aud` construction for all endpoints, well-known URL mismatch, revoke/introspect response shapes.
- `backend/src/index.ts` — Read directly. Confirms route mounting at `/v1/oauth`.
- `demo/client/client-demo.py` — Read directly. Confirms existing helper functions, `create_client_assertion` signature, token storage patterns.

### No secondary or tertiary sources needed
All findings come from authoritative source: the actual backend code being integrated against.

---

## Metadata

**Confidence breakdown:**
- DPoP proof claims: HIGH — Read directly from `validateDPoPProof` in dpop.ts
- Refresh grant params: HIGH — Read directly from `handleRefreshTokenGrant` in oauth.ts
- JWT `aud` `/v1/` prefix: HIGH — Confirmed from route mounting in index.ts and `aud` construction in oauth.ts
- Well-known URL mismatch: HIGH — Confirmed from well-known handler vs actual routes
- Response shapes: HIGH — Read directly from route handlers

**Research date:** 2026-02-23
**Valid until:** 2026-03-23 (stable — backend source is the ground truth)
