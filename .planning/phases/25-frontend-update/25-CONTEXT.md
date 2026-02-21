# Phase 25: Frontend Updates - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Update ShadowClaim.tsx React component to support the new shadow claim flow with agent confirmation step. The frontend must handle four challenge states: `initiated` (agent needs to confirm), `awaiting-payment` (Paddle checkout available), `completed` (payment successful), and `expired` (challenge timed out).

This phase focuses on UI updates and state management to match the backend flow implemented in Phase 24. New features like shadow overseer claim initiation belong in other phases.
</domain>

<decisions>
## Implementation Decisions

### Agent confirmation instructions
- Display the same details as standard claim procedure (reuse existing pattern)
- User-friendly format matching current claim flow

### Polling and state transitions
- Simplest solution - direct state changes
- No loading indicator required right now

### Payment UI presentation
- Overlay checkout (same approach as overseer subscription payment)
- Consistent with existing payment flow

### Claude's Discretion
- Error and expiration handling approach
- Exact transition animations (if any)
- Error message wording and guidance
- Polling frequency and cleanup strategy
</decisions>

<specifics>
## Specific Ideas

- Match standard claim procedure for consistency
- Use existing overseer payment overlay pattern
- Keep it simple - no complex animations or indicators needed
</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope
</deferred>

---

*Phase: 25-frontend-updates*
*Context gathered: 2026-02-20*
