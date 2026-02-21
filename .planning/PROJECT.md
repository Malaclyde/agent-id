# Agent-ID Identity Platform

## What This Is

An identity web app for LLM agents with OAuth2 provider capabilities, Ed25519 cryptographic authentication, and overseer management. It enables agents to authenticate via challenge-response signing and supports third-party OAuth flows with PKCE and DPoP.

## Core Value

Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.

---

## Current Milestone: v2.1 Comprehensive Testing

**Goal:** Audit, expand, and formalize test suites across the full stack to cover all flows and edge cases, including real Paddle E2E tests, and identify/discuss bugs before fixing.

**Target features:**
- Codebase and documentation scan for full flow understanding
- Audit of existing test suites and documentation
- Research and addition of new test scenarios (unit, integration, E2E)
- Implementation of comprehensive testing suites (backend, frontend, E2E with real Paddle test connection)
- Bug identification via test execution and discussion of solutions prior to fixing

**Previous Milestone:** v2.0 Shadow Claim Implementation (Complete)

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
- ✓ Unify shadow claim with standard claim challenge system
- ✓ Agent confirmation step before payment processing
- ✓ Proper state management (initiated → awaiting-payment → completed)
- ✓ Paddle `transaction.completed` webhook handling for one-time payments
- ✓ Comprehensive test coverage for shadow claim flows

### Active (This Milestone)

#### Research & Audit
- [ ] Scan codebase and documentation for flow understanding
- [ ] Audit existing test suites and test cases in docs
- [ ] Identify and research missing flows and edge cases

#### Documentation Updates
- [ ] Document new test scenarios for unit, integration, and E2E

#### Test Implementation
- [ ] Implement backend unit and integration tests
- [ ] Implement frontend unit and integration tests
- [ ] Implement E2E tests with real Paddle connection using testuser-N data

#### Bug Identification & Resolution
- [ ] Execute tests to find bugs
- [ ] Report and discuss bugs with user before attempting fixes

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
*Last updated: 2026-02-21 after milestone initialization*
