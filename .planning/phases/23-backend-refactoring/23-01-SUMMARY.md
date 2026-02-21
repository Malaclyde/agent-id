---
phase: 23-backend-refactoring
plan: 01
subsystem: api
tags: [hono, kv, typescript, shadow-claim, claim-challenges]

# Dependency graph
requires:
  - phase: Previous milestones (v1.0 foundation)
    provides: Existing agent registration, claim system, shadow overseer support
provides:
  - Unified shadow claim challenge system using 'claim:' prefix
  - isShadow flag to differentiate shadow claims from regular claims
  - Shadow claim state management (initiated, awaiting-payment, completed, expired)
  - 60-minute TTL for shadow claim challenges
  - Refactored status endpoint returning all four states
  - Legacy payment challenge system removal
affects:
  - Phase 24: Agent Confirmation Flow (depends on new challenge structure)
  - Phase 25: Frontend Updates (needs new status polling)
  - Phase 26: Webhook Integration (handles transaction.completed for shadow claims)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Unified challenge system: use 'claim:' prefix with isShadow flag for shadow claims"
    - "State management: explicit status field in KV challenge data"
    - "Breaking changes: intentional removal of legacy endpoints with deployment planning"

key-files:
  created: []
  modified:
    - backend/src/routes/agents.ts - Refactored shadow claim endpoints

key-decisions:
  - "Single commit for all three tasks: changes are interdependent and must work together"
  - "Keep parameter name as :challengeId (not :paymentChallengeId) for consistency"
  - "Use overseer_id field in challenge data to store shadow_overseer_id (consistent with regular claims)"
  - "Remove legacy endpoints entirely (not deprecate) per locked decision"

patterns-established:
  - "Unified challenge storage: All claims use 'claim:' prefix, differentiated by isShadow flag"
  - "Explicit state management: Challenge status field tracks flow progression"
  - "Consistent response structure: All status endpoint responses include agent_id, shadow_overseer_id, expires_at"

# Metrics
duration: 5min
completed: 2026-02-20
---

# Phase 23 Plan 01: Refactor shadow claim to use claim challenges with isShadow flag

**Refactored shadow claim backend to use unified claim challenge system with isShadow flag, removing legacy payment challenges and implementing proper state management (initiated → awaiting-payment → completed | expired).**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-20T00:00:00Z (approximate)
- **Completed:** 2026-02-20T00:05:00Z (approximate)
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- POST /v1/agents/malice/:agentId now creates claim challenges (not payment challenges)
- Challenge data includes isShadow: true, overseer_id as shadow_overseer_id, status: 'initiated', 60-minute TTL
- Status endpoint queries claim challenges and returns all four states (initiated, awaiting-payment, completed, expired)
- Legacy payment challenge endpoints completely removed (GET /malice/*/payment/* and POST /malice/*/complete)
- TypeScript compiles without errors
- Regular claim flow unaffected (still uses 5-minute TTL, no isShadow flag)

## Task Commits

All three tasks committed atomically in a single commit (changes are interdependent):

1. **Task 1: Refactor POST endpoint to use claim challenges** - `72696e4` (feat)
2. **Task 2: Update status endpoint for claim challenges** - `72696e4` (feat)
3. **Task 3: Remove legacy payment challenge endpoints** - `72696e4` (feat)

**Plan metadata:** `72696e4` (feat: complete shadow claim refactoring)

## Files Created/Modified

- `backend/src/routes/agents.ts` - Refactored shadow claim endpoints:
  - POST /malice/:agentId: Creates claim challenges with isShadow flag, 60-min TTL
  - GET /malice/status/:challengeId: Returns initiated/awaiting-payment/completed/expired states
  - Removed: GET /malice/:agentId/payment/:paymentChallengeId
  - Removed: POST /malice/:agentId/complete

## Decisions Made

- **Single commit approach**: All three tasks committed together because the refactoring is a coherent unit. The status endpoint needs the new challenge structure, and removing legacy endpoints completes the migration.
- **Parameter naming**: Changed from :paymentChallengeId to :challengeId for consistency with the rest of the API.
- **Challenge data structure**: Used overseer_id field (not shadow_overseer_id) to maintain consistency with regular claim challenges. The overseer_id stores the shadow overseer ID for shadow claims.
- **Legacy endpoint removal**: Deleted rather than deprecated per the locked decision. This is an intentional breaking change.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - TypeScript compilation passed on first attempt, all tasks completed as specified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 24: Agent Confirmation Flow**

Phase 24 can now proceed with:
- Challenge structure is ready with isShadow flag
- Status endpoint returns proper states
- 60-minute TTL configured for shadow claims

**Blockers for Phase 24:**
- None

**Concerns:**
- This is a breaking change to the shadow claim API. Existing in-flight shadow claims (using old payment challenge system) will fail after deployment.
- Frontend (Phase 25) will need to be updated to handle the new challenge_id (not payment_challenge_id) in responses.
- Deployment should occur during low-traffic period with rollback plan ready.

---
*Phase: 23-backend-refactoring*
*Completed: 2026-02-20*

## Self-Check: PASSED

- ✓ backend/src/routes/agents.ts exists and was modified
- ✓ SUMMARY.md exists at correct location
- ✓ Commits found: 72696e4 (feat), 526e2fe (docs)
- ✓ TypeScript compilation succeeded
