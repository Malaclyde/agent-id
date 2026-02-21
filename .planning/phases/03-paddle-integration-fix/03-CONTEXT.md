# Phase 3: Paddle Integration Fix - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix critical Paddle payment integration bugs before implementing tests. This includes:
- Fixing webhook signature validation
- Passing overseer_id in checkout requests
- Fixing /me endpoint to query Paddle directly
- Ensuring subscription info is returned from Paddle (not local DB)

This phase does NOT include:
- Implementing the test suite (Phase 4)
- Fixing bugs discovered during testing (Phase 5)

</domain>

<decisions>
## Implementation Decisions

### Webhook Event Handling
- Always respond HTTP 200 to all valid Paddle requests (even unhandled events)
- Handle only events necessary for our subscription flows
- Log unhandled events for future reference
- Must perform signature validation on all webhook requests

### Data Synchronization
- Paddle is the single source of truth
- No local DB caching for subscription data
- /me endpoint must query Paddle customer API directly

### Checkout Custom Data
- Pass `overseer_id` as custom data in all Paddle checkout requests
- This enables webhook handlers to associate subscriptions with the correct overseer

### Error Recovery
- Frontend: Show toast notification to user on errors
- Backend: Log all errors for debugging
- Never fail silently — errors must be visible

### Testing Verification
- Extensive automated testing required
- Tests should verify webhook handling, /me returns correct data, checkout includes overseer_id

### Claude's Discretion
- Specific Paddle SDK methods to use for signature validation
- Exact webhook event types to handle (subscription_created, subscription_updated, subscription_cancelled, etc.)
- Test framework selection (Vitest, Jest, etc.)
- Exact test coverage targets

</decisions>

<specifics>
## Specific Ideas

No specific references mentioned — open to standard approaches for implementation.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-paddle-integration-fix*
*Context gathered: 2026-02-15*
