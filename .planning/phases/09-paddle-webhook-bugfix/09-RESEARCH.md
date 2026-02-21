# Phase 9: Paddle Webhook Bugfix - Research

**Researched:** 2026-02-16
**Domain:** Paddle webhook security, event handling, and reliability
**Confidence:** HIGH

## Summary

This phase focuses on fixing critical Paddle webhook integration bugs identified during code review and testing. The research has uncovered several significant issues:

1. **Incorrect event name spelling**: Code uses `subscription.cancelled` (double 'L') but Paddle's official event is `subscription.canceled` (single 'L')
2. **Wrong signature delimiter**: Current implementation uses period `.` between timestamp and payload, but Paddle specification requires colon `:`
3. **Fake Paddle event**: `payment.shadow_claim_succeeded` is not a real Paddle webhook event type
4. **Unused nonce checking**: `checkPaddleNonce()` function exists but is never called
5. **Debug logging in production**: Lines 333-337 of webhook-security.ts contain debug logging
6. **Unhandled subscription events**: paused, resumed, trialing, past_due events are logged but not processed

The signature verification logic in `webhook-security.ts` has a critical bug that causes all webhooks to fail signature validation - it uses `.` instead of `:` in the signed payload construction.

**Primary recommendation:** Fix the signature delimiter bug first (highest priority), then address the spelling error for `subscription.canceled`, remove the fake `payment.shadow_claim_succeeded` event handler, implement nonce checking, and remove debug logging.


## Current Implementation State

### Files Involved
- `backend/src/routes/webhooks.ts` - Webhook route handler (168 lines)
- `backend/src/services/webhook-handler.ts` - Event handlers (444 lines)
- `backend/src/redacted/webhook-security.ts` - Signature verification (418 lines)

### Known Issues Summary

| Issue | File | Line | Severity | Impact |
|--------|-------|-------|----------|
| Wrong signature delimiter | webhook-security.ts | 354 | **CRITICAL** - All webhooks fail verification |
| Wrong event name (cancelled vs canceled) | webhooks.ts | 126 | **CRITICAL** - Cancellation events never handled |
| Fake Paddle event | webhooks.ts | 138 | **HIGH** - Shadow claims broken |
| Debug logging | webhook-security.ts | 333-337 | **LOW** - Logs sensitive info |
| Unused nonce check | webhooks.ts | - | **MEDIUM** - Replay attack vulnerability |
| TODO: use paddle middleware | webhooks.ts | 29 | **LOW** - Code debt |
| Unhandled events | webhooks.ts | 131-136 | **MEDIUM** - No action on paused/resumed/past_due/trialing |

### Detailed Analysis

#### 1. Signature Delimiter Bug (CRITICAL)

**Location:** `backend/src/redacted/webhook-security.ts:354`

**Current Code:**
```typescript
const dataToSign = `${timestamp}.${payload}`;
```

**Paddle Specification (from official docs):**
```
Paddle creates a signature by first concatenating timestamp (ts) with the body of the request, joined with a colon (:).
```

**Expected Code:**
```typescript
const dataToSign = `${timestamp}:${payload}`;
```

**Impact:** ALL webhooks fail signature validation because the expected signature doesn't match what Paddle sends.

**Evidence:** Phase 3 research confirmed manual verification is needed and documented correct format with `:`

#### 2. Event Name Spelling Error (CRITICAL)

**Location:** `backend/src/routes/webhooks.ts:126`

**Current Code:**
```typescript
case 'subscription.cancelled':
```

**Paddle Official Event Name:**
```
subscription.canceled
```

**Impact:** Cancellation webhooks are never handled; they fall through to the default case and are only logged.

**Evidence:** Paddle documentation at https://developer.paddle.com/webhooks/subscriptions/subscription-canceled shows `subscription.canceled` (single 'L')

**Affected Files (all need updating):**
- `backend/src/routes/webhooks.ts` - Line 126
- `docs/v1/endpoints/webhooks.md` - Multiple occurrences
- `docs/v1/endpoints/subscriptions.md` - Multiple occurrences
- `docs/v1/test scenarios/subscription.md` - Multiple occurrences
- `docs/v1/requirements/overseer/user-stories.md` - Multiple occurrences

#### 3. Fake Paddle Event (HIGH)

**Location:** `backend/src/routes/webhooks.ts:138-141`

**Current Code:**
```typescript
case 'payment.shadow_claim_succeeded':
  // Custom event for shadow claims
  await handleShadowClaimPayment(eventData, c.env.DB, c.env);
  break;
```

**Issue:** `payment.shadow_claim_succeeded` is NOT a real Paddle event type.

**Actual Paddle Event Types (from official docs):**
- `transaction.created`
- `transaction.updated`
- `transaction.completed`
- `subscription.created`
- `subscription.past_due`
- `subscription.canceled`

**Evidence:** Paddle webhook overview shows NO `payment.shadow_claim_succeeded` event. This is a custom/imagined event type.

**Impact:** Shadow subscription payments will never be processed correctly. This breaks the shadow claim feature entirely.

**Real Fix Needed:** Shadow claims should use one of these approaches:
1. Use `transaction.completed` with custom_data containing agent_id
2. Use `subscription.created` for one-time subscriptions
3. Handle manually via payment completion callback

#### 4. Unused Nonce Checking (MEDIUM)

**Location:** `backend/src/redacted/webhook-security.ts:412-417` (function exists), but never called

**Function Exists:**
```typescript
export async function checkPaddleNonce(
  nonce: string,
  env: { RATE_LIMITS: KVNamespace }
): Promise<boolean> {
  return checkWebhookNonce(env, `paddle:${nonce}`, 300);
}
```

**Not Used In:** `backend/src/routes/webhooks.ts` - validateWebhook middleware

**Impact:** Replay attacks possible - same webhook could be replayed within 5-minute window.

**Best Practice:** Paddle docs recommend checking `event_id` for deduplication, not nonce. Both approaches work, but implementing either prevents replay attacks.

#### 5. Debug Logging (LOW)

**Location:** `backend/src/redacted/webhook-security.ts:333-337`

**Current Code:**
```typescript
// Debug logging to help identify which format Paddle is sending
console.log('Paddle signature format:', {
  hasH1: !!h1Part,
  hasV1: !!v1Part,
  timestamp: timestamp?.substring(0, 10)
});
```

**Issue:** This logs in production and may leak timing information or signature format details to logs.

**Recommendation:** 
- Remove in production (use environment check)
- OR change to debug-level logging that can be disabled
- OR keep as-is if needed for troubleshooting (lowest priority)

#### 6. Unhandled Subscription Events (MEDIUM)

**Location:** `backend/src/routes/webhooks.ts:131-136`

**Current Code:**
```typescript
// Additional subscription events - log but don't fail
case 'subscription.paused':
case 'subscription.resumed':
case 'subscription.trialing':
case 'subscription.past_due':
  console.log(`Subscription event: ${eventType} for ${eventData.subscription_id}`);
  break;
```

**Issue:** These events are logged but no action is taken.

**Best Practice:** According to Paddle docs, these events should trigger specific actions:
- `subscription.paused`: Should deactivate oversights or mark as paused
- `subscription.resumed`: Should reactivate oversights
- `subscription.trialing`: Should set trial status (if we support trials)
- `subscription.past_due`: Should send payment failure notification or set warning status

**Current Impact:** Oversights remain active even when subscription is paused or past_due, potentially granting access to non-paying users.

#### 7. TODO Comment (LOW)

**Location:** `backend/src/routes/webhooks.ts:29`

**Current Code:**
```typescript
// TODO: use paddle middleware
```

**Issue:** Suggests using Paddle middleware for webhooks.

**Finding:** Paddle Node.js SDK does NOT provide webhook verification middleware. The manual implementation in `webhook-security.ts` is correct per Paddle documentation.

**Recommendation:** Remove TODO comment as it's misleading. Manual verification is the official approach.


## Paddle Webhook Best Practices

### Signature Verification

**Correct Implementation (from Paddle docs):**

```typescript
import { createHmac, timingSafeEqual } from "crypto";

// 1. Get Paddle-Signature header
const paddleSignature = req.headers["paddle-signature"] as string;

// 2. Extract timestamp and signature from header
// Format: ts=1671552777;h1=eb4d0dc8853be92b7f063b9f3ba5233eb920a09459b6e6b2c26705b4364db151
const parts = signature.split(';');
const tsPart = parts.find(p => p.startsWith('ts='));
const h1Part = parts.find(p => p.startsWith('h1='));

if (!tsPart || !h1Part) return false;

const timestamp = tsPart.substring(3);
const receivedSignature = h1Part.substring(3);

// 3. Check timestamp tolerance (5 minutes)
const now = Math.floor(Date.now() / 1000);
if (Math.abs(now - parseInt(timestamp)) > 300) return false;

// 4. Build signed payload: TIMESTAMP:BODY (colon, NOT period!)
const signedPayload = `${timestamp}:${payload}`;

// 5. Compute HMAC-SHA256
const expectedSignature = createHmac('sha256', secret)
  .update(signedPayload, 'utf8')
  .digest('hex');

// 6. Constant-time comparison
return timingSafeEqual(
  Buffer.from(receivedSignature, 'hex'),
  Buffer.from(expectedSignature, 'hex')
);
```

**Key Points:**
- Use colon `:` NOT period `.` between timestamp and payload
- Use `h1=` key (NOT `v1=`) - current code supports both which is good
- Use constant-time comparison to prevent timing attacks (already implemented correctly)
- Check timestamp is within 5 minutes (already implemented correctly)
- Do NOT transform raw body before verification (already using `c.req.text()` which is correct)

### Event Handling

**Recommended Paddle Event Types to Handle:**

| Event | Handler | Action |
|--------|---------|--------|
| `customer.created` | handleCustomerCreated | Link Paddle customer to overseer |
| `subscription.created` | handlePaymentSuccess | Create new subscription |
| `subscription.activated` | handlePaymentSuccess | Activate subscription |
| `subscription.updated` | handleTierUpdate | Update tier/limits |
| `subscription.canceled` | handleSubscriptionCancellation | Deactivate oversights |
| `subscription.paused` | NEW HANDLER | Mark as paused |
| `subscription.resumed` | NEW HANDLER | Reactivate |
| `subscription.past_due` | NEW HANDLER | Payment failed warning |
| `subscription.trialing` | NEW HANDLER | Trial status |
| `transaction.completed` | handlePaymentSuccess | One-time payment |

**Security Improvements:**
1. **Event ID Deduplication** (RECOMMENDED by Paddle)
   ```typescript
   const eventId = data.event_id;
   const processed = await env.RATE_LIMITS.get(`webhook:event:${eventId}`);
   if (processed) {
     return c.json({ success: true, received: true }); // Already processed
   }
   await env.RATE_LIMITS.put(`webhook:event:${eventId}`, '1', { expirationTtl: 86400 });
   ```

2. **IP Whitelisting** (OPTIONAL but RECOMMENDED)
   - Configure firewall to allow only Paddle webhook IPs
   - Production IPs: [get from Paddle dashboard]
   - Sandbox IPs: [get from Paddle dashboard]

### Error Handling

**Best Practices:**

1. **Always return 200 OK for valid requests** (even unhandled events)
   - Prevents Paddle from retrying indefinitely
   - Log unhandled events for future reference

2. **Never expose internal errors**
   - Current: Returns generic error message (good)
   - Improvement: Log full error details but return generic response

3. **Implement proper retry handling**
   - Paddle retries on 5xx errors with exponential backoff
   - Max retries: ~10 over 3 days
   - Each retry has new event_id

4. **Idempotent handlers**
   - Processing same event multiple times should be safe
   - Use event_id deduplication for this

## Architecture Patterns

### Recommended Webhook Handler Structure

```typescript
// 1. Validation middleware
async function validateWebhook(c: any, next: any) {
  // Extract and verify signature
  const signature = c.req.header('Paddle-Signature');
  const payload = await c.req.text();
  
  if (!verifyPaddleSignature(payload, signature, env.PADDLE_WEBHOOK_SECRET)) {
    return c.json({ success: false, error: 'Invalid signature' }, 401);
  }
  
  // Check rate limit
  const clientIP = c.req.header('CF-Connecting-IP');
  if (!await checkRateLimit(env, clientIP, 100, 60)) {
    return c.json({ success: false, error: 'Rate limit exceeded' }, 429);
  }
  
  // Store validated payload
  c.set('validatedPayload', payload);
  await next();
}

// 2. Main route handler
webhooks.post('/paddle', validateWebhook, async (c) => {
  const payload = c.get('validatedPayload');
  const data = JSON.parse(payload);
  
  // Check for duplicate event (prevent replay)
  const eventId = data.event_id;
  if (await isEventProcessed(env, eventId)) {
    return c.json({ success: true, received: true });
  }
  
  // Route to appropriate handler
  const handler = getEventHandler(data.event_type);
  if (handler) {
    await handler(data.data, c.env.DB, c.env);
  } else {
    console.log(`Unhandled Paddle event: ${data.event_type}`);
  }
  
  // Mark event as processed
  await markEventProcessed(env, eventId);
  
  // Always return 200 OK
  return c.json({ success: true, received: true });
});
```

### Anti-Patterns to Avoid

- **Transforming body before verification**: JSON.parse() changes body, breaks signature
- **Returning 500 for unhandled events**: Causes Paddle to retry indefinitely
- **Not checking timestamps**: Old signatures could be replayed
- **Non-constant-time comparison**: Enables timing attacks (already fixed)
- **Exposing error details**: Leaks internal state


## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Webhook signature verification | Custom HMAC | Current implementation (with bug fix) | Already correctly implements HMAC-SHA256 per Paddle docs |
| Paddle middleware | Custom wrapper | Manual verification | Paddle SDK doesn't provide middleware; manual approach is official |
| Event deduplication | Complex logic | Simple KV check with event_id | Paddle recommends event_id approach |
| Replay protection | Nonce | Event ID deduplication | Both work, event_id is Paddle's recommendation |

**Key Insight:** The current manual webhook verification implementation is CORRECT per Paddle's official documentation. The only issue is the delimiter bug (`.` instead of `:`). Don't replace with SDK or community packages.

## Common Pitfalls

### Pitfall 1: Wrong Signature Delimiter
**What goes wrong:** Using period `.` instead of colon `:` causes ALL webhooks to fail signature verification
**Why it happens:** Copy-paste error or misunderstanding of Paddle specification
**How to avoid:** Follow Paddle docs exactly: `${timestamp}:${payload}` not `${timestamp}.${payload}`
**Warning signs:** "Invalid Paddle signature" errors for ALL webhooks

### Pitfall 2: Wrong Event Name Spelling
**What goes wrong:** Using `subscription.cancelled` (double L) means events never match handler
**Why it happens:** British vs American spelling, or typo from old documentation
**How to avoid:** Always verify event names against Paddle official documentation
**Warning signs:** Specific events (cancellations) never trigger handlers

### Pitfall 3: Imaginary Paddle Events
**What goes wrong:** Implementing handlers for events that don't exist in Paddle
**Why it happens:** Assuming custom events without verifying with Paddle docs
**How to avoid:** Check official Paddle webhook documentation for all event types
**Warning signs:** Feature completely broken (shadow claims never process payments)

### Pitfall 4: Not Implementing Replay Protection
**What goes wrong:** Attackers can replay old valid webhooks to trigger handlers
**Why it happens:** Function exists (checkPaddleNonce) but never called
**How to avoid:** Call nonce check OR implement event_id deduplication
**Warning signs:** Same webhook processed multiple times within 5 minutes

### Pitfall 5: Logging Sensitive Data
**What goes wrong:** Production logs expose signature format, timing info
**Why it happens:** Debug logging left in production code
**How to avoid:** Use environment checks or debug-level logging
**Warning signs:** Logs contain "Paddle signature format: { hasH1: true, hasV1: false }"

## Code Examples

### Fix Signature Delimiter Bug

**Before (WRONG):**
```typescript
// backend/src/redacted/webhook-security.ts:354
const dataToSign = `${timestamp}.${payload}`;  // BUG: Period instead of colon
```

**After (CORRECT):**
```typescript
const dataToSign = `${timestamp}:${payload}`;  // FIX: Colon as per Paddle docs
```

### Fix Event Name Spelling

**Before (WRONG):**
```typescript
// backend/src/routes/webhooks.ts:126
case 'subscription.cancelled':  // BUG: Double 'L'
  await handleSubscriptionCancellation(eventData, c.env.DB, c.env);
  break;
```

**After (CORRECT):**
```typescript
case 'subscription.canceled':  // FIX: Single 'L' per Paddle docs
  await handleSubscriptionCancellation(eventData, c.env.DB, c.env);
  break;
```

### Remove Fake Paddle Event

**Before (WRONG):**
```typescript
// backend/src/routes/webhooks.ts:138-141
case 'payment.shadow_claim_succeeded':  // BUG: Not a real Paddle event
  await handleShadowClaimPayment(eventData, c.env.DB, c.env);
  break;
```

**After (CORRECT):**
```typescript
// Shadow claims should use transaction.completed with custom_data
case 'transaction.completed':
  // Check if this is a shadow claim via custom_data
  if (eventData.custom_data?.is_shadow_claim) {
    await handleShadowClaimPayment(eventData, c.env.DB, c.env);
  }
  break;
```

### Implement Event ID Deduplication

**New code to add:**
```typescript
// backend/src/redacted/webhook-security.ts (new function)
export async function isEventProcessed(
  env: { RATE_LIMITS: KVNamespace },
  eventId: string
): Promise<boolean> {
  const key = `webhook:event:${eventId}`;
  const existing = await env.RATE_LIMITS.get(key);
  return existing !== null;
}

export async function markEventProcessed(
  env: { RATE_LIMITS: KVNamespace },
  eventId: string
): Promise<void> {
  const key = `webhook:event:${eventId}`;
  // Store for 24 hours (Paddle retries for 3 days)
  await env.RATE_LIMITS.put(key, '1', { expirationTtl: 86400 });
}
```

**Update webhooks.ts to use:**
```typescript
webhooks.post('/paddle', validateWebhook, async (c) => {
  const payload = c.get('validatedPayload');
  const data = JSON.parse(payload);
  
  // Check for duplicate event (Paddle recommendation)
  if (await isEventProcessed(c.env, data.event_id)) {
    return c.json({ success: true, received: true });
  }
  
  // ... rest of handler
  
  // Mark event as processed
  await markEventProcessed(c.env, data.event_id);
  
  return c.json({ success: true, received: true });
});
```

### Implement Paused/Resumed Handlers

**New handlers to add:**
```typescript
// backend/src/services/webhook-handler.ts (add these functions)

export async function handleSubscriptionPaused(
  payload: PaddlePausePayload,
  db: D1Database,
  env: any
): Promise<void> {
  const { subscription_id } = payload;
  
  const drizzleDb = createDB(db);
  const overseer = await drizzleDb
    .select()
    .from(overseers)
    .where(eq(overseers.paddle_subscription_id, subscription_id))
    .limit(1);
  
  if (overseer.length === 0) {
    throw new Error('Overseer not found for subscription');
  }
  
  // Deactivate oversights (access suspended during pause)
  await drizzleDb
    .update(oversights)
    .set({
      active: false,
      updated_at: new Date().toISOString(),
    })
    .where(eq(oversights.overseer_id, overseer[0].id));
  
  logSubscriptionAction('paddle_paused', subscription_id, {
    overseer_id: overseer[0].id
  });
}

export async function handleSubscriptionResumed(
  payload: PaddleResumePayload,
  db: D1Database,
  env: any
): Promise<void> {
  const { subscription_id } = payload;
  
  const drizzleDb = createDB(db);
  const overseer = await drizzleDb
    .select()
    .from(overseers)
    .where(eq(overseers.paddle_subscription_id, subscription_id))
    .limit(1);
  
  if (overseer.length === 0) {
    throw new Error('Overseer not found for subscription');
  }
  
  // Reactivate oversights (access restored after resume)
  await drizzleDb
    .update(oversights)
    .set({
      active: true,
      updated_at: new Date().toISOString(),
    })
    .where(eq(oversights.overseer_id, overseer[0].id));
  
  logSubscriptionAction('paddle_resumed', subscription_id, {
    overseer_id: overseer[0].id
  });
}
```

## State of the Art

| Aspect | Current (Bug) | Correct (After Fix) | Changed In |
|---------|----------------|---------------------|-------------|
| Signature delimiter | `timestamp.payload` (period) | `timestamp:payload` (colon) | This phase |
| Cancellation event | `subscription.cancelled` | `subscription.canceled` | This phase |
| Shadow claim event | `payment.shadow_claim_succeeded` (fake) | `transaction.completed` with custom_data | This phase |
| Replay protection | None implemented | Event ID deduplication | This phase |
| Unhandled events | Log only | Handle paused/resumed/past_due | This phase |

**Deprecated/Outdated:**
- `v1=` signature key: Paddle changed to `h1=` (code supports both - good)
- Nonce-based replay protection: Event ID deduplication is Paddle's recommendation


## Open Questions

### 1. How should shadow claims work with real Paddle events?

**What we know:**
- `payment.shadow_claim_succeeded` is NOT a real Paddle event
- Current code handles it as if it exists
- Shadow claims need to activate oversight when payment completes

**What's unclear:**
- Should we use `transaction.completed` with `custom_data.is_shadow_claim`?
- Should we use `subscription.created` for one-time shadow subscriptions?
- Is there a Paddle feature for one-time subscription-like payments?

**Recommendation:**
Research Paddle's "one-time charge" or "one-time subscription" options. Likely approach:
1. Create a Paddle product with type=one_time for shadow claims
2. Use `transaction.completed` webhook with custom_data.agent_id to trigger shadow claim
3. Update handleShadowClaimPayment to work with transaction.completed payload

### 2. Should we implement nonce checking or event ID deduplication?

**What we know:**
- checkPaddleNonce() function exists but is never called
- Paddle documentation recommends checking event_id for deduplication
- Both approaches prevent replay attacks

**What's unclear:**
- Which approach is better for our use case?
- Should we implement both?

**Recommendation:**
Implement event ID deduplication (Paddle's official recommendation) because:
- Simpler: One function call, no additional nonce parsing
- More robust: event_id is always present in all Paddle webhooks
- Matches Paddle's examples exactly

Remove or deprecate checkPaddleNonce() function.

### 3. What should happen for subscription.past_due events?

**What we know:**
- Currently: event is logged but no action taken
- Overseer retains full access even if payment failed
- This is a security/revenue risk

**What's unclear:**
- Should we deactivate oversights immediately?
- Should we send email notification?
- Should we allow grace period (e.g., 7 days)?

**Recommendation:**
Implement three-tier approach:
1. **First past_due:** Send warning email, keep access active
2. **7 days past_due:** Deactivate oversights, downgrade to FREE tier
3. **30 days past_due:** Cancel subscription (Paddle will send subscription.canceled)

This matches common subscription billing practices.

### 4. Should we remove debug logging or make it conditional?

**What we know:**
- Lines 333-337 of webhook-security.ts log signature format
- This helps troubleshoot webhook issues in development
- In production, may leak sensitive information

**What's unclear:**
- Is this information already available elsewhere?
- Do we need it in production at all?

**Recommendation:**
Wrap in environment check:
```typescript
if (env.ENVIRONMENT === 'development' || env.ENVIRONMENT === 'test') {
  console.log('Paddle signature format:', {
    hasH1: !!h1Part,
    hasV1: !!v1Part,
    timestamp: timestamp?.substring(0, 10)
  });
}
```

This keeps debugging capability in dev/test without leaking info in production.

## Prioritized List of Fixes

### Priority 1 (CRITICAL - Blocks all webhooks)
1. **Fix signature delimiter bug** - `webhook-security.ts:354`
   - Change `${timestamp}.${payload}` to `${timestamp}:${payload}`
   - Impact: ALL webhooks fail without this fix
   - Time estimate: 5 minutes
   - Tests needed: Signature verification tests

### Priority 2 (CRITICAL - Breaks cancellation flow)
2. **Fix event name spelling** - `webhooks.ts:126`
   - Change `subscription.cancelled` to `subscription.canceled`
   - Update all documentation files (8+ occurrences)
   - Impact: Cancellation webhooks never handled
   - Time estimate: 30 minutes (code) + 30 minutes (docs)
   - Tests needed: Cancellation webhook test

### Priority 3 (HIGH - Breaks shadow claims)
3. **Remove fake Paddle event, implement real handling** - `webhooks.ts:138-141`
   - Research correct Paddle event for shadow claims
   - Replace `payment.shadow_claim_succeeded` with real event
   - Update handleShadowClaimPayment to match real payload
   - Impact: Shadow subscription feature completely broken
   - Time estimate: 2 hours (research + implementation)
   - Tests needed: Shadow claim webhook test

### Priority 4 (MEDIUM - Security vulnerability)
4. **Implement replay protection** - `webhooks.ts`
   - Add event ID deduplication functions to webhook-security.ts
   - Call isEventProcessed() before handling webhook
   - Call markEventProcessed() after handling
   - Impact: Replay attacks possible
   - Time estimate: 30 minutes
   - Tests needed: Deduplication tests

### Priority 5 (MEDIUM - Feature gaps)
5. **Handle paused/resumed/past_due events** - `webhooks.ts:131-136`
   - Add handleSubscriptionPaused() function
   - Add handleSubscriptionResumed() function
   - Add handleSubscriptionPastDue() function (or integrate into existing)
   - Add case statements for each event type
   - Impact: Oversights not updated when subscription status changes
   - Time estimate: 1 hour
   - Tests needed: Event handler tests for new handlers

### Priority 6 (LOW - Code quality)
6. **Remove or condition debug logging** - `webhook-security.ts:333-337`
   - Add environment check around console.log
   - OR remove entirely if not needed
   - Impact: Information leakage in logs
   - Time estimate: 10 minutes

### Priority 7 (LOW - Documentation)
7. **Remove TODO comment** - `webhooks.ts:29`
   - Remove or update TODO about "use paddle middleware"
   - Add comment explaining manual verification is official approach
   - Impact: Misleading for future developers
   - Time estimate: 5 minutes

## Sources

### Primary (HIGH Confidence)

- Paddle Webhooks Overview - https://developer.paddle.com/webhooks/overview
- Verify Webhook Signatures - https://developer.paddle.com/webhooks/signature-verification
- subscription.created Event - https://developer.paddle.com/webhooks/subscriptions/subscription-created
- subscription.canceled Event - https://developer.paddle.com/webhooks/subscriptions/subscription-canceled
- Phase 3 Research Document - `.planning/phases/03-paddle-integration-fix/03-RESEARCH.md`

### Secondary (MEDIUM Confidence)

- Webhook Response Guide - https://developer.paddle.com/webhooks/respond-to-webhooks
- Webhook Testing Guide - https://developer.paddle.com/webhooks/test-webhooks
- Test Scenarios - `docs/v1/test scenarios/subscription.md`

### Tertiary (LOW Confidence)

- None - All findings verified against official Paddle documentation

## Metadata

**Confidence Breakdown:**
- Standard Stack: HIGH - Paddle documentation is authoritative source
- Architecture: HIGH - Follows Paddle's official examples exactly
- Pitfalls: HIGH - Issues identified by code review against official docs
- Event Types: HIGH - Verified against Paddle's complete event list

**Research Date:** 2026-02-16
**Valid Until:** 90 days (Paddle API is stable, but check for updates)

**Files Referenced:**
- backend/src/routes/webhooks.ts
- backend/src/services/webhook-handler.ts
- backend/src/redacted/webhook-security.ts
- backend/src/utils/logging.ts
- backend/test/unit/webhook-handler.test.ts
- backend/test/integration/webhook-events.test.ts
- docs/v1/endpoints/webhooks.md
- docs/v1/endpoints/subscriptions.md
- docs/v1/test scenarios/subscription.md
- docs/v1/requirements/overseer/user-stories.md
