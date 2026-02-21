# Phase 24: Agent Confirmation Flow - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement agent confirmation endpoint that allows agents to explicitly authorize shadow claim challenges before payment processing. Agents must prove identity, verify they match the challenge's agent_id, and trigger transition to `awaiting-payment` state. Frontend will poll status endpoint to show progress to the shadow overseer.

</domain>

<decisions>
## Implementation Decisions

### Authentication Method
- Support **both DPoP proof and session token**
- Agents can confirm using either:
  - Valid DPoP proof (cryptographic identity verification)
  - Valid session token (Bearer cookie-based authentication)
- Either method acceptable — no preference for one over the other

### Shadow Overseer Visibility
- **No separate endpoint for overseer status**
- Shadow overseer sees progress via browser polling the existing status endpoint
- When agent confirms, challenge status changes to `awaiting-payment`
- Frontend detects status change and transitions to payment UI
- Status endpoint remains single source of truth for both parties

### Error Handling
- **Unified error scheme** for all failure scenarios
- Consistent error response structure across:
  - Agent doesn't match challenge's agent_id
  - Agent already claimed by real overseer
  - Challenge expired
  - Invalid authentication (DPoP or session)
  - Challenge not found
  - Challenge not in `initiated` state

### Claude's Discretion
- Success response format and HTTP status codes
- Error response structure details (unified scheme implementation)
- Shadow overseer email generation strategy (random? derived?)
- Shadow overseer password generation (length, complexity)
- Reuse criteria for existing shadow overseers (exact match? partial?)
- Specific error codes within unified scheme
- Validation error message content

</decisions>

<specifics>
## Specific Ideas

- "The overseer sees how the status progresses in the browser" — frontend polling approach
- Status changes from `initiated` → `awaiting-payment` is the signal to transition UI
- No additional preparation endpoints needed — keep it simple
- Authentication flexibility: agents can use whatever method they have available

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 24-agent-confirmation-flow*
*Context gathered: 2026-02-20*
