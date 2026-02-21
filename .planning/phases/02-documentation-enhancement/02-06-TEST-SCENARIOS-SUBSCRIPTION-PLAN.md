---
phase: 02-documentation-enhancement
plan: 06-test-scenarios-subscription
type: execute
wave: 2
depends_on:
  - 02-02-USER-STORIES-OVERSEER-PLAN
files_modified:
  - docs/v1/test scenarios/subscription.md
autonomous: true

must_haves:
  truths:
    - "All subscription test scenarios use structured format with name, preconditions, steps, expected outcome, actual behavior"
    - "All subscription test scenarios reference related user stories"
    - "Minimum 12 subscription scenarios documented including edge cases"
    - "All scenarios have explicit expected outcomes and actual behavior documentation"
  artifacts:
    - path: "docs/v1/test scenarios/subscription.md"
      provides: "Structured subscription test scenarios with edge cases"
      contains: "TS-S0"
  key_links:
    - from: "docs/v1/test scenarios/subscription.md"
      to: "docs/v1/requirements/overseer/user-stories.md"
      via: "Related User Stories references"
      pattern: "US-111\|US-112\|US-113\|US-118\|US-119\|US-120\|US-121\|US-122\|US-123"
    - from: "docs/v1/test scenarios/subscription.md"
      to: "docs/v1/endpoints/subscriptions.md"
      via: "Related Endpoints references"
      pattern: "POST /api/.*"
---

<objective>
Populate empty subscription.md file with 16+ structured test scenarios with explicit format creation from empty file to structured format with name, preconditions, scenario steps, expected outcome, actual behavior, and related user stories.

Purpose: Provide detailed, executable test scenarios for subscription procedures including payment processing, tier changes, cancellations, and webhook handling, enabling comprehensive testing of subscription functionality.

Output: Updated subscription.md with 16+ test scenarios in structured format (created from empty 0-byte file), covering happy paths, edge cases, and error handling. Each scenario has explicit "Actual Behavior" section.
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
@docs/v1/test scenarios/subscription.md
@docs/v1/requirements/overseer/user-stories.md
@docs/v1/endpoints/subscriptions.md
@docs/v1/endpoints/webhooks.md
</context>

<tasks>

<task type="auto">
  <name>Create subscription test scenarios with structured format including edge cases</name>
  <files>docs/v1/test scenarios/subscription.md</files>
  <action>
    1. Read existing subscription.md (currently empty - 0 bytes)
    2. Create subscription test scenarios using structured format from RESEARCH.md

    Subscription scenarios to create (12+):

    Subscription Management Scenarios:
    - TS-S001: Overseer changes subscription tier (upgrade/downgrade)
    - TS-S002: Overseer renews subscription
    - TS-S003: Overseer cancels subscription
    - TS-S004: Overseer queries subscription information via /me endpoint
    - TS-S005: Subscription grace period access (after cancellation)
    - TS-S006: Agent accesses subscription features when claimed

    Paddle Webhook Scenarios:
    - TS-S007: Paddle customer.created webhook received
    - TS-S008: Paddle payment.succeeded webhook received
    - TS-S009: Paddle subscription.activated webhook received
    - TS-S010: Paddle subscription.updated webhook received
    - TS-S011: Paddle subscription.cancelled webhook received
    - TS-S012: Paddle payment.shadow_claim_succeeded webhook received

    Edge Case Scenarios:
    - TS-S013: Payment failure during subscription change
    - TS-S014: Duplicate webhook event (idempotency)
    - TS-S015: Webhook received with expired/invalid signature
    - TS-S016: Subscription tier limit reached (max agents)

    Structured format template:
    ```markdown
    ### TS-SXXX: [Scenario Name]

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

    Example for TS-S001:
    ```markdown
    ### TS-S001: Overseer Changes Subscription Tier

    **Preconditions:**
    - [ ] Overseer has active subscription (FREE or paid tier)
    - [ ] Overseer is logged in with valid session
    - [ ] Overseer has valid payment method in Paddle

    **Scenario Steps:**
    1. Overseer navigates to subscription management in dashboard
    2. Overseer selects new tier (upgrade from FREE to PAID or downgrade)
    3. Overseer confirms change via POST /api/subscriptions/change with new tier details
    4. Backend validates tier availability and payment method
    5. Backend initiates Paddle checkout if payment required
    6. Overseer completes payment in Paddle checkout flow
    7. Paddle sends payment.succeeded webhook
    8. Backend processes webhook and updates subscription tier
    9. Backend adjusts OAuth client limits based on new tier

    **Expected Outcome:**
    - Subscription tier updated in database
    - New billing period starts
    - OAuth client limits adjusted immediately
    - Overseer can access new tier features
    - If downgrade: limits reduced, no access loss for existing registrations

    **Actual Behavior:**
    [To be verified during testing - marked as assumption]

    **Related User Stories:**
    - US-111: Change subscription (upgrade/downgrade)
    - US-119: Receive Paddle payment.succeeded webhook
    - US-120: Receive Paddle subscription.updated webhook
    ```

    Example for TS-S007 (Webhook):
    ```markdown
    ### TS-S007: Paddle customer.created Webhook Received

    **Preconditions:**
    - [ ] Overseer initiates first payment through Paddle checkout
    - [ ] Paddle creates new customer record
    - [ ] Paddle webhook endpoint configured: https://api.example.com/webhooks/paddle

    **Scenario Steps:**
    1. Overseer completes payment in Paddle checkout for first time
    2. Paddle creates customer record with customer email and customer ID
    3. Paddle sends POST request to /webhooks/paddle with event_type: "customer.created"
    4. Backend verifies Paddle signature header (currently broken - see webhooks.md)
    5. Backend extracts customer email and Paddle customer ID from webhook payload
    6. Backend finds overseer record by email
    7. Backend updates overseer record with paddle_customer_id

    **Expected Outcome:**
    - Overseer record updated with paddle_customer_id
    - Future webhooks can link payments to overseer via customer ID
    - Customer creation logged for audit
    - Returns 200 OK with { success: true, received: true }

    **Actual Behavior:**
    [To be verified during testing - signature validation may fail]

    **Related User Stories:**
    - US-118: Receive Paddle customer.created webhook
    ```

    Example for TS-S012 (Shadow Claim):
    ```markdown
    ### TS-S012: Paddle payment.shadow_claim_succeeded Webhook Received

    **Preconditions:**
    - [ ] Agent initiated shadow claim via POST /api/agents/malice/:agentId
    - [ ] Agent completed payment via shadow claim payment page
    - [ ] Paddle processed payment successfully
    - [ ] Shadow overseer created but not yet activated

    **Scenario Steps:**
    1. Paddle sends POST request to /webhooks/paddle with event_type: "payment.shadow_claim_succeeded"
    2. Backend verifies Paddle signature header (currently broken)
    3. Backend extracts agent_id, shadow_overseer_id, payment_reference, billing_period_end from webhook payload
    4. Backend finds agent record by agent_id
    5. Backend finds shadow overseer record by shadow_overseer_id
    6. Backend creates oversight relationship between agent and shadow overseer
    7. Backend sets agent's billing_period_end
    8. Backend resets agent's oauth_count to 0
    9. Backend activates shadow overseer subscription

    **Expected Outcome:**
    - Oversight relationship created (agent claimed by shadow overseer)
    - Agent's billing_period_end set to subscription period end
    - Agent's oauth_count reset to 0 (new OAuth period)
    - Shadow overseer subscription activated
    - Agent can now register OAuth clients per shadow overseer's tier
    - Returns 200 OK with { success: true, received: true }

    **Actual Behavior:**
    [To be verified during testing - shadow claim flow not fully tested]

    **Related User Stories:**
    - US-123: Handle Paddle payment.shadow_claim_succeeded webhook
    ```
  </action>
  <verify>grep -c "TS-S0" docs/v1/test\ scenarios/subscription.md returns >= 16; grep -c "Preconditions:" docs/v1/test\ scenarios/subscription.md returns >= 16; grep -c "Actual Behavior:" docs/v1/test\ scenarios/subscription.md returns >= 16</verify>
  <done>16+ test scenarios in structured format covering subscription management, Paddle webhooks, and edge cases</done>
</task>

</tasks>

<verification>
- grep -c "TS-S0" docs/v1/test\ scenarios/subscription.md >= 16
- grep -c "Preconditions:" docs/v1/test\ scenarios/subscription.md >= 16
- grep -c "Scenario Steps:" docs/v1/test\ scenarios/subscription.md >= 16
- grep -c "Expected Outcome:" docs/v1/test\ scenarios/subscription.md >= 16
- grep -c "Actual Behavior:" docs/v1/test\ scenarios/subscription.md >= 16
- grep -c "Related User Stories:" docs/v1/test\ scenarios/subscription.md >= 16
- grep "200 OK\|400 Bad Request\|401 Unauthorized" docs/v1/test\ scenarios/subscription.md | wc -l >= 3
</verification>

<success_criteria>
Subscription test scenarios created with:
- Structured format (name, preconditions, steps, expected outcome, actual behavior)
- 16+ scenarios covering subscription management, Paddle webhooks, and edge cases
- Related user story references
- Explicit error responses documented for negative cases
- Actual behavior documentation for verification gaps
- Empty subscription.md file populated with comprehensive test scenarios
</success_criteria>

<output>
After completion, create `.planning/phases/02-documentation-enhancement/02-06-TEST-SCENARIOS-SUBSCRIPTION-SUMMARY.md`
</output>
