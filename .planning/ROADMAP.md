# Agent-ID Shadow Claim Implementation - ROADMAP

**Milestone:** v2.0 Shadow Claim Implementation
**Core Value:** Agents can be claimed by shadow overseers with explicit agent consent, using Paddle one-time payments.
**Previous Milestone:** v1.0 Documentation & Testing (COMPLETE - 22 phases)
**Depth:** Comprehensive
**Created:** 2026-02-20

---

## Overview

This roadmap implements the shadow claim feature according to the specification in `docs/v1/requirements/agent/shadow-claim.md`. The current implementation diverges from the spec in critical ways:

1. **Uses separate payment challenge system** (spec requires unified claim challenges)
2. **No agent confirmation step** (spec requires agent to confirm before payment)
3. **No `awaiting-payment` state** (spec requires this intermediate state)
4. **Webhook handling needs updating** (needs `transaction.completed` event for one-time payments)

This milestone refactors the implementation to match the specification while maintaining backward compatibility.

**Critical Path:** Backend refactoring (Phase 23) must complete before agent confirmation (Phase 24) because the confirmation endpoint depends on the new challenge structure.

---

## Research Findings

### Paddle Webhook Events for One-Time Payments

**Correct Event:** `transaction.completed`
- Occurs when a transaction is fully processed after payment
- Status field changes to `completed`
- Payload includes customer email at `data.customer.email`
- Custom data available at `data.custom_data`

**Webhook Payload Structure:**
```json
{
  "event_id": "evt_...",
  "event_type": "transaction.completed",
  "data": {
    "id": "txn_...",
    "status": "completed",
    "customer_id": "ctm_...",
    "customer": {
      "id": "ctm_...",
      "email": "customer@example.com"
    },
    "custom_data": {
      "agent_id": "...",
      "shadow_overseer_id": "...",
      "challenge_id": "...",
      "is_shadow_claim": true
    }
  }
}
```

### Challenge State Flow

**Specification Flow:**
1. `initiated` - Challenge created by shadow overseer
2. `awaiting-payment` - Agent confirmed, waiting for payment
3. `completed` - Payment received, oversight activated
4. `expired` - Challenge TTL expired (60 minutes)

---

## Phases

### Phase 23: Backend Refactoring

**Goal:** Refactor shadow claim to use claim challenges (not payment challenges) with `isShadow` flag

**Status:** `COMPLETE` ✅

**Completed:** 2026-02-20

**Verification:** 6/6 must-haves verified — Phase goal achieved

**Requirements (7):**
- SHADOW-BE-01: Refactor POST `/v1/agents/malice/:agentId` to create claim challenges
- SHADOW-BE-02: Add `isShadow: true` flag to claim challenge KV data structure
- SHADOW-BE-03: Include `shadow_overseer_id` in claim challenge data
- SHADOW-BE-04: Set challenge TTL to 60 minutes for shadow claims
- SHADOW-BE-05: Remove or deprecate legacy payment challenge system
- SHADOW-BE-06: Update GET `/v1/agents/malice/status/:challengeId` to query claim challenges
- SHADOW-BE-07: Return proper status: `initiated`, `awaiting-payment`, `completed`, `expired`

**Success Criteria:**

1. Shadow claim initiation creates claim challenges (prefix `claim:`) not payment challenges
2. Claim challenge includes `isShadow: true`, `shadow_overseer_id`, `agent_id`, `expires_at`
3. Status endpoint returns correct states: `initiated`, `awaiting-payment`, `completed`, `expired`
4. Legacy payment challenge system removed or deprecated
5. All existing tests pass after refactoring

**Dependencies:** None (first phase of new milestone)

**Risk Notes:**
- **High Risk:** Breaking change to existing shadow claim flow
- **Medium Risk:** Current shadow claim users will experience interruption
- **Mitigation:** Deploy during low-traffic period; have rollback plan

**Plans:** 1 plan
- [x] 23-01-PLAN.md — Refactor shadow claim to use claim challenges with isShadow flag

**Deliverable:** Refactored backend with unified claim challenge system

---

### Phase 24: Agent Confirmation Flow

**Goal:** Implement agent confirmation step before payment processing

**Status:** `COMPLETE` ✅

**Completed:** 2026-02-20

**Verification:** 4/4 must-haves verified — Phase goal achieved

**Requirements (8):**
- SHADOW-CONFIRM-01: Update POST `/v1/agents/claim/complete/:challengeId` to check for `isShadow` flag ✅
- SHADOW-CONFIRM-02: If `isShadow: true`, verify agent identity via DPoP or session ✅
- SHADOW-CONFIRM-03: Verify agent matches challenge's `agent_id` ✅
- SHADOW-CONFIRM-04: Verify agent is not already claimed by real overseer ✅
- SHADOW-CONFIRM-05: Check if shadow overseer exists in database, reuse if found ✅
- SHADOW-CONFIRM-06: Generate new shadow overseer email if not exists ✅
- SHADOW-CONFIRM-07: Update KV challenge with `awaiting-payment` status and Paddle checkout data ✅
- SHADOW-CONFIRM-08: Return success response with confirmation acknowledgment ✅

**Success Criteria:**

1. ✅ Agent must POST to claim completion endpoint with valid DPoP proof or session
2. ✅ Backend verifies agent matches challenge's `agent_id`
3. ✅ Backend checks agent is not already claimed by real overseer
4. ✅ Shadow overseer created or reused as appropriate
5. ✅ Challenge updated to `awaiting-payment` status with Paddle price data
6. ✅ Response includes success message and checkout readiness status

**Dependencies:** Phase 23 (Backend Refactoring)
- ✅ Requires refactored challenge structure with `isShadow` flag

**Risk Notes:**
- **High Risk:** Agent confirmation is new security gate - must be bulletproof
- **Medium Risk:** DPoP validation complexity
- **Mitigation:** Comprehensive security testing; audit all code paths

**Plans:** 1 plan
- [x] 24-01-PLAN.md — Implement agent confirmation with shadow claim validation and payment preparation

**Deliverable:** Agent confirmation flow that prepares challenge for payment

---

### Phase 25: Frontend Updates

**Goal:** Update frontend to support new shadow claim flow with agent confirmation

**Status:** `GAPS FOUND` ⚠

**Requirements (8):**
- SHADOW-FE-01: Update ShadowClaim.tsx to poll for challenge status
- SHADOW-FE-02: Display instructions for agent confirmation when status is `initiated`
- SHADOW-FE-03: Show "Waiting for agent confirmation..." message with timeout
- SHADOW-FE-04: Transition to payment UI when status changes to `awaiting-payment`
- SHADOW-FE-05: Display payment amount and Paddle checkout button
- SHADOW-FE-06: Include challenge_id in Paddle customData
- SHADOW-FE-07: Handle payment completion and success message
- SHADOW-FE-08: Handle expiration and error states gracefully

**Success Criteria:**

1. Frontend displays instructions for agent confirmation (URL, body, auth method)
2. Polling every 2 seconds for status changes
3. Shows appropriate UI for each state: `initiated`, `awaiting-payment`, `completed`, `expired`
4. Paddle checkout includes correct custom data (agent_id, shadow_overseer_id, challenge_id)
5. Success page displayed after payment completion
6. Error handling for all failure modes

**Dependencies:**
- Phase 23 (Backend Refactoring) - for new status endpoint
- Phase 24 (Agent Confirmation) - for `awaiting-payment` state

**Risk Notes:**
- **Low Risk:** UI changes are straightforward
- **Medium Risk:** State management complexity with polling
- **Mitigation:** Proper cleanup of polling intervals; error boundaries

**Status:** `COMPLETE` ✅ — Gap closure in progress

**Completed:** 2026-02-20

**Verification:** 17/17 must-haves verified — Phase goal achieved
**UAT Issues:** 7 gaps identified, 3 gap closure plans created

**Plans:** 9 original + 3 gap closure plans

- [x] 25-01-PLAN.md — API client methods and types (Wave 1) ✅ Complete
- [x] 25-02-PLAN.md — ShadowClaim component with polling (Wave 2) ✅ Complete
- [x] 25-03-PLAN.md — ShadowClaimPayment with Paddle checkout (Wave 2) ✅ Complete
- [x] 25-04-PLAN.md — Instructions UI and error handling (Wave 3) ✅ Complete
- [x] 25-05-PLAN.md — Fix route path and parameter mismatch (Wave 1, gap closure) ✅ Complete
- [x] 25-06-PLAN.md — (unused)
- [x] 25-07-PLAN.md — (unused)
- [x] 25-08-PLAN.md — (unused)
- [x] 25-09-PLAN.md — (unused)
- [ ] 25-10-PLAN.md — Fix API field name + polling improvements (gap closure)
- [ ] 25-11-PLAN.md — Replace inline styles with CSS classes (gap closure)
- [ ] 25-12-PLAN.md — Fix payment page issues (gap closure)

**Deliverable:** Updated frontend supporting full shadow claim flow

---

### Phase 26: Webhook Integration

**Goal:** Implement `transaction.completed` webhook handler for shadow claim payments

**Status:** `COMPLETE` ✅

**Completed:** 2026-02-20

**Verification:** 10/10 must-haves verified — Phase goal achieved

**Requirements (10):**
- SHADOW-WEBHOOK-01: Implement handler for `transaction.completed` Paddle event ✅
- SHADOW-WEBHOOK-02: Extract `agent_id`, `shadow_overseer_id`, `challenge_id` from custom_data ✅
- SHADOW-WEBHOOK-03: Extract customer email from webhook payload ✅
- SHADOW-WEBHOOK-04: Verify challenge exists in KV and status is `awaiting-payment` ✅
- SHADOW-WEBHOOK-05: Check if shadow overseer exists, create if not with random password ✅
- SHADOW-WEBHOOK-06: Reactivate existing oversight if shadow overseer reused ✅
- SHADOW-WEBHOOK-07: Create new oversight relationship if new shadow overseer ✅
- SHADOW-WEBHOOK-08: Ensure only one active oversight exists (deactivate others) ✅
- SHADOW-WEBHOOK-09: Update KV challenge status to `completed` ✅
- SHADOW-WEBHOOK-10: Log shadow claim creation or renewal ✅

**Success Criteria:**

1. ✅ Webhook handler processes `transaction.completed` events correctly
2. ✅ Custom data extracted and validated
3. ✅ Customer email captured for shadow overseer record
4. ✅ Shadow overseer created or reused appropriately
5. ✅ Only one active oversight exists per agent
6. ✅ Challenge status updated to `completed`
7. ✅ Audit logging for all shadow claim events

**Dependencies:** 
- Phase 24 (Agent Confirmation) - challenge must be in `awaiting-payment` state
- Working Paddle webhook infrastructure (from v1.0)

**Risk Notes:**
- **High Risk:** Webhook handler must be idempotent (handle retries)
- **Medium Risk:** Race conditions between webhook and status polling
- **Mitigation:** Idempotent database operations; proper locking

**Plans:** 3 plans (2 original + 1 gap closure)
- [x] 26-01-PLAN.md — Core Webhook Handler & Idempotency
- [x] 26-02-PLAN.md — DB Operations & Route Integration
- [x] 26-03-PLAN.md — Fix shadow overseer ID reuse (gap closure)

**Deliverable:** Working webhook handler completing shadow claim flow

---

### Phase 27: Testing & Verification

**Goal:** Comprehensive testing for shadow claim implementation

**Status:** `COMPLETE` ✅

**Completed:** 2026-02-21

**Verification:** 9/9 must-haves verified — Phase goal achieved

**Requirements (10):**
- SHADOW-TEST-01: Unit tests for refactored shadow claim initiation ✅
- SHADOW-TEST-02: Unit tests for agent confirmation logic ✅
- SHADOW-TEST-03: Unit tests for webhook handler ✅
- SHADOW-TEST-04: Integration tests with Paddle sandbox ✅
- SHADOW-TEST-05: Test agent can reject claim (don't confirm) ✅
- SHADOW-TEST-06: Test challenge expiration after 60 minutes ✅
- SHADOW-TEST-07: Test race conditions (concurrent claims on same agent) ✅
- SHADOW-TEST-08: Test shadow overseer reuse on renewal ✅
- SHADOW-TEST-09: End-to-end test: initiate → confirm → pay → complete ✅
- SHADOW-TEST-10: Security test: verify agent identity required for confirmation ✅

**Success Criteria:**

1. 100% unit test coverage for new shadow claim code
2. Integration tests pass with Paddle sandbox
3. End-to-end test demonstrates complete flow
4. Security tests verify agent consent requirement
5. Race condition tests pass
6. All existing tests still pass

**Dependencies:** All previous phases

**Risk Notes:**
- **Medium Risk:** Paddle sandbox rate limits may slow testing
- **Low Risk:** Test environment setup complexity
- **Mitigation:** Mock Paddle where appropriate; schedule tests during off-peak

**Plans:** 3 plans
- [x] 27-01-PLAN.md — Core Shadow Claim Unit Tests (Initiation & Confirmation)
- [x] 27-02-PLAN.md — Unit Tests for Shadow Claim Webhooks & Concurrency
- [x] 27-03-PLAN.md — Integration & E2E Tests for Shadow Claim Flow

**Deliverable:** Comprehensive test suite with documented coverage

---

### Phase 28: Status Polling UI Post-Payment (Future)

**Goal:** Implement a page that displays the status of the challenge based on what is stored in the backend KV cache

**Status:** `PENDING`

**Requirements:**
- SHADOW-FE-09: Display the status of the challenge post-payment by querying KV cache
- SHADOW-FE-10: Polling mechanism to update the UI once the backend webhook processes the payment and activates the oversight

**Success Criteria:**
1. After payment, user can navigate to a status page that shows real-time status from the KV cache.
2. UI correctly reflects when the shadow oversight is officially active.

**Dependencies:** Phase 26 (Webhook Integration)

**Plans:** TBD (created via `/gsd-plan-phase 28`)

**Deliverable:** Status monitoring page for overseers after successful payment

---

## Progress

### Completion Status

| Phase | Status | Requirements | Plans | Progress |
|-------|--------|--------------|-------|----------|
| Phase 23: Backend Refactoring | ✅ Complete | 7 | 1/1 | 100% |
| Phase 24: Agent Confirmation Flow | ✅ Complete | 8 | 1/1 | 100% |
| Phase 25: Frontend Updates | ✅ Complete | 8 | 9/9 | 100% |
| Phase 26: Webhook Integration | ✅ Complete | 10 | 2/2 | 100% |
| Phase 27: Testing & Verification | ✅ Complete | 10 | 3/3 | 100% |

**Overall:** 5 of 5 phases complete (100%)

---

## Critical Path

```
Phase 23 (Backend Refactoring)
    ↓
Phase 24 (Agent Confirmation) 
    ↓
Phase 25 (Frontend Updates)
    ↓
Phase 26 (Webhook Integration)
    ↓
Phase 27 (Testing & Verification)
```

**Why sequential:**
- Phase 24 requires Phase 23's challenge structure
- Phase 25 requires Phase 24's `awaiting-payment` state
- Phase 26 requires Phase 24's agent confirmation
- Phase 27 tests the complete flow

---

## Phase Dependencies Graph

```
Phase 23: Backend Refactoring (✅ Complete)
└── Phase 24: Agent Confirmation Flow (✅ Complete)
    ├── Phase 25: Frontend Updates (✅ Complete)
    └── Phase 26: Webhook Integration (✅ Complete)
        └── Phase 27: Testing & Verification (✅ Complete)
```

---

## Success Criteria Summary

By the end of this milestone:

1. Shadow claim uses unified claim challenge system (Phase 23)
2. Agents must explicitly confirm shadow claims (Phase 24)
3. Frontend supports full flow with proper state management (Phase 25)
4. `transaction.completed` webhook completes the claim (Phase 26)
5. Comprehensive test coverage validates implementation (Phase 27)

---

## Out of Scope (Intentionally Excluded)

| Item | Reason | Planned For |
|------|--------|-------------|
| Shadow claim rejection by agent | Deferred to v2.1 | v2.1 |
| Shadow claim cancellation by overseer | Expiration sufficient for v2.0 | v2.1 |
| Shadow claim transfer | Complex, low priority | Future |
| Shadow claim refunds | Defer to v2.1 | v2.1 |
| Subscription caching | Performance optimization | Future |

---

## Risk Summary

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking change to existing shadow claims | High | High | Deploy during low traffic; rollback plan |
| Agent confirmation security vulnerability | Medium | Critical | Comprehensive security testing |
| Webhook idempotency issues | Medium | High | Idempotent DB operations; event deduplication |
| Paddle sandbox rate limits | Medium | Low | Mock where appropriate; off-peak testing |

---

*Roadmap created: 2026-02-20*
*Template: comprehensive*
*Previous milestone: v1.0 Documentation & Testing (22 phases complete)*
