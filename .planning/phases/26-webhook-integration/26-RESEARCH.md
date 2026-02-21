# Phase 26: Webhook Integration - Research

**Researched:** 2026-02-20
**Domain:** Payments / Webhooks (Paddle)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
#### Idempotency & Duplicate Events
- Check KV challenge status when handling the webhook.
- If the event was already processed (e.g., status is already `completed`), silently return 200 to Paddle to acknowledge receipt.

#### Expired Challenges (Late Payments)
- If the payment arrives after the challenge TTL has expired:
  - Check if the agent has already been claimed (e.g., by a real overseer or another shadow overseer in the meantime).
  - If the agent is *not* claimed, proceed to create and activate the shadow oversight anyway.

#### Deactivation Behavior
- When ensuring only one active oversight exists for the agent, deactivate the older ones by setting their `active` flag to `false` (do not hard-delete).

### Claude's Discretion
- Audit logging detail and format (e.g., logging shadow claim creations or renewals to console or DB).
- Handling the edge case where a late payment arrives but the agent IS already claimed (e.g., skip activation, log a warning, and return 200 since refunds are a v2.1 feature).

### Deferred Ideas (OUT OF SCOPE)
- Shadow claim refunds for conflicts or late payments (already deferred to v2.1 per roadmap).
</user_constraints>

## Summary

This research focuses on implementing the `transaction.completed` webhook for Paddle to finalize shadow claims. The core challenges involve securely handling incoming webhooks from Paddle, processing them idempotently, properly updating the KV challenge state, creating/updating the shadow overseer, and handling edge cases like late payments.

**Primary recommendation:** Use the official `@paddle/paddle-node` SDK strictly for validating webhook signatures and providing strict TypeScript interfaces. Implement idempotency via KV state verification as the absolute first step in processing, ensuring all duplicate webhooks exit gracefully with a `200 OK`.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@paddle/paddle-node` | 1.x | Signature validation and TS Types | Official SDK; handles the complex signature parsing (`Paddle-Signature` header). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@paddle/paddle-node` | Custom Crypto Validation | Hand-rolling Ed25519 signature validation is risky, error-prone, and harder to maintain across API version changes. |

**Installation:**
```bash
npm install @paddle/paddle-node
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── api/
│   └── webhooks/
│       └── paddle/
│           └── route.ts         # Endpoint for receiving webhooks
├── services/
│   └── shadow-claims/
│       ├── handle-transaction.ts # Core logic for webhook event
│       └── audit-logger.ts       # Structured audit logging
└── lib/
    └── paddle.ts                 # Paddle SDK initialization
```

### Pattern 1: Webhook Idempotency Layer
**What:** Verifying event status before any side-effects.
**When to use:** Always for payment webhooks, which are guaranteed "at-least-once" delivery.
**Example:**
```typescript
// Check if already processed
const challenge = await kv.get(`challenge:${customData.challengeId}`);
if (challenge.status === 'completed') {
  // Silently acknowledge to Paddle without reprocessing
  return new Response(null, { status: 200 });
}
```

### Anti-Patterns to Avoid
- **Hard Deleting Older Claims:** Instead, update the `active` flag to `false` for historical tracking and DB constraint integrity.
- **Throwing errors on duplicate events:** Paddle will continuously retry failing webhooks. If an event is safely ignored, returning 5xx or 4xx will create unnecessary log spam and retry queues. Always return `200` for duplicates or late events where action is skipped intentionally.
- **Processing webhooks inline without validation:** Always validate the `Paddle-Signature` to prevent spoofing.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Signature Verification | Custom crypto validation | `@paddle/paddle-node` | Paddle uses Ed25519 signatures; manual string construction and header parsing is delicate and breaks easily on minor whitespace issues. |
| Retry Logic | Custom queueing | Paddle Webhook Retries | Paddle automatically retries webhooks with exponential backoff if your server doesn't return a 2xx response. |

**Key insight:** Payment webhook reliability is critical. Leverage the provider's built-in robust systems (signatures, retries) rather than building intermediate layers.

## Common Pitfalls

### Pitfall 1: Late Payment Conflicts
**What goes wrong:** A customer takes 65 minutes to pay (TTL was 60m), and by then, the agent was claimed by someone else. The system blindly activates the shadow claim, creating a conflict.
**Why it happens:** The TTL expired but Paddle still processes the delayed payment.
**How to avoid:** Explicitly check the agent's current claim status during the webhook flow. If claimed, skip activation, log a warning, and acknowledge the webhook (200 OK).
**Warning signs:** Multiple active claims on a single agent; constraint violation errors in DB logs.

### Pitfall 2: Unhandled Custom Data
**What goes wrong:** Webhook fails because the expected `custom_data` (e.g., `challengeId`, `tier`) is missing or malformed.
**Why it happens:** Type assumptions on `custom_data` which is inherently an unstructured object in Paddle's schema.
**How to avoid:** Validate `custom_data` at the boundary (e.g., using Zod) before attempting to lookup KV or update claims.

## Code Examples

Verified patterns from official sources:

### Webhook Validation & Resolution
```typescript
// Source: https://developer.paddle.com/webhook-reference/signature-verification
import { Environment, Paddle } from '@paddle/paddle-node';

const paddle = new Paddle('YOUR_API_KEY', { environment: Environment.sandbox });

export async function POST(req: Request) {
  const signature = req.headers.get('paddle-signature');
  const body = await req.text();
  
  try {
    const eventData = paddle.webhooks.unmarshal(body, 'YOUR_WEBHOOK_SECRET', signature);
    
    if (eventData.eventType === 'transaction.completed') {
      const customData = eventData.data.customData;
      // Proceed with Idempotency & Challenge Logic
      await handleTransactionCompleted(eventData.data, customData);
    }
    
    return new Response('OK', { status: 200 });
  } catch (err) {
    // Signature validation failed
    console.error('Webhook signature verification failed', err);
    return new Response('Invalid signature', { status: 401 });
  }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Polling payment status | Webhook-driven status | Universal | Reduces server load; near instant resolution upon payment success. |
| Hard deleting records | Soft deleting (`active: false`) | Industry standard | Preserves audit trails and payment history for the user. |

## Open Questions

Things that couldn't be fully resolved:

1. **Audit Logging Infrastructure**
   - What we know: It is Claude's discretion to design the audit logging detail.
   - What's unclear: If there is a preferred structured logging tool (e.g., Winston, Pino, or Datadog) already in use in this project.
   - Recommendation: Use a structured JSON console logger (e.g., `console.info({ event: 'shadow_claim_activated', agentId: ... })`) for now until a dedicated telemetry stack is explicitly required.

## Sources

### Primary (HIGH confidence)
- Official Paddle Node.js SDK Documentation - Signature verification and Types (`transaction.completed`)
- CONTEXT.md constraints mapping to implementation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Paddle Node SDK is the official approach.
- Architecture: HIGH - Webhook endpoints with idempotency checks are standard payment patterns.
- Pitfalls: HIGH - Documented edge cases specifically address the User Constraints requested in CONTEXT.md.

**Research date:** 2026-02-20
**Valid until:** 2026-03-20