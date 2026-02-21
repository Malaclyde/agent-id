# Phase 23: Backend Refactoring - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Refactor shadow claim to use unified claim challenges (not payment challenges) with `isShadow` flag. This is pure backend refactoring - no new capabilities, just restructuring existing functionality to match the specification.

Key changes:
- Shadow claims currently use 'payment' prefix challenges (separate system)
- They should use 'claim' prefix challenges with `isShadow: true` flag
- New state flow: `initiated` → `awaiting-payment` → `completed` | `expired`

</domain>

<decisions>
## Implementation Decisions

### Challenge State Transitions
- **initiated** — Set when shadow overseer first calls POST `/v1/agents/malice/:agentId`
  - Challenge created with `isShadow: true`, `shadow_overseer_id`, `agent_id`, `expires_at`
  - Status returned to overseer so they can instruct agent
- **awaiting-payment** — Set when agent confirms via POST `/v1/agents/claim/complete/:challengeId`
  - Backend verifies agent identity (DPoP or session)
  - Verifies agent matches challenge's `agent_id`
  - Checks agent not already claimed by real overseer
  - Updates challenge with `awaiting-payment` status and Paddle checkout data
- **completed** — Set when Paddle webhook (`transaction.completed`) is received
  - Webhook handler extracts `challenge_id` from `custom_data`
  - Updates challenge status to `completed`
  - Creates/reuses shadow overseer and oversight relationship
- **expired** — Implicit when challenge TTL (60 minutes) expires
  - No explicit state change; challenge simply no longer exists in KV

### Legacy System Handling
- **Remove entirely** — No gradual deprecation
- Delete all 'payment' prefix challenge code
- Remove `/malice/status/:paymentChallengeId` endpoint (replaced by unified `/claim/status/:challengeId`)
- Remove `/malice/:agentId/payment/:paymentChallengeId` payment page endpoint
- Remove `/malice/:agentId/complete` POST endpoint
- This is a breaking change; existing in-flight shadow claims will fail
  - Acceptable risk per deployment plan (low-traffic deploy window)

### Status Endpoint Compatibility
- **Only support new system** — No dual-mode operation
- GET `/v1/agents/malice/status/:challengeId` will query 'claim' challenges (not 'payment')
- Returns status: `initiated`, `awaiting-payment`, `completed`, or `expired`
- Frontend must be updated to use new challenge IDs (Phase 25)

### Challenge TTL
- **Shadow claims:** 60 minutes (3600 seconds)
  - Sufficient time for: overseer initiates → agent confirms → overseer pays
  - Stored in KV with `expirationTtl: 3600`
- **Regular claims:** Keep existing 300 seconds (5 minutes)
  - No changes to regular claim flow
- **Cleanup:** Claude's discretion on implementation details

### Error Responses
- **Claude's discretion** on specific error messages and HTTP status codes
- Standard HTTP semantics expected:
  - 404: Challenge not found (expired or invalid ID)
  - 400: Bad request (missing fields, invalid format)
  - 403: Forbidden (agent doesn't match challenge, already claimed)
  - 401: Unauthorized (invalid DPoP proof or session)
  - 409: Conflict (agent already has real overseer)
  - 500: Internal server error

</decisions>

<specifics>
## Specific Ideas

None — straightforward refactoring to match existing specification. Implementation should follow established patterns in the codebase (consistent with how regular claim challenges work).

</specifics>

<deferred>
## Deferred Ideas

- Agent confirmation flow details — Phase 24
- Frontend updates for new status polling — Phase 25  
- Webhook handler implementation — Phase 26
- Testing and verification — Phase 27

All deferred to later phases as per critical path.

</deferred>

---

*Phase: 23-backend-refactoring*
*Context gathered: 2026-02-20*
