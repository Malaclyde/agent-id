---
phase: 31-end-to-end-test-implementation
verified: 2026-02-23T12:00:00Z
status: gaps_found
score: 2/7 must-haves verified
gaps:
  - truth: "Test infrastructure cleanly sets up and tears down an ephemeral backend environment."
    status: failed
    reason: "Playwright configuration misses 'cwd' resulting in webServers failing to start. Global setup clears an arbitrary directory 'test/e2e/.wrangler-state' instead of running migrations or clearing the actual D1 local DB, leading to SQL errors ('no such table: overseers')."
    artifacts:
      - path: "test/e2e/playwright.config.ts"
        issue: "webServer blocks missing 'cwd' parameter to execute 'npm run dev:backend' in the project root."
      - path: "test/e2e/setup/global.setup.ts"
        issue: "Fails to run D1 migrations to setup schema. Clears wrong state directory instead of passing '--persist-to' for the test run."
    missing:
      - "Set cwd parameter in playwright.config.ts webServer configurations."
      - "Run 'npm run db:migrate:test' inside test/e2e/setup/global.setup.ts."
  - truth: "Webhook simulation can directly inject payloads into the test backend without external network tunneling."
    status: failed
    reason: "E2E tests use 'simulateWebhook' which fetches '/v1/test-utils/simulate-webhook', but this route is never implemented in the backend."
    artifacts:
      - path: "backend/src/routes/test-utils.ts"
        issue: "Imports webhook handlers but has no route definition for '/simulate-webhook'."
    missing:
      - "Implement POST '/simulate-webhook' route inside test-utils.ts to invoke the imported webhook handlers."
  - truth: "E2E tests run deterministically without flaky failures."
    status: failed
    reason: "Blocked by the test infrastructure failures. Tests immediately fail with 'Missing script' or 'no such table' errors."
    artifacts:
      - path: "test/e2e/**/*.spec.ts"
        issue: "Tests cannot proceed past setup steps."
    missing:
      - "Fix infrastructure setup to unblock test execution."
  - truth: "Asynchronous webhook processing is reliably verified."
    status: failed
    reason: "Blocked by missing simulate-webhook API route, so E2E tests cannot trigger or verify webhooks."
    artifacts:
      - path: "backend/src/routes/test-utils.ts"
        issue: "Missing '/simulate-webhook' route."
    missing:
      - "Add '/simulate-webhook' logic to test-utils."
  - truth: "E2E tests successfully interact with Paddle Checkout iframes."
    status: failed
    reason: "The tests exist and are substantive but cannot be verified to run successfully because the environment setup failure blocks test execution."
    artifacts:
      - path: "test/e2e/fixtures/paddle.ts"
        issue: "E2E tests abort before executing checkout code."
    missing:
      - "Unblock tests to verify Paddle interactions work end-to-end."
---

# Phase 31: End-to-End Test Implementation Verification Report

**Phase Goal:** Full application workflows, including real third-party integrations, are automatically verifiable.
**Verified:** 2026-02-23T12:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | E2E tests can run across different browsers and contexts. | ✓ VERIFIED | `playwright.config.ts` projects setup covers chromium, firefox, webkit. |
| 2 | Test infrastructure cleanly sets up and tears down an ephemeral backend environment. | ✗ FAILED | Missing `cwd` in `playwright.config.ts` and `globalSetup` does not execute D1 migrations, causing "no such table" SQL errors on test start. |
| 3 | Webhook simulation can directly inject payloads into the test backend without external network tunneling. | ✗ FAILED | `backend/src/routes/test-utils.ts` imports handlers but lacks a route for `/simulate-webhook`. |
| 4 | E2E tests run deterministically without flaky failures. | ✗ FAILED | Tests crash instantly due to setup and missing API routes. |
| 5 | Tests can orchestrate interactions between an Overseer in one browser context and an Agent in another. | ✓ VERIFIED | `multi-actor.spec.ts` heavily leverages separate `overseerContext` and `agentContext`. |
| 6 | Asynchronous webhook processing is reliably verified. | ✗ FAILED | Blocked by missing `/simulate-webhook` implementation in the backend. |
| 7 | E2E tests successfully interact with Paddle Checkout iframes. | ✗ FAILED | `completePaddleCheckout` frame locator logic exists, but test crashes before reaching this step. |

**Score:** 2/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `test/e2e/playwright.config.ts` | Configures test runner and webServers. | ✗ STUB | `webServer` block missing `cwd` causing startup crash. |
| `test/e2e/setup/global.setup.ts` | Sets up clean DB with tables. | ✗ STUB | Fails to run `db:migrate:test`, tests execute against an empty database. |
| `backend/src/routes/test-utils.ts` | Provides `/simulate-webhook` endpoint. | ✗ STUB | Imports webhook handler services but lacks actual POST route implementation. |
| `test/e2e/fixtures/paddle.ts` | Iframe locators & webhook helper. | ✓ VERIFIED | Implemented properly but blocked by missing API endpoint upstream. |
| `test/e2e/multi-actor.spec.ts` | Orchestrates two roles in one spec. | ✓ VERIFIED | Extensive implementation of dual context scenarios. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `test/e2e/fixtures/paddle.ts` | `backend/src/routes/test-utils.ts` | POST `/v1/test-utils/simulate-webhook` | NOT_WIRED | The endpoint is fetch'ed by the fixture but does not exist in the Hono router. |
| `playwright.config.ts` | `npm run dev:backend` | `webServer` command | NOT_WIRED | Executes `npm run dev:backend` in wrong directory (missing `cwd` root context). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `test/e2e/setup/global.setup.ts` | 13 | Hardcoded dummy cleanup | 🛑 Blocker | E2E DB has no schema migrations, tests crash. |
| `backend/src/routes/test-utils.ts` | 8 | Unused imports | 🛑 Blocker | The webhook helpers are imported but the route using them is missing. |

### Gaps Summary

The end-to-end tests contain substantive verification scenarios, including multi-browser orchestration and iframe logic. However, the supporting infrastructure is broken:
1. **Broken Test Server Startup:** The `playwright.config.ts` does not specify `cwd: join(__dirname, '../../')` for its webServers, preventing the backend from starting correctly via `npm run dev:backend`.
2. **Missing Database Schema:** The `global.setup.ts` script deletes an arbitrary `.wrangler-state` directory but never executes D1 migrations, causing tests to fail with `no such table: overseers` errors.
3. **Missing API Endpoint:** The tests simulate webhooks by hitting `POST /v1/test-utils/simulate-webhook`, but the `test-utils.ts` Hono router fails to actually implement this route.

These gaps block the tests from executing successfully, rendering the application workflows unverified.

---
_Verified: 2026-02-23T12:00:00Z_
_Verifier: OpenCode (gsd-verifier)_