---
phase: 34-agent-demo-extended
plan: 03
subsystem: api
tags: [ed25519, key-rotation, dpop, shutil, dual-signature, cli]

# Dependency graph
requires:
  - phase: 34-agent-demo-extended
    provides: make_request HTTP wrapper, print_output utility, load_config/save_config, generate_keypair, create_dpop_proof
provides:
  - rotate-keys subcommand with full 2-step dual-signature key rotation
  - Automatic .env backup via shutil.copy2 before key update
  - New session_id persistence after rotation
affects: [35-agent-demo-oauth]

# Tech tracking
tech-stack:
  added: [shutil]
  patterns:
    - "Dual-signature rotation: DPoP proof with old key + body signature with new key"
    - "Atomic .env backup: shutil.copy2 before save_config to ensure recoverability"

key-files:
  created: []
  modified:
    - demo/agent/agent-demo.py

key-decisions:
  - "DPoP proof in complete step uses OLD private key (proves possession of current key)"
  - "Body signature in complete step uses NEW private key (proves possession of new key)"
  - "Backup via shutil.copy2(ENV_FILE, f'{ENV_FILE}.bak') before save_config — order ensures backup exists even if save fails"
  - "No Authorization Bearer header on complete step — backend authenticates via DPoP verification"

patterns-established:
  - "Dual-signature key rotation: initiate with Bearer auth, complete with DPoP (old key) + signature (new key)"
  - "File backup pattern: shutil.copy2 with ENV_FILE constant, single .env.bak overwrite"

# Metrics
duration: 2min
completed: 2026-02-22
---

# Phase 34 Plan 03: Key Rotation with Dual-Signature and .env Backup Summary

**rotate-keys subcommand with dual-signature Ed25519 key rotation (DPoP old key + body signature new key), automatic .env.bak backup via shutil.copy2, and new session persistence**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-22T18:48:34Z
- **Completed:** 2026-02-22T18:50:08Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Full 2-step rotate-keys subcommand: initiate rotation with Bearer auth, complete with DPoP proof (old key) and body signature (new key)
- Automatic .env backup to .env.bak via shutil.copy2 before updating keys and session
- New session_id returned by backend saved to .env alongside new keypair

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement rotate-keys subcommand with dual-signature flow** - `d8c00b5` (feat)
2. **Task 2: Verify shutil import and .env backup mechanism** - verification-only, no code changes needed

**Plan metadata:** (pending)

## Files Created/Modified
- `demo/agent/agent-demo.py` - Added `import shutil`, `cmd_rotate_keys` function with full initiate/complete flow, rotate-keys subparser, and command_handlers registration

## Decisions Made
- DPoP proof in complete step uses OLD private key — proves the agent currently possesses the registered key
- Body signature uses NEW private key — proves the agent possesses the key they want to rotate to
- No Authorization Bearer header on complete endpoint — backend authenticates entirely via DPoP verification against agent's current public key
- Backup happens before save_config — ensures .env.bak exists even if save operation fails
- Uses ENV_FILE constant throughout (not hardcoded ".env" strings)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 34 (Agent Demo Extended) is now complete with all 3 plans delivered
- All agent-facing CLI operations available: generate-keys, register, login, logout, info, configure, query, claim, revoke-overseer, rotate-keys
- Ready to proceed to Phase 35 (Agent Demo OAuth) for client registration and authorization
- No blockers for next phase

---
*Phase: 34-agent-demo-extended*
*Completed: 2026-02-22*
