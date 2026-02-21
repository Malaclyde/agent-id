# Phase 21: Add agent-oauth-registration-limit - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement OAuth registration request limits for agents based on subscription tier. Replace the broken `oauth_count`/`billing_period_end` tracking in the agents table with proper tracking using the existing `oauth_requests` table. Unclaimed agents (FREE tier) use calendar month-based limits. Claimed from Paddle.

 agents use billing period</domain>

<decisions>
## Implementation Decisions

### Limit enforcement
- Check limits at `/authorize` endpoint (not at `/token`)
- Return 403 error with `access_denied` error code when limit exceeded

### Storage - Remove old implementation
- Remove `oauth_count` column from `agents` table schema
- Remove `billing_period_end` column from `agents` table schema (or just stop using it)
- Remove functions: `incrementOAuthCountWithLimitCheck`, `incrementOAuthCount`, `canAgentPerformOAuth` from agent.ts
- Remove any billing period reset logic from agent.ts

### Storage - New implementation
- Use existing `oauth_requests` table for tracking
- Keep last 20 records per agent (auto-prune older records)
- Add new row to `oauth_requests` only when authorization code is successfully exchanged for access token (in `/token` endpoint), NOT at `/authorize`

### Period determination
- **Unclaimed agents (no overseer):** Calendar month-based limits
  - Count requests in current calendar month (1st of month to end of month)
  - Limit: 10 requests (FREE tier from subscription-config.ts)
- **Claimed agents (has overseer):** Billing period from Paddle
  - Query Paddle for subscription billing period end date
  - Count requests in current billing period
  - Most tiers have unlimited (-1), so no check needed

### Limits source
- Limits defined in `subscription-config.ts` (SUBSCRIPTION_TIERS)
- FREE: 10 requests
- BASIC/PRO/PREMIUM/SHADOW/ENTERPRISE: unlimited (-1)

### Error response format
- HTTP 403 status code
- JSON: `{ "error": "access_denied", "error_description": "OAuth limit reached (X/Y for this period)" }`
- Claude's discretion on exact wording

</decisions>

<specifics>
## Technical Details

**Files to modify:**
- `backend/src/db/schema/agents.ts` - Remove oauth_count, billing_period_end columns
- `backend/src/services/agent.ts` - Remove old limit checking functions
- `backend/src/routes/oauth.ts` - Update /authorize to use new limit checking
- `backend/src/routes/oauth.ts` - Add record to oauth_requests in handleAuthorizationCodeGrant (token exchange)
- Potentially add new service function for counting requests in period

**Key behavior:**
1. Agent calls /authorize
2. System checks: is agent claimed?
   - If unclaimed: count oauth_requests in current calendar month
   - If claimed: get billing period from Paddle, count oauth_requests in that period
3. If limit exceeded → return 403 error
4. If allowed → return authorization code
5. Agent calls /token to exchange code
6. On successful exchange → add row to oauth_requests table

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 21-agent-oauth-registration-limit*
*Context gathered: 2026-02-18*
