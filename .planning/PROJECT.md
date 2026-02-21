# Agent-ID Identity Platform

## What This Is

An identity web app for LLM agents with OAuth2 provider capabilities, Ed25519 cryptographic authentication, and overseer management. It enables agents to authenticate via challenge-response signing and supports third-party OAuth flows with PKCE and DPoP.

## Core Value

Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.

---

## Current Milestone: v2.0 Shadow Claim Implementation

**Goal:** Implement shadow claim feature allowing agents to be claimed without a real overseer account, using Paddle one-time payments.

**Target Features:**
- Unify shadow claim with standard claim challenge system
- Agent confirmation step before payment processing
- Proper state management (initiated → awaiting-payment → completed)
- Paddle `transaction.completed` webhook handling for one-time payments
- Comprehensive test coverage for shadow claim flows

**Previous Milestone:** v1.0 Documentation & Testing (22 phases, COMPLETE)

---

## Requirements

### Validated (Existing Capabilities)

- ✓ OAuth2 Authorization Code Flow with PKCE and DPoP
- ✓ Agent authentication via Ed25519 challenge-response
- ✓ Agent claim procedure with cryptographic verification
- ✓ Client registration and OAuth token management
- ✓ Basic subscription tier structure (FREE, BASIC, PRO, etc.)
- ✓ Overseer-agent oversight relationships
- ✓ Paddle payment integration with webhook handling
- ✓ Shadow overseer cryptographic ID generation
- ✓ Comprehensive documentation and test suite

### Active (This Milestone)

#### Phase 23: Backend Refactoring
- [ ] Refactor shadow claim to use claim challenges (not payment challenges)
- [ ] Add `isShadow` flag to claim challenge KV data
- [ ] Update `/v1/malice/:agentId` to create claim challenges
- [ ] Remove legacy shadow claim endpoints

#### Phase 24: Agent Confirmation Flow
- [ ] Update claim completion endpoint to check for `isShadow` flag
- [ ] Implement shadow claim confirmation logic
- [ ] Add agent verification before preparing payment
- [ ] Update KV with `awaiting-payment` status and Paddle data

#### Phase 25: Frontend Updates
- [ ] Update ShadowClaim component for new API flow
- [ ] Add polling for `awaiting-payment` status
- [ ] Display instructions for agent confirmation
- [ ] Update ShadowClaimPayment for Paddle checkout

#### Phase 26: Webhook Integration
- [ ] Implement `transaction.completed` webhook handler
- [ ] Extract agent_id, shadow_overseer_id, challenge_id from custom_data
- [ ] Handle shadow overseer creation/reuse
- [ ] Activate oversight and complete claim

#### Phase 27: Testing & Verification
- [ ] Unit tests for refactored shadow claim logic
- [ ] Integration tests with Paddle sandbox
- [ ] End-to-end tests for complete flow
- [ ] Security tests for agent consent verification

### Out of Scope

- Database migration to Drizzle ORM (deferred to future milestone)
- Repository redesign (public/private split) (deferred)
- Admin features and company registration (deferred)
- OAuth providers beyond current implementation (Google, Apple, GitHub) (deferred)
- OpenAPI/Swagger documentation (deferred)
- Real-time chat or video features (never)
- Mobile native apps (never for v1)
- Subscription caching optimization (deferred)
- TypeScript `any` type cleanup (deferred to dedicated refactoring milestone)

## Context

**Current State:**
- Backend: Cloudflare Workers + Hono + D1 (SQLite) + KV
- Frontend: React SPA for GitHub Pages
- Payment: Paddle Billing integration (working)
- Documentation: Complete and accurate
- Testing: Comprehensive test suite in place
- **Shadow Claim:** Partially implemented but diverges from spec

**Known Issues with Current Shadow Claim:**
- Uses separate payment challenge system (not unified with standard claims)
- No agent confirmation step (security risk)
- No `awaiting-payment` state management
- Webhook handling needs updating for `transaction.completed` event

**Technical Debt:**
- Large route files (agents.ts: 876 lines)
- 67+ TypeScript `any` types
- Complex SQL joins without query builder

## Constraints

- **Compatibility:** Cannot break existing OAuth/agent flows
- **Security:** Agents must explicitly confirm shadow claims
- **Testing:** Use Paddle sandbox for testing, minimize API calls
- **Timeline:** Complete within 5 phases

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Unify with claim challenges | Consistent architecture, matches spec | — Pending |
| Require agent confirmation | Security - agents control who oversees them | — Pending |
| Use transaction.completed webhook | Correct Paddle event for one-time payments | — Pending |
| Keep /agents/ prefix in API | Consistent with existing endpoints | — Pending |
| Deprecate payment challenge system | Single system reduces complexity | — Pending |

---
*Last updated: 2026-02-20 after milestone initialization*
