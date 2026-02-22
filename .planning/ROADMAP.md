# Project Roadmap

**Project:** Agent-ID Identity Platform
**Current Milestone:** v2.1 Comprehensive Testing
**Goal:** Audit, expand, and formalize test suites across the full stack to cover all flows and edge cases, including real Paddle E2E tests, and identify/discuss bugs before fixing.

## Overview
This roadmap details the path to delivering a comprehensive testing suite for the Agent-ID platform. The milestone consists of auditing existing documentation and code, building test infrastructure for backend and frontend environments, writing end-to-end tests connected to the real Paddle sandbox, and finally uncovering and reporting bugs before any fixes are applied.

---

## Phases

### Phase 28: Audit & Test Strategy
**Goal:** System documentation accurately reflects current application flows and outlines a complete testing strategy.
**Dependencies:** None
**Requirements:** AUDIT-01, AUDIT-02, AUDIT-03
**Plans:** 3 plans
- [ ] 28-01-PLAN.md — Audit and Rewrite Cryptographic Auth Flows
- [ ] 28-02-PLAN.md — Audit and Rewrite Subscription and Client Flows
- [ ] 28-03-PLAN.md — Identify Coverage Gaps and Document Test Strategy & Scenarios

**Success Criteria:**
1. Developer can read documentation to understand all existing application flows and edge cases.
2. Developer can view a report of coverage gaps between current tests and documented flows.
3. Developer can reference a master list of newly planned test scenarios for backend, frontend, and E2E.

---

### Phase 29: Backend Test Implementation
**Goal:** Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments.
**Dependencies:** Phase 28
**Requirements:** BETEST-01, BETEST-02, BETEST-03

**Success Criteria:**
1. Developer can run tests that dynamically generate Ed25519 keypairs and DPoP signatures.
2. Developer can execute tests against an ephemeral, mocked D1/KV database without network overhead.
3. Developer can verify all backend API endpoints pass integration tests via `app.fetch()`.

---

### Phase 30: Frontend Test Implementation
**Goal:** Frontend React components and edge cases are verifiable without relying on a live backend.
**Dependencies:** Phase 28
**Requirements:** FETEST-01, FETEST-02, FETEST-03

**Success Criteria:**
1. Developer can run Vitest to verify React component UI states.
2. Frontend tests successfully intercept and mock API requests using MSW.
3. Developer can verify complex frontend edge cases like polling timeouts and expired tokens via automated tests.

---

### Phase 31: End-to-End Test Implementation
**Goal:** Full application workflows, including real third-party integrations, are automatically verifiable.
**Dependencies:** Phase 29, Phase 30
**Requirements:** E2ETEST-01, E2ETEST-02, E2ETEST-03

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

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 28 - Audit & Test Strategy | System documentation accurately reflects current application flows and outlines a complete testing strategy. | AUDIT-01, AUDIT-02, AUDIT-03 | Pending |
| 29 - Backend Test Implementation | Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments. | BETEST-01, BETEST-02, BETEST-03 | Pending |
| 30 - Frontend Test Implementation | Frontend React components and edge cases are verifiable without relying on a live backend. | FETEST-01, FETEST-02, FETEST-03 | Pending |
| 31 - End-to-End Test Implementation | Full application workflows, including real third-party integrations, are automatically verifiable. | E2ETEST-01, E2ETEST-02, E2ETEST-03 | Pending |
| 32 - Bug Discovery & Reporting | All application bugs are identified and documented for future resolution. | BUGS-01, BUGS-02 | Pending |