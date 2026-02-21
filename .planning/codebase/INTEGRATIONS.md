# External Integrations

**Analysis Date:** 2026-02-14

## APIs & External Services

**Payment Processing:**
- **Paddle** - Subscription management and payment processing
  - SDK/Client: Custom REST API client (`backend/src/services/paddle-api.ts`)
  - Frontend Integration: Paddle.js initialized in `frontend/src/paddle-init.ts`
  - Environment Variables:
    - `VITE_PADDLE_TOKEN` - Public client-side token (frontend)
    - `PADDLE_API_KEY` - Server-side API key (backend secret)
    - `PADDLE_API_URL` - API endpoint (sandbox for dev, production for prod)
    - `PADDLE_WEBHOOK_SECRET` - Webhook signature verification

## Data Storage

**Databases:**
- **Cloudflare D1** (SQLite-compatible)
  - Connection: Via `DB` binding in Workers environment
  - ORM: Drizzle ORM with `drizzle-orm/d1` driver
  - Tables defined in `backend/src/db/schema/`:
    - `agents` - Agent identity records
    - `overseers` - User accounts with subscription data
    - `oversights` - Agent ownership relationships
    - `subscription_tiers` - Tier configurations
    - `oauth_clients`, `oauth_requests`, `access_tokens`, `authorization_codes` - OAuth 2.0 + DPoP
    - `sessions`, `challenges`, `client_blocks`, `revoked_tokens` - Security and session management

**File Storage:**
- Local filesystem only - No external file storage service detected

**Caching:**
- **Cloudflare KV** - Key-value namespaces for ephemeral data:
  - `CHALLENGES` - DPoP challenge storage
  - `SESSIONS` - Session token storage
  - `RATE_LIMITS` - Rate limiting counters
  - `SHADOW_CLAIMS` - Shadow overseer claim locks

## Authentication & Identity

**Auth Provider:**
- **Custom JWT-based authentication** using `jose` library
- **Ed25519 signature verification** for agent authentication
- **Password-based authentication** for overseers (bcryptjs)

**OAuth 2.0 + DPoP:**
- Custom OAuth 2.0 implementation with DPoP (Demonstrating Proof-of-Possession) extension
- Routes: `backend/src/routes/oauth.ts`
- Services: `backend/src/services/oauth-flow.ts`, `backend/src/services/dpop.ts`

## Monitoring & Observability

**Error Tracking:**
- Console logging via Hono logger middleware
- Structured logging utilities in `backend/src/utils/logging.ts`

**Logs:**
- Cloudflare Workers native logging (visible in Wrangler dashboard)
- Custom entity action logging for audit trail

## CI/CD & Deployment

**Hosting:**
- **Cloudflare Workers** - Serverless edge deployment
- **Wrangler CLI** for deployment (`wrangler deploy`)

**CI Pipeline:**
- Not detected - No GitHub Actions, Travis CI, or other CI configuration files found

## Environment Configuration

**Required Environment Variables** (from `backend/src/types/env.ts`):

**Core Secrets:**
- `JWT_SECRET` - JWT signing secret (REQUIRED in production)
- `SHADOW_SECRET` - Shadow overseer ID generation secret

**Paddle Integration:**
- `PADDLE_API_KEY` - Server-side API authentication
- `PADDLE_API_URL` - API base URL (`https://sandbox-api.paddle.com` or `https://api.paddle.com`)
- `PADDLE_WEBHOOK_SECRET` - Webhook signature verification
- `PADDLE_VENDOR_ID` - Vendor account ID
- `PADDLE_PRICE_ID_BASIC` - Basic tier price ID
- `PADDLE_PRICE_ID_PRO` - Pro tier price ID
- `PADDLE_PRICE_ID_PREMIUM` - Premium tier price ID
- `PADDLE_PRICE_ID_SHADOW` - Shadow tier price ID

**Application:**
- `ENVIRONMENT` - `development` or `production`
- `SERVICE_URL` - Backend service URL (optional, defaults to request origin)
- `FRONTEND_URL` - Frontend URL for redirects (e.g., `http://localhost:3000`)

**Secrets Location:**
- Development: `.dev.vars` file (gitignored)
- Production: Cloudflare Workers secrets (set via `wrangler secret put`)

## Webhooks & Callbacks

**Incoming:**
- **`POST /webhooks/paddle`** - Paddle webhook endpoint for subscription events
  - Handler: `backend/src/routes/webhooks.ts`
  - Security: Signature verification using `PADDLE_WEBHOOK_SECRET`
  - Rate limiting: Applied via `checkRateLimit` in `backend/src/redacted/webhook-security.ts`
  - Events handled:
    - `subscription.created`
    - `subscription.updated`
    - `subscription.cancelled`
    - `subscription.past_due`
    - `transaction.completed`
    - `transaction.past_due`

**Outgoing:**
- **Paddle API Calls** - Outbound requests to Paddle for:
  - Customer management (`/customers`)
  - Subscription operations (`/subscriptions`)
  - Price queries (`/prices`)
  - Portal sessions (`/customers/{id}/portal-sessions`)

## Frontend-Backend Communication

**API Proxy:**
- Vite dev server proxies `/api` and `/oauth` to backend (`http://localhost:8787`)
- Configured in `frontend/vite.config.ts`

**API Client:**
- Custom fetch-based client in `frontend/src/api/client.ts`

---

*Integration audit: 2026-02-14*
