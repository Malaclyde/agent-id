---
phase: 02-documentation-enhancement
plan: 01-user-stories-agent
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/v1/requirements/agent/user-stories.md
  - docs/v1/requirements/agent/claim.md
autonomous: true

must_haves:
  truths:
    - "All agent user stories follow WHO-WHAT-WHY template format"
    - "All agent user stories have acceptance criteria (minimum 3 per story)"
    - "All agent user stories reference related endpoints from Phase 1"
    - "All v1 agent features have corresponding user stories including OAuth token management"
  artifacts:
    - path: "docs/v1/requirements/agent/user-stories.md"
      provides: "Reformatted agent user stories with acceptance criteria"
      contains: "US-00"
    - path: "docs/v1/requirements/agent/claim.md"
      provides: "Claim-related agent user stories with acceptance criteria"
      contains: "US-00"
  key_links:
    - from: "docs/v1/requirements/agent/user-stories.md"
      to: "docs/v1/endpoints/agents.md"
      via: "Related Endpoints references"
      pattern: "- `POST /api/.*` - .*"
---

<objective>
Reformulate all agent user stories using WHO-WHAT-WHY template with acceptance criteria and related endpoint references.

Purpose: Provide clear, verifiable acceptance criteria for all agent features, enabling developers and testers to understand expected behavior.

Output: Updated user-stories.md with 19+ user stories in proper format, each with 3+ acceptance criteria and endpoint references including OAuth token management stories.
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
@docs/v1/requirements/agent/user-stories.md
@docs/v1/endpoints/agents.md
@docs/v1/endpoints/oauth.md
</context>

<tasks>

<task type="auto">
  <name>Reformulate agent user stories with WHO-WHAT-WHY template and acceptance criteria</name>
  <files>docs/v1/requirements/agent/user-stories.md</files>
  <action>
    1. Read existing user-stories.md (currently has simple bullet lists)
    2. Reformulate each story using WHO-WHAT-WHY template:
       "As a [WHO], I want [WHAT], so that [WHY]"
    3. Add acceptance criteria for each story (minimum 3 criteria per story)
    4. Add "Related Endpoints" section referencing docs/v1/endpoints/agents.md
    5. Number stories sequentially (US-001, US-002, etc.)

    Stories to reformulate (from existing content):
    - US-001: Register as an agent (initiate registration with name and public key)
    - US-002: Complete agent registration (sign challenge)
    - US-003: Log in as agent using DPoP JWT
    - US-004: Log out as agent
    - US-005: Register OAuth client using session ID (if claimed)
    - US-006: Register OAuth client using DPoP JWT (if claimed)
    - US-007: Respond to overseer claim with session ID
    - US-008: Respond to overseer claim with DPoP JWT
    - US-009: Initiate OAuth authorization procedure (send client payload to /authorize) with DPoP JWT
    - US-010: Initiate OAuth authorization with session ID
    - US-011: Return authorization code to requesting client
    - US-012: Query agent information (/me endpoint)
    - US-013: Reject/renounce current overseer

    Add missing user stories (based on Phase 1 endpoint documentation):
     - US-014: Initiate key rotation (start key replacement process)
     - US-015: Complete key rotation (replace public key with new signature)
     - US-016: Exchange OAuth authorization code for access token
     - US-017: Refresh OAuth access token using refresh token
     - US-018: Revoke OAuth access or refresh token
     - US-019: Introspect OAuth token status

    Format template per RESEARCH.md:
    ```markdown
    ### US-XXX: [Story Title]

    **As a** [WHO],
    **I want** [WHAT],
    **so that** [WHY].

    **Acceptance Criteria:**
    - [ ] Criterion 1
    - [ ] Criterion 2
    - [ ] Criterion 3

    **Related Endpoints:**
    - `METHOD /api/endpoint` - Purpose
    ```
  </action>
  <verify>grep -c "US-00" docs/v1/requirements/agent/user-stories.md returns >= 19; grep -c "Acceptance Criteria:" docs/v1/requirements/agent/user-stories.md returns >= 19</verify>
  <done>19+ user stories in WHO-WHAT-WHY format with 3+ acceptance criteria each and endpoint references</done>
</task>

<task type="auto">
  <name>Create claim-specific user stories with acceptance criteria</name>
  <files>docs/v1/requirements/agent/claim.md</files>
  <action>
    1. Read claim.md (currently verified accurate from Phase 1)
    2. Extract agent-side claim procedures into user stories
    3. Create user stories for:
       - US-C001: Respond to overseer claim initiation
       - US-C002: Reject overseer claim
       - US-C003: Renounce existing overseer relationship

    4. Format each with WHO-WHAT-WHY template, acceptance criteria, and endpoint references

    Example format:
    ```markdown
    ### US-C001: Respond to Overseer Claim

    **As an** agent that has received a claim request from an overseer,
    **I want** to respond to the claim by signing the challenge,
    **so that** I can establish oversight relationship and access subscription features.

    **Acceptance Criteria:**
    - [ ] Agent can post DPoP JWT to claim challenge URL
    - [ ] Agent can post session ID to claim challenge URL
    - [ ] Backend creates oversight record on successful response
    - [ ] Agent receives confirmation of successful claim acceptance

    **Related Endpoints:**
    - `POST /api/agents/claim/:challengeId` - Respond to overseer claim
    ```
  </action>
  <verify>grep -c "US-C0" docs/v1/requirements/agent/claim.md returns >= 3; grep -c "Acceptance Criteria:" docs/v1/requirements/agent/claim.md returns >= 3</verify>
  <done>3 claim-specific user stories with acceptance criteria and endpoint references</done>
</task>

</tasks>

<verification>
- grep -c "US-00" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "As a" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "I want" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "so that" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "Acceptance Criteria:" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "Related Endpoints:" docs/v1/requirements/agent/user-stories.md >= 19
- grep -c "US-C0" docs/v1/requirements/agent/claim.md >= 3
</verification>

<success_criteria>
All agent user stories reformatted with:
- WHO-WHAT-WHY template format
- 3+ acceptance criteria per story
- Related endpoint references from Phase 1 documentation
- 19+ user stories covering all agent features including OAuth token management
- 3 claim-specific stories in claim.md
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-01-USER-STORIES-AGENT-SUMMARY.md`
</output>
