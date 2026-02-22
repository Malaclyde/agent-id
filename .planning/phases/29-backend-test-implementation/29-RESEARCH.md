# Phase 29: Backend Test Implementation - Research

**Researched:** Sun Feb 22 2026
**Domain:** Backend Testing, Cloudflare Workers, Ephemeral Databases, Cryptography
**Confidence:** HIGH

## Summary
The current backend test suite relies exclusively on Vitest running in the standard Node.js environment (`environment: 'node'`) using a deeply mocked service layer (`vi.mock(...)`). It bypasses database interactions and does not accurately replicate the Cloudflare Workers runtime, particularly missing `D1Database`, `KVNamespace`, and `Web Crypto API` parity. 

To achieve the goals defined in `29-CONTEXT.md`, the backend must migrate its test infrastructure to `@cloudflare/vitest-pool-workers`. This enables testing against a real ephemeral `D1Database` and authentic Cloudflare Web Crypto implementations without network overhead, satisfying all cryptographic and relationship verification requirements.

**Primary recommendation:** Downgrade `vitest` from `v4` to `v3.2.x` to enable `@cloudflare/vitest-pool-workers`, implement custom D1 schema parsing to bypass `miniflare` migration limitations, and inject a Map-based `KVNamespace` mock via `app.fetch()`.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `vitest` | `^3.2.0` | Test Runner | Required downgrade; `vitest-pool-workers` currently lacks `v4` support. |
| `@cloudflare/vitest-pool-workers` | `latest` | Worker Runtime Simulation | Provides identical Web Crypto API parity and fully functional ephemeral `D1Database` bindings inside tests. |
| `@noble/ed25519` | `^2.2.3` | Cryptographic Keys | Existing dependency; used to dynamically generate test keys. |

## Architecture Patterns

### Recommended Test Helpers Structure
```
backend/test/
├── helpers/
│   ├── db.ts       # D1 setup (migrations) and teardown (table clearing)
│   ├── kv.ts       # In-memory Map implementation of KVNamespace
│   ├── crypto.ts   # Dynamic Ed25519 keypair and DPoP signature generator
│   └── builder.ts  # Fluent API for inserting test data (Agent/Overseer relationships)
├── integration/    # app.fetch() endpoint tests with webhooks
└── unit/           # Service layer tests utilizing real env.DB and Map KV
```

### Pattern: D1 Migrations Execution (Custom Schema Parsing)
**What:** Loading `.sql` files into the ephemeral `D1Database` natively.
**When to use:** In a `beforeAll` block for any test suite requiring the database.
**Example:**
```typescript
import { env } from "cloudflare:test";

// Vite's import.meta.glob correctly bundles SQL inside the worker environment
const migrations = import.meta.glob('../../migrations/*.sql', { query: '?raw', import: 'default', eager: true }) as Record<string, string>;

export const setupTestDB = async () => {
  for (const key of Object.keys(migrations).sort()) {
    const sql = migrations[key];
    if (!sql) continue;
    
    // Strip comments to prevent SQLite syntax errors and batch execute
    const statements = sql.replace(/--.*/g, '').split(';').map(s => s.trim()).filter(s => s.length > 0);
    const batch = statements.map(s => env.DB.prepare(s));
    
    if (batch.length > 0) await env.DB.batch(batch);
  }
};
```

### Anti-Patterns to Avoid
- **Relying on `applyD1Migrations` from `cloudflare:test`:** Fails consistently due to strict `TEST_MIGRATIONS` binding typing errors (`parameter 2 is not of type 'D1Migration[]'`). The custom regex parser with `env.DB.batch()` is proven and stable.
- **Mocking Drizzle or DB Layers:** Stop using `vi.mock('../../src/db')`. The application services correctly accept `db: D1Database` as a parameter. Pass the real `env.DB` to them directly.

## Technical Approach to Context Decisions

1. **Ephemeral Data Architecture (D1 / KV Isolation & Teardown)**
   - **Setup:** Call `setupTestDB()` (which executes the `import.meta.glob` bundled SQL scripts via `env.DB.batch()`) in `beforeAll` hooks for each test file to create the tables.
   - **Teardown:** In `afterEach`, dynamically clear the database state by selecting all non-system tables (`sqlite_%`, `_cf_%`, `d1_%`) and executing `DELETE FROM <table>` rather than dropping the tables entirely.
   - **KV Maps:** The context explicitly mandated Map objects for KV to prioritize speed. Create a dummy `KVNamespace` object that wires `get`, `put`, and `delete` to a `Map<string, string>`, passing it into `app.fetch(req, { ...env, CHALLENGES: kvMock })`.

2. **Time & Webhook Simulation**
   - Use `vi.useFakeTimers()` to advance webhook processing wait times.
   - Trigger Paddle webhooks by crafting a valid HTTP `Request` to `http://localhost/v1/webhooks/paddle`, securely signing it with an internal `PADDLE_WEBHOOK_SECRET` passed within the Hono environment bindings, and executing it via `await app.fetch(request, env)`.

3. **Cryptographic Key Strategy**
   - Create a helper `generateTestKeyPair()` utilizing `@noble/ed25519` that generates a new 32-byte private key and derives the public key for each individual test case to prevent cross-test ID collision.
   - Implement `generateTestDPoP(method, url, keypair)` to securely generate and sign valid tokens specifically for `SELF.fetch()` invocations testing protected endpoints.

## Common Pitfalls

### Pitfall 1: Vitest Version Incompatibility
**What goes wrong:** Attempting to install `@cloudflare/vitest-pool-workers` errors out with peer dependency conflicts on `vitest`.
**Why it happens:** The repository uses `vitest@4.0.18`, but `@cloudflare/vitest-pool-workers` requires `vitest@2.0.x - 3.2.x`.
**How to avoid:** Hard-downgrade `vitest`, `@vitest/coverage-v8`, and `@vitest/ui` to `^3.2.0` in `backend/package.json` before implementation.

### Pitfall 2: Worker File System Isolation
**What goes wrong:** Tests crash when attempting to read migration files via `fs.readdirSync`.
**Why it happens:** Cloudflare's Vitest runner executes the tests *inside* a Worker environment (`/bundle/`), which doesn't have native Node.js filesystem access.
**How to avoid:** Rely strictly on Vite's build-time file embedding (`import.meta.glob`) to pull raw SQL strings into the test file.

### Pitfall 3: D1 `DELETE FROM` Authorization Errors
**What goes wrong:** Erasing tables using a wildcard `DELETE FROM` loops causes `D1_ERROR: not authorized: SQLITE_AUTH`.
**Why it happens:** D1 heavily protects internal namespace tables (`d1_%`, `_cf_%`, `sqlite_%`).
**How to avoid:** Explicitly filter internal table names out of the query: `WHERE name NOT LIKE 'sqlite_%' AND name NOT LIKE '_cf_%' AND name NOT LIKE 'd1_%'`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `environment: 'node'` | `pool: '@cloudflare/vitest-pool-workers/config'` | Phase 29 | Replaces global NodeJS globals with Cloudflare web standards. |
| `vi.mock('../../src/db')` | `import { env } from 'cloudflare:test'` | Phase 29 | Actual Drizzle SQL generation and D1 sqlite engine validation is tested. |

## Open Questions

1. **Test Concurrency:**
   - **What we know:** `vitest-pool-workers` runs test files concurrently by default, and `isolatedStorage: true` isolates `env.DB` instances across *workers*, but not automatically between tests in the *same file*.
   - **What's unclear:** The `poolOptions.workers.isolatedStorage` behavior across test suites might be sufficient to replace manual DB clearing if tests aren't run sequentially in the same file.
   - **Recommendation:** Keep manual `DELETE FROM <table>` in `afterEach` per the Context decision to guarantee absolute data safety between distinct test blocks within the same file.