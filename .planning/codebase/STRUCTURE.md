# Codebase Structure

**Analysis Date:** 2026-02-14

## Directory Layout

```
subscription/
├── backend/                    # Cloudflare Worker backend
│   ├── src/
│   │   ├── db/                # Database layer
│   │   │   ├── schema/        # Drizzle ORM table definitions
│   │   │   └── index.ts       # DB connection factory
│   │   ├── middleware/        # Hono middleware
│   │   │   └── auth.ts        # Authentication middleware
│   │   ├── routes/            # HTTP route handlers
│   │   │   ├── agents.ts      # Agent management endpoints
│   │   │   ├── clients.ts     # OAuth client management
│   │   │   ├── oauth.ts       # OAuth2 authorization flows
│   │   │   ├── overseers.ts   # Overseer management
│   │   │   ├── subscriptions.ts # Subscription management
│   │   │   └── webhooks.ts    # Paddle webhook handlers
│   │   ├── services/          # Business logic layer
│   │   │   ├── __tests__/     # Service unit tests
│   │   │   ├── agent.ts       # Agent CRUD operations
│   │   │   ├── challenge.ts   # Challenge management
│   │   │   ├── client-limits.ts # Client registration limits
│   │   │   ├── dpop.ts        # DPoP proof validation
│   │   │   ├── oauth-client.ts # OAuth client operations
│   │   │   ├── oauth-flow.ts  # OAuth2 token flows
│   │   │   ├── oauth-history.ts # Authorization tracking
│   │   │   ├── overseer.ts    # Overseer operations
│   │   │   ├── oversights.ts  # Agent-overseer relationships
│   │   │   ├── ownership.ts   # Claim/declaim logic
│   │   │   ├── paddle.ts      # Paddle API integration
│   │   │   ├── paddle-api.ts  # Paddle API client
│   │   │   ├── paddle-customer.ts # Paddle customer ops
│   │   │   ├── session.ts     # Session management
│   │   │   ├── subscription.ts # Subscription logic
│   │   │   ├── subscription-config.ts # Tier configuration
│   │   │   └── webhook-handler.ts # Webhook processing
│   │   ├── types/             # TypeScript type definitions
│   │   │   ├── env.ts         # Environment/bindings types
│   │   │   └── models.ts      # Domain model types
│   │   ├── utils/             # Utility functions
│   │   │   ├── crypto.ts      # Cryptographic operations
│   │   │   ├── helpers.ts     # General helpers (UUID, dates)
│   │   │   ├── logging.ts     # Audit logging
│   │   │   └── password.ts    # Password hashing
│   │   └── index.ts           # Worker entry point
│   ├── drizzle/               # Drizzle ORM migrations
│   │   ├── meta/              # Migration metadata
│   │   └── *.sql              # SQL migration files
│   ├── migrations/            # D1 migration scripts
│   │   └── *.sql              # Database migrations
│   ├── scripts/               # Utility scripts
│   ├── package.json           # Backend dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── vitest.config.ts       # Test runner config
│   └── wrangler.toml          # Cloudflare Worker config
├── frontend/                  # React SPA frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   │   └── client.ts      # ApiClient class with all endpoints
│   │   ├── components/        # Reusable UI components
│   │   │   └── Header.tsx     # Navigation header
│   │   ├── context/           # React contexts
│   │   │   └── AuthContext.tsx # Authentication state
│   │   ├── pages/             # Page components (routes)
│   │   │   ├── AgentDashboard.tsx
│   │   │   ├── Home.tsx
│   │   │   ├── OverseerAuth.tsx
│   │   │   ├── OverseerDashboard.tsx
│   │   │   ├── RegisteredClients.tsx
│   │   │   ├── SubscriptionCancelled.tsx
│   │   │   ├── SubscriptionManagement.tsx
│   │   │   └── SubscriptionSuccess.tsx
│   │   ├── types/             # TypeScript types
│   │   │   └── index.ts       # Domain types
│   │   ├── App.tsx            # Main app component with routes
│   │   ├── index.css          # Global styles
│   │   ├── main.tsx           # Entry point
│   │   ├── paddle-init.ts     # Paddle.js initialization
│   │   └── vite-env.d.ts      # Vite type declarations
│   ├── test/                  # Test files
│   │   └── integration/       # Playwright E2E tests
│   ├── package.json           # Frontend dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── vite.config.ts         # Vite build config
│   └── index.html             # HTML entry point
├── docs/                      # Documentation
│   ├── v1/                    # Current version docs
│   │   ├── design/            # Design assets
│   │   ├── flows/             # Process flows
│   │   ├── requirements/      # Requirements docs
│   │   └── test scenarios/    # Test scenarios
│   ├── v0/                    # Legacy docs
│   └── outdated documentation/ # Archived docs
├── test/                      # Testing utilities
│   └── manual-console/        # Manual testing console
├── package.json               # Root package with workspace scripts
└── .planning/                 # Planning documents
    └── codebase/              # Codebase analysis docs
```

## Directory Purposes

**`backend/src/db/schema/`:**
- Purpose: Drizzle ORM table definitions
- Contains: SQLite table schemas with type inference
- Key files: `agents.ts`, `overseers.ts`, `oauth-clients.ts`, `subscription-tiers.ts`, etc.
- Pattern: Each table has its own file with `$inferInsert` and `$inferSelect` types

**`backend/src/routes/`:**
- Purpose: HTTP endpoint handlers organized by domain
- Contains: Hono router instances with CRUD endpoints
- Key files: `agents.ts` (largest, ~876 lines), `oauth.ts` (OAuth2 flows)
- Pattern: Each route file exports a Hono router mounted in `index.ts`

**`backend/src/services/`:**
- Purpose: Business logic, external API integration
- Contains: Service modules with async functions
- Key files: `subscription.ts`, `paddle.ts`, `ownership.ts`, `oauth-flow.ts`
- Pattern: Services depend on DB layer, may call external APIs

**`backend/src/services/__tests__/`:**
- Purpose: Unit tests for service layer
- Contains: Vitest test files
- Key files: `oauth-enforcement.test.ts`, `limits.test.ts`, `claim-unclaim.test.ts`

**`backend/src/middleware/`:**
- Purpose: Cross-cutting HTTP concerns
- Contains: `auth.ts` - authentication extraction and guards
- Pattern: Hono middleware functions using `createMiddleware()`

**`frontend/src/pages/`:**
- Purpose: Top-level route components
- Contains: Page components mapped to URL paths
- Key files: `OverseerDashboard.tsx` (main management UI), `AgentDashboard.tsx`
- Pattern: Each page corresponds to a route in `App.tsx`

**`frontend/src/api/`:**
- Purpose: HTTP client for backend API
- Contains: `client.ts` - singleton `ApiClient` class
- Pattern: Class-based client with typed methods for each endpoint

**`frontend/src/context/`:**
- Purpose: React context providers
- Contains: `AuthContext.tsx` - authentication state management
- Pattern: Context + Provider + hook for consuming

## Key File Locations

**Entry Points:**
- Backend: `backend/src/index.ts` - Hono app setup and route mounting
- Frontend: `frontend/src/main.tsx` - React root and context initialization
- Frontend HTML: `frontend/index.html` - SPA entry HTML

**Configuration:**
- Backend: `backend/wrangler.toml` - Cloudflare Worker bindings and env vars
- Frontend: `frontend/vite.config.ts` - Vite build configuration
- TypeScript: `backend/tsconfig.json`, `frontend/tsconfig.json`

**Core Logic:**
- OAuth2 implementation: `backend/src/routes/oauth.ts`, `backend/src/services/oauth-flow.ts`
- Subscription management: `backend/src/services/subscription.ts`
- DPoP validation: `backend/src/services/dpop.ts`
- Challenge handling: `backend/src/services/challenge.ts`

**Testing:**
- Unit tests: `backend/src/services/__tests__/*.test.ts`
- Integration tests: `frontend/test/integration/*.spec.js`
- Manual testing: `test/manual-console/`

## Naming Conventions

**Files:**
- Routes: `[domain].ts` (e.g., `agents.ts`, `oauth.ts`)
- Services: `[domain].ts` (e.g., `subscription.ts`, `paddle.ts`)
- Schemas: `[table-name].ts` (e.g., `agents.ts`, `oauth-clients.ts`)
- Tests: `[subject].test.ts` (e.g., `limits.test.ts`)

**Directories:**
- kebab-case for multi-word directories (e.g., `test scenarios/`, `manual-console/`)
- Lowercase single words (e.g., `routes/`, `services/`)

**TypeScript:**
- Interfaces: PascalCase (e.g., `Agent`, `SubscriptionWithLimits`)
- Functions: camelCase (e.g., `getAgentById`, `validateDPoPProof`)
- Constants: UPPER_SNAKE_CASE (e.g., `SUBSCRIPTION_TIERS`)

## Where to Add New Code

**New API Endpoint:**
- Route handler: `backend/src/routes/[domain].ts`
- Business logic: `backend/src/services/[domain].ts`
- Database schema (if needed): `backend/src/db/schema/[table].ts`
- Export in barrel: `backend/src/db/schema/index.ts`

**New Frontend Page:**
- Page component: `frontend/src/pages/[PageName].tsx`
- Add route in: `frontend/src/App.tsx`
- Add API method in: `frontend/src/api/client.ts` (if new endpoint)

**New Database Table:**
- Schema: `backend/src/db/schema/[table-name].ts`
- Export: Add to `backend/src/db/schema/index.ts`
- Migration: Create in `backend/migrations/`

**Utilities/Helpers:**
- Backend: `backend/src/utils/[category].ts`
- Frontend: Add to appropriate existing file or create new utility module

## Special Directories

**`backend/drizzle/`:**
- Purpose: Drizzle ORM migrations and metadata
- Generated: No (manually managed SQL)
- Committed: Yes

**`backend/migrations/`:**
- Purpose: D1 database migration scripts
- Generated: No (hand-written SQL)
- Committed: Yes

**`backend/.wrangler/`:**
- Purpose: Wrangler CLI state and local dev data
- Generated: Yes (by wrangler dev)
- Committed: No (in `.gitignore`)

**`frontend/dist/`:**
- Purpose: Vite build output
- Generated: Yes (by `npm run build`)
- Committed: No (in `.gitignore`)

**`test/manual-console/`:**
- Purpose: Manual testing utilities and documentation
- Contains: Test scripts, HTML test pages, result documentation
- Generated: No (hand-written)
- Committed: Yes

---

*Structure analysis: 2026-02-14*
