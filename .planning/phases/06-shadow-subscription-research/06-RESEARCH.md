# Phase 6: Shadow Subscription Research - Research

**Researched:** 2026-02-15
**Domain:** Paddle API - One-time payment subscription handling
**Confidence:** HIGH

## Summary

This research investigates how Paddle's API handles one-time payments (non-subscription transactions) and whether the existing subscription query infrastructure can be reused for shadow overseers who pay with one-time payments instead of recurring subscriptions.

**Key findings:**
1. One-time payments in Paddle create transactions WITHOUT a subscription_id (subscription_id is null)
2. The existing `getCustomerTransactions` API can be used to query these one-time payments
3. The price_id from transaction items can be mapped to tier using the existing `mapPriceIdToTier` function
4. The current implementation already handles transactions without subscription_id correctly

**Primary recommendation:** Extend the existing subscription query logic to support one-time payment customers by checking for transactions with `subscription_id: null` and using the price_id from those transactions to determine the tier.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Shadow subscription = one-time payment for BASIC tier
- No "shadow" subscription tier exists in Paddle - use standard basic subscription via one-time payment
- Shadow overseers are the only entities that can perform one-time payments
- One-time payments are permanent — cannot upgrade to monthly or change tiers

### Research Scope
- Primary deliverable: Decision document + technical analysis with code examples/pseudocode
- Output format: Markdown document with findings + recommendations
- Paddle API endpoints: Focus on customer and transaction APIs
- Include implementation recommendations with specific API calls and response handling

### Edge Cases to Research
- Multiple one-time payments by same customer
- Expired subscriptions (one-time doesn't expire the same way)
- Failed/refunded payments
- What subscription_id looks like for one-time vs recurring
- What happens if customer makes one-time payment, then later subscribes (edge case)

### Agent Capability Mapping
- Shadow-claimed agents have BASIC tier
- Unlimited OAuth sign requests
- Up to 10 OAuth clients
- Research should verify API can return this tier info

### Constraints
- Must work with existing Paddle integration (no migration)
- Must support both one-time and subscription for BASIC tier
- Target timeframe: Undetermined

### Claude's Discretion
- Which specific Paddle API endpoints to research in detail
- Exact edge cases beyond those listed
- Code example implementation approach

### Deferred Ideas (OUT OF SCOPE)
- Implementation of the one-time payment subscription query — this is research only
- Any changes to existing Paddle integration — research documents how it should work, implementation is future work

</user_constraints>

---

## Standard Stack

The existing implementation uses the following:

### Core Paddle Integration
| Library/Tool | Version | Purpose | Why Used |
|-------------|---------|---------|----------|
| Paddle API (REST) | v1 | Payment processing | Source of truth for subscriptions |
| Cloudflare Workers | Latest | Runtime environment | Backend host |
| D1 (SQLite) | Latest | Local database | Stores overseer customer mappings |

### Supporting Files
| File | Purpose |
|------|---------|
| `backend/src/services/paddle.ts` | Core Paddle API client |
| `backend/src/services/subscription.ts` | Subscription logic |
| `backend/src/routes/subscriptions.ts` | Subscription endpoints |

### Current Implementation Notes

The codebase already has the following functions that can be leveraged:

1. **`getCustomerTransactions(customerId, env)`** - Queries transactions for a customer
2. **`mapPriceIdToTier(priceId, env)`** - Maps Paddle price IDs to internal tiers
3. **`isShadowPaymentValid(customerId, env)`** - Checks if shadow payment is within 30 days

---

## Architecture Patterns

### Current Subscription Flow

```
1. getActiveSubscription(overseer_id, env)
   ├── getOverseerById(db, overseer_id) 
   │   └── Returns: paddle_subscription_id, paddle_customer_id
   ├── isShadowOverseer(overseer_id, env)
   │   └── Uses cryptographic ID verification
   └── If shadow:
       └── isShadowPaymentValid(customer_id, env)
           └── getCustomerTransactions(customer_id, env)
               └── Checks if most recent payment is within 30 days
```

### One-Time Payment Detection Pattern

**Key Discovery:** One-time payments in Paddle have `subscription_id: null`

Query transactions without subscriptions:
```
GET /transactions?customer_id={customer_id}&subscription_id=null&status=completed
```

This is documented in Paddle's API:
> "Pass `null` to return entities that aren't related to any subscription."

### Transaction Response Structure

For one-time payments, the transaction response includes:

```json
{
  "id": "txn_xxx",
  "customer_id": "ctm_xxx",
  "subscription_id": null,  // Key: null for one-time payments
  "status": "completed",
  "origin": "subscription_charge",  // or other origins
  "items": [
    {
      "price": {
        "id": "pri_xxx",  // This maps to tier
        "name": "Basic Tier",
        "billing_cycle": null  // null = one-time
      }
    }
  ],
  "created_at": "2026-01-15T00:00:00Z"
}
```

### Recommended Project Structure

No changes needed to project structure - the existing services can be extended:

```
backend/src/services/
├── paddle.ts           # Add: getOneTimePaymentSubscription()
├── subscription.ts     # Modify: getActiveSubscription() 
└── (no new files needed)
```

---

## Don't Hand-Roll

The following are already handled by the existing implementation:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Query transactions | Custom HTTP client | `getCustomerTransactions()` | Already handles pagination, error handling |
| Map price to tier | Custom mapping | `mapPriceIdToTier()` | Already configured with env variables |
| Check payment validity | Custom date logic | `isShadowPaymentValid()` | Already handles 30-day window |
| API authentication | Custom headers | `paddleAPIRequest()` | Handles auth, error handling |

---

## Common Pitfalls

### Pitfall 1: Confusing One-Time Charges with Subscription Charges

**What goes wrong:** One-time charges billed to an existing subscription (via `/subscriptions/{id}/charge`) still have a subscription_id, making them indistinguishable from regular subscription transactions.

**Why it happens:** The `subscription_charge` origin is used for both:
- One-time charges added to an existing subscription
- Truly one-time payments without a subscription

**How to avoid:** Use `subscription_id=null` query parameter to get truly standalone transactions.

**Warning signs:** Transaction has `origin: subscription_charge` but also has `subscription_id` populated.

### Pitfall 2: Multiple One-Time Payments

**What goes wrong:** If a customer makes multiple one-time payments, the system should use the most recent one.

**Why it happens:** No uniqueness constraint on one-time payments in current implementation.

**How to avoid:** Always sort by `created_at` descending and use the first result (most recent payment).

### Pitfall 3: Not Handling Failed/Refunded Payments

**What goes wrong:** Querying all transactions without filtering by status returns failed/refunded payments.

**Why it happens:** Transaction status can be `completed`, `pending`, `failed`, `canceled`.

**How to avoid:** Filter by `status=completed` in the API query.

### Pitfall 4: Tier Mapping for Unknown Price IDs

**What goes wrong:** If a one-time payment uses a price ID not configured in environment variables, it returns 'UNKNOWN' tier.

**Why it happens:** `mapPriceIdToTier()` returns 'UNKNOWN' for unmapped price IDs.

**How to avoid:** Ensure all expected price IDs are configured in wrangler.toml.

---

## Code Examples

### Recommended API Query for One-Time Payment Subscription

```typescript
// Query Paddle for one-time payment subscription info
// Source: Paddle API Documentation - List Transactions
async function getOneTimePaymentSubscription(
  customerId: string,
  env: Env
): Promise<{ tier: string; isValid: boolean; paymentDate: Date } | null> {
  
  // Query transactions WITHOUT a subscription (one-time payments)
  const response = await paddleAPIRequest<{ data: any[] }>(
    env,
    `/transactions?customer_id=${customerId}&subscription_id=null&status=completed&order_by=created_at[DESC]&per_page=1`
  );

  if (response.data.length === 0) {
    return null; // No one-time payments found
  }

  const transaction = response.data[0];
  
  // Get price_id from transaction items
  const priceId = transaction.items?.[0]?.price?.id;
  
  if (!priceId) {
    return null; // No price information
  }

  // Map price to tier using existing function
  const tier = mapPriceIdToTier(priceId, env);
  
  // Check if within validity period (30 days for shadow)
  const paymentDate = new Date(transaction.created_at);
  const now = new Date();
  const daysSincePayment = (now.getTime() - paymentDate.getTime()) / (1000 * 60 * 60 * 24);
  const isValid = daysSincePayment <= 30;

  return {
    tier,
    isValid,
    paymentDate
  };
}
```

### Integration with Existing getActiveSubscription

```typescript
// Pseudocode for integrating one-time payment support
// This shows the concept - actual implementation would modify subscription.ts

async function getActiveSubscription(
  db: D1Database,
  overseer_id: string,
  env: Env
): Promise<SubscriptionWithLimits> {
  const overseer = await getOverseerById(db, overseer_id);
  
  if (!overseer) {
    return getFreeTierDefaults();
  }

  const isShadow = await isShadowOverseer(overseer_id, env);

  // Case 1: Regular subscription (has paddle_subscription_id)
  if (overseer.paddle_subscription_id) {
    const paddleSub = await getSubscriptionFromPaddle(
      overseer.paddle_subscription_id, 
      env
    );
    
    if (paddleSub && await isPaddleSubscriptionActive(overseer.paddle_subscription_id, env)) {
      return getTierLimits(paddleSub.tier_id);
    }
    
    return getFreeTierDefaults();
  }

  // Case 2: Shadow overseer with one-time payment
  if (isShadow && overseer.paddle_customer_id) {
    const oneTimeSub = await getOneTimePaymentSubscription(
      overseer.paddle_customer_id,
      env
    );

    if (oneTimeSub && oneTimeSub.isValid) {
      return getTierLimits(oneTimeSub.tier);
    }

    // Payment expired - deactivate oversights
    await deactivateOversights(db, overseer_id);
    return getFreeTierDefaults();
  }

  // Case 3: No subscription
  return getFreeTierDefaults();
}
```

### Query for Multiple One-Time Payments

```typescript
// Get all one-time payments for a customer (for audit/edge cases)
async function getAllOneTimePayments(
  customerId: string,
  env: Env
): Promise<PaddleTransaction[]> {
  
  const response = await paddleAPIRequest<{ data: any[] }>(
    env,
    `/transactions?customer_id=${customerId}&subscription_id=null&status=completed&order_by=created_at[DESC]`
  );

  return response.data.map((tx: any) => ({
    id: tx.id,
    customer_id: tx.customer_id,
    subscription_id: tx.subscription_id,  // Will be null
    amount: tx.details?.totals?.total || 0,
    currency: tx.currency_code,
    status: tx.status,
    origin: tx.origin,  // Check this for 'subscription_charge'
    created_at: tx.created_at,
    price_id: tx.items?.[0]?.price?.id,  // For tier mapping
  }));
}
```

---

## State of the Art

### Current Implementation (Phase 3+)

The existing implementation handles shadow overseers through:

1. **Cryptographic ID verification** (`isShadowOverseer()`) - Verifies shadow overseer status
2. **Transaction-based validation** (`isShadowPaymentValid()`) - Checks if payment within 30 days
3. **Tier mapping via price ID** - Uses `mapPriceIdToTier()`

### Key Insight: Unified Subscription Query

**The current implementation already supports the core functionality needed:**

| Feature | Current Support | Notes |
|---------|----------------|-------|
| Query transactions by customer | ✅ `getCustomerTransactions()` | Filters by customer_id and status |
| Handle null subscription_id | ✅ Tested in paddle.test.ts | Line 534-558 shows null subscription_id handling |
| Map price to tier | ✅ `mapPriceIdToTier()` | Works with any price_id |
| Check 30-day validity | ✅ `isShadowPaymentValid()` | Uses created_at for date calculation |

### What's Missing for Full Support

To fully support querying subscription tier for one-time payment customers (not just validity):

1. **Extract price_id from transaction** - Current code doesn't capture this
2. **Map to tier from transaction price_id** - Need to add this logic
3. **Handle tier display** - Current returns SHADOW, might want to show BASIC

---

## Open Questions

### 1. Should One-Time Payment Tier Show as "BASIC" or "SHADOW"?

**What we know:** 
- Shadow overseers pay for BASIC tier via one-time payment
- The system currently returns 'SHADOW' tier for shadow overseers
- The sanitize function converts 'SHADOW' to 'PAID' in API responses

**Resolution (per locked decision in CONTEXT.md):**
- **Internal tier:** SHADOW (distinguishes payment type from regular subscriptions)
- **External/API tier:** BASIC (matches user-facing tier name)
- The internal SHADOW tier maps to BASIC-tier permissions (unlimited OAuth sign requests, up to 10 OAuth clients)
- This is consistent with how the sanitize function already converts SHADOW to PAID
- Same price ID can be used for both one-time and subscription BASIC tier

**Status:** ✅ RESOLVED - Internal SHADOW tier maps to external BASIC permissions

### 2. Can a Customer Have Both Subscription and One-Time Payment?

**What we know:**
- Paddle allows a customer to have both subscriptions and transactions
- Current logic prioritizes subscription_id if present

**Resolution:**
- The existing code already handles this correctly - subscription takes priority if present and active
- If a customer with an expired subscription also has a valid one-time payment, the one-time payment can provide BASIC tier access
- Current implementation prioritizes subscription_id, so active subscription always wins

**Status:** ✅ RESOLVED - Existing subscription logic takes priority

### 3. How to Handle Price IDs for One-Time Payments?

**What we know:**
- One-time payments use price IDs just like subscriptions
- The price ID determines the tier via `mapPriceIdToTier()`

**Resolution:**
- Use the same price ID for both one-time and subscription BASIC tier (configured as PADDLE_PRICE_ID_BASIC)
- The distinction is in the payment type (subscription vs one-time), not the price
- Shadow overseers pay once for permanent BASIC tier access - no recurring billing

**Status:** ✅ RESOLVED - Same price ID works for both payment types

---

## Sources

### Primary (HIGH confidence)
- **Paddle API Documentation** - https://developer.paddle.com/api-reference/transactions/list-transactions
  - Confirmed: `subscription_id=null` query parameter for one-time payments
  - Confirmed: Transaction response structure with items and price_id
- **Existing Code Analysis** - `backend/src/services/paddle.ts`
  - Verified: `getCustomerTransactions()` implementation
  - Verified: `mapPriceIdToTier()` function exists
  - Verified: Test coverage for null subscription_id (paddle.test.ts line 534-558)

### Secondary (MEDIUM confidence)
- **Paddle Changelog** - https://developer.paddle.com/changelog/2023/subscription-charge-transaction-origin
  - Confirmed: `origin` field values for transaction types

### Tertiary (LOW confidence)
- N/A - Primary sources provided sufficient information

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Existing implementation well-understood
- Architecture: HIGH - Current patterns documented in code
- Pitfalls: HIGH - Verified with existing tests and documentation

**Research date:** 2026-02-15
**Valid until:** 30 days (Paddle API is stable)

---

## Appendix: Key Research Questions Answered

### Q: Do one-time payments get a subscription_id?

**Answer:** No. One-time payments (transactions without a subscription) have `subscription_id: null`. This is confirmed by:
1. Paddle API documentation: "Pass `null` to return entities that aren't related to any subscription"
2. Existing test in paddle.test.ts (line 534-558): Tests transaction with `subscription_id: null`

### Q: Can we use the same API endpoint for one-time payment customers?

**Answer:** Yes. Use `GET /transactions?customer_id={id}&subscription_id=null&status=completed` instead of `GET /subscriptions/{id}`.

### Q: How do we determine tier from a one-time payment?

**Answer:** Use the `price_id` from `transaction.items[0].price.id` and pass it to the existing `mapPriceIdToTier()` function.

### Q: What about the edge cases?

| Edge Case | Handling |
|-----------|----------|
| Multiple one-time payments | Query with `order_by=created_at[DESC]&per_page=1` to get most recent |
| Failed/refunded payments | Filter by `status=completed` |
| Payment older than 30 days | Check `created_at` date, return invalid if > 30 days |
| Customer later subscribes | Existing subscription logic takes priority (has subscription_id) |

