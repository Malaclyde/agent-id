---
phase: 31-end-to-end-test-implementation
verified: 2026-02-23T22:45:00Z
status: gaps_found
score: 1/3 must-haves verified
must_haves:
  truths:
    - "Developer can run Playwright tests handling cross-origin iframes and multi-browser contexts"
    - "Automated tests successfully complete a real Paddle Checkout sandbox flow using testuser-N data"
    - "Automated tests successfully verify asynchronous webhook outcomes using polling or a tunnel"
  artifacts:
    - path: "test/e2e/playwright.config.ts"
      provides: "Playwright infrastructure: multi-browser, webServer, globalSetup"
    - path: "test/e2e/setup/global.setup.ts"
      provides: "Pre-test DB wipe and D1 migration"
    - path: "backend/src/routes/test-utils.ts"
      provides: "Webhook simulation endpoint and test helpers"
    - path: "test/e2e/fixtures/paddle.ts"
      provides: "completePaddleCheckout and simulateWebhook helpers"
    - path: "test/e2e/fixtures/contexts.ts"
      provides: "Multi-actor browser context fixtures (overseerPage, agentPage)"
    - path: "test/e2e/multi-actor.spec.ts"
      provides: "Cross-role OAuth authorization E2E test"
    - path: "test/e2e/registration-flow.spec.ts"
      provides: "Overseer registration/login/session E2E tests"
    - path: "test/e2e/subscription-flow.spec.ts"
      provides: "Paddle subscription checkout and upgrade verification"
    - path: "test/e2e/shadow-claim.spec.ts"
      provides: "Shadow claim one-time payment E2E test"
  key_links:
    - from: "playwright.config.ts"
      to: "global.setup.ts"
      via: "globalSetup path reference"
    - from: "playwright.config.ts webServer"
      to: "backend + frontend dev servers"
      via: "cwd + command + port"
    - from: "global.setup.ts"
      to: "D1 database"
      via: "npm run db:migrate:test"
    - from: "subscription-flow.spec.ts"
      to: "test-utils.ts /simulate-webhook"
      via: "paddle.ts simulateWebhook()"
    - from: "shadow-claim.spec.ts"
      to: "test-utils.ts /create-agent"
      via: "request.post()"
    - from: "shadow-claim.spec.ts"
      to: "test-utils.ts /simulate-webhook"
      via: "paddle.ts simulateWebhook()"
gaps:
  - truth: "Automated tests successfully complete a real Paddle Checkout sandbox flow using testuser-N data"
    status: failed
    reason: "subscription-flow.spec.ts sends event_type 'subscription.activated' but test-utils.ts simulate-webhook switch has no case for it — returns 400. Shadow-claim.spec.ts calls POST /v1/test-utils/create-agent which does not exist in test-utils.ts."
    artifacts:
      - path: "backend/src/routes/test-utils.ts"
        issue: "Missing 'subscription.activated' case in simulate-webhook switch (line 94-121). Real webhooks.ts handles it at line 157 by calling handlePaymentSuccess, but test-utils.ts omits it."
      - path: "backend/src/routes/test-utils.ts"
        issue: "Missing POST /create-agent endpoint. shadow-claim.spec.ts line 33 calls it but no route exists."
    missing:
      - "Add case 'subscription.activated': await handlePaymentSuccess(data, c.env.DB, c.env); break; to simulate-webhook switch"
      - "Add POST /create-agent route to test-utils.ts that inserts an agent row directly for E2E setup"
  - truth: "Automated tests successfully verify asynchronous webhook outcomes using polling or a tunnel"
    status: failed
    reason: "The polling pattern (expect.poll) is correctly implemented in tests, and the simulateWebhook helper is wired to the endpoint. However, the endpoint rejects the event types that the tests actually send. Additionally, shadow-claim.spec.ts sends 'agent.confirmed' (line 74) which is not handled by the switch."
    artifacts:
      - path: "backend/src/routes/test-utils.ts"
        issue: "Switch statement handles 7 event types but is missing 'subscription.activated' and 'agent.confirmed' which are the exact types sent by the E2E tests"
      - path: "test/e2e/shadow-claim.spec.ts"
        issue: "Depends on 'agent.confirmed' internal event (line 74) and /create-agent endpoint (line 33), neither of which exist in test-utils.ts"
    missing:
      - "Add case 'subscription.activated' to simulate-webhook switch, delegating to handlePaymentSuccess"
      - "Add case 'agent.confirmed' to simulate-webhook switch with logic to update shadow claim challenge state in KV"
---

# Phase 31: End-to-End Test Implementation — Verification Report

**Phase Goal:** Full application workflows, including real third-party integrations, are automatically verifiable.
**Verified:** 2026-02-23T22:45:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification (previous stale VERIFICATION.md was deleted)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Developer can run Playwright tests handling cross-origin iframes and multi-browser contexts | ✓ VERIFIED | playwright.config.ts has 3 browser projects (chromium, firefox, webkit), webServer blocks with correct `cwd`, globalSetup wired to D1 migrations, contexts.ts provides isolated overseerPage/agentPage, paddle.ts uses `page.frameLocator()` for cross-origin Paddle iframe |
| 2 | Automated tests successfully complete a real Paddle Checkout sandbox flow using testuser-N data | ✗ FAILED | completePaddleCheckout fixture exists and fills iframe with test card 4242..., testuser-N emails used. BUT simulate-webhook rejects `subscription.activated` (test-utils.ts has no case for it → 400). Shadow-claim test blocked at setup: /create-agent endpoint missing. |
| 3 | Automated tests successfully verify asynchronous webhook outcomes using polling or a tunnel | ✗ FAILED | expect.poll pattern correctly implemented in subscription-flow.spec.ts (line 93-100). simulateWebhook helper correctly POSTs to /v1/test-utils/simulate-webhook. BUT the endpoint rejects the event types the tests actually send: `subscription.activated` and `agent.confirmed` are not in the switch. |

**Score:** 1/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `test/e2e/playwright.config.ts` | Playwright infra with multi-browser, webServer, cwd | ✓ VERIFIED | 100 lines. 3 browser projects. Both webServer blocks have `cwd: join(__dirname, '../../')`. Backend uses `--persist-to test/e2e/.wrangler-state`. ENABLE_TEST_ROUTES=true passed. |
| `test/e2e/setup/global.setup.ts` | DB cleanup + D1 migration before tests | ✓ VERIFIED | 29 lines. Removes `.wrangler-state`, runs `npm run db:migrate:test`. Script exists in both root and backend package.json. Persist paths aligned. |
| `backend/src/routes/test-utils.ts` | Webhook simulation + test helpers | ⚠️ PARTIAL | 131 lines. Substantive implementation with ENABLE_TEST_ROUTES guard. POST /simulate-webhook exists with 7 event type cases. BUT missing `subscription.activated` and `agent.confirmed` cases. Missing POST /create-agent endpoint. |
| `test/e2e/fixtures/paddle.ts` | Checkout iframe helper + webhook simulator | ✓ VERIFIED | 71 lines. `completePaddleCheckout` automates iframe card fill. `simulateWebhook` POSTs to /v1/test-utils/simulate-webhook with error handling. |
| `test/e2e/fixtures/contexts.ts` | Multi-actor browser context fixtures | ✓ VERIFIED | 31 lines. Extends base test with overseerContext/agentContext via `browser.newContext()`, provides overseerPage/agentPage. Properly cleans up contexts. |
| `test/e2e/multi-actor.spec.ts` | Cross-role workflow E2E test | ✓ VERIFIED | 189 lines. Full 7-step flow: overseer registration → client registration → agent registration (with Ed25519 signing) → claim → agent confirms → OAuth authorization → activity verification. Uses contexts fixture. |
| `test/e2e/registration-flow.spec.ts` | Overseer registration/login E2E tests | ✓ VERIFIED | 129 lines. 4 tests: registration, login with new credentials, session persistence on reload, logout. Uses Playwright auto-retrying locators. |
| `test/e2e/subscription-flow.spec.ts` | Paddle subscription checkout E2E | ⚠️ PARTIAL | 121 lines. 3 tests. Main test calls completePaddleCheckout + simulateWebhook + expect.poll. Uses testuser-N emails. BUT sends `subscription.activated` which test-utils.ts rejects. |
| `test/e2e/shadow-claim.spec.ts` | Shadow claim payment E2E | ⚠️ PARTIAL | 106 lines. Multi-step flow with test.step blocks. Uses completePaddleCheckout + simulateWebhook. BUT blocked: calls nonexistent /create-agent endpoint and sends unhandled `agent.confirmed` event type. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| playwright.config.ts | global.setup.ts | `globalSetup: join(...)` (line 35) | ✓ WIRED | Path resolves correctly |
| playwright.config.ts | Backend dev server | webServer[0] with cwd + command (line 75-86) | ✓ WIRED | cwd present, port 8787, ENABLE_TEST_ROUTES=true, --persist-to aligned |
| playwright.config.ts | Frontend dev server | webServer[1] with cwd + command (line 88-98) | ✓ WIRED | cwd present, port 3000, Paddle env vars passed |
| global.setup.ts | D1 database | `npm run db:migrate:test` (line 20) | ✓ WIRED | Script exists in root package.json (line 10), delegates to backend, persist path aligned |
| subscription-flow.spec.ts | simulate-webhook endpoint | paddle.ts `simulateWebhook()` → POST /v1/test-utils/simulate-webhook | ✗ BROKEN | simulateWebhook sends `subscription.activated`, test-utils.ts switch has no case → returns 400 |
| shadow-claim.spec.ts | /create-agent endpoint | `request.post(baseUrl + '/v1/test-utils/create-agent')` | ✗ NOT_WIRED | Endpoint does not exist in test-utils.ts |
| shadow-claim.spec.ts | simulate-webhook endpoint | paddle.ts `simulateWebhook()` with `agent.confirmed` | ✗ BROKEN | `agent.confirmed` not in switch → returns 400 |
| test-utils.ts | webhook-handler.ts | `import { handlePaymentSuccess, ... }` (line 8-16) | ✓ WIRED | All 8 imported handlers exist as exports in webhook-handler.ts |
| test-utils.ts | shadowClaimService.ts | `import { processShadowClaimWebhook }` (line 17) | ✓ WIRED | Function exported at line 285 of shadowClaimService.ts |
| test-utils.ts | backend/src/index.ts | `import testUtils` + `app.route('/v1/test-utils', testUtils)` | ✓ WIRED | Imported at line 12, guarded at lines 58-63, mounted at line 64 |
| contexts.ts | multi-actor.spec.ts | `import { test, expect } from './fixtures/contexts'` | ✓ WIRED | Imported at line 1 |
| contexts.ts | registration-flow.spec.ts | `import { test, expect } from './fixtures/contexts'` | ✓ WIRED | Imported at line 1 |
| paddle.ts | subscription-flow.spec.ts | `import { completePaddleCheckout, simulateWebhook }` | ✓ WIRED | Imported at line 2, both used |
| paddle.ts | shadow-claim.spec.ts | `import { completePaddleCheckout, simulateWebhook }` | ✓ WIRED | Imported at line 2, both used |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| E2ETEST-01: Playwright scaffolding for cross-origin iframes and multi-browser contexts | ✓ SATISFIED | — |
| E2ETEST-02: Real Paddle Checkout sandbox flows using testuser-N data | ✗ BLOCKED | simulate-webhook rejects `subscription.activated`; shadow-claim blocked by missing `/create-agent` endpoint |
| E2ETEST-03: Verify asynchronous webhook outcomes using polling or a tunnel | ✗ BLOCKED | Polling pattern (expect.poll) correct, but webhook injection fails for `subscription.activated` and `agent.confirmed` |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| shadow-claim.spec.ts | 74 | Comment: `// Hypothetical internal event for simulation` | ⚠️ Warning | Acknowledges `agent.confirmed` is not a real Paddle event; the backend has no handler for it |
| shadow-claim.spec.ts | 59 | `return null` in catch block | ℹ️ Info | Valid error handling for JSON parse failure, not a stub |
| paddle.ts | 38,41 | `placeholder*="MM"`, `placeholder*="CVC"` | ℹ️ Info | CSS attribute selectors, not placeholder content — false positive |

### Human Verification Required

### 1. Paddle Sandbox Iframe Interaction
**Test:** Run `npx playwright test subscription-flow` against a live Paddle sandbox environment
**Expected:** Paddle iframe loads, test card `4242424242424242` is accepted, checkout completes with success indicator
**Why human:** Paddle sandbox iframe DOM structure may differ from what `completePaddleCheckout` expects; selectors (`input[name="cardnumber"]`, `button:has-text("Pay")`) depend on Paddle's current UI

### 2. Visual Registration Flow
**Test:** Run `npx playwright test registration-flow` and inspect screenshots
**Expected:** Auth card renders correctly, form fields are visible and fillable, dashboard shows after registration
**Why human:** Visual layout correctness and timing of redirects can't be fully verified from code alone

### 3. Multi-Actor State Isolation
**Test:** Run `npx playwright test multi-actor` and verify console output
**Expected:** Overseer and agent operate in fully isolated browser contexts; no session/cookie leakage between contexts
**Why human:** State isolation edge cases (especially around localStorage and shared backend state) need runtime verification

---

## Gaps Summary

**3 gaps** block goal achievement, all located in `backend/src/routes/test-utils.ts`:

1. **Missing `subscription.activated` event type** in the simulate-webhook switch statement. The real `webhooks.ts` handles this at line 157 by calling `handlePaymentSuccess()`. The test-utils.ts switch omits it, so `subscription-flow.spec.ts` line 82 will receive a 400 error when it tries to simulate the webhook.

2. **Missing `agent.confirmed` event type** in the simulate-webhook switch statement. The shadow-claim E2E test (line 74) sends this hypothetical internal event to advance the claim state, but the endpoint rejects it.

3. **Missing `POST /create-agent` endpoint** in test-utils.ts. The shadow-claim E2E test (line 33) calls `POST /v1/test-utils/create-agent` to seed an agent for test setup, but no such route exists.

All 3 gaps are in the same file (`test-utils.ts`) and are additive — they require adding ~15-25 lines of code total. The rest of the infrastructure (Playwright config, global setup, fixtures, test specs, handler wiring) is verified and correct.

**Root cause:** The simulate-webhook switch was modeled after the test-utils router's initial design (7 event types) but was not synchronized with the event types that the E2E test specs actually send. The `/create-agent` endpoint was mentioned in the 31-03 SUMMARY as having been added, but is not present in the current file.

---

_Verified: 2026-02-23T22:45:00Z_
_Verifier: Antigravity (gsd-verifier)_
