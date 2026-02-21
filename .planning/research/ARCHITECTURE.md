# Architecture Patterns: Comprehensive Testing Suite

**Domain:** Full-stack Application Testing (Cloudflare Workers, React SPA, Paddle, Cryptographic Auth)
**Researched:** Sat Feb 21 2026
**Overall confidence:** HIGH

## Recommended Architecture

The testing architecture introduces dedicated test runners and harnesses that integrate tightly with the existing Cloudflare/React ecosystem. It is structured into three distinct layers: Unit, Integration, and End-to-End (E2E), orchestrating local emulators (Miniflare/Wrangler) and real sandbox environments (Paddle).

### Layer Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                       CI/CD Pipeline                        │
│ (GitHub Actions: Preview Deploys -> E2E -> Prod Deploy)     │
└──────────────────────┬───────────────────────────────┬──────┘
                       │                               │
┌──────────────────────▼────────────────┐  ┌───────────▼───────────┐
│           Playwright (E2E)            │  │   Paddle Sandbox      │
│ - Browses React SPA                   │  │ - Processes Checkout  │
│ - Completes Paddle Checkout Iframe    ├──► - Dispatches Webhooks │
│ - Injects Ed25519 Auth state          │  │                       │
└──────────────────────┬────────────────┘  └───────────┬───────────┘
                       │                               │
┌──────────────────────▼───────────────────────────────▼───────────┐
│                   Staging / Local Environment                    │
│ - Frontend: Vite Dev Server (Local) or GH Pages Preview (CI)     │
│ - Backend: Wrangler Dev (Local) or CF Workers Preview (CI)       │
│ - DB: Local SQLite (Miniflare D1) or CF D1 Preview Database      │
└──────────────────────────────────────────────────────────────────┘
```

### Component Boundaries and Integration Points

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **Vitest (Frontend)** | Runs React SPA unit/component tests in isolated jsdom environment. | React Components, Mock API Handlers (MSW) |
| **Vitest Pool Workers (Backend)** | Runs backend unit/integration tests using `@cloudflare/vitest-pool-workers`. | Hono App (`app.fetch`), In-memory D1/KV emulators |
| **Playwright (E2E Runner)** | Automates full browser workflows, including third-party iframes (Paddle). | Frontend SPA, Backend API, Paddle Sandbox |
| **Crypto Test Harness** | Utility factory to generate Ed25519 keypairs and sign DPoP proofs dynamically. | Playwright Fixtures, Vitest API Integration Tests |
| **Webhook Tunnel (Local Dev)** | Exposes local `wrangler dev` environment to the public internet for testing webhooks. | `cloudflared` (Cloudflare Tunnels), Paddle Sandbox |

## New Components Needed

1. **`tests/test-utils/crypto.ts`**: A dedicated utility to generate Ed25519 keys, structure Bearer session tokens, and construct valid DPoP signatures for test requests.
2. **`playwright.config.ts` + Fixtures**: Custom Playwright setup that provisions a fresh local D1 database before each test suite and seeds initial overseer/agent state.
3. **Mock Service Worker (MSW)** (Optional but recommended): For React SPA component testing to intercept API calls without needing the backend running.
4. **Local Webhook Tunnel (`cloudflared`)**: A script to automatically spin up a secure tunnel during local E2E testing so Paddle Sandbox webhooks can reach the local Hono instance.

## Data Flow Changes (Test vs. Production)

### Database (D1) & KV Routing
- **Unit/Integration Tests:** Use completely isolated, in-memory SQLite instances provided by Miniflare (`@cloudflare/vitest-pool-workers`). Data is wiped between test files.
- **Local E2E Tests:** Run against a persistent local SQLite file (`.wrangler/state/v3/d1`). A global setup script runs `wrangler d1 execute <local-db> --file=schema.sql` and seeds data before Playwright starts.
- **CI E2E Tests:** GitHub Actions provisions a temporary, ephemeral D1 database (`wrangler d1 create test-db-${GITHUB_SHA}`) and binds it to a Preview Worker deployment. The database is dropped after the run.

### Paddle Sandbox E2E Flow
Testing real Paddle checkouts requires a specific data flow to handle asynchronous webhooks:
1. Playwright initiates checkout in the React SPA.
2. Playwright interacts with the Paddle iframe (using test card numbers) to complete payment.
3. **The Webhook Gap:** The test must wait for Paddle's asynchronous webhook to hit the backend and update the database (D1).
4. **Resolution:** Playwright repeatedly polls an API endpoint (or UI state) on the test backend until the subscription status updates to `active`, rather than assuming immediate success.

### Cryptographic Auth Flow
- **Overseer (Bearer):** Test harness injects a valid Bearer token directly into the browser's `localStorage` (via Playwright `page.evaluate`) to bypass manual login flows for specific tests.
- **Agent (DPoP + Ed25519):** E2E tests acting as agents generate a test keypair, hit the registration endpoint, and use a custom Playwright request interceptor to attach dynamic `DPoP` and `Signature` headers to all outbound API calls.

## Patterns to Follow

### Pattern 1: In-Memory Worker Testing
**What:** Using `app.fetch` instead of network calls for backend integration tests.
**When:** Testing Hono routes, D1 queries, and DPoP validation logic.
**Example:**
```typescript
import { env } from 'cloudflare:test';
import app from '../../src/index';

test('validates DPoP proof', async () => {
  const req = new Request('http://localhost/api/agent/data', {
    headers: { 'DPoP': generateTestProof(testKey) }
  });
  const res = await app.fetch(req, env);
  expect(res.status).toBe(200);
});
```

### Pattern 2: Polling for Asynchronous Webhooks in E2E
**What:** Waiting for Paddle webhook side-effects using Playwright's `expect.poll`.
**When:** Verifying a successful checkout actually provisioned the user's workspace/features.
**Example:**
```typescript
await page.frameLocator('.paddle-checkout-iframe').getByText('Pay Now').click();
// Wait for webhook to process and update DB
await expect.poll(async () => {
  const res = await request.get('/api/user/subscription');
  const data = await res.json();
  return data.status;
}, { timeout: 15000 }).toBe('active');
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mocking Paddle in E2E
**What:** Stubbing out the Paddle SDK in Playwright tests.
**Why bad:** Misses iframe communication errors, SDK version mismatches, and actual webhook parsing failures.
**Instead:** Use the real Paddle Sandbox environment with test credit cards for at least the "Happy Path" E2E tests. Use mocking only for edge-case Unit tests.

### Anti-Pattern 2: Hardcoding Ed25519 Signatures
**What:** Recording a static HTTP request with a DPoP signature and reusing it in tests.
**Why bad:** DPoP proofs include timestamps (JWT `iat`) and nonces. Hardcoded signatures will expire and fail validation.
**Instead:** Dynamically generate the DPoP proof at test execution time using a shared test utility.

### Anti-Pattern 3: Shared CI Databases
**What:** Running all PR E2E tests against a single "staging" D1 database.
**Why bad:** Concurrent PRs running tests will mutate each other's state, leading to flaky failures.
**Instead:** Provision dynamic D1 databases per CI run or namespace the test data aggressively.

## Scalability Considerations (Test Suite)

| Concern | Initial (Local) | Advanced (CI/CD) |
|---------|-----------------|------------------|
| **DB Isolation** | Single `.wrangler` local SQLite | Ephemeral D1 databases per PR |
| **Webhook Delivery** | `cloudflared` tunnel running locally | Dedicated Staging Worker endpoint |
| **Test Execution Time**| Sequential E2E | Fully parallelized Playwright workers |

## Suggested Build Order

To systematically introduce this testing suite without breaking existing functionality, build in the following order:

1. **Phase 1: Foundation & Test Utils**
   - Install Vitest, `@cloudflare/vitest-pool-workers`.
   - Create `test-utils/crypto.ts` for Ed25519 and DPoP generation.
   - Refactor backend to ensure `env` bindings are dependency-injected for testing.

2. **Phase 2: Backend Integration Testing**
   - Write integration tests for Hono endpoints using `app.fetch()`.
   - Validate DPoP auth middleware and D1 interactions using in-memory SQLite.
   - Add tests for Paddle Webhook parsing and signature validation (mocking the payload).

3. **Phase 3: Frontend Component Testing**
   - Install Vitest, React Testing Library, and MSW.
   - Test UI components handling Auth states and the Paddle Checkout modal initialization.

4. **Phase 4: Local E2E Environment (Playwright)**
   - Install Playwright.
   - Create local orchestration scripts (`npm run test:e2e:local` which starts Vite, Wrangler, and an Ngrok/Cloudflared tunnel).
   - Write core E2E flows (Login, Agent Registration).

5. **Phase 5: Paddle Sandbox E2E Integration**
   - Configure Paddle Sandbox to point to the local tunnel.
   - Write the full checkout flow E2E test utilizing `expect.poll` for webhook completion.

6. **Phase 6: CI/CD Pipeline Formalization**
   - Update GitHub Actions to spin up ephemeral D1 databases and Worker Preview deployments.
   - Point Paddle Sandbox (or a dedicated Test Paddle Sandbox account) to the Preview worker.
   - Gate PR merges on successful E2E execution.
