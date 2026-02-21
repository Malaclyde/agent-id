# Testing Patterns

**Analysis Date:** 2026-02-14

## Test Framework

### Backend Unit/Integration Tests

**Runner:** Vitest 4.0.18
**Config:** `backend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['**/*.test.ts'],
    exclude: ['node_modules', 'dist'],
  },
});
```

**Assertion Library:** Vitest built-in (Jest-compatible)

**Run Commands:**
```bash
# Backend tests
cd backend && npm run test          # Run all tests
cd backend && npm run test:watch    # Watch mode
cd backend && npm run test:ui       # UI mode
cd backend && npm run test:integration  # Paddle API integration tests
```

### Frontend E2E Tests

**Runner:** Playwright 1.50.0
**Config:** `frontend/test/integration/playwright.config.js`

**Key configuration:**
- Single worker to avoid database race conditions
- Base URL: `http://localhost:3000`
- Screenshots/videos on failure

**Run Commands:**
```bash
# Frontend tests
cd frontend && npm run test:integration           # Run all tests
cd frontend && npm run test:integration:ui        # UI mode
cd frontend && npm run test:integration:debug     # Debug mode
cd frontend && npm run test:integration:report    # Show report
```

## Test File Organization

### Location
- **Backend unit tests:** Co-located in `__tests__/` subdirectory: `backend/src/services/__tests__/limits.test.ts`
- **Backend integration tests:** Separate `backend/test/` directory: `backend/test/paddle-api.test.ts`
- **Frontend E2E tests:** `frontend/test/integration/` directory

### Naming
- **Backend:** `*.test.ts` pattern
- **Frontend:** `*.spec.js` pattern

### Structure
```
backend/
├── src/
│   └── services/
│       ├── __tests__/
│       │   ├── limits.test.ts          # Unit tests for client-limits.ts
│       │   ├── oauth-enforcement.test.ts
│       │   └── claim-unclaim.test.ts
│       ├── client-limits.ts
│       └── ...
├── test/
│   └── paddle-api.test.ts              # Integration tests

frontend/
└── test/
    └── integration/
        ├── fixtures.js                 # Test utilities/fixtures
        ├── playwright.config.js
        ├── subscription-tests.spec.js
        └── paddle-sandbox-tests.spec.js
```

## Test Structure

### Backend Unit Test Pattern

**File header with description:**
```typescript
/**
 * Client Limits Service Tests
 *
 * Tests for client counting, limit enforcement, and client management.
 */
```

**Import organization:**
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { countClientsByOverseer, canRegisterClient } from '../client-limits';
import type { SubscriptionWithLimits } from '../subscription';
import { getActiveSubscription } from '../subscription';

// Mock dependencies
vi.mock('../subscription');
```

**Suite organization:**
```typescript
describe('Client Limits Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('canRegisterClient', () => {
    it('should allow registration when under limit', async () => {
      // Test implementation
    });

    it('should block registration when at limit', async () => {
      // Test implementation
    });
  });
});
```

### Test Patterns

**Setup and teardown:**
```typescript
const mockDB = {
  prepare: vi.fn(),
  batch: vi.fn(),
  exec: vi.fn(),
} as any;

const mockEnv = {
  PADDLE_API_KEY: 'test-key',
  SHADOW_SECRET: 'test-secret',
} as any;

describe('Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
});
```

**Mocking dependencies:**
```typescript
vi.mock('../subscription');

// In test:
vi.mocked(getActiveSubscription).mockResolvedValue(mockSubscription);
vi.mocked(countClientsByOverseer).mockResolvedValue(3);
```

**Spying on module functions:**
```typescript
const agentModule = await import('../agent');
vi.spyOn(agentModule, 'getAgentById').mockResolvedValue(mockAgent);
```

**Assertions:**
```typescript
expect(result.allowed).toBe(true);
expect(result.reason).toContain('Client limit reached');
expect(result.data).toBeInstanceOf(Array);
expect(result.data.length).toBeGreaterThan(0);
await expect(promise).rejects.toThrow('Expected error');
```

## Mocking

### Framework: Vitest

**Mock external modules:**
```typescript
vi.mock('../subscription');
vi.mock('../../db');
```

**Mock return values:**
```typescript
vi.mocked(getActiveSubscription).mockResolvedValue(mockSubscription);
vi.mocked(getEntitySubscription).mockRejectedValue(new Error('Failed'));
```

**Mock D1 database:**
```typescript
const mockDB = {
  prepare: vi.fn().mockReturnValue({
    bind: vi.fn().mockReturnValue({
      run: vi.fn().mockResolvedValue({ success: true }),
      first: vi.fn().mockResolvedValue({ id: 'agent_123', oauth_count: 1 }),
    }),
  }),
} as any;
```

**Spy on imported functions:**
```typescript
const agentModule = await import('../agent');
vi.spyOn(agentModule, 'getAgentById').mockResolvedValue(mockAgent);
```

### What to Mock

**DO mock:**
- External API calls (Paddle API)
- Database operations (D1 queries)
- Other service modules being tested indirectly
- Time-based functions

**DO NOT mock:**
- The module under test
- Data structures/type definitions
- Pure utility functions being tested

## Fixtures and Factories

### Test Data Location
- **Backend:** Inline in test files using constants
- **Frontend:** `frontend/test/integration/fixtures.js`

### Backend Fixture Pattern
```typescript
const mockSubscription: SubscriptionWithLimits = {
  tier_id: 'FREE',
  num_allowed_agents: 0,
  num_allowed_requests: 10,
  num_allowed_registrations: 5,
  is_free_tier: true,
};

// Constants at bottom of file
const FREE_TIER_LIMITS = { num_allowed_registrations: 5 };
const BASIC_TIER_LIMITS = { num_allowed_registrations: 10 };
```

### Frontend Fixtures
```typescript
// frontend/test/integration/fixtures.js
export const TEST_USERS = {
  FREE: {
    email: 'testuser-1@testuser.com',
    password: 'TestPassword123!',
    tier: 'FREE',
  },
  BASIC: {
    email: 'testuser-2@testuser.com',
    password: 'TestPassword123!',
    tier: 'BASIC',
  },
  PRO: {
    email: 'testuser-3@testuser.com',
    password: 'TestPassword123!',
    tier: 'PRO',
  },
};

export function generateRandomEmail(prefix = 'test-overseer') {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `${prefix}-${timestamp}-${random}@example.com`;
}
```

### Custom Playwright Fixtures
```typescript
export const test = base.extend({
  authenticatedFreeTierPage: async ({ page }, use) => {
    await loginAsTestUser(page, 'FREE');
    await use(page);
    await logoutOverseer(page);
  },
  // ... more fixtures
});
```

## Coverage

### Requirements
- **No explicit coverage target** configured
- **Manual coverage assessment** through test review

### View Coverage
```bash
cd backend && npm run test:ui  # Vitest UI shows coverage
```

## Test Types

### Unit Tests
- **Scope:** Individual functions/modules
- **Location:** `backend/src/**/__tests__/*.test.ts`
- **Characteristics:** Fast, isolated, mocked dependencies

### Integration Tests
- **Scope:** API interactions, database operations
- **Location:** `backend/test/paddle-api.test.ts`
- **Characteristics:** May call real external APIs (Paddle Sandbox)

### E2E Tests
- **Scope:** Full user workflows
- **Location:** `frontend/test/integration/*.spec.js`
- **Characteristics:** Browser automation, real services

## Common Patterns

### Async Testing
```typescript
it('should handle async operation', async () => {
  const result = await asyncFunction();
  expect(result).toBeDefined();
});
```

### Error Testing
```typescript
it('should throw error for invalid data', async () => {
  await expect(
    createCustomer(testEnv, '', '', {})
  ).rejects.toThrow();
});
```

### Retry Logic Testing
```typescript
it('should retry on contention', async () => {
  let attempts = 0;
  mockDB.prepare.mockImplementation(() => {
    attempts++;
    if (attempts < 3) throw new Error('Contention');
    return { run: vi.fn().mockResolvedValue({ success: true }) };
  });
  
  const result = await operationWithRetry(mockDB);
  expect(attempts).toBe(3);
  expect(result.success).toBe(true);
});
```

### Database State Testing
```typescript
it('should update database record', async () => {
  const runMock = vi.fn().mockResolvedValue({ success: true });
  mockDB.prepare.mockReturnValue({
    bind: vi.fn().mockReturnValue({ run: runMock }),
  });
  
  await updateOperation(mockDB, 'id-123');
  
  expect(mockDB.prepare).toHaveBeenCalledWith(
    expect.stringContaining('UPDATE')
  );
  expect(runMock).toHaveBeenCalled();
});
```

## Test Utilities

### Frontend Helpers
```typescript
// Page navigation
export async function navigateToHome(page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
}

// User actions
export async function registerOverseer(page, name, email, password) {
  await navigateToHome(page);
  await navigateToOverseerAuth(page);
  await switchToSignupMode(page);
  await clickEmailProvider(page);
  await fillRegistrationForm(page, { name, email: finalEmail, password });
  await submitRegistrationForm(page);
  await page.waitForURL('**/overseer/dashboard', { timeout: 15000 });
}
```

---

*Testing analysis: 2026-02-14*
