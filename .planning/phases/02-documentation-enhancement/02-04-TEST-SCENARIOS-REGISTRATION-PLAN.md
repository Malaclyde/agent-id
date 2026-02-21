---
phase: 02-documentation-enhancement
plan: 04-test-scenarios-registration
type: execute
wave: 2
depends_on:
  - 02-01-USER-STORIES-AGENT-PLAN
  - 02-02-USER-STORIES-OVERSEER-PLAN
files_modified:
  - docs/v1/test scenarios/registration.md
autonomous: true

must_haves:
  truths:
    - "All registration test scenarios use structured format with name, preconditions, steps, expected outcome, actual behavior"
    - "All registration test scenarios reference related user stories"
    - "Minimum 8 registration scenarios documented including edge cases"
    - "All scenarios have explicit expected outcomes and actual behavior documentation"
  artifacts:
    - path: "docs/v1/test scenarios/registration.md"
      provides: "Structured registration test scenarios with edge cases"
      contains: "TS-R0"
  key_links:
    - from: "docs/v1/test scenarios/registration.md"
      to: "docs/v1/requirements/agent/user-stories.md"
      via: "Related User Stories references"
      pattern: "US-001\|US-002"
    - from: "docs/v1/test scenarios/registration.md"
      to: "docs/v1/requirements/overseer/user-stories.md"
      via: "Related User Stories references"
      pattern: "US-100"
---

<objective>
Transform simplified descriptions and remove TODO section into 14+ structured test scenarios with explicit format change from numbered list + TODOs to structured format with name, preconditions, scenario steps, expected outcome, actual behavior, and related user stories.

Purpose: Provide detailed, executable test scenarios for registration procedures including edge cases, enabling comprehensive testing of both agent and overseer registration.

Output: Updated registration.md with 14+ test scenarios in structured format (transformed from numbered list with TODOs removed), covering happy paths, edge cases, and error handling. Each scenario has explicit "Actual Behavior" section.
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
@docs/v1/test scenarios/registration.md
@docs/v1/requirements/agent/user-stories.md
@docs/v1/requirements/overseer/user-stories.md
@docs/v1/endpoints/agents.md
@docs/v1/endpoints/overseers.md
</context>

<tasks>

<task type="auto">
  <name>Reformulate registration test scenarios with structured format including edge cases</name>
  <files>docs/v1/test scenarios/registration.md</files>
  <action>
    1. Read existing registration.md (currently has 3 overseer tests + 2 agent tests + TODOs for proper format)
    2. Reformulate each scenario using structured format from RESEARCH.md
    3. Remove TODO section once all scenarios are properly formatted

    Overseer scenarios to reformulate:
    - TS-R001: Overseer registration with new data (success)
    - TS-R002: Overseer registration with duplicate email (fail - expected error)
    - TS-R003: Overseer registration with Paddle customer data (load existing customer)
    - TS-R004: Overseer login with valid credentials (success)
    - TS-R005: Overseer login with invalid credentials (fail - expected error)
    - TS-R006: Overseer logout (success)

    Agent scenarios to reformulate:
    - TS-R007: Agent registration with new data (success)
    - TS-R008: Agent registration with duplicate public key (fail - expected error)
    - TS-R009: Agent login with valid DPoP JWT (success)
    - TS-R010: Agent login with invalid DPoP JWT (fail - expected error)
    - TS-R011: Agent logout (success)

    Edge case scenarios (add minimum 3):
    - TS-R012: Overseer registration with invalid email format (error case)
    - TS-R013: Agent registration with invalid public key format (error case)
    - TS-R014: Registration with missing required fields (error case)

    Structured format template:
    ```markdown
    ### TS-RXXX: [Scenario Name]

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

    Example for TS-R001:
    ```markdown
    ### TS-R001: Overseer Registration with New Data

    **Preconditions:**
    - [ ] No overseer account exists with this email
    - [ ] Email is valid format
    - [ ] Password meets security requirements

    **Scenario Steps:**
    1. User fills out registration form with email, name, password
    2. User submits form to POST /api/overseers/register
    3. Backend validates email format and password strength
    4. Backend hashes password using bcrypt
    5. Backend creates overseer record in database
    6. Backend returns 201 Created with overseer UUID

    **Expected Outcome:**
    - Overseer account created successfully
    - Overseer receives unique UUID
    - Password is hashed (not stored in plain text)
    - Response status is 201 Created
    - Can log in with provided credentials

    **Actual Behavior:**
    [Verified to work as expected - Phase 1 audit confirmed]

    **Related User Stories:**
    - US-100: Register as overseer using password method
    ```

    Example for TS-R002 (error case):
    ```markdown
    ### TS-R002: Overseer Registration with Duplicate Email

    **Preconditions:**
    - [ ] Overseer account already exists with test@example.com

    **Scenario Steps:**
    1. User attempts to register with email: test@example.com
    2. Backend checks if email already exists in database

    **Expected Outcome:**
    - Registration request rejected
    - Returns 409 Conflict error
    - Clear error message: "Email already registered"
    - No new account created

    **Actual Behavior:**
    [Verified to work as expected]

    **Related User Stories:**
    - US-100: Register as overseer using password method
    ```
  </action>
  <verify>grep -c "TS-R0" docs/v1/test\ scenarios/registration.md returns >= 14; grep -c "Preconditions:" docs/v1/test\ scenarios/registration.md returns >= 14; grep -c "Actual Behavior:" docs/v1/test\ scenarios/registration.md returns >= 14; grep -c "TODO" docs/v1/test\ scenarios/registration.md returns 0</verify>
  <done>14+ test scenarios in structured format covering happy paths, edge cases, and error handling; TODO section removed</done>
</task>

</tasks>

<verification>
- grep -c "TS-R0" docs/v1/test\ scenarios/registration.md >= 14
- grep -c "Preconditions:" docs/v1/test\ scenarios/registration.md >= 14
- grep -c "Scenario Steps:" docs/v1/test\ scenarios/registration.md >= 14
- grep -c "Expected Outcome:" docs/v1/test\ scenarios/registration.md >= 14
- grep -c "Actual Behavior:" docs/v1/test\ scenarios/registration.md >= 14
- grep -c "Related User Stories:" docs/v1/test\ scenarios/registration.md >= 14
- grep "409 Conflict\|400 Bad Request" docs/v1/test\ scenarios/registration.md | wc -l >= 3
- grep -c "TODO" docs/v1/test\ scenarios/registration.md = 0
</verification>

<success_criteria>
Registration test scenarios enhanced with:
- Structured format (name, preconditions, steps, expected outcome, actual behavior)
- 14+ scenarios covering both overseer and agent registration
- Related user story references
- Explicit error responses documented for negative cases
- Actual behavior documentation for verification gaps
- TODO section removed (all scenarios properly formatted)
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-04-TEST-SCENARIOS-REGISTRATION-SUMMARY.md`
</output>
