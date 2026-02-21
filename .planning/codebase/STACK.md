# Technology Stack

**Analysis Date:** 2026-02-14

## Languages

**Primary:**
- **TypeScript** (5.3.3+) - Used for all backend (`backend/src/**/*.ts`) and frontend (`frontend/src/**/*.tsx`) code

**Configuration:**
- **TOML** - Wrangler configuration (`wrangler.toml`)
- **SQL** - Database migrations (`backend/migrations/*.sql`)

## Runtime

**Environment:**
- **Node.js** with ES modules (ESNext)
- `type: "module"` in all `package.json` files

**Package Manager:**
- **npm** - Primary package manager
- **Lockfile:** Present (`package-lock.json` in all packages)

## Frameworks

**Backend:**
- **Hono** (^4.7.4) - Minimal, fast web framework for Cloudflare Workers
  - Entry point: `backend/src/index.ts`
  - Uses CORS middleware for cross-origin requests
  - Logger middleware for request logging

**Frontend:**
- **React** (^18.3.1) - UI framework
- **React Router DOM** (^7.1.1) - Client-side routing
  - Entry point: `frontend/src/main.tsx`
  - App root: `frontend/src/App.tsx`

**Database:**
- **Drizzle ORM** (^0.45.1) - Type-safe SQL-like ORM for D1
- **Drizzle Kit** (^0.31.8) - Schema management and migrations

**Testing:**
- **Vitest** (^4.0.18) - Backend unit testing
- **Playwright** (^1.50.0) - Frontend integration/E2E testing

**Build/Dev:**
- **Vite** (^6.0.7) - Frontend build tool and dev server
- **Wrangler** (^3.105.0) - Cloudflare Workers CLI and deployment
- **tsx** (^4.19.2) - TypeScript execution for scripts

## Key Dependencies

**Critical:**
- **jose** (^5.9.6) - JWT signing and verification for authentication
- **bcryptjs** (^3.0.3) - Password hashing for overseer accounts
- **@noble/ed25519** (^2.2.3) - Ed25519 cryptographic signatures for agent authentication
- **@noble/hashes** (^1.7.1) - SHA256 and HMAC for shadow overseer ID generation

**Infrastructure:**
- **Cloudflare Workers Types** (^4.20250124.0) - Type definitions for Workers runtime
- **D1 SQLite Driver** - Better-sqlite3 for local development (`better-sqlite3` ^12.6.2)

**UI:**
- **lucide-react** (^0.563.0) - Icon library for frontend

## Configuration

**Environment:**
- **Backend:** `.dev.vars` file for local secrets, `wrangler.toml` for configuration
- **Frontend:** `.env.local` for environment variables (VITE_ prefix)
- **Required env vars** (defined in `backend/src/types/env.ts`):
  - `JWT_SECRET` - Required for production
  - `PADDLE_API_KEY` - For payment processing
  - `PADDLE_WEBHOOK_SECRET` - For webhook verification
  - `SHADOW_SECRET` - For shadow overseer ID generation

**Build:**
- `backend/tsconfig.json` - TypeScript configuration for backend
- `frontend/tsconfig.json` - TypeScript configuration for frontend
- `backend/drizzle.config.ts` - Drizzle ORM configuration
- `backend/vitest.config.ts` - Vitest test configuration

## Platform Requirements

**Development:**
- Node.js (latest LTS recommended)
- npm
- Wrangler CLI installed globally or via npx

**Production:**
- **Cloudflare Workers** - Edge compute platform
- **Cloudflare D1** - SQLite-based edge database
- **Cloudflare KV** - Key-value storage for sessions, challenges, rate limits, shadow claims

**Database Bindings** (from `wrangler.toml`):
- `DB` - D1 database for persistent data
- `CHALLENGES` - KV namespace for ephemeral challenges
- `SESSIONS` - KV namespace for session storage
- `RATE_LIMITS` - KV namespace for rate limiting
- `SHADOW_CLAIMS` - KV namespace for shadow claim locks

---

*Stack analysis: 2026-02-14*
