# Architecture

**Analysis Date:** 2026-02-14

## Pattern Overview

**Overall:** Modular Monolith (Single Cloudflare Worker with service-layer organization)

**Key Characteristics:**
- Backend runs as a Cloudflare Worker using Hono framework
- Frontend is a React SPA with client-side routing
- Authentication via dual methods: Bearer sessions (overseers) and DPoP proofs (agents)
- Data persistence via D1 (SQLite) and KV (ephemeral state)
- OAuth2/OIDC compliant authorization flows
- Subscription management via Paddle.com integration

## Layers

**Routes Layer:**
- Purpose: HTTP request handling, input validation, response formatting
- Location: `backend/src/routes/`
- Contains: Hono route handlers for REST endpoints
- Depends on: Services, Middleware
- Used by: External clients, Frontend SPA

**Middleware Layer:**
- Purpose: Cross-cutting concerns - authentication, CORS, logging
- Location: `backend/src/middleware/`
- Contains: `auth.ts` - Bearer token and DPoP validation
- Depends on: Services (session, agent)
- Used by: Routes layer

**Services Layer:**
- Purpose: Business logic, external API integration, data orchestration
- Location: `backend/src/services/`
- Contains: Domain services (agent, overseer, subscription, OAuth, ownership, etc.)
- Depends on: Database layer, External APIs (Paddle)
- Used by: Routes layer

**Database Layer:**
- Purpose: Schema definition, query building
- Location: `backend/src/db/`
- Contains: Drizzle ORM schema definitions, connection factory
- Depends on: D1Database binding
- Used by: Services layer

**Client Layer (Frontend):**
- Purpose: UI rendering, user interaction, API consumption
- Location: `frontend/src/`
- Contains: React components, pages, API client, auth context
- Depends on: Backend API
- Used by: End users

## Data Flow

**Agent Registration Flow:**

1. Client POSTs to `/api/agents/register/initiate` with name and public_key
2. Route validates input, checks for duplicate public_key via `getAgentByPublicKey()`
3. Challenge data stored in KV (`CHALLENGES` namespace) with 60s TTL
4. Client receives challenge_id and canonicalized challenge_data
5. Client signs challenge_data with Ed25519 private key
6. Client POSTs signature to `/api/agents/register/complete/:challengeId`
7. Route verifies signature via `verifyEd25519Signature()`
8. `createAgent()` service creates record in `agents` table via Drizzle ORM
9. Challenge deleted from KV, session created via `createSession()`
10. Session ID returned to client for Bearer authentication

**OAuth2 Authorization Flow:**

1. Client POSTs to `/oauth/authorize` with client_id, redirect_uri, code_challenge (PKCE)
2. Route validates client exists and redirect_uri matches registered URIs
3. Agent authentication via Bearer token or DPoP proof
4. `validateDPoPForAuth()` verifies cryptographic proof if DPoP used
5. Subscription limits checked via `canAgentPerformOAuth()`
6. Authorization code created via `createAuthorizationCode()` and stored in DB
7. Code returned to client, which exchanges it at `/oauth/token`
8. Token endpoint validates code, PKCE verifier, issues JWT access_token

**Overseer Claim Agent Flow:**

1. Authenticated overseer POSTs to `/api/agents/claim/initiate` with agent_id
2. Route checks agent not already under real overseer oversight
3. If shadow oversight exists, deactivates it via `deactivateOversight()`
4. Challenge created in KV with 5-minute TTL
5. Agent visits `/api/agents/claim/complete/:challengeId` (authenticated)
6. `claimAgent()` service creates oversight record linking overseer to agent
7. Both parties can now manage the agent relationship

**Subscription Upgrade Flow:**

1. Authenticated overseer POSTs to `/api/subscriptions/upgrade` with target_tier
2. Route fetches Paddle price ID from `getPaddlePriceId()`
3. Creates Paddle checkout via Paddle.js or API
4. Webhook handler at `/webhooks/paddle` receives subscription events
5. `updateOverseerSubscription()` updates overseer's paddle_subscription_id
6. Agent limits derived from overseer's subscription tier

**State Management:**

- **Sessions:** Stored in KV (`SESSIONS` namespace), 30-minute TTL
- **Challenges:** Stored in KV with short TTLs (1-60 minutes)
- **Authentication State:** Frontend uses React Context (`AuthContext.tsx`)
- **Database State:** D1 SQLite for persistent data with Drizzle ORM

## Key Abstractions

**Challenge-Based Authentication:**
- Purpose: Cryptographic proof-of-possession for key-based auth
- Files: `backend/src/services/challenge.ts`, `backend/src/routes/agents.ts`
- Pattern: Two-phase (initiate/complete) with temporary KV storage

**DPoP (Demonstrating Proof-of-Possession):**
- Purpose: Bind access tokens to specific clients/keys
- Files: `backend/src/services/dpop.ts`, `backend/src/middleware/auth.ts`
- Pattern: JWT signed with agent's private key, verified against stored public key

**Oversight Model:**
- Purpose: Flexible agent-overseer relationship with shadow support
- Files: `backend/src/services/oversights.ts`, `backend/src/services/ownership.ts`
- Pattern: `oversights` table tracks active relationships; agents derive limits from overseer's subscription

**Paddle-First Subscription Management:**
- Purpose: External source of truth for billing
- Files: `backend/src/services/subscription.ts`, `backend/src/services/paddle.ts`
- Pattern: No local subscription state; query Paddle API on-demand

## Entry Points

**Backend API Entry:**
- Location: `backend/src/index.ts`
- Triggers: HTTP requests to Cloudflare Worker
- Responsibilities: Hono app setup, middleware chain, route mounting, error handling

**Frontend Entry:**
- Location: `frontend/src/main.tsx`
- Triggers: Browser loads SPA
- Responsibilities: React root creation, router setup, auth context initialization, Paddle.js initialization

**Paddle Webhook Entry:**
- Location: `backend/src/routes/webhooks.ts` - `/webhooks/paddle`
- Triggers: Paddle sends subscription event notifications
- Responsibilities: Signature verification, event processing, subscription state updates

**OAuth Entry Points:**
- Authorization: `backend/src/routes/oauth.ts` - `/oauth/authorize`
- Token: `backend/src/routes/oauth.ts` - `/oauth/token`
- Responsibilities: OAuth2 authorization code flow with PKCE

## Error Handling

**Strategy:** Centralized error handling at route level with service-layer exceptions

**Patterns:**
- Routes catch errors and return JSON `{ success: false, error: "message" }`
- HTTP status codes: 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 409 (conflict), 500 (server error)
- Hono's `app.onError()` catches unhandled errors and returns 500
- Services throw descriptive errors that routes catch and format

## Cross-Cutting Concerns

**Logging:**
- Approach: `backend/src/utils/logging.ts` - `logEntityAction()` for audit trails
- Usage: Log subscription changes, ownership transfers, OAuth authorizations

**Validation:**
- Approach: Input validation at route level; cryptographic validation in services
- Examples: `validateEd25519PublicKey()`, `validateDPoPProof()`, schema validation

**Authentication:**
- Approach: Middleware extracts auth state; guards (`requireAgent`, `requireOverseer`) enforce it
- Dual methods: Bearer sessions (stateful) for overseers, DPoP proofs (stateless) for agents

**Rate Limiting:**
- Approach: KV-based rate limiting in `RATE_LIMITS` namespace
- Usage: Challenge endpoints protected against abuse

---

*Architecture analysis: 2026-02-14*
