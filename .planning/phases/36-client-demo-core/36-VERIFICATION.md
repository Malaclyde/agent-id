---
phase: 36-client-demo-core
verified: 2026-02-22T20:59:26Z
status: human_needed
score: 13/13 must-haves verified
human_verification:
  - test: "End-to-End OAuth Token Exchange"
    expected: "Client successfully completes OAuth token exchange with the backend, receives tokens, and saves them to .env"
    why_human: "Requires a running backend server, registered OAuth client, and manual browser interaction to get the initial authorization code"
---

# Phase 36: Client Demo - Core Verification Report

**Phase Goal:** Client demo script handles configuration, PKCE, key generation, and token exchange.
**Verified:** 2026-02-22T20:59:26Z
**Status:** human_needed
**Re-verification:** No

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can import and use base64url encoding/decoding functions | ✓ VERIFIED | `base64url_encode` and `base64url_decode` functions exist and are used. |
| 2 | User can generate Ed25519 keypairs with base64url encoding | ✓ VERIFIED | `generate_keypair` returns b64url encoded keys via `SigningKey.generate`. |
| 3 | User can validate that public key derives from private key | ✓ VERIFIED | `validate_keys_match` verifies public key derivation. |
| 4 | User can load configuration from .env file with CLIENT_* namespace | ✓ VERIFIED | `load_config` loads from `.env` and uses `CLIENT_ID`, etc. |
| 5 | User can save configuration to .env file | ✓ VERIFIED | `save_config` writes config using `dotenv.set_key`. |
| 6 | User can generate PKCE verifier/challenge pair with S256 method | ✓ VERIFIED | `generate_pkce_pair` generates cryptographically secure pairs using SHA256. |
| 7 | User can create client assertion JWT for token endpoint authentication | ✓ VERIFIED | `create_client_assertion` creates valid JWT signed with Ed25519. |
| 8 | User can start HTTP callback server that blocks until tokens received | ✓ VERIFIED | `CallbackHandler` with `HTTPServer` blocking on `handle_request()`. |
| 9 | Callback server handles both GET (query params) and POST (body) requests | ✓ VERIFIED | `do_GET` and `do_POST` implemented in `CallbackHandler`. |
| 10 | User can run 'client-demo.py generate-keys --save' to create and store keys | ✓ VERIFIED | `cmd_generate_keys` parses `--save` and writes to config. |
| 11 | User can run 'client-demo.py generate-verifier' to get PKCE pair | ✓ VERIFIED | `cmd_generate_verifier` outputs JSON pair correctly. |
| 12 | User can run 'client-demo.py token-exchange' with required flags to complete OAuth flow | ✓ VERIFIED | `cmd_token_exchange` implements `/v1/oauth/token` exchange request. |
| 13 | Tokens are saved to .env after successful token exchange | ✓ VERIFIED | `cmd_token_exchange` uses `set_key` to write `AGENT_{id}_ACCESS_TOKEN`. |

**Score:** 13/13 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `demo/client/client-demo.py` | Core crypto utilities, config, CLI, client assertion | ✓ VERIFIED | 706 lines, no stubs, all required methods implemented. |
| `demo/client/requirements.txt` | Python dependencies (`pynacl`, `python-dotenv`) | ✓ VERIFIED | Exists and contains required dependencies. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `generate_keypair()` | `base64url_encode()` | Direct call | ✓ VERIFIED | Called on generated public/private bytes. |
| `load_config()` | `.env file` | `load_dotenv` | ✓ VERIFIED | Proper use of `dotenv` to load config. |
| `create_client_assertion()` | Ed25519 Key | `private_key.sign()` | ✓ VERIFIED | Payload properly encoded and signed. |
| `token-exchange command` | `/v1/oauth/token` | HTTP POST | ✓ VERIFIED | `urllib.request` performs the POST using `client_assertion`. |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| CCONF-01 | ✓ SATISFIED | None |
| CCONF-02 | ✓ SATISFIED | None |
| CCONF-03 | ✓ SATISFIED | None |
| CTOKEN-01 | ✓ SATISFIED | None |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `demo/client/client-demo.py` | - | None | - | None |

### Human Verification Required

### 1. End-to-End OAuth Token Exchange
**Test:** Run the token exchange flow (`generate-keys`, `generate-verifier`, authorize on backend, and `token-exchange`).
**Expected:** The client gets authorized, receives valid tokens, displays them, and stores them in `.env`.
**Why human:** Requires a running backend server, registered OAuth client, and manual browser interaction to get the initial authorization code.

### Gaps Summary

No programmatic gaps found. All automated checks pass, script correctly implements required client demo functionality. Awaiting human verification to ensure end-to-end functionality across components.

---

*Verified: 2026-02-22T20:59:26Z*
*Verifier: OpenCode (gsd-verifier)*
