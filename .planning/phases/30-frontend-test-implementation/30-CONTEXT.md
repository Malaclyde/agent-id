# Phase 30: Frontend Test Implementation — Context

## Overview

**Phase Goal:** Frontend React components and edge cases are verifiable without relying on a live backend.

**Success Criteria:**
1. Developer can run Vitest to verify React component UI states.
2. Frontend tests successfully intercept and mock API requests using MSW.
3. Developer can verify complex frontend edge cases like polling timeouts and expired tokens via automated tests.

---

## Component Coverage

**Decision:** Treat all components equally — no priority ranking.

Components requiring tests:
- `Home.tsx` — Landing page with human/agent flow selection
- `Header.tsx` — Navigation, auth state display
- `OverseerAuth.tsx` — Login/register forms
- `OverseerDashboard.tsx` — Agent management, declaim flow, downgrade modal
- `AgentDashboard.tsx` — Agent info, OAuth history, shadow upgrade
- `RegisteredClients.tsx` — OAuth client CRUD
- `SubscriptionManagement.tsx` — Tier display, upgrade/cancel flows, Paddle integration
- `ShadowClaim.tsx` — Challenge flow, polling, error states
- `ShadowClaimPayment.tsx` — Payment flow continuation
- `SubscriptionSuccess.tsx` — Post-checkout success
- `SubscriptionCancelled.tsx` — Post-checkout cancellation
- `AuthContext.tsx` — Auth state management, session restoration

---

## MSW Mock Strategy

### Handler Organization

**Decision:** Organize handlers by endpoint.

Structure:
```
frontend/test/
├── mocks/
│   ├── handlers/
│   │   ├── agents.ts      # /v1/agents/* endpoints
│   │   ├── overseers.ts   # /v1/overseers/* endpoints
│   │   ├── clients.ts     # /v1/clients/* endpoints
│   │   └── subscriptions.ts # /v1/subscriptions/* endpoints
│   └── server.ts          # MSW server setup
```

### Response Scenarios

**Decision:** Each test defines its own response via `server.use()` — no default success handlers.

Pattern:
```typescript
// In test file
import { server } from '../mocks/server';

it('shows error when login fails', async () => {
  server.use(
    http.post('/v1/overseers/login', () => {
      return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 });
    })
  );
  // ... test implementation
});
```

Benefits:
- Explicit test expectations
- No hidden defaults
- Each test is self-contained

### Authentication State

**Decision:** Mock localStorage directly; MSW handlers read from `Authorization` header.

Pattern:
```typescript
// Test utility for auth state
function setAuthState(sessionId: string | null, authType: 'agent' | 'overseer' | null) {
  if (sessionId) {
    localStorage.setItem('sessionId', sessionId);
  } else {
    localStorage.removeItem('sessionId');
  }
  if (authType) {
    localStorage.setItem('authType', authType);
  } else {
    localStorage.removeItem('authType');
  }
}

// MSW handler reads header
http.get('/v1/agents/me', ({ request }) => {
  const auth = request.headers.get('Authorization');
  if (!auth) {
    return HttpResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  // ... return mock agent
});
```

### Paddle.js Mocking

**Decision:** Create a Paddle mock utility that tracks checkout calls.

Utility should:
- Mock `window.Paddle.Checkout.open`
- Track calls with arguments (priceId, customer, customData)
- Allow tests to verify correct checkout configuration
- Allow tests to simulate success/error callbacks

Pattern:
```typescript
// test/mocks/paddle.ts
const paddleCalls: Array<{
  priceId: string;
  customer: { email: string; name: string };
  customData: Record<string, unknown>;
}> = [];

function mockPaddle() {
  (window as any).Paddle = {
    Checkout: {
      open: vi.fn((config) => {
        paddleCalls.push({
          priceId: config.items[0].priceId,
          customer: config.customer,
          customData: config.customData
        });
      })
    }
  };
}

function clearPaddleCalls() {
  paddleCalls.length = 0;
}

export { mockPaddle, paddleCalls, clearPaddleCalls };
```

---

## Edge Case Behaviors

### Polling Failures (ShadowClaim)

**Decision:** Display message that automatic refresh failed; retry button already in UI.

Current implementation has:
- Exponential backoff polling (2s → 30s max)
- Manual "Check Status" button for user-triggered refresh
- Error state with retry button

Tests should verify:
- Network error during poll shows error state
- User can click manual check to retry
- Challenge expiration shows expired state

### Challenge Expiration

**Decision:** Already implemented — error displayed.

UI shows:
- "Challenge Expired" heading
- Expiration message
- "Start New Claim" button

### Session Expiration (401 Response)

**Decision:** Show modal: "Session expired, please login again" with login link.

Tests should verify:
- 401 response triggers modal
- Modal contains login link
- Clicking login navigates to auth page

**Note:** This behavior may need implementation. Tests should document expected behavior.

### Subscription States

**Decision:** Tests document current behavior, add `gsd-todo` for review.

States to test:
- `status: 'past_due'` — Document current UI
- `status: 'paused'` — Document current UI
- `will_renew: false` — Document current UI
- Grace period active — Document current UI

Add `gsd-todo` comment in tests for product review.

### Loading & Empty States

**Decision:** Spinner + explanatory text.

| Scenario | Expected UI |
|----------|-------------|
| Initial load | Spinner + "Loading [component name]..." |
| Load error | Error message + retry button |
| Empty result | Empty state message (e.g., "No agents claimed yet") |
| Refreshing | Spinner + "Updating..." (if applicable) |

---

## Test Utilities & Organization

### Shared Mock Factories

Create factory functions for mock data:

```typescript
// test/factories/agent.ts
export function createMockAgent(overrides?: Partial<Agent>): Agent {
  return {
    id: 'agent-123',
    name: 'Test Agent',
    description: 'Test description',
    oauth_count: 0,
    billing_period_end: null,
    ...overrides
  };
}

// test/factories/overseer.ts
export function createMockOverseer(overrides?: Partial<Overseer>): Overseer {
  return {
    id: 'overseer-123',
    name: 'Test User',
    email: 'test@example.com',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides
  };
}

// test/factories/subscription.ts
export function createMockSubscription(overrides?: Partial<Subscription>): Subscription {
  return {
    id: 'sub-123',
    tier: 'FREE',
    max_agents: 5,
    max_clients: 10,
    max_oauth_per_period: 100,
    billing_period_end: null,
    is_active: true,
    grace_period_end: null,
    created_at: '2026-01-01T00:00:00Z',
    will_renew: true,
    scheduled_cancel_at: null,
    ...overrides
  };
}
```

### Test Data Builders

For complex scenarios, provide fluent builder pattern:

```typescript
// test/builders/test-state.ts
export class TestStateBuilder {
  private agents: Agent[] = [];
  private overseer: Overseer | null = null;
  private subscription: Subscription | null = null;

  withOverseer(overrides?: Partial<Overseer>): this {
    this.overseer = createMockOverseer(overrides);
    return this;
  }

  withAgents(count: number, overrides?: Partial<Agent>): this {
    for (let i = 0; i < count; i++) {
      this.agents.push(createMockAgent({ 
        id: `agent-${i}`,
        ...overrides 
      }));
    }
    return this;
  }

  withSubscription(tier: string, overrides?: Partial<Subscription>): this {
    this.subscription = createMockSubscription({ tier, ...overrides });
    return this;
  }

  build(): TestState {
    return {
      overseer: this.overseer,
      agents: this.agents,
      subscription: this.subscription
    };
  }
}
```

### Directory Structure

```
frontend/test/
├── mocks/
│   ├── handlers/
│   │   ├── agents.ts
│   │   ├── overseers.ts
│   │   ├── clients.ts
│   │   └── subscriptions.ts
│   ├── server.ts
│   └── paddle.ts
├── factories/
│   ├── agent.ts
│   ├── overseer.ts
│   ├── subscription.ts
│   ├── client.ts
│   └── index.ts
├── builders/
│   └── test-state.ts
├── utils/
│   ├── auth-helpers.ts
│   └── render-helpers.tsx
├── unit/
│   ├── context/
│   │   └── auth-context.test.tsx
│   ├── components/
│   │   └── header.test.tsx
│   └── pages/
│       ├── home.test.tsx
│       ├── overseer-auth.test.tsx
│       ├── overseer-dashboard.test.tsx
│       ├── agent-dashboard.test.tsx
│       ├── registered-clients.test.tsx
│       ├── subscription-management.test.tsx
│       ├── shadow-claim.test.tsx
│       ├── shadow-claim-payment.test.tsx
│       ├── subscription-success.test.tsx
│       └── subscription-cancelled.test.tsx
└── setup.ts
```

---

## gsd-todo Items

1. **Subscription state behavior review** — Review UI display for `past_due`, `paused`, `will_renew: false` states after tests document current behavior.

---

## Locked Decisions

- All components get equal test coverage priority
- MSW handlers organized by endpoint
- No default success handlers — tests define their own responses
- localStorage mocking for auth state
- Paddle mock utility for checkout tracking
- Session expiration shows modal with login link
- Spinner + explanatory text for loading states
- Test factories for mock data, builders for complex scenarios
