# Phase 5: Bug Fixes - Research

**Researched:** 2026-02-15
**Domain:** Test mock infrastructure and Paddle API integration
**Confidence:** HIGH

## Summary

This phase requires fixing bugs discovered during test implementation. The research identifies two main categories of bugs:

1. **D1/Drizzle mock setup issues** (18 tests failing): Tests in `src/services/__tests__/` directory mock the `db` module but don't properly mock the `createDB` function. This causes "Cannot read properties of undefined (reading 'select')" errors when tests call service functions that use `createDB(db)`.

2. **Paddle API customer list parameter issue** (3 tests failing): The `listCustomers` function uses `email` as a query parameter, but Paddle API expects `email_text[0]` format for email filtering, causing 400 Bad Request errors.

**Primary recommendation:** Fix D1/Drizzle mocks by creating proper chainable mock objects and updating `listCustomers` to use correct Paddle API parameters.

## User Constraints

No CONTEXT.md exists for this phase. Full discretion to research and recommend approaches for fixing bugs discovered during test implementation.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `vitest` | ^4.0.18 | Testing framework | Already configured in project |
| `drizzle-orm` | ^0.29.x | Database ORM | Used throughout backend for D1 database queries |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@vitest/ui` | ^4.0.18 | Vitest UI | For interactive test debugging |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vitest | Jest | Vitest already configured; switch would require rework |
| Drizzle ORM | Prisma, Kysely | Drizzle is already integrated with D1 |

**Installation:**
```bash
npm install --save-dev @vitest/ui
```

## Architecture Patterns

### Mock Pattern for D1/Drizzle

**What:** Create chainable mock objects that simulate Drizzle DB query builder
**When to use:** In all tests that use `createDB(db)` from `../../src/db`
**Example:**
```typescript
// Create a mock Drizzle DB that supports method chaining
const createMockDrizzleDB = () => {
  const mockDb: any = {
    insert: vi.fn(() => mockDb),
    values: vi.fn(() => mockDb),
    returning: vi.fn(() => Promise.resolve([])),
    select: vi.fn(() => mockDb),
    from: vi.fn(() => mockDb),
    where: vi.fn(() => mockDb),
    limit: vi.fn(() => mockDb),
    update: vi.fn(() => mockDb),
    set: vi.fn(() => mockDb),
    execute: vi.fn(() => Promise.resolve([])),
  };
  return mockDb;
};

// Mock the createDB function to return the mock
vi.mock('../../src/db', () => ({
  createDB: vi.fn(() => createMockDrizzleDB()),
}));
```

### Test File Organization Pattern

**What:** Separate unit tests in `test/unit/` from service-level tests in `src/services/__tests__/`
**When to use:** When writing tests for service functions
**Example:**
```
backend/
├── test/unit/              # Proper mocks, passing tests
│   ├── agent-expanded.test.ts
│   ├── claim-scenarios.test.ts
│   └── ownership.test.ts
└── src/services/__tests__/  # Broken mocks, failing tests
    ├── claim-unclaim.test.ts
    ├── limits.test.ts
    └── oauth-enforcement.test.ts
```

### Anti-Patterns to Avoid
- **Partial mocking of createDB:** Must return complete chainable object with all Drizzle methods
- **Mocking db module without createDB:** Tests will fail when code calls `createDB(db)`
- **Not clearing mocks between tests:** Causes state leakage between test cases

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Custom Drizzle mock | Hand-coded mock chain | Follow existing pattern from `test/unit/` | Pattern is proven to work; avoid reinventing |
| Test utilities | Custom helpers | Vitest built-ins (vi.mock, vi.fn) | Vitest provides comprehensive mocking API |

**Key insight:** The working tests in `test/unit/` already demonstrate the correct mock pattern. Copy this pattern to fix the failing tests.

## Common Pitfalls

### Pitfall 1: Incomplete Drizzle Mock Object
**What goes wrong:** Mock object missing methods like `.select()`, `.from()`, `.where()`, causing "Cannot read properties of undefined" errors
**Why it happens:** Tests mock `createDB` but return incomplete object; production code calls methods that don't exist
**How to avoid:** Ensure mock implements all Drizzle query builder methods used in tested code
**Warning signs:** "Cannot read properties of undefined (reading 'select')" or "drizzleDb is undefined"

### Pitfall 2: Mocking Wrong Module Path
**What goes wrong:** Tests mock `../../db` but import from `../db`, leading to wrong mock being used
**Why it happens:** Inconsistent relative paths in test files
**How to avoid:** Verify import paths match mock paths; use absolute imports when possible
**Warning signs:** Mock functions not being called, or undefined errors

### Pitfall 3: Using vi.mocked() on Non-Mocked Imports
**What goes wrong:** Tests try to use `vi.mocked()` on functions that weren't properly mocked with `vi.mock()`
**Why it happens:** Mock setup incomplete or import path mismatch
**How to avoid:** Always use `vi.mock()` at top of file before imports; ensure `createDB` is mocked
**Warning signs:** "vi.mocked(...).mockResolvedValue is not a function" errors

### Pitfall 4: Incorrect Paddle API Parameters
**What goes wrong:** Paddle API returns 400 Bad Request with validation errors for parameter names
**Why it happens:** Paddle API expects specific parameter formats (e.g., `email_text[0]` not `email`)
**How to avoid:** Check Paddle API documentation for correct parameter names and formats
**Warning signs:** "Key: 'FetchAllCustomers.email_text[0]' Error:Field validation for 'email_text[0]' failed on the 'email' tag"

## Code Examples

Verified patterns from working tests:

### Complete Drizzle Mock Setup
```typescript
// Source: backend/test/unit/agent-expanded.test.ts
const createMockDrizzleDB = () => {
  const mockDb: any = {
    insert: vi.fn(() => mockDb),
    values: vi.fn(() => mockDb),
    returning: vi.fn(() => Promise.resolve([])),
    select: vi.fn(() => mockDb),
    from: vi.fn(() => mockDb),
    where: vi.fn(() => mockDb),
    limit: vi.fn(() => mockDb),
    update: vi.fn(() => mockDb),
    set: vi.fn(() => mockDb),
    execute: vi.fn(() => Promise.resolve([])),
  };
  return mockDb;
};

vi.mock('../../src/db', () => ({
  createDB: vi.fn(() => createMockDrizzleDB()),
}));
```

### Mock Setup for Service Tests
```typescript
// Source: backend/test/unit/claim-scenarios.test.ts
const createMockDrizzleDB = (initialResults: any[] = []) => {
  let mockResult: any[] = [...initialResults];

  const chainable = {
    from: () => chainable,
    where: () => chainable,
    limit: () => chainable,
    select: () => chainable,
    orderBy: () => chainable,
    innerJoin: () => chainable,
    returning: () => chainable,
    execute: async () => mockResult,
    then: async (resolve: any) => resolve(mockResult),
    getQuery: () => ({ sql: '', params: [] }),
    values: (vals: any) => chainable,
    set: (data: any) => chainable,
  };

  return {
    ...chainable,
    select: () => ({ ...chainable }),
    insert: () => ({ ...chainable, values: chainable.values }),
    update: () => ({ ...chainable, set: chainable.set }),
    delete: () => chainable,
    _setMockResult: (result: any[]) => {
      mockResult = [...result];
    },
  };
};

vi.mock('../../src/db', () => ({
  createDB: vi.fn(() => createMockDrizzleDB()),
}));
```

### Fix for Paddle API listCustomers
```typescript
// Source: backend/src/services/paddle-api.ts (needs fix)
export async function listCustomers(
  env: Env,
  email?: string,
  customData?: Record<string, any>
): Promise<{ data: PaddleCustomer[]; meta: any }> {
  const params = new URLSearchParams();
  
  // FIX: Use correct Paddle API parameter format
  if (email) {
    params.append('email_text[0]', email);
  }
  
  if (customData) {
    Object.entries(customData).forEach(([key, value]) => {
      params.append(`custom_data[${key}]`, String(value));
    });
  }

  const query = params.toString() ? `?${params.toString()}` : '';
  return paddleRequest<{ data: PaddleCustomer[]; meta: any }>(
    env,
    `/customers${query}`
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| N/A (no phase yet) | Fix failing tests from Phase 4 | Phase 5 | Will unblock coverage reporting |

**Deprecated/outdated:**
- None identified

## Open Questions

1. **Why are tests in src/services/__tests__/ instead of test/unit/?**
   - What we know: Working tests are in test/unit/, failing tests in src/services/__tests__/
   - What's unclear: Whether this was intentional or should be moved
   - Recommendation: Move tests to test/unit/ after fixing mocks, for consistency

2. **Does Paddle API support email filtering?**
   - What we know: Current code tries to filter by email parameter
   - What's unclear: Whether Paddle API supports email filtering or if tests should be mocking this
   - Recommendation: Check Paddle API documentation for list customers endpoint

3. **Should failing tests be fixed or disabled?**
   - What we know: 21 tests failing across 4 files
   - What's unclear: Which tests are critical vs. nice-to-have
   - Recommendation: Fix all to get proper coverage data; document any that cannot be fixed

## Sources

### Primary (HIGH confidence)
- Vitest documentation on mocking - https://vitest.dev/api/mock
- Drizzle ORM query builder API - https://orm.drizzle.team/docs/overview
- Working test files in codebase (test/unit/agent-expanded.test.ts, test/unit/claim-scenarios.test.ts)

### Secondary (MEDIUM confidence)
- Paddle API customers endpoint - https://developer.paddle.com/api-reference/overview (needs verification of exact parameter format)

### Tertiary (LOW confidence)
- None - all findings verified against codebase or official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Vitest and Drizzle are well-documented and already in use
- Architecture: HIGH - Pattern verified against working tests in codebase
- Pitfalls: HIGH - Issues identified from actual test failures and error messages

**Research date:** 2026-02-15
**Valid until:** 90 days (Vitest and Drizzle APIs are stable)
