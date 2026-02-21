---
phase: 02-documentation-enhancement
plan: 03-test-scenarios-claim
type: execute
wave: 2
depends_on:
  - 02-01-USER-STORIES-AGENT-PLAN
  - 02-02-USER-STORIES-OVERSEER-PLAN
files_modified:
  - docs/v1/test scenarios/claim.md
autonomous: true

must_haves:
  truths:
    - "All claim test scenarios use structured format with name, preconditions, steps, expected outcome, actual behavior"
    - "All claim test scenarios reference related user stories"
    - "Minimum 7 claim scenarios documented including edge cases"
    - "All scenarios have explicit expected outcomes and actual behavior documentation"
  artifacts:
    - path: "docs/v1/test scenarios/claim.md"
      provides: "Structured claim test scenarios with edge cases"
      contains: "TS-0"
  key_links:
    - from: "docs/v1/test scenarios/claim.md"
      to: "docs/v1/requirements/agent/claim.md"
      via: "Related User Stories references"
      pattern: "US-C0"
---

<objective>
Transform 7 simple bullet points into 10+ structured test scenarios with explicit format change from simple bullet list to structured format with name, preconditions, scenario steps, expected outcome, actual behavior, and related user stories.

Purpose: Provide detailed, executable test scenarios for claim procedures including edge cases, enabling comprehensive testing of claim functionality.

Output: Updated claim.md with 10+ test scenarios in structured format (transformed from simple bullet list), covering happy paths, edge cases, and error handling. Each scenario has explicit "Actual Behavior" section.
</objective>

<execution_context>
@./.opencode/get-shit-done/workflows/execute-plan.md
@./.opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/02-documentation-enhancement/02-RESEARCH.md
@docs/v1/test scenarios/claim.md
@docs/v1/requirements/agent/claim.md
@docs/v1/endpoints/agents.md
@docs/v1/endpoints/overseers.md
</context>

<tasks>

<task type="auto">
  <name>Reformulate claim test scenarios with structured format including edge cases</name>
  <files>docs/v1/test scenarios/claim.md</files>
  <action>
    1. Read existing claim.md (currently has 7 simple bullet points plus TODO for edge cases)
    2. Reformulate each scenario using structured format from RESEARCH.md:

    Scenarios to reformulate:
    - TS-001: Overseer claims unclaimed agent (happy path)
    - TS-002: Agent renounces overseer (happy path)
    - TS-003: Overseer ends oversight (happy path)
    - TS-004: Unclaimed agent gets shadow claimed (happy path)
    - TS-005: Shadow-claimed agent gets shadow claimed again (edge case)
    - TS-006: Shadow-claimed agent gets claimed by human overseer (edge case)
    - TS-007: Overseer attempts to claim already claimed agent (edge case - negative case)
    - TS-008: Agent does not respond to claim procedure (edge case - timeout)
    - TS-009: Overseer without subscription attempts to claim (edge case - negative case)
    - TS-010: Invalid claim challenge ID (error case)

    Structured format template:
    ```markdown
    ### TS-XXX: [Scenario Name]

    **Preconditions:**
    - [ ] Condition 1
    - [ ] Condition 2

    **Scenario Steps:**
    1. Step 1
    2. Step 2
    3. Step 3

    **Expected Outcome:**
    - Expected result 1
    - Expected result 2

    **Actual Behavior:**
    [Document current implementation behavior - verified to work as expected or document gaps]

    **Related User Stories:**
    - US-XXX: [Story title]
    ```

    Example for TS-001:
    ```markdown
    ### TS-001: Overseer Claims Unclaimed Agent

    **Preconditions:**
    - [ ] Overseer has registered account with paid subscription (not FREE)
    - [ ] Overseer is logged in with valid session
    - [ ] Agent has registered account
    - [ ] Agent is not currently claimed (no oversight record exists)

    **Scenario Steps:**
    1. Overseer clicks "claim agent" in dashboard or calls POST /api/overseers/claim with agent ID
    2. Backend validates overseer has paid subscription tier
    3. Backend creates claim challenge with unique challenge ID
    4. Backend stores claim challenge in challenges table with overseer_id, agent_id, expiration
    5. Overseer receives claim challenge URL: https://api.example.com/claim/{challengeId}
    6. Overseer shares claim challenge URL with agent
    7. Agent visits URL or posts DPoP JWT to endpoint
    8. Backend validates challenge is not expired and matches agent
    9. Backend creates oversight record in oversights table
    10. Backend returns success response to agent

    **Expected Outcome:**
    - Oversight record created in database with overseer_id, agent_id, active=true
    - Agent now has overseer relationship and can access subscription features
    - Overseer dashboard shows claim completed status
    - Agent can register OAuth clients (if subscription tier permits)

    **Actual Behavior:**
    [Verified to work as expected - Phase 1 audit confirmed]

    **Related User Stories:**
    - US-105: Initiate agent claim (overseer)
    - US-C001: Respond to overseer claim (agent)
    ```

    For negative/edge cases (TS-007, TS-009, TS-010), document expected error handling:
    - TS-007: Expect 409 Conflict with clear error message "Agent already claimed"
    - TS-009: Expect 403 Forbidden with error "Subscription tier does not permit claims"
    - TS-010: Expect 404 Not Found with error "Challenge not found or expired"
  </action>
  <verify>grep -c "TS-0" docs/v1/test\ scenarios/claim.md returns >= 10; grep -c "Preconditions:" docs/v1/test\ scenarios/claim.md returns >= 10; grep -c "Actual Behavior:" docs/v1/test\ scenarios/claim.md returns >= 10</verify>
  <done>10+ test scenarios in structured format covering happy paths, edge cases, and error handling</done>
</task>

</tasks>

<verification>
- grep -c "TS-0" docs/v1/test\ scenarios/claim.md >= 10
- grep -c "Preconditions:" docs/v1/test\ scenarios/claim.md >= 10
- grep -c "Scenario Steps:" docs/v1/test\ scenarios/claim.md >= 10
- grep -c "Expected Outcome:" docs/v1/test\ scenarios/claim.md >= 10
- grep -c "Actual Behavior:" docs/v1/test\ scenarios/claim.md >= 10
- grep -c "Related User Stories:" docs/v1/test\ scenarios/claim.md >= 10
- grep "409 Conflict\|403 Forbidden\|404 Not Found" docs/v1/test\ scenarios/claim.md | wc -l >= 3
</verification>

<success_criteria>
Claim test scenarios enhanced with:
- Structured format (name, preconditions, steps, expected outcome, actual behavior)
- 10+ scenarios covering happy paths, edge cases, and error handling
- Related user story references
- Explicit error responses documented for negative cases
- Actual behavior documentation for verification gaps
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-03-TEST-SCENARIOS-CLAIM-SUMMARY.md`
</output>
