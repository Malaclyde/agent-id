---
phase: 21-agent-oauth-registration-limit
verified: 2026-02-18T21:30:00Z
status: passed
score: 1/1 must-haves verified
re_verification: true
  previous_status: passed
  previous_score: 2/2
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 21 (Re-Verification): Active Subscription Scheduled for Cancellation

**Phase Goal:** OAuth request limiting using oauth_requests table - verify billing period works for active subscriptions scheduled for cancellation

**Verified:** 2026-02-18
**Status:** PASSED
**Re-verification:** Yes — user fixed issue themselves, verifying fix is correct

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Subscriptions with status='active' but scheduled_change.action='cancel' return billing_period_end correctly | ✓ VERIFIED | subscription.ts lines 131-166: status='active' passes activeStatuses check (line 131-132), currentPeriodEnd calculated correctly (lines 153-154) using current_period_end or scheduledCancelAt fallback |

**Score:** 1/1 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `backend/src/services/subscription.ts` | Returns billing_period_end for active subscriptions scheduled for cancellation | ✓ VERIFIED | Lines 131-166 handle status='active' correctly; lines 153-154 calculate currentPeriodEnd: uses current_period_end if available, falls back to scheduledCancelAt if not |

### Key Logic Verification

**subscription.ts lines 131-166:**

1. **Status check (lines 131-138):** 
   - `activeStatuses = ['active', 'trialing', 'past_due']`
   - Status='active' **passes** this check → continues to return tier limits with billing_period_end
   - Does NOT fall back to FREE tier

2. **Billing period calculation (lines 153-154):**
   ```typescript
   const currentPeriodEnd = paddleSub.current_period_end 
     ? paddleSub.current_period_end 
     : scheduledCancelAt 
       ? scheduledCancelAt 
       : undefined;
   ```
   - If `paddleSub.current_period_end` exists → use it
   - Otherwise, if `scheduledCancelAt` (from scheduled_change.effective_at) exists → use it
   - Otherwise → undefined

3. **Return (line 161):**
   ```typescript
   return {
     ...tierLimits,
     id: paddleSub.id,
     status: paddleSub.status,
     billing_period_end: currentPeriodEnd,
     ...
   };
   ```

**Result:** For a subscription with:
- `status = 'active'`
- `scheduled_change.action = 'cancel'`
- `scheduled_change.effective_at = '2026-02-28'` (e.g.)
- `current_period_end = '2026-02-20'` (or null)

The function correctly returns `billing_period_end` from either `current_period_end` or falls back to `scheduledCancelAt`.

### TypeScript Compilation

✓ TypeScript compiles without errors

---

## Verification Summary

**User's specific check verified:** Subscriptions with `status='active'` but `scheduled_change.action='cancel'` correctly return `billing_period_end`:

1. **Status check passes:** status='active' is in `activeStatuses` → doesn't return FREE tier defaults
2. **billing_period_end populated:** Uses `paddleSub.current_period_end` if available, otherwise falls back to `scheduledCancelAt` (the effective_at date from the scheduled cancellation)
3. **oauth-limit.ts integration:** `getBillingPeriodFromPaddle` receives this billing_period_end and correctly uses it for OAuth limit calculations

The fix is correct and complete.

---

_Verified: 2026-02-18T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
