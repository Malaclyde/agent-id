---
phase: 35-agent-demo-oauth
plan: 01
subsystem: cli
tags: [oauth, client-registration, ed25519, python, argparse]

# Dependency graph
requires:
  - phase: 33-agent-demo-core
    provides: Agent registration, login, DPoP authentication
provides:
  - register-client subcommand with key generation and explicit key options
  - POST /v1/clients/register/agent API integration
  - Client key storage under CLIENT_<client-id>_* namespace
affects: [phase-35-plan-02, phase-36-client-demo]

# Tech tracking
tech-stack:
  added: []
  patterns: [OAuth client registration with key management, Bearer auth for agent endpoints]

key-files:
  created: []
  modified: [demo/agent/agent-demo.py]

key-decisions:
  - "Store client keys using server-generated client ID as namespace (per CONTEXT.md)"
  - "Require --generate or explicit --private-key/--public-key for new registration"

patterns-established:
  - "CLIENT_<client-id>_* namespace for multi-client key storage"
  - "Fail-fast HTTP wrapper with print_output for JSON response"

# Metrics
duration: 2min
completed: 2026-02-22
---

# Phase 35 Plan 01: Register-Client Subcommand

**OAuth client registration with Ed25519 key generation and explicit key provision options**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-22T14:30:00Z
- **Completed:** 2026-02-22T14:32:00Z
- **Tasks:** 1/1
- **Files modified:** 1

## Accomplishments
- Added `register-client` subcommand to agent-demo.py CLI
- Implemented three key provision options: --generate, explicit keys, or neither (not allowed for new registration)
- Integrated with POST /v1/clients/register/agent API using Bearer auth
- Keys saved to .env under CLIENT_<client-id>_* namespace per CONTEXT.md

## Task Commits

1. **Task 1: Add register-client subcommand with key provision options** - `52eec59` (feat)

**Plan metadata:** `5595be0` (docs: create phase plan)

## Files Created/Modified
- `demo/agent/agent-demo.py` - Added cmd_register_client function, subparser, and command handler

## Decisions Made
- Store client keys using server-generated client ID as namespace (not client name) - per CONTEXT.md
- Require either --generate OR both --private-key and --public-key - no key flags not allowed for new registration

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## Next Phase Readiness
- Plan 35-02 (authorize subcommand) can proceed
- No blockers

---
*Phase: 35-agent-demo-oauth*
*Completed: 2026-02-22*
