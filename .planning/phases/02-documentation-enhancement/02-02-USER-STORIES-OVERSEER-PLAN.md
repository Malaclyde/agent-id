---
phase: 02-documentation-enhancement
plan: 02-user-stories-overseer
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/v1/requirements/overseer/user-stories.md
autonomous: true

must_haves:
  truths:
    - "All overseer user stories follow WHO-WHAT-WHY template format"
    - "All overseer user stories have acceptance criteria (minimum 3 per story)"
    - "All overseer user stories reference related endpoints from Phase 1"
    - "All v1 overseer features have corresponding user stories"
  artifacts:
    - path: "docs/v1/requirements/overseer/user-stories.md"
      provides: "Reformatted overseer user stories with acceptance criteria"
      contains: "US-0"
  key_links:
    - from: "docs/v1/requirements/overseer/user-stories.md"
      to: "docs/v1/endpoints/overseers.md"
      via: "Related Endpoints references"
      pattern: "- `POST /api/.*` - .*"
    - from: "docs/v1/requirements/overseer/user-stories.md"
      to: "docs/v1/endpoints/clients.md"
      via: "Related Endpoints references"
      pattern: "- `POST /api/.*` - .*"
    - from: "docs/v1/requirements/overseer/user-stories.md"
      to: "docs/v1/endpoints/subscriptions.md"
      via: "Related Endpoints references"
      pattern: "- `POST /api/.*` - .*"
---

<objective>
Reformulate all overseer user stories using WHO-WHAT-WHY template with acceptance criteria and related endpoint references.

Purpose: Provide clear, verifiable acceptance criteria for all overseer features, enabling developers and testers to understand expected behavior.

Output: Updated user-stories.md with 23+ user stories in proper format, each with 3+ acceptance criteria and endpoint references including Paddle webhook stories.
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
@docs/v1/requirements/overseer/user-stories.md
@docs/v1/endpoints/overseers.md
@docs/v1/endpoints/clients.md
@docs/v1/endpoints/subscriptions.md
</context>

<tasks>

<task type="auto">
  <name>Reformulate overseer user stories with WHO-WHAT-WHY template and acceptance criteria</name>
  <files>docs/v1/requirements/overseer/user-stories.md</files>
  <action>
    1. Read existing user-stories.md (currently has simple bullet lists)
    2. Reformulate each story using WHO-WHAT-WHY template:
       "As a [WHO], I want [WHAT], so that [WHY]"
    3. Add acceptance criteria for each story (minimum 3 criteria per story)
    4. Add "Related Endpoints" section referencing docs/v1/endpoints/overseers.md, clients.md, subscriptions.md
    5. Number stories sequentially (US-100, US-101, etc. - using 100+ to distinguish from agent stories)

    Stories to reformulate (from existing content):
    - US-100: Register as overseer using password method
    - US-101: Register as overseer using OAuth service (future, mark as [PLANNED])
    - US-102: Log in as overseer using password method
    - US-103: Log in as overseer using OAuth method (future, mark as [PLANNED])
    - US-104: Log out as overseer
    - US-105: Initiate agent claim
    - US-106: Declaim agent (end oversight)
    - US-107: Register OAuth client
    - US-108: Mark claimed agent for cancellation
    - US-109: Mark client registration for cancellation
    - US-110: Deactivate client registration
    - US-111: Change subscription (upgrade/downgrade)
    - US-112: Cancel subscription
    - US-113: Renew subscription
    - US-114: Query overseer information (/me endpoint)

    Add missing user stories (based on Phase 1 endpoint documentation):
    - US-115: Block OAuth client (prevent OAuth flow with specific client)
    - US-116: Allow OAuth client (unblock)
    - US-117: View OAuth activity (list recent OAuth authorizations)
    - US-118: Receive Paddle customer.created webhook
    - US-119: Receive Paddle payment.succeeded webhook
    - US-120: Receive Paddle subscription.activated webhook
    - US-121: Receive Paddle subscription.updated webhook
    - US-122: Receive Paddle subscription.cancelled webhook
    - US-123: Handle Paddle payment.shadow_claim_succeeded webhook

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

    Note: Mark OAuth registration/login stories with [PLANNED] tag as these are not yet implemented.
  </action>
  <verify>grep -c "US-1" docs/v1/requirements/overseer/user-stories.md returns >= 23; grep -c "Acceptance Criteria:" docs/v1/requirements/overseer/user-stories.md returns >= 23</verify>
  <done>23+ user stories in WHO-WHAT-WHY format with 3+ acceptance criteria each and endpoint references</done>
</task>

</tasks>

<verification>
- grep -c "US-1" docs/v1/requirements/overseer/user-stories.md >= 23
- grep -c "As a" docs/v1/requirements/overseer/user-stories.md >= 23
- grep -c "I want" docs/v1/requirements/overseer/user-stories.md >= 23
- grep -c "so that" docs/v1/requirements/overseer/user-stories.md >= 23
- grep -c "Acceptance Criteria:" docs/v1/requirements/overseer/user-stories.md >= 23
- grep -c "Related Endpoints:" docs/v1/requirements/overseer/user-stories.md >= 23
- grep "PLANNED" docs/v1/requirements/overseer/user-stories.md | grep -c "101\|103" returns 2 (OAuth stories marked)
</verification>

<success_criteria>
All overseer user stories reformatted with:
- WHO-WHAT-WHY template format
- 3+ acceptance criteria per story
- Related endpoint references from Phase 1 documentation
- 23+ user stories covering all overseer features including Paddle webhook handling
- Future OAuth stories marked with [PLANNED] tag
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-02-USER-STORIES-OVERSEER-SUMMARY.md`
</output>
