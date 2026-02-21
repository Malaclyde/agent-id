---
status: diagnosed
phase: 21-agent-oauth-registration-limit
source: 21-01-SUMMARY.md
started: 2026-02-18T15:25:00Z
updated: 2026-02-18T15:55:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Unclaimed agent OAuth limit enforcement
expected: When an unclaimed agent (no overseer) makes more than 10 OAuth requests in a calendar month, the /authorize endpoint returns HTTP 403 with { "error": "access_denied", "error_description": "OAuth limit reached (X/10 for this period)" }
result: issue
reported: "the function pruneOldRequests in the backend unfortunately works incorrectly and removes all the latest oauth_requests from the db"
severity: blocker
fix_applied: "Fixed pruneOldRequests - now keeps latest 15 approved + 15 denied, deletes rest"

### 2. Claimed agent uses billing period from Paddle
expected: When a claimed agent (has overseer with Paddle subscription) makes OAuth requests, the system checks their billing period from Paddle, not calendar month. Most paid tiers have unlimited (-1) so no limit applies.
result: issue
reported: "the paddlePeriod in the checkOAuthLimit function is null"
severity: blocker

### 3. OAuth request recorded at token exchange
expected: OAuth requests are recorded to oauth_requests table ONLY after successful token exchange at /token endpoint (not at /authorize). The record includes agent_id, client_id, scope, and status='approved'.
result: pass
fix_applied: "Also recorded at /authorize when denied - correct behavior"

### 4. 403 error format correct
expected: When limit is exceeded, the response is properly formatted JSON with error="access_denied" and error_description containing the limit message.
result: pass

### 5. Pruning keeps latest 15 approved + 15 denied
expected: The oauth_requests table auto-prunes to keep only the last 15 approved and 15 denied records per agent. Older records are automatically deleted.
result: pass
fix_applied: "Fixed pruneOldRequests in oauth-history.ts - now correctly keeps latest 15 approved and latest 15 denied requests per agent, deletes the rest"

## Summary

total: 5
passed: 3
issues: 2
pending: 0
skipped: 0

## Gaps

- truth: "Pruning keeps last 20 records per agent"
  status: fixed
  reason: "User reported: the function pruneOldRequests in the backend unfortunately works incorrectly and removes all the latest oauth_requests from the db"
  severity: blocker
  test: 1
  root_cause: "Logic was inverted - deleting recent records instead of old ones"
  artifacts:
    - path: "backend/src/services/oauth-history.ts"
      issue: "pruneOldRequests had inverted delete logic"
  missing:
    - "Separate queries for approved/denied status"
  fix_applied: "Rewrote pruneOldRequests to keep latest 15 approved + 15 denied, TypeScript compiles"

- truth: "Pruning should keep latest 15 approved and latest 15 denied requests per agent"
  status: fixed
  reason: "User reported new mechanism request"
  severity: blocker
  test: 5
  root_cause: "Function didn't exist with correct logic"
  artifacts:
    - path: "backend/src/services/oauth-history.ts"
      issue: "Needed new implementation"
  missing:
    - "Separate approved/denied queries"
  fix_applied: "Implemented new mechanism: MAX_APPROVED_HISTORY=15, MAX_DENIED_HISTORY=15"

- truth: "Claimed agents use billing period from Paddle subscription"
  status: failed
  reason: "User reported: the paddlePeriod in the checkOAuthLimit function is null"
  severity: blocker
  test: 2
  root_cause: "When subscription is cancelled but still active (grace period), Paddle returns current_period_end as undefined but has scheduled_cancel_at set. getActiveSubscription doesn't handle this - needs to use scheduled_cancel_at as billing_period_end when current_period_end is null"
  artifacts:
    - path: "backend/src/services/subscription.ts"
      issue: "Line 158: billing_period_end: paddleSub.current_period_end - returns undefined when subscription is cancelled/paused"
  missing:
    - "Use scheduled_cancel_at as billing_period_end when current_period_end is null/undefined"
  fix_plan: "21-02-PLAN.md"
