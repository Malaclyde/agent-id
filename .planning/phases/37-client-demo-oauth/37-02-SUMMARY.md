---
phase: 37-client-demo-oauth
plan: 02
status: complete
completed: 2026-02-25
subsystem: demo/client
affects: []

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
    - urllib

patterns:
  established:
    - DPoP-bound access token request (Authorization: DPoP + DPoP header)
    - Mutually exclusive --access/--refresh flags via argparse groups
  followed:
    - Fail-fast HTTP wrapper (make_request + sys.exit(1))
    - Raw JSON output via print_output
    - private_key_jwt client authentication (revoke, introspect)
    - Endpoint-specific aud in client assertion JWTs

decisions:
  - Userinfo uses DPoP proof (NOT private_key_jwt) — different auth from revoke/introspect
  - Each endpoint's client_assertion uses its own endpoint URL as aud (revoke -> revoke endpoint, introspect -> introspect endpoint)
  - No post-revocation cleanup of .env tokens (per CONTEXT.md)
  - token_type_hint included but cosmetic (backend accepts but ignores)

key_files:
  - path: demo/client/client-demo.py
    role: Client demo CLI script
    exports: [cmd_userinfo, cmd_revoke, cmd_introspect]

requires:
  satisfied:
    - COAUTH-01 (userinfo with DPoP)
    - CTOKEN-03 (token revocation)
    - COAUTH-02 (token introspection)
---

# Phase 37 Plan 02 Summary

## What Was Done

Added three new subcommands to `demo/client/client-demo.py`, completing all Phase 37 requirements.

### Command Handlers

1. **`cmd_userinfo(args) -> int`** — Queries userinfo endpoint with DPoP-bound access token. Loads access token from `AGENT_{id}_ACCESS_TOKEN` env var. Generates DPoP proof using `create_dpop_proof()` (from Plan 01) with `method="GET"`, `uri=userinfo_endpoint`, and `access_token` for ath claim binding. Sends GET request with `Authorization: DPoP {access_token}` and `DPoP: {proof}` headers. Prints raw JSON via `print_output`.

2. **`cmd_revoke(args) -> int`** — Revokes access or refresh token using `private_key_jwt` client authentication. Determines token type from mutually exclusive `--access`/`--refresh` flags. Client assertion aud is the revoke endpoint URL (`/v1/oauth/revoke`). Sends form-urlencoded POST with token, client_id, client_assertion, token_type_hint. No post-revocation .env cleanup.

3. **`cmd_introspect(args) -> int`** — Introspects token for status and metadata. Nearly identical to revoke: same `private_key_jwt` auth, same `--access`/`--refresh` flags, same form-urlencoded POST. Client assertion aud is the introspect endpoint URL (`/v1/oauth/introspect`). Prints raw JSON response (includes `active`, `client_id`, `token_type`, `exp`, `scope`, etc.).

### CLI Definitions

- `userinfo --agent-id <id>` — registered with required --agent-id
- `revoke --agent-id <id> (--access | --refresh)` — mutually exclusive group via `add_mutually_exclusive_group(required=True)`
- `introspect --agent-id <id> (--access | --refresh)` — same pattern, separate group variable name

### Final CLI Command List (9 total)

| Command | Auth | Key Flags |
|---------|------|-----------|
| generate-keys | None | --save |
| generate-verifier | None | None |
| token-exchange | private_key_jwt | --token, --code-verifier, --agent-id |
| config | None | --backend-url, --client-id, etc. |
| refresh | private_key_jwt | --agent-id |
| discover | None | None |
| userinfo | DPoP | --agent-id |
| revoke | private_key_jwt | --agent-id, --access/--refresh |
| introspect | private_key_jwt | --agent-id, --access/--refresh |

## Verification

- Syntax check: PASSED
- All 3 new functions present in AST
- CLI help shows all 9 commands
- `revoke --help` shows `--agent-id` and mutually exclusive `--access`/`--refresh`
- `introspect --help` shows same pattern
- `userinfo --help` shows `--agent-id`
