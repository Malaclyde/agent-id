---
created: 2026-02-20T09:46
title: Fix shadow claim duplicate API calls
area: ui
files:
  - frontend/src/pages/ShadowClaim.tsx:24-44
  - frontend/src/main.tsx:13
  - frontend/src/api/client.ts:274-286
---

## Problem

When navigating to `/malice/<agentId>`, the frontend makes TWO POST requests to initiate shadow claim, resulting in:
- Backend creates two separate shadow claims with different `shadow_id` values
- First response returns shadow_id A, payment_challenge_id A
- Second response returns shadow_id B, payment_challenge_id B
- Frontend uses the SECOND response's payment_challenge_id
- Polling status of challenge B returns "expired" (due to backend bugs)
- User sees "Challenge Expired" error

### Root Cause

React StrictMode is enabled in `frontend/src/main.tsx` (line 13). In React 18 development mode, StrictMode intentionally double-invokes useEffect to help detect side effect issues.

In `ShadowClaim.tsx`, the useEffect at lines 24-44:
1. First run: calls `api.initiateShadowClaim(agentId)`
2. Cleanup (nothing to clean up)
3. Second run: calls `api.initiateShadowClaim(agentId)` again

## Solution

Add a ref to prevent duplicate API calls in ShadowClaim.tsx:

```tsx
const initiatedRef = useRef(false);

useEffect(() => {
  if (!agentId || initiatedRef.current) {
    return;
  }
  
  initiatedRef.current = true;
  
  const initiateClaim = async () => {
    // ... existing code
  };
  
  initiateClaim();
}, [agentId]);
```

## Related Backend Issues (separate todo needed)

The frontend fix alone won't make the flow work - there are also backend bugs:

1. **Wrong challenge type lookup** (agents.ts:591 vs 674)
   - Creates challenge with type 'payment' (line 674)
   - Status endpoint looks for type 'claim' (line 591)
   - Always returns "expired"

2. **Requires authentication** (agents.ts:584-587)
   - Status endpoint requires overseer authentication
   - Shadow claim is initiated by unauthenticated human
   - Should work without auth

3. **Plan mismatch**
   - Plan says poll `/v1/agents/claim/status/:challengeId`
   - Backend requires auth and looks up wrong type
