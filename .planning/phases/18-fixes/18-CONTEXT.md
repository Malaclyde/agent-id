# Phase 18: Fixes - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix two OAuth-related bugs:
1. SQL error in subscription pane when counting OAuth usage (unclaimed agents)
2. Unclaimed agents blocked from OAuth registration despite having 10-call limit

</domain>

<decisions>
## Implementation Decisions

### Bug #1: Subscription Pane SQL Error
- **Root cause:** SQLite doesn't support `ANY()` array syntax like PostgreSQL
- **Fix approach:** Use Drizzle's `inArray()` instead of raw SQL with `ANY()`
- **File:** `backend/src/routes/subscriptions.ts` line 61

### Bug #2: Unclaimed Agents Blocked at /authorize
- **Root cause:** `canAgentPerformOAuth()` returns false immediately for FREE tier (unclaimed agents) without checking the 10-call limit
- **Current behavior:** FREE tier is blocked before count is evaluated
- **Expected behavior:** FREE tier (unclaimed) agents should get 10 OAuth calls per billing period
- **Fix approach:** Modify `canAgentPerformOAuth()` in `backend/src/services/agent.ts` to check the limit for FREE tier instead of blanket denial
- **Limit:** 10 OAuth registration calls per billing period (already exists in FREE tier defaults)

### Claude's Discretion
- Exact error message wording if it needs adjustment
- Whether to also record the denied request in oauth_requests table (currently not recorded when blocked)
- Test approach - unit tests or manual verification

</decisions>

<specifics>
## Specific Bugs

### Bug #1: SQL Error in Subscription Pane
- **Error:** `Failed query: select count(*) from "oauth_requests" where "oauth_requests"."agent_id" = ANY((?)) params: 3a2ff82a-112a-4fde-be06-38978a43cf89`
- **Triggers:** When an overseer with claimed agents logs in and switches to subscription pane
- **Line:** `backend/src/routes/subscriptions.ts` line 61

### Bug #2: Unclaimed Agent OAuth Blocked
- **Triggers:** When an unclaimed agent (no overseer) tries POST /v1/oauth/authorize
- **Expected:** Should allow up to 10 OAuth registration calls per billing period
- **Actual:** Blocked immediately with "Subscription is not active" or "OAuth authorization denied"
- **Files:** 
  - `backend/src/services/agent.ts` - `canAgentPerformOAuth()` function
  - `backend/src/services/agent.ts` - `incrementOAuthCountWithLimitCheck()` function

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 18-fixes*
*Context gathered: 2026-02-17*
