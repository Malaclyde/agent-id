# Project Roadmap

**Project:** Agent-ID Identity Platform
**Current Milestone:** Planning Next Milestone

## Overview

This roadmap tracks the evolution of the Agent-ID identity platform.

## Milestones

- ✅ **v2.2 Demo Scripts** — Phases 33-37 (shipped 2026-02-27)
- 📋 **v2.3 Platform Evolution** — Phases 38+ (planned)

## Phases

<details>
<summary>✅ v2.2 Demo Scripts (Phases 33-37) — SHIPPED 2026-02-27</summary>

- [x] Phase 33: Agent Demo - Core (5/5 plans) — completed 2026-02-22
- [x] Phase 34: Agent Demo - Extended Operations (3/3 plans) — completed 2026-02-22
- [x] Phase 35: Agent Demo - OAuth Client (2/2 plans) — completed 2026-02-22
- [x] Phase 36: Client Demo - Core (4/4 plans) — completed 2026-02-22
- [x] Phase 37: Client Demo - OAuth Operations (2/2 plans) — completed 2026-02-27

</details>

### 📋 v2.3 Platform Evolution (Planned)
### Phase 29: Backend Test Implementation
**Goal:** Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments.
**Dependencies:** Phase 28
**Requirements:** BETEST-01, BETEST-02, BETEST-03
**Plans:** 12 plans
- [x] 29-01-PLAN.md — Test Infrastructure Setup & DB/KV Helpers
- [x] 29-02-PLAN.md — Cryptographic & Data Builder Helpers
- [x] 29-03-PLAN.md — Core API & Webhook Integration Tests
- [x] 29-04-PLAN.md — Overseers & Agents Integration Tests
- [x] 29-05-PLAN.md — Clients & Subscriptions Integration Tests
- [x] 29-06-PLAN.md — OAuth API Integration Tests
- [x] 29-07-PLAN.md — Fix Vitest Pool Configuration (Gap Closure)
- [x] 29-08-PLAN.md — Fix Failing Unit Tests (Gap Closure)
- [x] 29-09-PLAN.md — Fix Overseer API Tests (Gap Closure)
- [x] 29-10-PLAN.md — Fix Agent API Tests (Gap Closure)
- [x] 29-11-PLAN.md — Suite Stability & Ghost Test Removal (Gap Closure)
- [x] 29-12-PLAN.md — Paddle API Mocks & Logic Regressions (Gap Closure)

- [ ] Phase 38: Security Audit & Hardening
- [ ] Phase 39: Drizzle ORM Migration
**Success Criteria:**
1. Developer can run tests that dynamically generate Ed25519 keypairs and DPoP signatures.
2. Developer can execute tests against an ephemeral, mocked D1/KV database without network overhead.
3. Developer can verify all backend API endpoints pass integration tests via `app.fetch()`.

---

### Phase 30: Frontend Test Implementation
**Goal:** Frontend React components and edge cases are verifiable without relying on a live backend.
**Dependencies:** Phase 28
**Requirements:** FETEST-01, FETEST-02, FETEST-03
**Plans:** 13 plans
- [x] 30-01-PLAN.md — MSW Installation & Core Setup
- [x] 30-02-PLAN.md — Test Factories & Builders
- [x] 30-03-PLAN.md — MSW Handlers by Endpoint
- [x] 30-04-PLAN.md — Test Utilities (Auth, Render, Paddle Mocks)
- [x] 30-05-PLAN.md — Home & Header Tests (Update Existing)
- [x] 30-06-PLAN.md — AuthContext Tests (Update to MSW)
- [x] 30-07-PLAN.md — OverseerAuth & Subscription Result Pages
- [x] 30-08-PLAN.md — RegisteredClients Tests
- [x] 30-09-PLAN.md — OverseerDashboard Tests
- [x] 30-10-PLAN.md — AgentDashboard Tests
- [x] 30-11-PLAN.md — SubscriptionManagement Tests (Paddle Integration)
- [x] 30-12-PLAN.md — ShadowClaim Tests (Polling & Edge Cases)
- [x] 30-13-PLAN.md — ShadowClaimPayment Tests

**Success Criteria:**
1. Developer can run Vitest to verify React component UI states.
2. Frontend tests successfully intercept and mock API requests using MSW.
3. Developer can verify complex frontend edge cases like polling timeouts and expired tokens via automated tests.

---

### Phase 31: End-to-End Test Implementation
**Goal:** Full application workflows, including real third-party integrations, are automatically verifiable.
**Dependencies:** Phase 29, Phase 30
**Requirements:** E2ETEST-01, E2ETEST-02, E2ETEST-03
**Plans:** 3 plans
- [ ] 31-01-PLAN.md — Playwright Infrastructure & Webhook Test Setup
- [ ] 31-02-PLAN.md — Multi-Actor Flow & Registration Refactor
- [ ] 31-03-PLAN.md — Paddle Checkout Sandbox & Polling

**Success Criteria:**
1. Developer can run Playwright tests handling cross-origin iframes and multi-browser contexts.
2. Automated tests successfully complete a real Paddle Checkout sandbox flow using testuser-N data.
3. Automated tests successfully verify asynchronous webhook outcomes using polling or a tunnel.

---

### Phase 32: Bug Discovery & Reporting
**Goal:** All application bugs are identified and documented for future resolution.
**Dependencies:** Phase 29, Phase 30, Phase 31
**Requirements:** BUGS-01, BUGS-02

**Success Criteria:**
1. Developer has executed all test suites (Backend, Frontend, E2E) across the full stack.
2. User can review a comprehensive report of identified bugs.
3. Developer and user have discussed the bug report prior to implementing fixes.

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 33. Agent Demo Core | v2.2 | 5/5 | Complete | 2026-02-22 |
| 34. Agent Demo Extended | v2.2 | 3/3 | Complete | 2026-02-22 |
| 35. Agent Demo OAuth | v2.2 | 2/2 | Complete | 2026-02-22 |
| 36. Client Demo Core | v2.2 | 4/4 | Complete | 2026-02-22 |
| 37. Client Demo OAuth | v2.2 | 2/2 | Complete | 2026-02-27 |


| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 28 - Audit & Test Strategy | System documentation accurately reflects current application flows and outlines a complete testing strategy. | AUDIT-01, AUDIT-02, AUDIT-03 | Complete |
| 29 - Backend Test Implementation | Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments. | BETEST-01, BETEST-02, BETEST-03 | Complete |
| 30 - Frontend Test Implementation | Frontend React components and edge cases are verifiable without relying on a live backend. | FETEST-01, FETEST-02, FETEST-03 | Complete |
| 31 - End-to-End Test Implementation | Full application workflows, including real third-party integrations, are automatically verifiable. | E2ETEST-01, E2ETEST-02, E2ETEST-03 | Pending |
| 32 - Bug Discovery & Reporting | All application bugs are identified and documented for future resolution. | BUGS-01, BUGS-02 | Pending |
