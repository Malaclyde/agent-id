# Phase 14: Extended Subscription Information Display - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Enhance the subscription pane in the frontend to display additional subscription information: billing period end date and renewal status. The "Cancel Subscription" button should change to "Renew Subscription" when appropriate, with proper Paddle checkout flow. Requires research on Paddle's behavior for subscription tier changes.

</domain>

<decisions>
## Implementation Decisions

### Additional subscription data to display
- **Billing period end date** — Show the end date of the current billing period
- **Renewal status** — Show information about whether payment will be renewed

### Button behavior
- **If NOT going to be renewed:** Show "Renew Subscription" button instead of "Cancel Subscription"
- **Renew button action:** Redirect to appropriate Paddle checkout (same subscription tier)
- **If going to be renewed:** Show "Cancel Subscription" button (existing behavior)

### Research needed (REQUIRED before planning)
- **Paddle subscription tier change behavior:** When a customer changes subscription tier (e.g., Basic → Pro) effective next month:
  - Does Paddle return information that current subscription is cancelled AND a new one will begin?
  - Or is this handled in a single subscription object?
  - Will the appropriate tier be displayed?
  - If NOT handled by Paddle: Query logic must detect if customer has purchased another subscription
    - If current subscription set to expire BUT customer purchased another → show "Cancel" (not "Renew")

### UI display logic
- If current subscription is set to expire (canceled at period end) → show "Renew Subscription" button
- If current subscription is active and will renew → show "Cancel Subscription" button
- If current subscription is past_due, trialing, or other state → handle appropriately

</decisions>

<specifics>
## Specific Ideas

- The button text should dynamically change based on renewal status
- "Renew Subscription" should use same Paddle checkout flow as initial subscription
- Need to handle edge case: subscription changed to different tier (should show current tier, not new one)

</specifics>

<deferred>
## Deferred Ideas

- Invoice history display — future phase
- Payment method on file display — future phase
- Usage breakdown by type — future phase
- Historical usage charts — future phase

</deferred>

---

*Phase: 14-extended-subscription-information-display*
*Context gathered: 2026-02-17*
