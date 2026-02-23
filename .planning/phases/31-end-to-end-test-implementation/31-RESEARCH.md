# Phase 31: End-to-End Test Implementation - Research

**Researched:** 2026-02-23
**Domain:** E2E Testing with Playwright, Multi-context browsers, Iframe interactions, Webhook assertions
**Confidence:** HIGH

## Summary

This phase implements robust end-to-end tests to verify full application workflows, particularly focusing on multi-actor flows and third-party checkout integration (Paddle). Playwright is the standard tool for handling multiple concurrent browser contexts and seamlessly interacting with cross-origin iframes. Webhook verification can be handled either via local tunneling (`cloudflared`/`ngrok`) or through deterministic polling (`expect.poll()`).

**Primary recommendation:** Use Playwright's `browser.newContext()` for multi-actor tests, `page.frameLocator()` for Paddle checkout interactions, and favor `expect.poll()` against the backend for reliable webhook assertion.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@playwright/test` | 1.x | E2E Testing Framework | Native multi-context isolation and first-class cross-origin iframe support via `frameLocator`. |
| `cloudflared` | latest | Local Tunneling | Securely exposes the local worker to Paddle's real webhook deliveries in E2E. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `msw` / `page.route()` | latest | Network Mocking | For simulating specific API failure states or injecting the direct `SELF.fetch` webhook mock when bypassing full external network overhead. |

**Installation:**
```bash
npm install -D @playwright/test
npx playwright install --with-deps
```

## Architecture Patterns

### Recommended Project Structure
```
tests/e2e/
├── setup/               # Global setup (e.g., ngrok/cloudflared initialization)
├── fixtures/            # Playwright custom fixtures (e.g., multi-actor setups)
├── checkout.spec.ts     # Paddle checkout and webhook flows
└── multi-actor.spec.ts  # Overseer + Agent interactions
```

### Pattern 1: Multi-Actor Contexts (Overseer + Agent)
**What:** Testing workflows where an Overseer performs actions that an Agent immediately sees.
**When to use:** Multi-tenant or multi-role system verification.
**Example:**
```typescript
import { test, expect } from '@playwright/test';

test('overseer and agent interaction', async ({ browser }) => {
  // Create isolated contexts (no shared cookies/storage)
  const overseerContext = await browser.newContext();
  const agentContext = await browser.newContext();

  const overseerPage = await overseerContext.newPage();
  const agentPage = await agentContext.newPage();

  // Act as overseer
  await overseerPage.goto('/overseer/dashboard');
  await overseerPage.getByRole('button', { name: 'Assign Task' }).click();

  // Verify as agent
  await agentPage.goto('/agent/tasks');
  await expect(agentPage.getByText('New Task Assigned')).toBeVisible();
});
```

### Pattern 2: Asserting Asynchronous Webhooks
**What:** Verifying that a third-party webhook (Paddle) successfully updated the system state.
**When to use:** After completing a real sandbox checkout flow.
**Example:**
```typescript
// Instead of hardcoded sleep() or flappy timeouts, poll the backend state
await expect.poll(async () => {
  const res = await request.get(`/api/users/testuser-1/status`);
  const data = await res.json();
  return data.subscriptionStatus;
}, {
  timeout: 15000, // wait up to 15s for webhook to arrive and process
}).toBe('active');
```

### Anti-Patterns to Avoid
- **Hardcoded Sleeps (`page.waitForTimeout`):** Never use arbitrary delays to wait for webhooks. Always use `expect.poll()` or wait for a UI state change.
- **Leaking Contexts:** Using the single default `page` fixture for multi-actor tests. Always instantiate new contexts via `browser.newContext()`.
- **Direct Element Locators inside Iframes:** Using `page.locator('.paddle-input')` will fail for cross-origin iframes. Always use `page.frameLocator()`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-origin iframe targeting | `postMessage` hacks or raw `contentWindow` access | Playwright `page.frameLocator()` | Playwright handles strict cross-origin security natively and waits for frames to load. |
| Multi-browser sessions | Running separate test files or instances | `browser.newContext()` | Native memory-isolated contexts are fast and reliable. |
| Webhook testing tunnels | Custom reverse proxies | `cloudflared` or direct `SELF.fetch()` mocking | Avoids maintaining brittle local network routing scripts. |

## Common Pitfalls

### Pitfall 1: Iframe Locators Timing Out
**What goes wrong:** Playwright fails to find the Paddle checkout inputs.
**Why it happens:** Attempting to interact before the third-party iframe script has fully injected the DOM, or the frame is strictly sandboxed.
**How to avoid:** Wait for a specific container to appear before probing the frame.
```typescript
const checkoutFrame = page.frameLocator('iframe[title*="Paddle"]');
await checkoutFrame.getByLabel('Card number').waitFor({ state: 'visible' });
await checkoutFrame.getByLabel('Card number').fill('4111 1111 1111 1111');
```

### Pitfall 2: Local Webhook Delivery Fails in CI
**What goes wrong:** Webhook tests pass locally but timeout in CI.
**Why it happens:** Paddle cannot reach the CI runner's localhost.
**How to avoid:** Either ensure the CI step securely provisions a temporary `cloudflared` tunnel URL to register with Paddle, or fallback to the pre-decided `[28-03-D03]` approach of injecting the webhook payload directly into `SELF.fetch()` to simulate the delivery without external networking.

## Code Examples

### Paddle Sandbox Checkout Interaction
```typescript
test('successful paddle checkout', async ({ page }) => {
  await page.goto('/pricing');
  await page.getByRole('button', { name: 'Subscribe' }).click();

  // Pierce the Paddle iframe
  const paddleFrame = page.frameLocator('iframe[name="paddle-checkout"]');
  
  // Fill sandbox details
  await paddleFrame.getByPlaceholder('Card number').fill('4111 1111 1111 1111');
  await paddleFrame.getByPlaceholder('MM / YY').fill('12 / 30');
  await paddleFrame.getByPlaceholder('CVC').fill('123');
  
  await paddleFrame.getByRole('button', { name: 'Pay' }).click();

  // Wait for success modal in main page
  await expect(page.getByText('Payment Successful')).toBeVisible();
});
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Cypress Multi-Window | Playwright `newContext()` | ~2021 | Full native support for simulating multiple users in the same test block without hacks. |
| Timeouts for async | `expect.poll()` | Playwright 1.x | Flakiness drastically reduced by aggressively polling assertions. |

## Open Questions

1. **Webhook Strategy in CI**
   - What we know: E2ETEST-03 requires explicit handling via tunnel or polling, and `[28-03-D03]` defined direct injection.
   - What's unclear: Should the CI environment spin up an actual `cloudflared` tunnel against the real Paddle sandbox, or rely on `SELF.fetch` injection for true reliability?
   - Recommendation: Use real sandbox webhooks (via tunnel) for local development/nightly E2E, but use the `SELF.fetch()` injection pattern for standard PR pipeline E2E to prevent network flakiness.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Playwright is the industry standard for these exact requirements.
- Architecture: HIGH - Context isolation and frameLocators are heavily documented native features.
- Pitfalls: HIGH - Iframe timing and webhook routing are the two most common E2E failure points.
