---
phase: 31-end-to-end-test-implementation
plan: 05
status: complete
type: gap_closure
started: 2026-02-23T23:00:00Z
completed: 2026-02-23T23:10:00Z
subsystem: backend/test-utils
affects: []

artifacts:
  modified:
    - backend/src/routes/test-utils.ts

decisions:
  - id: 31-05-D01
    description: "subscription.activated delegates to handlePaymentSuccess (same as real webhooks.ts). agent.confirmed is a test-only internal event that updates KV challenge status directly."

verification:
  - check: "grep subscription.activated backend/src/routes/test-utils.ts"
    result: "1 match — case exists in switch"
  - check: "grep agent.confirmed backend/src/routes/test-utils.ts"
    result: "1 match — case exists in switch"
  - check: "grep create-agent backend/src/routes/test-utils.ts"
    result: "2 matches — route + JSDoc"
  - check: "npx tsc --noEmit"
    result: "No errors"

tech_stack:
  unchanged: true

gaps_closed:
  - "subscription.activated missing from simulate-webhook switch → added, delegates to handlePaymentSuccess"
  - "agent.confirmed missing from simulate-webhook switch → added, updates KV challenge status to awaiting-payment"
  - "POST /create-agent endpoint missing → added, inserts agent row via Drizzle"
---

# Phase 31 Plan 05 Summary — Gap Closure: Missing Event Types & Create-Agent Endpoint

## What Was Done

Closed 3 verification gaps in `backend/src/routes/test-utils.ts` (131 → 172 lines):

1. **Added `subscription.activated` case** (line 144-146): Delegates to `handlePaymentSuccess(data, c.env.DB, c.env)`, matching how the real `webhooks.ts` handles this event. Unblocks `subscription-flow.spec.ts` line 82.

2. **Added `agent.confirmed` case** (line 147-160): Test-only internal event. Reads challenge from KV (`claim:{challenge_id}`), updates status to `awaiting-payment`, writes back with 1-hour TTL. Unblocks `shadow-claim.spec.ts` line 74.

3. **Added `POST /create-agent` endpoint** (line 87-103): Accepts `{ id, name, public_key }`, inserts agent row via Drizzle using already-imported `agents` table and `createDB`. Unblocks `shadow-claim.spec.ts` line 33.

## Key Details

- **No new imports needed** — `handlePaymentSuccess`, `agents`, and `createDB` were already imported
- **No existing code modified** — all changes are purely additive
- **Switch now has 9 named cases** + default (was 7 + default)
- All changes align with existing patterns in the file (try/catch, `c.json()` responses, Drizzle usage)

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `backend/src/routes/test-utils.ts` | 131 → 172 | +41 lines: POST /create-agent route, subscription.activated case, agent.confirmed case |
