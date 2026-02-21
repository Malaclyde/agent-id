# Phase 6: Shadow Subscription Research - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Research Paddle's capabilities to determine how one-time basic tier payments can be queried for agent subscription status. The output is a research document with findings and implementation recommendations for future implementation. This is NOT implementing the feature — just researching how it would work.

</domain>

<decisions>
## Implementation Decisions

### Shadow subscription definition
- "Shadow subscription" = one-time payment for BASIC tier
- No "shadow" subscription tier exists in Paddle
- Standard basic subscription via one-time payment (not recurring)
- Shadow overseers are the only entities that can perform one-time payments
- One-time payments are permanent — cannot upgrade to monthly or change tiers

### Research scope
- Primary deliverable: Decision document + technical analysis with code examples/pseudocode
- Output format: Markdown document with findings + recommendations
- Paddle API endpoints: Claude's discretion (focus on customer and transaction APIs)
- Include implementation recommendations with specific API calls and response handling

### Edge cases to research
- Multiple one-time payments by same customer
- Expired subscriptions (one-time doesn't expire the same way)
- Failed/refunded payments
- What subscription_id looks like for one-time vs recurring
- What happens if customer makes one-time payment, then later subscribes (edge case - should never happen but document anyway)

### Agent capability mapping (from existing docs)
- Shadow-claimed agents have BASIC tier
- Unlimited OAuth sign requests
- Up to 10 OAuth clients
- This is already documented — research should verify API can return this tier info

### Constraints
- Must work with existing Paddle integration (no migration)
- Must support both one-time and subscription for BASIC tier
- Target timeframe: Undetermined

### Claude's Discretion
- Which specific Paddle API endpoints to research in detail
- Exact edge cases beyond those listed
- Code example implementation approach

</decisions>

<specifics>
## Specific Ideas

- **Key research question:** For customers who make a one-time payment (vs monthly subscription), do they get a subscription_id? Can we use this ID to query their subscription tier using the same endpoint as recurring subscribers?
- **Paddle API questions:** Does Paddle return subscription info (active status, expiration) for one-time payment customers using the same API endpoints?
- **Known:** Shadow overseers can only do one-time payments — they cannot upgrade or switch to monthly billing

</specifics>

<deferred>
## Deferred Ideas

- Implementation of the one-time payment subscription query — this is research only
- Any changes to existing Paddle integration — research documents how it should work, implementation is future work

</deferred>

---

*Phase: 06-shadow-subscription-research*
*Context gathered: 2026-02-15*
