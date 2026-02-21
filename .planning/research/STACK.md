# Testing Stack Additions

**Project:** Comprehensive Testing Suite (Cloudflare/React)
**Milestone:** SUBSEQUENT MILESTONE — Adding comprehensive testing suite to existing app
**Researched:** Sat Feb 21 2026

## Recommended Stack

### Core Testing Frameworks
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `vitest` | 4.0.x | Unit & Integration Runner | Vite-native, instantly works with the existing React frontend build pipeline and avoids complex Babel config. Standard for modern Cloudflare projects. |
| `@cloudflare/vitest-pool-workers` | 0.12.x | Backend Worker Testing | Executes tests directly inside the `workerd` runtime rather than Node.js. Critical for guaranteeing our Ed25519 challenge-response crypto works exactly as it does in production (Web Crypto API vs Node Crypto). Native D1/KV bindings for integration testing. |

### End-to-End (E2E) & Edge-Case Auditing
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `@playwright/test` | 1.58.x | Full Stack E2E Testing | Unmatched capability to interact with cross-origin iframes (required to automate Paddle's Checkout UI). Supports multi-context browser instances natively, meaning we can simulate an Overseer in one window and an Agent responding to claims in another. Native network interception (`route.abort()`) allows simulating edge-case failures (e.g. dropping OAuth tokens, 500ing Paddle endpoints). |

### Frontend Component Testing
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `@testing-library/react` | 16.3.x | React Component Testing | Asserts complex UI states (e.g., Subscription Tier displays, Agent claiming UI) based on user behavior rather than React implementation details. |
| `@testing-library/jest-dom` | 6.9.x | Custom DOM Matchers | Simplifies assertions (e.g., `expect(claimButton).toBeDisabled()`). |
| `happy-dom` | 20.7.x | Lightweight DOM for Vitest | Significantly faster than `jsdom` for running component unit tests. |
| `msw` | 2.12.x | API Mocking (Mock Service Worker) | Intercepts frontend network requests during testing to simulate edge cases (e.g. 401 Unauthorized during Agent Claim or 503 from Paddle) without needing the full backend running. |

### Infrastructure (Testing & CI)
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `cloudflared` | 0.7.x | Local Webhook Exposure | Used in local E2E runs to securely tunnel traffic to `localhost`. Required so that Paddle's Sandbox environment can successfully hit our local `POST /webhooks/paddle` endpoint, allowing Playwright to assert the complete, real-world payment lifecycle. |

## What NOT to Add (Anti-Patterns)

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| E2E Framework | Playwright | Cypress | **Iframe and Multi-tab Limitations:** Cypress historically struggles with cross-origin iframes like Paddle's checkout (`sandbox-checkout.paddle.com`). It also lacks native multi-context support, making it nearly impossible to write a single test that simultaneously acts as an Overseer and an unauthenticated Agent executing the claim procedure. |
| Backend Mocks | `@cloudflare/vitest-pool-workers` | `miniflare` (Standalone) | **Node.js Parity Issues:** Running tests in standard Node.js using Miniflare 2/Jest leads to false positives, especially regarding the Web Crypto API used for Ed25519 and DPoP signatures. `vitest-pool-workers` uses the real `workerd` runtime. |
| Webhook Tunnels | `cloudflared` | `ngrok` | **Rate Limits & Stack Consistency:** We are already deploying on Cloudflare. `cloudflared` provides native, robust tunneling without the strict rate limits often encountered on ngrok's free tier, making E2E tests flakier. |
| Frontend Runner | Vitest | Jest | **Build Pipeline Duplication:** Jest requires re-configuring Babel/SWC to understand JSX and imports that Vite already handles. Vitest uses the exact same `vite.config.ts`, keeping test and production environments identical. |

## Testing Strategy & Integration Points

1. **Unit Tests (Backend):** Test cryptographic logic (Ed25519/DPoP verification) and token management logic using `vitest` + `@cloudflare/vitest-pool-workers`.
2. **Component Tests (Frontend):** Test the Agent Claim UI and Subscription Tier displays using `vitest` + `@testing-library/react`. Mock edge cases (network drops, invalid auth) using `msw`.
3. **Real Paddle E2E Tests:**
   - Boot local dev server (`wrangler dev`).
   - Open a `cloudflared` tunnel exposing the worker.
   - Configure Playwright to override the base URL and supply the tunnel URL to Paddle as the webhook endpoint.
   - Playwright navigates the React UI -> Clicks "Upgrade to Pro" -> Enters test credit card in the Paddle iframe.
   - Assert Paddle webhook triggers locally and the React UI upgrades to PRO via subscription polling or WebSocket events.

## Installation

```bash
# Core Runner & Backend Worker Testing
npm install -D vitest @cloudflare/vitest-pool-workers

# E2E Testing
npm install -D @playwright/test
npx playwright install --with-deps chromium

# Frontend React Testing
npm install -D @testing-library/react @testing-library/jest-dom happy-dom msw

# Local Webhook Tunnels (if not installed globally)
npm install -D cloudflared
```

## Sources

- NPM Registry (Versions valid as of Feb 2026)
- Cloudflare Docs: Testing Workers with Vitest (https://developers.cloudflare.com/workers/testing/vitest-integration/)
- Playwright Docs: Iframe Handling and Multi-page contexts (https://playwright.dev/docs/frames)
- Paddle Docs: Sandbox Environment & Testing Webhooks (https://developer.paddle.com/concepts/testing/testing-checkout)