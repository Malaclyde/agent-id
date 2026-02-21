---
phase: 02-documentation-enhancement
plan: 05-test-scenarios-client
type: execute
wave: 2
depends_on:
  - 02-01-USER-STORIES-AGENT-PLAN
  - 02-02-USER-STORIES-OVERSEER-PLAN
files_modified:
  - docs/v1/test scenarios/client.md
autonomous: true

must_haves:
  truths:
    - "All client/OAuth test scenarios use structured format with name, preconditions, steps, expected outcome, actual behavior"
    - "All client/OAuth test scenarios reference related user stories"
    - "Minimum 10 client scenarios documented including edge cases"
    - "All scenarios have explicit expected outcomes and actual behavior documentation"
  artifacts:
    - path: "docs/v1/test scenarios/client.md"
      provides: "Structured client OAuth test scenarios with edge cases"
      contains: "TS-C0"
  key_links:
    - from: "docs/v1/test scenarios/client.md"
      to: "docs/v1/requirements/agent/user-stories.md"
      via: "Related User Stories references"
      pattern: "US-005\|US-006"
    - from: "docs/v1/test scenarios/client.md"
      to: "docs/v1/requirements/overseer/user-stories.md"
      via: "Related User Stories references"
      pattern: "US-107"
    - from: "docs/v1/test scenarios/client.md"
      to: "docs/v1/endpoints/clients.md"
      via: "Related Endpoints references"
      pattern: "POST /api/clients"
---

<objective>
Transform simple numbered descriptions into 15+ structured test scenarios with explicit format change from numbered list to structured format with name, preconditions, scenario steps, expected outcome, actual behavior, and related user stories.

Purpose: Provide detailed, executable test scenarios for client registration and OAuth flows including edge cases, enabling comprehensive testing of OAuth functionality.

Output: Updated client.md with 15+ test scenarios in structured format (transformed from numbered list), covering happy paths, edge cases, and error handling. Each scenario has explicit "Actual Behavior" section.
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
@docs/v1/test scenarios/client.md
@docs/v1/requirements/agent/user-stories.md
@docs/v1/requirements/overseer/user-stories.md
@docs/v1/endpoints/clients.md
@docs/v1/endpoints/oauth.md
</context>

<tasks>

<task type="auto">
  <name>Reformulate client/OAuth test scenarios with structured format including edge cases</name>
  <files>docs/v1/test scenarios/client.md</files>
  <action>
    1. Read existing client.md (currently has key assumptions + 4 agent tests + 2 overseer tests + 4 OAuth registration tests)
    2. Reformulate each scenario using structured format from RESEARCH.md

    Agent client scenarios to reformulate:
    - TS-C001: Unclaimed agent can't register client (error case - expected failure)
    - TS-C002: Claimed agent can register client (happy path)
    - TS-C003: Shadow-claimed agent can register client (happy path)
    - TS-C004: Agent respects tier limit (edge case - max clients reached)

    Overseer client scenarios to reformulate:
    - TS-C005: Tier limit enforcement (edge case - max clients reached by overseer)
    - TS-C006: Shared client limit across overseer + claimed agents (complex edge case)

    OAuth registration scenarios (from existing content):
    - TS-C007: Overseer A registers client C1, all agents use it (happy path)
    - TS-C008: Overseer B registers client C2, all agents use it (happy path)
    - TS-C009: Claimed agents register their own clients (happy path)
    - TS-C010: Unclaimed agent limited to 10 registrations (FREE tier edge case)

    Add edge case scenarios (minimum 5):
    - TS-C011: Client registration with invalid redirect URI (error case)
    - TS-C012: Client registration with duplicate client_id (error case)
    - TS-C013: OAuth flow with unauthorized client (error case)
    - TS-C014: OAuth flow with expired authorization code (error case)
    - TS-C015: Client marked for cancellation cannot complete OAuth flow (edge case)

    Structured format template:
    ```markdown
    ### TS-CXXX: [Scenario Name]

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

    Example for TS-C001:
    ```markdown
    ### TS-C001: Unclaimed Agent Cannot Register Client

    **Preconditions:**
    - [ ] Agent has registered account
    - [ ] Agent is not claimed by any overseer
    - [ ] Agent has valid DPoP JWT or session ID

    **Scenario Steps:**
    1. Agent attempts to register OAuth client via POST /api/clients
    2. Backend checks agent's oversight status
    3. Backend determines agent is unclaimed

    **Expected Outcome:**
    - Client registration request rejected
    - Returns 403 Forbidden error
    - Clear error message: "Only claimed agents can register OAuth clients"
    - No client record created

    **Actual Behavior:**
    [Verified to work as expected - assumption from existing documentation]

    **Related User Stories:**
    - US-005: Register OAuth client using session ID (if claimed)
    - US-006: Register OAuth client using DPoP JWT (if claimed)
    ```

    Example for TS-C007 (OAuth flow):
    ```markdown
    ### TS-C007: OAuth Flow with Overseer's Client Registration

    **Preconditions:**
    - [ ] Overseer A has registered and claimed agents B and C
    - [ ] Overseer A has registered client C1 via POST /api/clients
    - [ ] Client C1 has valid redirect_uri and client_id
    - [ ] Overseer's subscription allows OAuth flows

    **Scenario Steps:**
    1. External client initiates OAuth flow with client_id=C1, redirect_uri to C1's URI
    2. System redirects to POST /api/oauth/authorize with client payload
    3. Agent (B or C) initiates authorization by posting to /api/authorize with DPoP JWT
    4. Backend validates client_id and redirect_uri match registered client C1
    5. Backend checks agent is claimed by overseer who owns client C1
    6. Backend creates authorization code with PKCE verifier
    7. Backend returns authorization code to external client via redirect
    8. External client exchanges authorization code for access token via POST /api/oauth/token

    **Expected Outcome:**
    - Authorization code generated and returned
    - Access token issued to external client
    - OAuth flow completes successfully for all agents (B and C)
    - Agent identity verified in access token claims

    **Actual Behavior:**
    [To be verified during testing - marked as assumption]

    **Related User Stories:**
    - US-009: Initiate OAuth authorization procedure (agent)
    - US-011: Return authorization code to requesting client (agent)
    - US-107: Register OAuth client (overseer)
    ```
  </action>
  <verify>grep -c "TS-C0" docs/v1/test\ scenarios/client.md returns >= 15; grep -c "Preconditions:" docs/v1/test\ scenarios/client.md returns >= 15; grep -c "Actual Behavior:" docs/v1/test\ scenarios/client.md returns >= 15</verify>
  <done>15+ test scenarios in structured format covering client registration, OAuth flows, and edge cases</done>
</task>

</tasks>

<verification>
- grep -c "TS-C0" docs/v1/test\ scenarios/client.md >= 15
- grep -c "Preconditions:" docs/v1/test\ scenarios/client.md >= 15
- grep -c "Scenario Steps:" docs/v1/test\ scenarios/client.md >= 15
- grep -c "Expected Outcome:" docs/v1/test\ scenarios/client.md >= 15
- grep -c "Actual Behavior:" docs/v1/test\ scenarios/client.md >= 15
- grep -c "Related User Stories:" docs/v1/test\ scenarios/client.md >= 15
- grep "403 Forbidden\|400 Bad Request\|401 Unauthorized" docs/v1/test\ scenarios/client.md | wc -l >= 3
</verification>

<success_criteria>
Client/OAuth test scenarios enhanced with:
- Structured format (name, preconditions, steps, expected outcome, actual behavior)
- 15+ scenarios covering client registration, OAuth flows, and edge cases
- Related user story references
- Explicit error responses documented for negative cases
- Actual behavior documentation for verification gaps
- Complex scenarios (shared client limits, OAuth flows) properly documented
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-05-TEST-SCENARIOS-CLIENT-SUMMARY.md`
</output>
