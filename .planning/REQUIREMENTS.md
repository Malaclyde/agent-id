# Requirements: Shadow Claim Implementation Milestone

**Defined:** 2026-02-20
**Core Value:** Agents can be claimed by shadow overseers with explicit agent consent, using Paddle one-time payments.
**Previous Milestone:** v1.0 Documentation & Testing (COMPLETE - 22 phases)

---

## v2.0 Requirements

### Backend Refactoring (SHADOW-BE)

- [ ] **SHADOW-BE-01**: Refactor POST `/v1/agents/malice/:agentId` to create claim challenges (not payment challenges)
- [ ] **SHADOW-BE-02**: Add `isShadow: true` flag to claim challenge KV data structure
- [ ] **SHADOW-BE-03**: Include `shadow_overseer_id` in claim challenge data
- [ ] **SHADOW-BE-04**: Set challenge TTL to 60 minutes for shadow claims
- [ ] **SHADOW-BE-05**: Remove or deprecate legacy payment challenge system
- [ ] **SHADOW-BE-06**: Update GET `/v1/agents/malice/status/:challengeId` to query claim challenges
- [ ] **SHADOW-BE-07**: Return proper status: `initiated`, `awaiting-payment`, `completed`, `expired`

### Agent Confirmation Flow (SHADOW-CONFIRM)

- [x] **SHADOW-CONFIRM-01**: Update POST `/v1/agents/claim/complete/:challengeId` to check for `isShadow` flag
- [x] **SHADOW-CONFIRM-02**: If `isShadow: true`, verify agent identity via DPoP or session
- [x] **SHADOW-CONFIRM-03**: Verify agent matches challenge's `agent_id`
- [x] **SHADOW-CONFIRM-04**: Verify agent is not already claimed by real overseer
- [x] **SHADOW-CONFIRM-05**: Check if shadow overseer exists in database, reuse if found
- [x] **SHADOW-CONFIRM-06**: Generate new shadow overseer email if not exists
- [x] **SHADOW-CONFIRM-07**: Update KV challenge with `awaiting-payment` status and Paddle checkout data
- [x] **SHADOW-CONFIRM-08**: Return success response with confirmation acknowledgment

### Frontend Updates (SHADOW-FE)

- [ ] **SHADOW-FE-01**: Update ShadowClaim.tsx to poll for challenge status
- [ ] **SHADOW-FE-02**: Display instructions for agent confirmation when status is `initiated`
- [ ] **SHADOW-FE-03**: Show "Waiting for agent confirmation..." message with timeout
- [ ] **SHADOW-FE-04**: Transition to payment UI when status changes to `awaiting-payment`
- [ ] **SHADOW-FE-05**: Display payment amount and Paddle checkout button
- [ ] **SHADOW-FE-06**: Include challenge_id in Paddle customData
- [ ] **SHADOW-FE-07**: Handle payment completion and success message
- [ ] **SHADOW-FE-08**: Handle expiration and error states gracefully

### Webhook Integration (SHADOW-WEBHOOK)

- [x] **SHADOW-WEBHOOK-01**: Implement handler for `transaction.completed` Paddle event
- [x] **SHADOW-WEBHOOK-02**: Extract `agent_id`, `shadow_overseer_id`, `challenge_id` from custom_data
- [x] **SHADOW-WEBHOOK-03**: Extract customer email from webhook payload
- [x] **SHADOW-WEBHOOK-04**: Verify challenge exists in KV and status is `awaiting-payment`
- [x] **SHADOW-WEBHOOK-05**: Check if shadow overseer exists, create if not with random password
- [x] **SHADOW-WEBHOOK-06**: Reactivate existing oversight if shadow overseer reused
- [x] **SHADOW-WEBHOOK-07**: Create new oversight relationship if new shadow overseer
- [x] **SHADOW-WEBHOOK-08**: Ensure only one active oversight exists (deactivate others)
- [x] **SHADOW-WEBHOOK-09**: Update KV challenge status to `completed`
- [x] **SHADOW-WEBHOOK-10**: Log shadow claim creation or renewal

### Testing & Verification (SHADOW-TEST)

- [ ] **SHADOW-TEST-01**: Unit tests for refactored shadow claim initiation
- [ ] **SHADOW-TEST-02**: Unit tests for agent confirmation logic
- [ ] **SHADOW-TEST-03**: Unit tests for webhook handler
- [ ] **SHADOW-TEST-04**: Integration tests with Paddle sandbox
- [ ] **SHADOW-TEST-05**: Test agent can reject claim (don't confirm)
- [ ] **SHADOW-TEST-06**: Test challenge expiration after 60 minutes
- [ ] **SHADOW-TEST-07**: Test race conditions (concurrent claims on same agent)
- [ ] **SHADOW-TEST-08**: Test shadow overseer reuse on renewal
- [ ] **SHADOW-TEST-09**: End-to-end test: initiate → confirm → pay → complete
- [ ] **SHADOW-TEST-10**: Security test: verify agent identity required for confirmation

---

## v2.1 Requirements (Deferred)

### Shadow Claim Enhancements

- **SHADOW-V2-01**: Allow agents to explicitly reject shadow claims
- **SHADOW-V2-02**: Add shadow claim history/audit log
- **SHADOW-V2-03**: Support partial refunds for shadow claims
- **SHADOW-V2-04**: Add shadow claim expiration notifications

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real overseer → shadow overseer migration | Not required for v2.0 |
| Shadow claim cancellation by overseer | Expiration sufficient for v2.0 |
| Shadow claim transfer between agents | Complex, low priority |
| Shadow claim refunds | Defer to v2.1 |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SHADOW-BE-01 | Phase 23 | Complete |
| SHADOW-BE-02 | Phase 23 | Complete |
| SHADOW-BE-03 | Phase 23 | Complete |
| SHADOW-BE-04 | Phase 23 | Complete |
| SHADOW-BE-05 | Phase 23 | Complete |
| SHADOW-BE-06 | Phase 23 | Complete |
| SHADOW-BE-07 | Phase 23 | Complete |
| SHADOW-CONFIRM-01 | Phase 24 | Complete |
| SHADOW-CONFIRM-02 | Phase 24 | Complete |
| SHADOW-CONFIRM-03 | Phase 24 | Complete |
| SHADOW-CONFIRM-04 | Phase 24 | Complete |
| SHADOW-CONFIRM-05 | Phase 24 | Complete |
| SHADOW-CONFIRM-06 | Phase 24 | Complete |
| SHADOW-CONFIRM-07 | Phase 24 | Complete |
| SHADOW-CONFIRM-08 | Phase 24 | Complete |
| SHADOW-FE-01 | Phase 25 | Pending |
| SHADOW-FE-02 | Phase 25 | Pending |
| SHADOW-FE-03 | Phase 25 | Pending |
| SHADOW-FE-04 | Phase 25 | Pending |
| SHADOW-FE-05 | Phase 25 | Pending |
| SHADOW-FE-06 | Phase 25 | Pending |
| SHADOW-FE-07 | Phase 25 | Pending |
| SHADOW-FE-08 | Phase 25 | Pending |
| SHADOW-WEBHOOK-01 | Phase 26 | Complete |
| SHADOW-WEBHOOK-02 | Phase 26 | Complete |
| SHADOW-WEBHOOK-03 | Phase 26 | Complete |
| SHADOW-WEBHOOK-04 | Phase 26 | Complete |
| SHADOW-WEBHOOK-05 | Phase 26 | Complete |
| SHADOW-WEBHOOK-06 | Phase 26 | Complete |
| SHADOW-WEBHOOK-07 | Phase 26 | Complete |
| SHADOW-WEBHOOK-08 | Phase 26 | Complete |
| SHADOW-WEBHOOK-09 | Phase 26 | Complete |
| SHADOW-WEBHOOK-10 | Phase 26 | Complete |
| SHADOW-TEST-01 | Phase 27 | Complete |
| SHADOW-TEST-02 | Phase 27 | Complete |
| SHADOW-TEST-03 | Phase 27 | Complete |
| SHADOW-TEST-04 | Phase 27 | Complete |
| SHADOW-TEST-05 | Phase 27 | Complete |
| SHADOW-TEST-06 | Phase 27 | Complete |
| SHADOW-TEST-07 | Phase 27 | Complete |
| SHADOW-TEST-08 | Phase 27 | Complete |
| SHADOW-TEST-09 | Phase 27 | Complete |
| SHADOW-TEST-10 | Phase 27 | Complete |

**Coverage:**
- v2.0 requirements: 43 total
- Mapped to phases: 43 (100%)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-20*
