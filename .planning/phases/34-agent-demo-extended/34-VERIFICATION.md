---
phase: 34-agent-demo-extended
verified: 2026-02-22T19:05:00Z
status: passed
score: 12/12 must-haves verified
---

# Phase 34: Agent Demo - Extended Operations Verification Report

**Phase Goal:** Agent demo script handles queries, claims, oversight, and key rotation.
**Verified:** 2026-02-22T19:05:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can query OAuth history via CLI | ✓ VERIFIED | `cmd_query` (L900) with `target=="history"` → GET `/v1/agents/me/oauth-history` (L922), registered as `"query"` in command_handlers (L1274) |
| 2 | User can query overseer info via CLI | ✓ VERIFIED | `cmd_query` (L900) with `target=="overseers"` → GET `/v1/agents/me/overseer` (L924), uses Bearer auth (L919) |
| 3 | Queries output raw pretty-printed JSON without pagination | ✓ VERIFIED | `print_output` (L690-700) parses with `json.loads` and dumps with `json.dumps(obj, indent=2)`, no pagination/truncation. Called at L927. |
| 4 | API errors fail fast with raw JSON bodies | ✓ VERIFIED | `make_request` (L654-687) catches `HTTPError`, prints raw `e.read().decode('utf-8')` to `sys.stderr` (L683), calls `sys.exit(1)` (L684). `SystemExit` not caught by `except Exception` in callers. |
| 5 | User can complete claim with session auth | ✓ VERIFIED | `cmd_claim` (L934) checks `has_session` (L942/959), adds `Bearer` header (L960), POSTs to `/v1/agents/claim/complete/{challenge_id}` (L953/966) |
| 6 | User can complete claim with DPoP auth | ✓ VERIFIED | When no session_id but keys exist (L943/961), loads private key (L962), creates DPoP proof (L963), sets `DPoP` header (L964) |
| 7 | User can revoke overseer without confirmation | ✓ VERIFIED | `cmd_revoke_overseer` (L971) — no `input()` calls anywhere in file. POSTs to `/v1/agents/revoke-overseer` (L988/991) immediately. |
| 8 | API errors output raw JSON to stderr and exit 1 (claims/revoke) | ✓ VERIFIED | Both `cmd_claim` and `cmd_revoke_overseer` use `make_request` without wrapping in try/except for HTTP errors. make_request handles all error output. |
| 9 | User can rotate keys via single CLI command | ✓ VERIFIED | `cmd_rotate_keys` (L996) performs full 2-step initiate/complete flow in one function (72 lines), registered as `"rotate-keys"` (L1277) |
| 10 | Key rotation uses dual-signature (old key DPoP + new key signature) | ✓ VERIFIED | Step 4: `new_private_key.sign(challenge_data...)` (L1035). Step 5: `create_dpop_proof(old_private_key, ...)` (L1040). Complete headers have DPoP (old key, L1043) with NO Bearer header. Body has signature from new key (L1045). |
| 11 | .env auto-overwritten with .env.bak backup | ✓ VERIFIED | `shutil.copy2(ENV_FILE, f"{ENV_FILE}.bak")` (L1054) uses ENV_FILE constant. Backup occurs BEFORE `save_config(config)` (L1059). |
| 12 | New session_id saved to .env | ✓ VERIFIED | Extracts `new_session_id = complete_data["session_id"]` (L1051), sets `config["session_id"] = new_session_id` (L1058), calls `save_config(config)` (L1059). |

**Score:** 12/12 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `demo/agent/agent-demo.py` | Contains `make_request` | ✓ VERIFIED | L654, 34 lines, substantive HTTP wrapper with error handling |
| `demo/agent/agent-demo.py` | Contains `print_output` | ✓ VERIFIED | L690, 11 lines, parses and pretty-prints JSON |
| `demo/agent/agent-demo.py` | Contains `cmd_query` | ✓ VERIFIED | L900, 32 lines, handles history + overseers targets |
| `demo/agent/agent-demo.py` | Contains `cmd_claim` | ✓ VERIFIED | L934, 35 lines, dual auth (session/DPoP) |
| `demo/agent/agent-demo.py` | Contains `cmd_revoke_overseer` | ✓ VERIFIED | L971, 23 lines, session auth, no confirmation |
| `demo/agent/agent-demo.py` | Contains `cmd_rotate_keys` | ✓ VERIFIED | L996, 72 lines, full 2-step dual-signature flow |
| `demo/agent/agent-demo.py` | Contains `shutil.copy2` | ✓ VERIFIED | L1054, uses ENV_FILE constant |
| `demo/agent/agent-demo.py` | Contains `import shutil` | ✓ VERIFIED | L21 |

File is 1289 lines total — substantive, no stubs, no placeholders.

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `cmd_query` | `/v1/agents/me/oauth-history` | `make_request` | ✓ WIRED | URL built at L922, make_request called at L926 |
| `cmd_query` | `/v1/agents/me/overseer` | `make_request` | ✓ WIRED | URL built at L924, make_request called at L926 |
| `cmd_claim` | `/v1/agents/claim/complete/{id}` | `make_request` | ✓ WIRED | URL built at L953, make_request called at L966 with POST + body |
| `cmd_revoke_overseer` | `/v1/agents/revoke-overseer` | `make_request` | ✓ WIRED | URL built at L988, make_request called at L991 with POST |
| `cmd_rotate_keys` | `/v1/agents/rotate-key/initiate` | `make_request` | ✓ WIRED | URL built at L1020, make_request called at L1027-1029 with Bearer auth |
| `cmd_rotate_keys` | `/v1/agents/rotate-key/complete/{id}` | `make_request` | ✓ WIRED | URL built at L1039, make_request called at L1047-1049 with DPoP (old key) |
| `cmd_rotate_keys` | `.env` backup | `shutil.copy2` | ✓ WIRED | shutil.copy2 at L1054 → save_config at L1059 (correct order) |

All 7 key links verified and correctly wired.

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| AAUTH-05: Key rotation with dual-signature | ✓ SATISFIED | `cmd_rotate_keys` performs initiate (Bearer) → complete (DPoP old key + signature new key) |
| AQUERY-01: Query OAuth history | ✓ SATISFIED | `cmd_query` with `target="history"` → GET `/v1/agents/me/oauth-history` |
| AQUERY-02: Query overseer info | ✓ SATISFIED | `cmd_query` with `target="overseers"` → GET `/v1/agents/me/overseer` |
| ACLAIM-01: Complete claim challenge | ✓ SATISFIED | `cmd_claim` with dual auth (session Bearer or DPoP fallback) |
| ACLAIM-02: Revoke overseer | ✓ SATISFIED | `cmd_revoke_overseer` with session auth, no confirmation prompt |

All 5 requirements satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No TODO/FIXME/placeholder patterns found | — | — |
| — | — | No `input()` calls found (no unwanted prompts) | — | — |
| — | — | No stub/empty implementations found | — | — |

Clean — no anti-patterns detected.

### Human Verification Required

### 1. Query History End-to-End
**Test:** Run `python agent-demo.py query history` with a valid session
**Expected:** Raw pretty-printed JSON of OAuth authorization history
**Why human:** Requires running backend server with test data

### 2. Query Overseers End-to-End
**Test:** Run `python agent-demo.py query overseers` with a valid session
**Expected:** Raw pretty-printed JSON of current overseer information
**Why human:** Requires running backend server with test data

### 3. Claim with Session Auth
**Test:** Run `python agent-demo.py claim --challenge-id <id> --overseer-id <id>` with active session
**Expected:** Claim completes, raw JSON response displayed
**Why human:** Requires valid claim challenge from backend

### 4. Claim with DPoP Auth
**Test:** Remove session_id from .env, run claim with keys only
**Expected:** DPoP auth path used, claim completes
**Why human:** Requires valid claim challenge and DPoP verification on backend

### 5. Revoke Overseer
**Test:** Run `python agent-demo.py revoke-overseer` with active session and existing overseer
**Expected:** Overseer revoked immediately (no confirmation prompt), raw JSON response
**Why human:** Requires existing overseer relationship in backend

### 6. Key Rotation End-to-End
**Test:** Run `python agent-demo.py rotate-keys` with valid session and keys
**Expected:** New keys generated, rotation completed, .env.bak created, .env updated with new keys and session
**Why human:** Requires running backend with full rotation endpoint support

### Gaps Summary

No gaps found. All 12 observable truths are verified against actual code. All 8 artifacts exist and are substantive. All 7 key links are correctly wired. All 5 requirements are satisfied. No anti-patterns detected.

The implementation is complete and structurally sound:
- `make_request` provides fail-fast HTTP with raw error bodies to stderr + `sys.exit(1)`
- `print_output` provides consistent raw JSON pretty-printing
- `cmd_query` handles both history and overseer targets with Bearer auth
- `cmd_claim` auto-selects between Bearer and DPoP auth based on config state
- `cmd_revoke_overseer` executes immediately with no confirmation prompt
- `cmd_rotate_keys` performs full 2-step dual-signature rotation with correct key usage (old key for DPoP, new key for body signature), .env backup before update, and new session persistence

---

_Verified: 2026-02-22T19:05:00Z_
_Verifier: OpenCode (gsd-verifier)_
