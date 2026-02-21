# Domain Pitfalls: Adding Comprehensive Testing Suite (incl. Real Paddle E2E)

**Domain:** Quality Assurance / Billing Integration
**Researched:** Sat Feb 21 2026

## Critical Pitfalls

Mistakes that cause unreliable test suites, leading developers to ignore tests or merge broken code.

### Pitfall 1: Asynchronous Webhook Flakiness in Paddle E2E
**What goes wrong:** Real E2E tests initiate a checkout in the Paddle Sandbox and immediately assert that the local database reflects the new subscription or payment state. The test fails randomly because Paddle's webhooks take variable amounts of time to arrive.
**Why it happens:** Payment processing and webhook dispatch are inherently asynchronous and out of the test runner's direct control.
**Consequences:** High rate of flaky tests. Developers lose trust in the E2E suite ("it just failed because it's the billing test").
**Warning signs:** Tests that "work locally but fail in CI", or tests that pass when you add `sleep(5000)` but fail without it.
**Prevention:** Do not use static sleep times. Implement a polling mechanism with a timeout (e.g., check DB every 1s for up to 30s) to wait for the expected state. Alternatively, for CI speed, route webhooks through a fast interceptor specifically built for the test environment.
**Phase to address:** E2E Infrastructure Setup.

### Pitfall 2: Sandbox Rate Limits & Test Data Pollution
**What goes wrong:** The CI pipeline runs E2E tests in parallel on every pull request. The tests hit the Paddle Sandbox API simultaneously, triggering HTTP 429 (Rate Limit Exceeded) errors, or test cards start getting declined due to velocity checks by the payment processor's fraud engine.
**Why it happens:** Sandbox environments are not built for production-level scale. Test databases and Paddle sandbox accounts get cluttered with thousands of orphaned test subscriptions.
**Consequences:** Spurious test failures blocking deployments; manual cleanup of the Paddle Sandbox required.
**Warning signs:** Random HTTP 429s from Paddle APIs; unexpected "Card Declined" errors in E2E tests using documented test cards.
**Prevention:** 
1. **Tiered Execution:** Use mocked responses (integration tests) for standard PR checks. Reserve real Paddle E2E tests for `main` branch merges, release candidates, or nightly runs.
2. **Backoff:** Implement exponential backoff for Paddle API clients in the test environment.
3. **Teardown:** Ensure E2E tests explicitly cancel subscriptions and delete test entities in an `afterAll` hook, even if the test fails.
**Phase to address:** CI/CD & Test Automation Setup.

### Pitfall 3: "Mocking the Universe" When Retrofitting
**What goes wrong:** When adding unit tests to an existing, tightly-coupled codebase, developers write hundreds of lines of complex mocks just to test a single function.
**Why it happens:** Legacy code without Dependency Injection (DI) cannot be easily isolated.
**Consequences:** Brittle tests that break on any internal implementation change, while failing to catch actual bugs because the mocks don't accurately represent reality (e.g., mocking a database call to return a success when the real DB constraint would fail).
**Warning signs:** Test files where the mock setup is 5x larger than the test assertions. Tests passing while the application is demonstrably broken.
**Prevention:** When retrofitting, heavily favor **Integration Tests** over pure Unit Tests. Spin up a real test database (e.g., using Testcontainers) and test the boundaries (HTTP request to DB state). Refactor tightly coupled code toward DI iteratively, adding true unit tests only after refactoring.
**Phase to address:** Unit/Integration Test Writing.

## Moderate Pitfalls

Mistakes that cause technical debt, wasted effort, or missed edge cases.

### Pitfall 1: Chasing Blanket Coverage Metrics
**What goes wrong:** The team mandates "80% overall test coverage," leading developers to write low-value tests for getters, setters, and trivial helpers, while complex integration points (like a payment failure handling) remain untested.
**Warning signs:** High line coverage metrics, but production bugs still frequently occur in critical business logic.
**Prevention:** Discard blanket percentage goals initially. Map out **Critical User Journeys (CUJs)** (e.g., Upgrade Subscription, Downgrade, Payment Failed, Cancellation). Require 100% coverage *only* on the code paths facilitating those CUJs. Add coverage gating selectively.
**Phase to address:** Test Strategy & Audit Phase.

### Pitfall 2: Ignoring Idempotency in Webhook Handlers
**What goes wrong:** Tests only verify the "happy path" where a Paddle webhook arrives exactly once. In production, webhooks are frequently delivered multiple times due to network retries or vendor-side issues.
**Warning signs:** Duplicate subscriptions, double-provisioned credits, or database constraint errors showing up in production error logs.
**Prevention:** In the Integration Test suite, write explicit tests that fire the exact same Paddle webhook payload twice in rapid succession. Assert that the second delivery results in a graceful `200 OK` without duplicating state or throwing a 500 error.
**Phase to address:** Integration Test Writing (Edge Cases).

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| **1. Audit & Strategy** | Treating all missing tests as equal priority | Map Critical User Journeys (CUJs) first; audit specifically for missing paths in billing, auth, and data integrity. |
| **2. Test Infrastructure** | Shared staging database for integration tests | Use isolated, ephemeral databases per test worker (e.g., Docker Testcontainers) to prevent state cross-talk. |
| **3. Integration Tests** | Overlooking edge cases (declines, retries) | Explicitly document and implement tests for Paddle's non-happy-path webhooks (e.g., `subscription_payment_failed`, `subscription_canceled`). |
| **4. Real E2E (Paddle)** | Flaky assertions due to async webhooks | Implement intelligent polling for state changes rather than fixed timeouts; run real E2E sparingly to avoid sandbox rate limits. |

## Sources

- Industry best practices for testing legacy codebases (Working Effectively with Legacy Code paradigms).
- Payment Gateway Integrator knowledge (Stripe/Paddle async webhook best practices).
- Standard CI/CD parallelization anti-patterns.
