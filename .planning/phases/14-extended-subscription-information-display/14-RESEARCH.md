# Phase 14: Extended Subscription Information Display - Research

**Phase:** 14-extended-subscription-information-display
**Researcher:** gsd-phase-researcher
**Date:** 2026-02-17

## Research Questions

### 1. Paddle Subscription Tier Change Behavior

**Question:** When a customer changes subscription tier (e.g., Basic → Pro) effective next month, what information does Paddle return?

**Answer:** Paddle handles tier changes within the same subscription object. Key points:
- There's no rigid hierarchy of products in Paddle - tier changes are "replacing items" on the subscription
- When changing tiers, you include the new `price_id` and Paddle manages the transition
- The subscription's `status` remains `active` during the transition
- `current_period_end` continues to show the current billing period end
- The new tier takes effect based on the `proration_billing_mode`:
  - `prorated_immediately` - charge prorated amount now
  - `prorated_next_billing_period` - charge prorated amount on next billing date
  - `do_not_bill` - don't charge for the change

**For this phase:** The current implementation already handles tier changes correctly. The subscription status and tier are correctly returned.

### 2. Cancel-at-Period-End Behavior

**Question:** When a customer cancels their subscription at the end of the billing period, what does the API return?

**Answer:** Key findings:
- When canceling with `effective_from: "next_billing_period"` (the default):
  - Status remains `active` until the effective date
  - A `scheduled_change` object is created with `action: "cancel"` and `effective_at` set to the next billing date
  - `next_billed_at` becomes `null` (no future billing scheduled)
  - `canceled_at` is set when the cancellation takes effect
  
- To determine if a subscription will NOT renew (should show "Renew" button):
  - Check `next_billed_at`: if `null`, no future billing
  - Check `scheduled_change`: if it has a cancellation scheduled, it won't renew

### 3. Required Backend Changes

**Current State:**
- `getSubscriptionsByCustomer()` returns: `id`, `customer_id`, `status`, `tier_id`, `current_period_start`, `current_period_end`, `price_id`
- Missing: `scheduled_change`, `next_billed_at`, `canceled_at`

**Needed for renewal status:**
- Add `scheduled_change` to the Paddle subscription mapping
- Add `next_billed_at` to determine if there will be a future billing
- Add `canceled_at` to know when cancellation took effect

### 4. Frontend Display Logic

Based on the research, here's the recommended display logic:

| Subscription State | Button Text | Display Message |
|-------------------|-------------|-----------------|
| `active` + `next_billed_at` not null | "Cancel Subscription" | "Renews on [date]" |
| `active` + `next_billed_at` is null + has `scheduled_change` = cancel | "Renew Subscription" | "Cancels on [date]" |
| `canceled` | "Renew Subscription" | "Expired on [date]" |
| `past_due` | "Cancel Subscription" | "Payment overdue" |
| `trialing` | "Cancel Subscription" | "Trial ends on [date]" |
| `paused` | "Resume Subscription" | "Paused" |

### 5. Renewal Status Field

Add a new field to the subscription response:

```typescript
interface Subscription {
  // existing fields...
  will_renew: boolean;  // true if next_billed_at is set, false if canceled or no more billing
  scheduled_cancel_at: string | null;  // if cancellation is scheduled
}
```

## Implementation Recommendations

1. **Backend changes needed:**
   - Update `getSubscriptionsByCustomer()` to include `scheduled_change`, `next_billed_at`, and `canceled_at` from Paddle response
   - Add `will_renew` and `scheduled_cancel_at` to the subscription response

2. **Frontend changes needed:**
   - Update Subscription type to include new fields
   - Modify button text logic based on `will_renew`
   - Display appropriate status messages

## Sources

- Paddle Developer Documentation: https://developer.paddle.com/
- Subscription API Reference: https://developer.paddle.com/api-reference/subscriptions/overview
- Cancel Subscription: https://developer.paddle.com/api-reference/subscriptions/cancel-subscription
- Upgrade/Downgrade: https://developer.paddle.com/build/subscriptions/replace-products-prices-upgrade-downgrade

