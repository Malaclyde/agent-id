---
phase: 35-agent-demo-oauth
verified: 2026-02-22T14:40:00Z
status: passed
score: 8/8 must-haves verified
---

# Phase 35: Agent Demo - OAuth Client Verification Report

**Phase Goal:** Agent demo script handles OAuth client registration and authorization.
**Verified:** 2026-02-22
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence |
| --- | ------- | ---------- | -------- |
| 1   | User can register an OAuth client with name and redirect URI | ✓ VERIFIED | Lines 1070-1142 show complete implementation with --name and --redirect-uri args (required=True) |
| 2   | User can generate new keypair with --generate flag | ✓ VERIFIED | Lines 1087-1089 show generate_keypair() called when --generate flag present (73-line implementation) |
| 3   | User can provide explicit keys with --private-key and --public-key flags | ✓ VERIFIED | Lines 1090-1097 show explicit key handling with validate_keys_match() function |
| 4   | Client keys are stored in .env using CLIENT_<client-id>_* namespace | ✓ VERIFIED | Lines 1135-1137 show set_key() calls with CLIENT_{client_id}_PUBLIC_KEY pattern |
| 5   | User can initiate OAuth authorization with client ID and redirect URI | ✓ VERIFIED | Lines 1145-1202 show complete implementation with --client-id and --redirect-uri args (required=True) |
| 6   | User must provide PKCE code challenge via --code-challenge flag | ✓ VERIFIED | Line 1171 shows code_challenge from args, line 1426 shows --code-challenge required |
| 7   | Authorization code is printed to stdout in raw JSON format | ✓ VERIFIED | Line 1201 shows print_output(response) which outputs full JSON (no pagination) |
| 8   | Script auto-selects Bearer session or DPoP authentication | ✓ VERIFIED | Lines 1184-1194 show dual auth pattern: Bearer if has_session, DPoP fallback |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `demo/agent/agent-demo.py` (cmd_register_client) | Register client with key provision options | ✓ VERIFIED | 73-line implementation (lines 1070-1142), all key options implemented |
| `demo/agent/agent-demo.py` (cmd_authorize) | Authorize with PKCE support | ✓ VERIFIED | 58-line implementation (lines 1145-1202), all flags present |

**Supporting functions verified:**
- `generate_keypair()` - 54 lines, creates Ed25519 keypair
- `validate_keys_match()` - 33 lines, validates key pair matches
- `make_request()` - 35 lines, unified HTTP wrapper
- `print_output()` - 12 lines, outputs full JSON
- `set_key()` - Imported from dotenv, used for .env updates
- `load_private_key()` - Loads Ed25519 private key
- `create_dpop_proof()` - Creates DPoP proof header

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `cmd_register_client` | POST /v1/clients/register/agent | make_request with Bearer auth | ✓ WIRED | Line 1118: URL constructed, Line 1121: Bearer {session_id}, Line 1125: POST request |
| `cmd_register_client` | .env file | set_key with CLIENT_* namespace | ✓ WIRED | Lines 1135-1137: CLIENT_{client_id}_PUBLIC_KEY, PRIVATE_KEY, ID saved |
| `cmd_authorize` | POST /v1/oauth/authorize | make_request with Bearer or DPoP auth | ✓ WIRED | Line 1165: URL constructed, Lines 1184-1194: dual auth (Bearer preferred, DPoP fallback) |
| `cmd_authorize` | print_output | authorization code to stdout | ✓ WIRED | Line 1201: print_output(response) prints full JSON response |

### CLI Commands Verified

**register-client command:**
```bash
$ python demo/agent/agent-demo.py register-client --help
usage: agent-demo.py register-client [-h] --name NAME
                                     --redirect-uri REDIRECT_URI
                                     [--scope SCOPE] [--generate]
                                     [--private-key PRIVATE_KEY]
                                     [--public-key PUBLIC_KEY]
```
✓ All required flags present: --name, --redirect-uri
✓ Key provision options: --generate OR --private-key + --public-key
✓ Optional: --scope

**authorize command:**
```bash
$ python demo/agent/agent-demo.py authorize --help
usage: agent-demo.py authorize [-h] --client-id CLIENT_ID
                               --redirect-uri REDIRECT_URI
                               --code-challenge CODE_CHALLENGE [--scope SCOPE]
                               [--state STATE]
```
✓ All required flags present: --client-id, --redirect-uri, --code-challenge
✓ Optional: --scope (defaults to "id name description subscription"), --state

### Requirements Coverage

| Requirement | Status | Evidence |
| ----------- | ------ | -------- |
| AOAUTH-01: User can register an OAuth client as an agent with key generation or provision options | ✓ SATISFIED | cmd_register_client implements all three key options (--generate, explicit keys, or neither) |
| AOAUTH-02: User can initiate OAuth authorization for a client, receiving authorization code | ✓ SATISFIED | cmd_authorize implements PKCE flow and outputs authorization code via print_output |

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| None | - | - | No anti-patterns found in verified code |

### Human Verification Required

**No human verification required** - All verification items can be confirmed programmatically through:
1. Code structure analysis (functions exist and are substantive)
2. CLI help output (flags are present and properly configured)
3. Pattern matching (URLs, namespaces, auth patterns verified)

### Gaps Summary

**No gaps found.** All must-haves from both 35-01-PLAN.md and 35-02-PLAN.md have been verified:

**Truths verified:**
- OAuth client registration with name and redirect URI ✓
- Key generation via --generate flag ✓
- Explicit key provision via --private-key and --public-key flags ✓
- Client key storage in .env with CLIENT_<client-id>_* namespace ✓
- OAuth authorization initiation with client ID and redirect URI ✓
- PKCE code challenge via --code-challenge flag ✓
- Authorization code printed to stdout in raw JSON ✓
- Dual auth auto-selection (Bearer preferred, DPoP fallback) ✓

**Artifacts verified:**
- demo/agent/agent-demo.py with cmd_register_client (73 lines) ✓
- demo/agent/agent-demo.py with cmd_authorize (58 lines) ✓
- All supporting helper functions (generate_keypair, validate_keys_match, make_request, etc.) ✓

**Key links verified:**
- cmd_register_client → POST /v1/clients/register/agent via Bearer auth ✓
- cmd_register_client → .env file via set_key with CLIENT_* namespace ✓
- cmd_authorize → POST /v1/oauth/authorize via Bearer or DPoP auth ✓
- cmd_authorize → print_output for JSON output ✓

Phase 35 goal achieved. Ready to proceed to Phase 36.

---

_Verified: 2026-02-22T14:40:00Z_
_Verifier: OpenCode (gsd-verifier)_
