# Phase 22: Shadow Claim in Frontend - Context

**Gathered:** 2026-02-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement frontend UI pages for shadow claim flow. Backend already has `/v1/agents/malice/*` endpoints implemented. Frontend needs:
- Page to initiate shadow claim at `/malice/:agentId`
- Page for payment at `/malice/:agentId/payment/:paymentChallengeId`
- Integration with Paddle for one-time payment checkout

This is purely frontend work. Backend gaps (email format, KV retention) are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Loading State
- Show empty page with loading progress bar labeled "Please wait..." while waiting for backend response on initial POST

### Instructions Display
- Display in human-friendly format (NOT code block)
- Text: "Tell your agent to post this body: {overseerId: [id]} to this callback url: [url] and sign this request with their DPoP JWT"
- Show overseerId and callback URL clearly as styled text

### Payment Display
- DO NOT show "BASIC" tier name
- Show price (e.g., "$19 one-time") and capabilities
- Display: "Your agent will get: X agents, Y clients, Z OAuth registrations per billing period"
- Use actual values from backend or hardcode reasonable defaults

### Button Label
- Button must be labeled exactly "pay" (lowercase)

### Paddle Integration
- Pass custom_data with: { is_shadow_claim: true, agent_id, shadow_overseer_id }

### Payment Success
- Show "Payment successful!" message
- Show "Redirecting to home..." after 3 seconds
- Redirect to / (home page)

### Payment Failure
- Show "Payment failed" message
- Provide "Try Again" button

### Polling Behavior
- Poll every 2 seconds for challenge completion
- Redirect to payment page when status === "completed"

</decisions>

<specifics>
## Specific Flow (User Provided)

1. User visits `/malice/:agentid` (unauthenticated)
2. Frontend POSTs to backend to initiate shadow claim
3. While waiting: show "Please wait..." with loading progress bar
4. Backend returns challenge_id + shadow_overseer_id
5. Display instructions for human to relay to their agent
6. Frontend polls `/v1/agents/claim/status/:challengeId` for completion
7. When challenge complete → redirect to payment page
8. Show one-time payment option (price + capabilities, NOT "BASIC")
9. "pay" button opens Paddle checkout
10. After payment success → redirect to home page

Backend details (already implemented):
- Creates shadow overseer with fake email and random password
- Includes paddle_customer_id in overseer record
- Handles is_shadow_claim flag in webhook

</specifics>

<deferred>
## Deferred Ideas

None — backend implementation is correct as-is.

</deferred>

---

*Phase: 22-shadow-claim-in-frontend*
*Context gathered: 2026-02-18*
