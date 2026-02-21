# Phase 3: Paddle Integration Fix - Research

**Researched:** 2026-02-15
**Domain:** Paddle payment integration (webhooks, subscriptions, checkout)
**Confidence:** HIGH

## Summary

This phase requires fixing critical Paddle payment integration bugs. The research covers webhook signature verification, checkout custom data handling, /me endpoint fixes, and subscription data synchronization. Key findings:

1. **Webhook signature**: Current manual HMAC implementation is correct per Paddle docs, but header format may need adjustment (`h1` vs `v1`)
2. **Official SDK**: `@paddle/paddle-node-sdk` doesn't provide direct webhook verification - manual verification is still required (or use community package)
3. **Checkout customData**: Frontend already passes `overseer_id` correctly; backend passes it in upgrade endpoint
4. **/me endpoint**: Currently falls back to FREE tier when no local subscription exists, needs to query Paddle directly
5. **Test framework**: Project uses Vitest (already configured)

**Primary recommendation:** Install `@paddle/paddle-node-sdk` for API calls, but keep manual webhook verification (or use `paddle-billing` community package for easier verification). Fix /me endpoint to query Paddle customer API directly.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Always respond HTTP 200 to all valid Paddle requests (even unhandled events)
- Handle only events necessary for our subscription flows
- Log unhandled events for future reference
- Must perform signature validation on all webhook requests
- Paddle is the single source of truth
- No local DB caching for subscription data
- /me endpoint must query Paddle customer API directly
- Pass `overseer_id` as custom data in all Paddle checkout requests
- Frontend: Show toast notification to user on errors
- Backend: Log all errors for debugging
- Never fail silently — errors must be visible

### Claude's Discretion
- Specific Paddle SDK methods to use for signature validation
- Exact webhook event types to handle (subscription_created, subscription_updated, subscription_cancelled, etc.)
- Test framework selection (Vitest, Jest, etc.)
- Exact test coverage targets

### Deferred Ideas (OUT OF SCOPE)
None
</user_constraints>

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@paddle/paddle-node-sdk` | ^1.7.0 | Paddle API client for Node.js | Official SDK from Paddle |
| `vitest` | ^4.0.18 | Testing framework | Already configured in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `paddle-billing` | latest | Webhook parsing/verification | Alternative to manual signature verification |
| `@types/node` | ^22.x | TypeScript types | For Node.js-specific types in tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@paddle/paddle-node-sdk` | Manual fetch calls | SDK provides TypeScript types and convenience methods |
| Manual webhook verification | `paddle-billing` package | Community package simplifies verification but adds dependency |
| Vitest | Jest | Vitest already configured; switch would require rework |

**Installation:**
```bash
npm install @paddle/paddle-node-sdk
```

## Architecture Patterns

### Recommended Project Structure
```
backend/
├── src/
│   ├── services/
│   │   ├── paddle.ts           # Paddle API calls (existing)
│   │   └── webhook-handler.ts  # Webhook event handlers (existing)
│   ├── routes/
│   │   ├── webhooks.ts         # Webhook endpoints (existing)
│   │   └── subscriptions.ts    # /me endpoint (needs fix)
│   └── redacted/
│       └── webhook-security.ts  # Signature verification (keep or replace)
```

### Pattern 1: Webhook Signature Verification
**What:** Verify incoming Paddle webhooks using HMAC-SHA256
**When to use:** Every incoming webhook request
**Example:**
```typescript
// Current manual approach (works correctly per Paddle docs)
// Source: https://developer.paddle.com/webhooks/signature-verification
import crypto from 'crypto';

function verifyPaddleSignature(payload: string, signature: string, secret: string): boolean {
  // Parse header: "ts=1234567890;h1=abc123..."
  const parts = signature.split(';');
  const timestamp = parts.find(p => p.startsWith('ts='))?.substring(3);
  const receivedSig = parts.find(p => p.startsWith('h1='))?.substring(3);
  
  // Build signed payload: timestamp + '.' + payload
  const signedPayload = `${timestamp}.${payload}`;
  
  // Compute HMAC-SHA256
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');
  
  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(receivedSig),
    Buffer.from(expectedSig)
  );
}
```

### Pattern 2: Checkout Custom Data
**What:** Pass overseer_id in Paddle checkout customData
**When to use:** When initiating subscription upgrades
**Example:**
```typescript
// Frontend (SubscriptionManagement.tsx) - already correct
(window as any).Paddle.Checkout.open({
  items: [{ priceId: response.price_id, quantity: 1 }],
  customData: {
    tier: tier,
    overseer_id: user.id  // This links webhook to overseer
  }
});

// Backend (subscriptions.ts upgrade endpoint) - already correct
return c.json({
  customData: { overseer_id: overseerId }
});
```

### Pattern 3: /me Endpoint Querying Paddle
**What:** Query Paddle customer API directly instead of relying on local DB
**When to use:** In GET /api/subscriptions/me endpoint
**Example:**
```typescript
// Fix: Query Paddle directly even if no local subscription exists
subscriptions.get('/me', async (c) => {
  const overseerId = c.get('overseerId');
  const overseer = await getOverseerById(c.env.DB, overseerId);
  
  // If no paddle_customer_id, return FREE tier
  if (!overseer?.paddle_customer_id) {
    return c.json({ success: true, subscription: getFreeTierDefaults() });
  }
  
  // Query Paddle customer API directly
  const paddleCustomer = await getPaddleCustomer(overseer.paddle_customer_id, c.env);
  
  // If has subscription_id, query subscription details
  if (overseer.paddle_subscription_id) {
    const subscription = await getSubscriptionFromPaddle(
      overseer.paddle_subscription_id, 
      c.env
    );
    // ... return subscription info
  }
  
  return c.json({ success: true, subscription: getFreeTierDefaults() });
});
```

### Anti-Patterns to Avoid
- **Returning FREE tier silently when Paddle has data:** If overseer has `paddle_customer_id` but no local subscription record, query Paddle to see if there's active subscription (webhook may have failed)
- **Hardcoding webhook secret:** Always read from environment variable `PADDLE_WEBHOOK_SECRET`
- **Not handling all event types:** Paddle may send events you're not expecting; always return 200 OK

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Webhook signature verification | Custom HMAC implementation | Keep current implementation (it's correct) OR use `paddle-billing` package | Current manual approach is correct per Paddle docs; no need to add dependency |
| Paddle API calls | fetch() wrappers | `@paddle/paddle-node-sdk` | SDK provides TypeScript types and convenience methods |
| Test setup | Jest configuration | Vitest (already configured) | Project already uses Vitest |

**Key insight:** The current manual webhook signature verification is actually correct according to Paddle's official documentation. The issue might be:
1. Header name format (though HTTP headers are case-insensitive)
2. Signature key name (`h1` vs `v1` - current code uses `v1` but Paddle docs show `h1`)
3. Timestamp tolerance (current 5 minutes is fine)

## Common Pitfalls

### Pitfall 1: Wrong Signature Header Key
**What goes wrong:** Webhook verification fails because code looks for `v1=` but Paddle sends `h1=`
**Why it happens:** Paddle updated their signature format; older implementations used `v1`
**How to avoid:** Check the actual signature header format from Paddle (use `h1=` in parsing)
**Warning signs:** "Invalid Paddle signature" errors in logs

### Pitfall 2: Body Parsing Before Verification
**What goes wrong:** JSON.parse() or express.json() transforms the body, breaking signature verification
**Why it happens:** Signature is computed on raw body; any transformation changes the hash
**How to avoid:** Verify signature BEFORE parsing JSON; use raw body for HMAC computation
**Warning signs:** Intermittent signature failures

### Pitfall 3: /me Returns Wrong Data When Webhooks Fail
**What goes wrong:** If webhook processing fails, local DB has no subscription record, /me returns FREE tier even though Paddle has active subscription
**Why it happens:** Webhook failures leave gaps in local data; /me doesn't query Paddle as fallback
**How to avoid:** /me should always query Paddle as source of truth, not just local DB
**Warning signs:** Users with active subscriptions see FREE tier limits

### Pitfall 4: Not Handling All Paddle Event Types
**What goes wrong:** Paddle sends events not handled, returns error, Paddle retries indefinitely
**Why it happens:** Unhandled event types cause 500 errors
**How to avoid:** Always return 200 OK for valid requests; log but don't error on unknown events
**Warning signs:** Repeated webhook deliveries for same event

## Code Examples

Verified patterns from official sources:

### Paddle Webhook Signature Verification (Manual)
```typescript
// Source: https://developer.paddle.com/webhooks/signature-verification
import crypto from 'crypto';

export async function verifyPaddleSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  // Parse signature header: "ts=1234567890;h1=abc123..."
  const parts = signature.split(';');
  const tsPart = parts.find(p => p.startsWith('ts='));
  const h1Part = parts.find(p => p.startsWith('h1='));
  
  if (!tsPart || !h1Part) return false;
  
  const timestamp = tsPart.substring(3);
  const receivedSignature = h1Part.substring(3);
  
  // Check timestamp tolerance (5 minutes)
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - parseInt(timestamp)) > 300) return false;
  
  // Build signed payload: timestamp.payload
  const signedPayload = `${timestamp}.${payload}`;
  
  // Compute HMAC-SHA256
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(signedPayload, 'utf8')
    .digest('hex');
  
  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(receivedSignature, 'hex'),
    Buffer.from(expectedSignature, 'hex')
  );
}
```

### Initialize Paddle Node.js SDK
```typescript
// Source: https://www.npmjs.com/package/@paddle/paddle-node-sdk
import { Paddle } from '@paddle/paddle-node-sdk';

const paddle = new Paddle(process.env.PADDLE_API_KEY, {
  environment: process.env.NODE_ENV === 'production' ? 'production' : 'sandbox'
});
```

### Paddle Webhook Events to Handle
```typescript
// Source: https://developer.paddle.com/webhooks/overview
const SUBSCRIPTION_EVENTS = [
  'subscription.created',    // New subscription
  'subscription.activated',  // Subscription is now active
  'subscription.updated',    // Tier change, etc.
  'subscription.paused',     // Subscription paused
  'subscription.resumed',    // Subscription resumed
  'subscription.canceled',   // Subscription cancelled
  'subscription.trialing',   // Trial started
  'subscription.past_due',   // Payment failed
];

const TRANSACTION_EVENTS = [
  'transaction.completed',   // One-time payment succeeded
  'transaction.billed',      // Transaction billed
  'transaction.canceled',    // Transaction canceled
];

const CUSTOMER_EVENTS = [
  'customer.created',        // New customer
  'customer.updated',        // Customer updated
];
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual webhook verification | Manual (still correct) | N/A | Current implementation is valid |
| Local DB as cache | Paddle as single source | Phase 3 | /me must query Paddle directly |
| header `v1=` | header `h1=` | Paddle update | May need to update parsing |
| Test framework TBD | Vitest | Already configured | No change needed |

**Deprecated/outdated:**
- `p_signature` (Paddle Classic): Replaced by `Paddle-Signature` header with `h1` key
- Legacy Paddle.js events: Replaced by Paddle Billing webhooks

## Open Questions

1. **Which signature key format is Paddle sending?**
   - What we know: Current code parses `v1=`, but docs show `h1=`
   - What's unclear: Whether Paddle uses `v1` or `h1` (or both)
   - Recommendation: Add logging to see actual header format, support both

2. **Does the sandbox use different signature format?**
   - What we know: Sandbox and production should work the same
   - What's unclear: If testing in sandbox shows different format
   - Recommendation: Test with sandbox webhooks to verify

3. **What test coverage targets?**
   - What we know: Phase 4 will implement tests
   - What's unclear: Specific percentage or key scenarios
   - Recommendation: Target webhook handlers, /me endpoint, and checkout flow

## Sources

### Primary (HIGH confidence)
- Paddle Developer Documentation - https://developer.paddle.com/webhooks/signature-verification
- Paddle Node.js SDK npm - https://www.npmjs.com/package/@paddle/paddle-node-sdk
- Paddle Webhooks Overview - https://developer.paddle.com/webhooks/overview

### Secondary (MEDIUM confidence)
- Hookdeck Paddle Webhook Guide - https://hookdeck.com/webhooks/platforms/how-to-secure-and-verify-paddle-webhooks-with-hookdeck
- Community paddle-billing package - https://github.com/kossnocorp/paddle-billing

### Tertiary (LOW confidence)
- Various blog posts on Paddle integration (not verified against official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Official Paddle SDK and Vitest are well-documented
- Architecture: HIGH - Patterns match Paddle official documentation
- Pitfalls: HIGH - Common issues identified from Paddle docs and community discussions

**Research date:** 2026-02-15
**Valid until:** 90 days (Paddle API is stable, but check for updates)
