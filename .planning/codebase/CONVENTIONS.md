# Coding Conventions

**Analysis Date:** 2026-02-14

## Naming Patterns

### Files
- **Backend services:** `kebab-case.ts` (e.g., `client-limits.ts`, `paddle-api.ts`)
- **Backend routes:** `kebab-case.ts` matching entity (e.g., `agents.ts`, `overseers.ts`)
- **Backend schema:** `kebab-case.ts` matching table (e.g., `oauth-clients.ts`, `subscription-tiers.ts`)
- **Backend tests:** Co-located in `__tests__/filename.test.ts` pattern (e.g., `backend/src/services/__tests__/limits.test.ts`)
- **Frontend pages:** `PascalCase.tsx` (e.g., `AgentDashboard.tsx`, `OverseerAuth.tsx`)
- **Frontend components:** `PascalCase.tsx` (e.g., `Header.tsx`)
- **Frontend utilities:** `kebab-case.ts` (e.g., `api/client.ts`)
- **Frontend context:** `PascalCase.tsx` (e.g., `AuthContext.tsx`)

### Functions
- **Camel case** for all function names: `createAgent()`, `getAgentById()`, `incrementOAuthCount()`
- **Async functions** prefixed with action verb: `async function claimAgent()`
- **Boolean predicates** prefixed with `is`, `can`, `has`: `isShadowOverseer()`, `canAgentPerformOAuth()`, `hasOversight()`
- **Private helpers** kept in module scope without underscore prefix

### Variables
- **Camel case** for all variables: `mockSubscription`, `challengeId`
- **Constants at module level:** UPPER_SNAKE_CASE in tests: `const FREE_TIER_LIMITS = { num_allowed_registrations: 5 };`
- **Type definitions:** PascalCase with descriptive names: `SubscriptionWithLimits`, `CreateAgentInput`
- **Environment variables:** UPPER_SNAKE_CASE in `Env` interface: `PADDLE_API_KEY`, `JWT_SECRET`

### Types
- **Interfaces** for object shapes: `interface CreateAgentInput { name: string; }`
- **Type aliases** for unions/complex types: `type AuthType = 'agent' | 'overseer' | null;`
- **Drizzle schema types** inferred: `type Agent = typeof agents.$inferSelect;`
- **React props:** Interface with component name: `interface AuthContextType { ... }`

## Code Style

### Formatting
- **No explicit formatter** (Prettier/ESLint) detected
- **Indentation:** 2 spaces (observed throughout)
- **Line length:** ~100-120 characters (observed)
- **Semicolons:** Required
- **Quotes:** Single quotes for strings

### TypeScript Configuration
**Backend (`backend/tsconfig.json`):**
- Target: ESNext
- Module: ESNext
- Strict mode enabled
- Path alias: `@/*` → `src/*`
- JSX: react-jsx with hono/jsx

**Frontend (`frontend/tsconfig.json`):**
- Target: ES2020
- Module: ESNext
- Strict mode enabled
- Path alias: `@/*` → `src/*`
- JSX: react-jsx
- Additional checks: `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`

## Import Organization

### Order
1. **External dependencies** first (e.g., `import { Hono } from 'hono';`)
2. **Internal type imports** next (e.g., `import type { Env } from '../types/env';`)
3. **Internal modules** (e.g., `import { createAgent } from '../services/agent';`)
4. **Relative imports** within same directory last

### Patterns
```typescript
// External imports
import { Hono } from 'hono';
import { eq, sql } from 'drizzle-orm';
import * as ed from '@noble/ed25519';

// Type imports
import type { Agent } from '../db/schema';
import type { Env } from '../types/env';

// Internal service imports
import { createDB } from '../db';
import { agents } from '../db/schema';
import { getAgentById } from './agent';
```

### Path Aliases
- **Backend:** `@/*` maps to `src/*` - used for imports like `import { createDB } from '@/db';`
- **Frontend:** `@/*` maps to `src/*` - used for imports like `import { useAuth } from '@/context/AuthContext';`

## Error Handling

### Backend Patterns
**Service layer:** Throw descriptive errors
```typescript
if (!input.name || input.name.trim().length === 0) {
  throw new Error('Name is required');
}
```

**Route handlers:** Catch and format JSON responses
```typescript
try {
  const result = await someOperation();
  return c.json({ success: true, data: result });
} catch (error) {
  return c.json({ 
    success: false, 
    error: error instanceof Error ? error.message : 'Operation failed' 
  }, 400);
}
```

**Global error handler (`backend/src/index.ts`):**
```typescript
app.onError((err, c) => {
  console.error('Unhandled error:', err);
  return c.json({ error: 'Internal server error' }, 500);
});
```

### Frontend Patterns
**API client:** Return error messages in consistent format
**React components:** Try-catch with user-friendly messages

## Logging

### Backend
**Framework:** Console-based logging via Hono's logger middleware
**Patterns:**
- Use `console.error()` for errors
- Use `console.warn()` for retry warnings
- Use `console.log()` for operational info

**Custom logging utility (`backend/src/utils/logging.ts`):**
```typescript
logSubscriptionAction('shadow_overseer_deleted', overseerId, {
  agent_id: agentId,
  reason: 'Agent claimed by real overseer'
});
```

## Comments

### When to Comment
- **JSDoc** for public functions with parameters and return types
- **File headers** for test files explaining scope
- **Section dividers** for logically grouped code:
```typescript
// ============================================================================
// Shadow Overseer Cryptographic ID Functions
// ============================================================================
```
- **Implementation notes** for non-obvious logic

### JSDoc Pattern
```typescript
/**
 * Claim an agent by creating an oversight relationship
 * @param db - D1 database instance
 * @param agentId - Agent ID to claim
 * @param overseerId - Overseer ID (real or shadow)
 * @param env - Environment for shadow overseer validation
 * @returns The updated agent record
 */
export async function claimAgent(...)
```

## Function Design

### Size
- **Small, focused functions** (generally <50 lines)
- **Single responsibility** per function
- **Early returns** for validation errors

### Parameters
- **Named parameters** via destructuring for options: `function createAgent(db: D1Database, input: CreateAgentInput)`
- **Environment object** passed explicitly for config access
- **Database instance** passed as first parameter

### Return Values
- **Explicit return types** on exported functions
- **Nullable types** for "not found" scenarios: `Promise<Agent | null>`
- **Result objects** for complex outcomes: `{ success: boolean; reason?: string; newCount?: number }`

## Module Design

### Backend Structure
**Exports:** Named exports preferred
```typescript
export async function createAgent(...) { ... }
export async function getAgentById(...) { ... }
export interface CreateAgentInput { ... }
```

**No barrel files** - import directly from source files

### Frontend Structure
**React components:** Default export for pages
```typescript
export default function AgentDashboard() { ... }
```

**Custom hooks:** Named export
```typescript
export function useAuth() { ... }
```

**Context pattern:**
```typescript
const AuthContext = createContext<AuthContextType | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) { ... }
export function useAuth() { ... }
```

## Database Patterns

### Drizzle ORM
**Schema definition:**
```typescript
export const agents = sqliteTable('agents', {
  id: text('id').primaryKey(),
  name: text('name').notNull(),
  public_key: text('public_key').notNull().unique(),
  created_at: text('created_at').notNull().default(sql`datetime('now')`),
}, (table) => ({
  publicKeyIdx: index('idx_agents_public_key').on(table.public_key),
}));
```

**Type inference:**
```typescript
export type NewAgent = typeof agents.$inferInsert;
export type Agent = typeof agents.$inferSelect;
```

## Security Patterns

### Cryptographic Functions
- **@noble packages** for crypto: `@noble/ed25519`, `@noble/hashes`
- **Constant-time comparison** for signatures:
```typescript
function constantTimeCompare(a: Uint8Array, b: Uint8Array): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a[i] ^ b[i];
  }
  return result === 0;
}
```

---

*Convention analysis: 2026-02-14*
