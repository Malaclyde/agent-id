# Phase 6: Shadow Subscription Research - Executive Findings

**Created:** 2026-02-15
**Phase:** 06-shadow-subscription-research
**Status:** Research Complete

---

## Executive Summary

This document summarizes the key findings from researching Paddle's one-time payment capabilities for shadow subscription handling. The research determines how to query subscription status for customers who pay with one-time payments instead of recurring subscriptions.

---

## Key Findings

### Finding 1: One-Time Payments Have `subscription_id: null`

**Discovery:** Paddle's API returns `subscription_id: null` for one-time payments (non-subscription transactions).

**Implication:** We can use this to distinguish between recurring subscriptions and one-time payments.

**Source:** Paddle API Documentation - List Transactions endpoint

---

### Finding 2: Query Pattern for One-Time Payment Subscription

**API Call:**
```
GET /transactions?customer_id={customer_id}&subscription_id=null&status=completed&order_by=created_at[DESC]&per_page=1
```

**Key Parameters:**
- `subscription_id=null` - Returns transactions NOT related to any subscription
- `status=completed` - Filters out failed/refunded payments
- `order_by=created_at[DESC]` - Gets most recent payment first
- `per_page=1` - Only need the latest payment

**Source:** Paddle API Documentation

---

### Finding 3: Price ID Maps to Tier

**Mechanism:** The `price_id` from `transaction.items[0].price.id` can be passed to the existing `mapPriceIdToTier()` function.

**Implementation:**
```typescript
const priceId = transaction.items?.[0]?.price?.id;
const tier = mapPriceIdToTier(priceId, env);
```

**Note:** This uses the existing infrastructure - no new tier mapping needed.

**Source:** Existing code analysis (`backend/src/services/paddle.ts`)

---

### Finding 4: Tier Display Resolution

**Decision:** Internal SHADOW tier maps to external BASIC permissions

| Aspect | Value |
|--------|-------|
| Internal tier name | SHADOW (for system differentiation) |
| External/API tier name | BASIC (matches user-facing tier) |
| User permissions | Unlimited OAuth sign requests, up to 10 OAuth clients |

This is consistent with how the sanitize function already converts SHADOW to PAID in API responses.

**Source:** CONTEXT.md locked decisions

---

### Finding 5: Same Price ID for Both Payment Types

**Discovery:** The same `PADDLE_PRICE_ID_BASIC` price ID can be used for both:
- Recurring subscription BASIC tier
- One-time payment BASIC tier

**Implication:** No separate Paddle price configuration needed for shadow subscriptions.

**Rationale:** The distinction is in the payment type (subscription vs one-time), not the price.

---

## Implementation Recommendations

### Extend getActiveSubscription()

The existing `getActiveSubscription()` function in `subscription.ts` should be extended:

```typescript
// For shadow overseers with one-time payment
if (isShadow && overseer.paddle_customer_id) {
  const oneTimeSub = await getOneTimePaymentSubscription(
    overseer.paddle_customer_id,
    env
  );

  if (oneTimeSub && oneTimeSub.isValid) {
    return getTierLimits(oneTimeSub.tier);
  }
}
```

### New Function: getOneTimePaymentSubscription()

Create helper to query one-time payment subscription info:

```typescript
async function getOneTimePaymentSubscription(
  customerId: string,
  env: Env
): Promise<{ tier: string; isValid: boolean; paymentDate: Date } | null>
```

### Edge Case Handling

| Edge Case | Handling |
|-----------|----------|
| Multiple one-time payments | Query with `per_page=1` to get most recent |
| Failed/refunded payments | Filter by `status=completed` |
| Payment older than 30 days | Check `created_at`, return invalid if expired |
| Customer later subscribes | Subscription takes priority (has subscription_id) |

---

## Requirements Coverage

| Requirement | Status | Section |
|-------------|--------|---------|
| SHADOW-RESEARCH-01: Paddle one-time payment capabilities | ✅ Complete | One-Time Payment Detection Pattern |
| SHADOW-RESEARCH-02: Paddle returns subscription info for one-time payments | ✅ Complete | Transaction Response Structure |
| SHADOW-RESEARCH-03: Shadow-claimed agents can register clients | ✅ Complete | Agent Capability Mapping |
| SHADOW-RESEARCH-04: Document findings for implementation | ✅ Complete | Code Examples, Recommendations |

---

## Next Steps

This research is complete. Implementation of the one-time payment subscription query is deferred to a future phase.

**Before implementation:**
1. Ensure PADDLE_PRICE_ID_BASIC is configured in wrangler.toml
2. Add `getOneTimePaymentSubscription()` function to paddle.ts
3. Update `getActiveSubscription()` to handle shadow overseers
4. Write unit tests for new functions

---

## References

- Paddle API Documentation: https://developer.paddle.com/api-reference/transactions/list-transactions
- Existing code: `backend/src/services/paddle.ts`
- Research document: `.planning/phases/06-shadow-subscription-research/06-RESEARCH.md`

---

*End of Executive Summary*
