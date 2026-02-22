# Requirements: Comprehensive Testing Milestone

**Defined:** 2026-02-21
**Core Value:** Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.
**Previous Milestone:** v2.0 Shadow Claim Implementation (COMPLETE)

---

## v2.1 Requirements

### Auditing & Documentation (AUDIT)

- [x] **AUDIT-01**: System documents all existing application flows and edge cases based on codebase and current `docs/v1` documentation.
- [x] **AUDIT-02**: System identifies coverage gaps between current test suites and documented flows in `docs/v1`.
- [x] **AUDIT-03**: System documents new test scenarios (unit, integration, E2E) to cover identified edge cases and missing flows.

### Backend Testing (BETEST)

- [x] **BETEST-01**: Testing suite includes utility for dynamic Ed25519 keypair and DPoP signature generation.
- [x] **BETEST-02**: Testing suite includes in-memory D1/KV ephemeral database mocking via vitest-pool-workers.
- [x] **BETEST-03**: Testing suite includes backend integration tests invoking `app.fetch()` for all API endpoints.

### Frontend Testing (FETEST)

- [ ] **FETEST-01**: Testing suite includes component-level tests for React UI states via Vitest and Testing Library.
- [ ] **FETEST-02**: Testing suite includes MSW setup to mock backend API responses.
- [ ] **FETEST-03**: Testing suite covers complex frontend edge cases including polling timeouts and expired tokens.

### End-to-End Testing (E2ETEST)

- [ ] **E2ETEST-01**: Testing suite includes Playwright scaffolding configured for cross-origin iframes and multi-browser contexts.
- [ ] **E2ETEST-02**: Testing suite executes real Paddle Checkout sandbox flows using specified test data (testuser-N).
- [ ] **E2ETEST-03**: Testing suite explicitly handles and asserts asynchronous webhook outcomes (using cloudflared/ngrok or polling).

### Bug Resolution (BUGS)

- [ ] **BUGS-01**: Developer executes test suites across full stack to identify application bugs.
- [ ] **BUGS-02**: Developer reports and discusses identified bugs with the user prior to implementing any code fixes.

---

## v2.2 Requirements (Deferred)

- **TEST-V2-01**: Performance/load testing with tools like K6.
- **TEST-V2-02**: Fully automated testing in CI/CD pipeline blocking PR merges (out of scope for local testing suite audit).

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fixing bugs immediately upon discovery | Constraint: Bugs must be discussed before fixes are applied. |
| Production Database Testing | Constraint: All tests must run on ephemeral test instances or Paddle sandbox. |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUDIT-01 | Phase 28 | Complete |
| AUDIT-02 | Phase 28 | Complete |
| AUDIT-03 | Phase 28 | Complete |
| BETEST-01 | Phase 29 | Complete |
| BETEST-02 | Phase 29 | Complete |
| BETEST-03 | Phase 29 | Complete |
| FETEST-01 | Phase 30 | Complete |
| FETEST-02 | Phase 30 | Complete |
| FETEST-03 | Phase 30 | Complete |
| E2ETEST-01 | Phase 31 | Pending |
| E2ETEST-02 | Phase 31 | Pending |
| E2ETEST-03 | Phase 31 | Pending |
| BUGS-01 | Phase 32 | Pending |
| BUGS-02 | Phase 32 | Pending |

**Coverage:**
- v2.1 requirements: 14 total
- Mapped to phases: 14 (100%)
- Unmapped: 0

---
*Requirements defined: 2026-02-21*