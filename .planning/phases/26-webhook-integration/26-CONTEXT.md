# Phase 26: Webhook Integration - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the `transaction.completed` Paddle webhook handler for shadow claims. Extract custom data, verify challenge state, create or reuse shadow overseer, manage active oversight relationships, and update KV challenge status.

</domain>

<decisions>
## Implementation Decisions

### Idempotency & Duplicate Events
- Check KV challenge status when handling the webhook.
- If the event was already processed (e.g., status is already `completed`), silently return 200 to Paddle to acknowledge receipt.

### Expired Challenges (Late Payments)
- If the payment arrives after the challenge TTL has expired:
  - Check if the agent has already been claimed (e.g., by a real overseer or another shadow overseer in the meantime).
  - If the agent is *not* claimed, proceed to create and activate the shadow oversight anyway.

### Deactivation Behavior
- When ensuring only one active oversight exists for the agent, deactivate the older ones by setting their `active` flag to `false` (do not hard-delete).

### Claude's Discretion
- Audit logging detail and format (e.g., logging shadow claim creations or renewals to console or DB).
- Handling the edge case where a late payment arrives but the agent IS already claimed (e.g., skip activation, log a warning, and return 200 since refunds are a v2.1 feature).

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

- Shadow claim refunds for conflicts or late payments (already deferred to v2.1 per roadmap).

</deferred>

---

*Phase: 26-webhook-integration*
*Context gathered: 2026-02-20*
