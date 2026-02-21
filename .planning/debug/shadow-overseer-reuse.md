---
status: diagnosed
trigger: "Shadow Overseer Reuse (Test 6 in Phase 26 UAT) - new shadow overseer ID generated instead of reusing existing one"
created: 2026-02-20T00:00:00Z
updated: 2026-02-20T00:00:00Z
symptoms_prefilled: true
goal: find_root_cause_only
---

## Current Focus

hypothesis: CONFIRMED - The /malice/:agentId endpoint always generates a new shadow overseer ID even when one already exists
test: Read agents.ts lines 776-822 and ownership.ts for isShadowOverseer
expecting: Found the bug - line 795-796 always generates new ID regardless of existing shadow overseer
next_action: Report root cause

## Symptoms

expected: When processing a renewal, if the shadow overseer already exists in the database, the existing record should be reused and paddle_customer_id is updated.
actual: A new shadow overseer ID is generated every time, even when one already exists
errors: None reported
reproduction: Process a renewal for an agent that already has a shadow overseer
started: Unknown - design issue

## Eliminated

## Evidence

- timestamp: 2026-02-20T00:00:00Z
  checked: Context provided
  found: Webhook handler correctly reuses shadow overseers by ID, but the /malice/:agentId endpoint generates the ID that gets stored in the challenge
  implication: The root cause is in the /malice/:agentId endpoint - it needs to check for existing shadow overseer before generating a new one

- timestamp: 2026-02-20T00:00:00Z
  checked: backend/src/routes/agents.ts lines 776-822
  found: |
    The `/malice/:agentId` endpoint:
    - Lines 786-793: Correctly checks if agent has active oversight and allows renewal if shadow overseer
    - Lines 795-796: ALWAYS generates new shadow overseer ID via `generateShadowOverseerId(c.env)`
    
    The bug is that even after detecting an existing shadow overseer (line 791-793), the code still generates a NEW ID on line 795.
  implication: The existing shadow overseer ID is discarded and a new one is created. This new ID flows through the challenge, Paddle checkout, and webhook - resulting in a new overseer record being created instead of reusing the existing one.

- timestamp: 2026-02-20T00:00:00Z
  checked: backend/src/services/ownership.ts
  found: `isShadowOverseer()` function correctly verifies shadow overseer IDs via cryptographic signature
  implication: The function works correctly - the issue is that its result is not used to determine whether to reuse the existing ID

## Resolution

root_cause: |
  In `backend/src/routes/agents.ts`, the `/malice/:agentId` endpoint (lines 776-822) checks if a shadow overseer already exists (lines 786-793), but then ALWAYS generates a new shadow overseer ID on lines 795-796, ignoring the existing one.
  
  The fix should be:
  ```javascript
  // After line 793, before line 795:
  let shadowOverseerId: string;
  if (activeOversight && isShadow) {
    // Reuse existing shadow overseer ID
    shadowOverseerId = activeOversight.overseer_id;
  } else {
    // Generate new shadow overseer ID
    shadowOverseerId = await generateShadowOverseerId(c.env);
  }
  ```
fix: Modify lines 795-796 to conditionally generate new ID only when no existing shadow overseer
verification: Test renewal flow - existing shadow overseer ID should be reused
files_changed: [backend/src/routes/agents.ts]
