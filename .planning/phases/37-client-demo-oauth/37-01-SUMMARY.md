---
phase: 37-client-demo-oauth
plan: 01
status: complete
completed: 2026-02-25
subsystem: demo/client
affects: [37-02]

artifacts:
  created: []
  modified:
    - demo/client/client-demo.py

tech-stack:
  added: []
  used:
    - python
    - PyNaCl
    - python-dotenv
    - hashlib
    - urllib

patterns:
  established:
    - DPoP proof JWT construction (typ=dpop+jwt, no jwk in header)
    - Access token hashing for ath claim (SHA-256 + base64url)
  followed:
    - Fail-fast HTTP wrapper (make_request + sys.exit(1))
    - Raw JSON output via print_output
    - private_key_jwt client authentication for token endpoint
    - Token auto-save to .env with AGENT_{id}_* namespace

decisions:
  - Hardcoded /v1/oauth/ prefix for all endpoint URLs (well-known URLs are buggy, missing /v1/)
  - DPoP proof header has NO jwk field (validateDPoPProof gets key from client record)
  - Refresh always overwrites BOTH access and refresh tokens in .env (server always rotates)

key_files:
  - path: demo/client/client-demo.py
    role: Client demo CLI script
    exports: [hash_access_token, create_dpop_proof, cmd_refresh, cmd_discover]

requires:
  satisfied:
    - CTOKEN-02 (refresh token grant)
    - COAUTH-03 (OpenID discovery)
---

# Phase 37 Plan 01 Summary

## What Was Done

Added helper functions and two new subcommands to `demo/client/client-demo.py`:

### Helper Functions (DPoP Proof Construction section)

1. **`hash_access_token(access_token: str) -> str`** — Computes SHA-256 hash of access token, returns base64url-encoded digest (no padding). Used for DPoP `ath` claim per RFC 9449.

2. **`create_dpop_proof(private_key, method, uri, access_token=None) -> str`** — Creates DPoP proof JWT with header `{"typ": "dpop+jwt", "alg": "EdDSA"}` (NO jwk). Payload includes `jti`, `htm`, `htu`, `iat`, and optional `ath` claim when access_token provided.

### Command Handlers

3. **`cmd_refresh(args) -> int`** — Refreshes access token using `grant_type=refresh_token` with `private_key_jwt` client authentication. Sends POST to `/v1/oauth/token` with client assertion (aud = token endpoint). Auto-saves both new access_token and refresh_token to `.env` using `set_key()`. Prints full token JSON to stdout.

4. **`cmd_discover(args) -> int`** — Fetches OpenID discovery document from `/v1/oauth/.well-known/openid-configuration`. Simple GET, no auth. Prints raw JSON via `print_output`. Note: URLs in response lack `/v1/` prefix (known backend bug) — displayed as-is.

### CLI Definitions

- `refresh --agent-id <id>` subcommand registered in argparse and command_handlers
- `discover` subcommand registered (no flags, reads backend_url from .env)

## Verification

- Syntax check: PASSED
- All 4 new functions present in AST
- CLI help shows both `refresh` and `discover` commands
- `refresh --help` shows `--agent-id` flag
- `discover --help` shows no required flags
