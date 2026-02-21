---
created: 2026-02-20T09:48
title: Fix shadow claim backend endpoint bugs
area: api
files:
  - backend/src/routes/agents.ts:583-609
  - backend/src/routes/agents.ts:641-690
  - backend/src/routes/agents.ts:697-790
---

## Problem

The shadow claim backend implementation has three critical bugs that prevent the flow from working:

### Bug #1: Wrong Challenge Type Lookup

**Location:** `backend/src/routes/agents.ts`

| Line | Issue |
|------|-------|
| 674 | Creates challenge: `storeChallenge(..., 'payment', paymentChallengeId, ...)` |
| 591 | Looks up challenge: `getChallenge(..., 'claim', challengeId)` |

The status endpoint always returns "expired" because it looks for a 'claim' type challenge but the shadow claim initiation creates a 'payment' type challenge.

### Bug #2: Requires Authentication

**Location:** `backend/src/routes/agents.ts:584-587`

```typescript
const overseerId = c.get('overseerId');
if (!overseerId) {
  return c.json({ success: false, error: 'Not authenticated' }, 401);
}
```

The `/claim/status/:challengeId` endpoint requires an authenticated overseer, but:
- Shadow claim is initiated by an unauthenticated human
- The frontend polls this endpoint without auth
- Should work without authentication

### Bug #3: Plan Mismatch - No 'completed' Status

The plan specifies the status endpoint should return:
- `pending`, `completed`, `rejected`, `expired`

But the current implementation:
- Only returns `pending` or `expired`
- Doesn't handle the 'payment' challenge type at all (wrong type)
- Doesn't track or return 'completed' status

## Solution

Three fixes needed:

### Fix #1: Create new status endpoint for payment challenges

Add a new endpoint or modify existing to look up 'payment' type challenges:
- Endpoint: GET `/v1/agents/malice/status/:paymentChallengeId`
- Or modify existing to accept type parameter
- Should work WITHOUT authentication (unauthenticated human is polling)

### Fix #2: Remove authentication requirement

The status polling should work for unauthenticated users since:
- The human is just checking if their agent completed the challenge
- No sensitive data is returned (just challenge status)

### Fix #3: Return proper status values

Handle these statuses:
- `pending` - challenge exists, not yet completed
- `completed` - challenge was completed (agent posted to callback)
- `expired` - challenge not found or past expiration

## Related

Frontend has a separate issue: React StrictMode causes duplicate API calls.
See todo: `2026-02-20-shadow-claim-frontend-fix.md`
