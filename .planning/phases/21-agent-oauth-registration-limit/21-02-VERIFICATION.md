---
phase: 21-agent-oauth-registration-limit
verified: 2026-02-18T20:45:00Z
status: passed
score: 2/2 must-haves verified
re_verification: true
  previous_status: gaps_found
  previous_gaps:
    - "Claimed agents with paused subscriptions have billing_period_end from Paddle"
    - "checkOAuthLimit correctly uses billing period for paused subscriptions"
  gaps_closed:
    - "subscription.ts now returns billing_period_end for paused subscriptions (lines 134-146)"
    - "oauth-limit.ts correctly uses billing period via getBillingPeriodFromPaddle (lines 109-127)"
  gaps_remaining: []
  regressions: []
---

# Phase 21 (Gap Closure 02): OAuth Limit Paused Subscription Verification

**Phase Goal:** Implement OAuth registration request limits for agents based on subscription tier. Replace broken oauth_count/billing_period_end tracking with proper tracking using oauth_requests table.

**Gap Closure Goal:** Fix billing period lookup for claimed agents with paused subscriptions - they were falling back to FREE tier incorrectly.

**Verified:** 2026-02-18
**Status:** PASSED
**Re-verification:** Yes — gap closure verification

## Goal Achievement

### Observable Truths (Gap Closure 02)

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Claimed agents with paused subscriptions have billing_period_end from Paddle | ✓ VERIFIED | `subscription.ts` lines 134-146: When `paddleSub.status === 'paused'`, returns `billing_period_end: paddleSub.current_period_end` |
| 2   | checkOAuthLimit correctly uses billing period for paused subscriptions | ✓ VERIFIED | `oauth-limit.ts` lines 109-127: For claimed agents, calls `getBillingPeriodFromPaddle` which now returns period (since subscription.ts provides billing_period_end for paused). Falls back to FREE tier only when `paddlePeriod` is null. |

**Score:** 2/2 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `backend/src/services/subscription.ts` | Returns billing_period_end for paused subscriptions | ✓ VERIFIED | Lines 134-146 handle paused status, return `billing_period_end: paddleSub.current_period_end` |
| `backend/src/services/oauth-limit.ts` | Uses billing period correctly | ✓ VERIFIED | getBillingPeriodFromPaddle (lines 68-84) returns period when billing_period_end exists. checkOAuthLimit (lines 109-127) uses paddlePeriod when available. |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| oauth-limit.ts | subscription.ts getEntitySubscription | import + function call | ✓ WIRED | Line 13 import, lines 73 & 125 calls |
| oauth.ts /authorize | oauth-limit.ts checkOAuthLimit | import + function call | ✓ WIRED | Line 6 import, line 127 call at /authorize |
| checkOAuthLimit | getBillingPeriodFromPaddle | function call | ✓ WIRED | Line 111: `const paddlePeriod = await getBillingPeriodFromPaddle(db, agentId, env)` |

### Requirements Coverage (Phase 21 Full)

| Requirement | Status | Details |
| ----------- | ------ | --------|
| Unclaimed agents limited to 10 per calendar month | ✓ SATISFIED | checkOAuthLimit uses FREE tier limit for unclaimed (21-01 verified) |
| Claimed agents use billing period from Paddle | ✓ SATISFIED | getBillingPeriodFromPaddle queries subscription (21-01 verified + gap closure) |
| Limit checked at /authorize, returns 403 | ✓ SATISFIED | Returns 403 with access_denied error (21-01 verified) |
| OAuth recorded at /token exchange | ✓ SATISFIED | recordOAuthRequest called after tokens generated (21-01 verified) |
| Old columns removed | ✓ SATISFIED | No oauth_count or billing_period_end in agents schema (21-01 verified) |
| Auto-prune 20 records | ✓ SATISFIED | MAX_HISTORY_PER_AGENT = 20 (21-01 verified) |
| **Paused subscriptions have billing_period_end** | ✓ SATISFIED | Gap closure: subscription.ts lines 134-146 |
| **checkOAuthLimit uses billing period for paused** | ✓ SATISFIED | Gap closure: oauth-limit.ts lines 109-127 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| subscription.ts | 15, 28 | Import-related TODO comments | ℹ️ Info | Not implementation stubs - just import path comments |
| ownership.ts | 15 | Import-related TODO comment | ℹ️ Info | Not implementation stub |
| client-limits.ts | 14 | Import-related TODO comment | ℹ️ Info | Not implementation stub |

**Note:** These TODO comments are about import paths, not implementation stubs. The actual implementation code is substantive (371 lines in subscription.ts, 159 in oauth-limit.ts).

### Backend Build

✓ TypeScript typecheck passes without errors

---

## Gap Closure Summary

The gap closure plan 21-02 successfully fixed the billing period lookup for paused subscriptions:

1. **Root cause:** `getEntitySubscription` in subscription.ts returned FREE tier defaults when subscription status was not active/trialing/past_due, causing `billing_period_end` to be undefined for paused subscriptions.

2. **Fix applied:** Added handling for `pausedStatuses = ['paused']` in subscription.ts (lines 132, 134-146). When subscription is paused, it now returns the tier limits along with `billing_period_end: paddleSub.current_period_end`.

3. **Verification result:** 
   - `getBillingPeriodFromPaddle` now correctly returns a period for paused subscriptions (since `billing_period_end` is now populated)
   - `checkOAuthLimit` uses this period instead of falling back to FREE tier calendar month
   - TypeScript compiles without errors

---

_Verified: 2026-02-18T20:45:00Z_
_Verifier: Claude (gsd-verifier)_
