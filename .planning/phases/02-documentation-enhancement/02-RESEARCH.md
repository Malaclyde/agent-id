# Phase 2: Documentation Enhancement - Research

**Researched:** 2026-02-14
**Domain:** User story documentation, test scenario documentation, requirements enhancement
**Confidence:** HIGH

## Summary

This research investigates how to effectively plan Phase 2: Documentation Enhancement for the Agent-ID project. The phase requires improving requirements documentation with properly formatted user stories and comprehensive testing scenarios.

**Current State Analysis:**
- User stories exist but lack proper formatting and acceptance criteria
- Test scenarios are written as simple lists without structured format
- Registration.md explicitly has TODOs for proper test scenario formatting
- Phase 1 audit identified 40+ endpoints across 6 route files
- Backend features documented in Phase 1 need corresponding user stories
- Edge cases and error handling scenarios are not documented

**Primary recommendation:** Use the standard user story template ("As a <WHO>, I want <WHAT> so that <WHY>") with acceptance criteria, and implement structured test scenario documentation with name, scenario steps, expected outcome, and actual behavior sections.

## Standard Stack

### Core Documentation Standards

| Standard/Format | Purpose | Why Standard |
|-----------------|---------|--------------|
| User Story Template | "As a <WHO>, I want <WHAT> so that <WHY>" | Industry standard for agile requirements |
| Acceptance Criteria | Conditions of satisfaction for each story | Defines completion criteria |
| Markdown | Documentation format | Version-controlled, GitHub-native |
| Test Scenario Format | Structured test documentation | Consistent testing approach |

### User Story Components

| Component | Description | When to Use |
|------------|-------------|---------------|
| Card | Written description (WHO-WHAT-WHY) | Planning, as reminder |
| Conversation | Discussions about story | Flesh out details |
| Confirmation | Tests/acceptance criteria | Define completion |

### Test Scenario Components

| Component | Description | Required |
|------------|-------------|------------|
| Name | Unique scenario identifier | Yes |
| Scenario Steps | Step-by-step procedure | Yes |
| Expected Outcome | What should happen | Yes |
| Actual Behavior | Current implementation behavior | Yes (for gaps) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| WHO-WHAT-WHY template | Job stories | Job stories for product discovery, user stories for features |
| Markdown | Google Docs | Markdown provides version control |

## Architecture Patterns

### Recommended Documentation Structure

```
docs/v1/
├── requirements/
│   ├── agent/
│   │   ├── user-stories.md         # Reformatted with acceptance criteria
│   │   └── claim.md               # VERIFIED in Phase 1
│   ├── overseer/
│   │   └── user-stories.md         # Reformatted with acceptance criteria
│   └── subscription/
│       ├── subscription-model.md      # Marked OUTDATED in Phase 1
│       └── subscription-provider.md  # VERIFIED in Phase 1
└── test scenarios/
    ├── claim.md                     # Structured format
    ├── client.md                    # Structured format
    ├── registration.md               # Structured format
    └── subscription.md             # Structured format
```

### Pattern 1: User Story with Acceptance Criteria
**What:** Standardized format for documenting requirements
**When to use:** All user-facing features

**Template:**
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

**Example:**
```markdown
### US-001: Register as an Agent

**As an** entity that wants to create an agent account,
**I want** to register as an agent,
**so that** I can authenticate with Ed25519 cryptographic keys.

**Acceptance Criteria:**
- [ ] Agent can initiate registration with name and Ed25519 public key
- [ ] System returns a challenge that must be signed
- [ ] Agent can complete registration by signing the challenge
- [ ] Agent receives a unique agent UUID
- [ ] Cannot register with duplicate public key
- [ ] Agent can log in using DPoP JWT after registration

**Related Endpoints:**
- `POST /api/agents/register/initiate` - Start registration
- `POST /api/agents/register/complete/:challengeId` - Complete registration
- `POST /api/agents/login` - Login with DPoP
```

### Pattern 2: Structured Test Scenario
**What:** Consistent format for test documentation
**When to use:** All test scenarios

**Template:**
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
[Document if different from expected]

**Related User Stories:**
- US-XXX
```

**Example:**
```markdown
### TS-001: Overseer Claims Unclaimed Agent

**Preconditions:**
- [ ] Overseer has registered account
- [ ] Overseer is logged in with valid session
- [ ] Agent has registered account
- [ ] Agent is not currently claimed
- [ ] Overseer has paid subscription tier (not FREE)

**Scenario Steps:**
1. Overseer clicks "claim agent" in dashboard
2. Overseer provides agent ID
3. Backend initiates claim challenge
4. Overseer receives claim challenge URL
5. Overseer gives URL to agent
6. Agent posts DPoP JWT to claim challenge URL
7. Backend creates oversight record
8. Dashboard displays claim completed

**Expected Outcome:**
- Oversight record created in database
- Agent now has overseer relationship
- Dashboard shows claim completed status
- Agent can now access subscription features

**Actual Behavior:**
[Verified to work as expected]

**Related User Stories:**
- US-005: Claim ownership of agent
```

### Pattern 3: Edge Case Test Scenario
**What:** Document boundary conditions and unusual inputs
**When to use:** Minimum 10 edge cases required

**Template:**
```markdown
### Edge Case: [Name]

**Description:** What unusual condition this tests

**Scenario Steps:**
1. [Steps]

**Expected Behavior:** System handles gracefully

**Error Handling:** Expected error code/message
```

**Example:**
```markdown
### Edge Case: Claim Already Claimed Agent

**Description:** Overseer attempts to claim agent already claimed by another overseer

**Scenario Steps:**
1. Overseer A has claimed Agent X
2. Overseer B attempts to claim Agent X
3. Backend processes claim request

**Expected Behavior:**
- Claim request rejected
- Returns 409 Conflict error
- Clear error message: "Agent is already claimed"
- No changes to oversight table

**Error Handling:**
- HTTP 409 Conflict
- Error body: `{ "error": "Agent already claimed by another overseer" }`
```

### Anti-Patterns to Avoid

- **Vague user stories:** "As a user, I can do things" - too generic
- **Missing acceptance criteria:** No way to verify completion
- **Test scenarios without expected outcomes:** Can't verify pass/fail
- **Incomplete test scenario steps:** Ambiguous test procedures
- **No preconditions:** Tests fail due to missing setup

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| User story format | Custom formats | WHO-WHAT-WHY template | Industry standard, well-understood |
| Acceptance criteria | Ad-hoc lists | Condition of satisfaction format | Clear completion criteria |
| Test documentation | Narrative descriptions | Structured scenario format | Consistent, executable |
| Test numbering | Random IDs | Sequential prefixes (US-XXX, TS-XXX) | Organized, traceable |

**Key insight:** Documentation standards exist for a reason. Using established patterns makes documentation maintainable and understandable.

## Common Pitfalls

### Pitfall 1: User Stories Without Acceptance Criteria
**What goes wrong:** No clear definition of "done"
**Why it happens:** Authors forget to add conditions of satisfaction
**How to avoid:** Always include at least 3 acceptance criteria per story
**Warning signs:** Story only has WHO-WHAT-WHY, no completion checks

### Pitfall 2: Test Scenarios as Simple Lists
**What goes wrong:** Test steps not clear, expected outcomes missing
**Why it happens:** Writing tests quickly without structure
**How to avoid:** Use structured format with name, steps, expected outcome
**Warning signs:** Test scenarios are numbered lists without clear sections

### Pitfall 3: Missing Edge Cases
**What goes wrong:** Production bugs from boundary conditions
**Why it happens:** Focus on happy path, forget edge cases
**How to avoid:** Systematically list edge cases (empty inputs, invalid values, limits)
**Warning signs:** All tests pass in development, fail in production

### Pitfall 4: No Expected vs Actual Behavior
**What goes wrong:** Can't identify implementation gaps
**Why it happens:** Only documenting expected behavior
**How to avoid:** Always document what actually happens vs what should
**Warning signs:** Test scenarios don't have "actual behavior" section

### Pitfall 5: Inconsistent Formatting
**What goes wrong:** Hard to read and maintain documentation
**Why it happens:** Different authors use different styles
**How to avoid:** Use templates consistently, follow examples
**Warning signs:** Documentation has inconsistent heading levels, spacing, terminology

## Code Examples

### User Story Reformatted from Existing

**Before (docs/v1/requirements/agent/user-stories.md):**
```markdown
As an entity that wants to create an agent account, i can:
- register as an agent

As an agent, I can:
- log in using a dpop JWT
- log out
```

**After (reformatted):**
```markdown
### US-001: Register as an Agent

**As an** entity that wants to create an agent account,
**I want** to register as an agent,
**so that** I can authenticate with Ed25519 cryptographic keys.

**Acceptance Criteria:**
- [ ] Can initiate registration with name and public key
- [ ] Receive and complete registration challenge
- [ ] Receive unique agent UUID upon completion
- [ ] Public key is unique (duplicate keys rejected)

**Related Endpoints:**
- `POST /api/agents/register/initiate`
- `POST /api/agents/register/complete/:challengeId`
```

### Test Scenario Reformatted from Existing

**Before (docs/v1/test scenarios/claim.md):**
```markdown
1. An overseer claims an unclaimed agent
```

**After (reformatted):**
```markdown
### TS-001: Overseer Claims Unclaimed Agent

**Preconditions:**
- [ ] Overseer has registered account with paid subscription
- [ ] Overseer is logged in
- [ ] Agent has registered account
- [ ] Agent is unclaimed

**Scenario Steps:**
1. Overseer initiates claim for agent via dashboard
2. Backend creates claim challenge
3. Overseer receives claim challenge URL
4. Agent signs challenge with DPoP JWT
5. Backend creates oversight record

**Expected Outcome:**
- Oversight record created in database
- Agent now associated with overseer
- Overseer dashboard shows claim completed

**Actual Behavior:**
[To be verified during testing]

**Related User Stories:**
- US-005: Initiate agent claim (overseer)
- US-006: Respond to claim initiated by overseer (agent)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Simple user story lists | Structured format with acceptance criteria | 2000s | Clear completion criteria |
| Narrative test cases | Structured scenarios with preconditions/steps/expected | 2010s | Executable, verifiable tests |
| Ad-hoc documentation | Template-driven documentation | 2015s | Consistency, maintainability |

**Deprecated/outdated:**
- Use cases (replaced by user stories for agile)
- Narrative test documentation (replaced by structured scenarios)
- Requirements documents (replaced by user stories and acceptance criteria)

## Open Questions

1. **User Story Scope**
   - What we know: Need to cover all v1 features
   - What's unclear: Granularity of stories (epics vs individual stories)
   - Recommendation: Start with epics, decompose into stories as needed

2. **Test Scenario Execution**
   - What we know: Need structured scenarios
   - What's unclear: Whether to execute tests during this phase
   - Recommendation: This phase documents scenarios, execution in later phase

3. **Edge Case Minimum**
   - What we know: Requirement states minimum 10 edge cases
   - What's unclear: What counts as an edge case
   - Recommendation: Focus on boundary conditions, invalid inputs, rate limits

## Sources

### Primary (HIGH confidence)
- Mountain Goat Software (Mike Cohn) - User story template and best practices
- Atlassian - Agile and Scrum documentation practices
- Phase 1 research - Endpoint inventory and feature list
- Existing documentation - Current state of user stories and test scenarios

### Secondary (MEDIUM confidence)
- ISTQB glossary - Testing terminology (attempted, 404)
- Industry standard practices - User stories and test scenario documentation

### Tertiary (LOW confidence)
- None - All findings verified from primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Industry-standard user story template widely used
- Architecture: HIGH - Based on existing documentation structure and Phase 1 audit
- Pitfalls: HIGH - Common documentation anti-patterns well-documented

**Research date:** 2026-02-14
**Valid until:** 2026-03-14 (30 days for stable domain)

## Key Findings for Planner

### Must Document (Critical Path)

**User Stories:**
1. **Agent Features** (15+ user stories needed)
   - Registration (initiate/complete)
   - Login/logout with DPoP
   - OAuth client registration (claimed agent)
   - Claim response (session ID/DPoP JWT)
   - Authorization procedure
   - Query own information
   - Revoke overseer
   - Key rotation (initiate/complete)

2. **Overseer Features** (15+ user stories needed)
   - Registration (password method, OAuth future)
   - Login/logout
   - Initiate agent claim
   - Declaim agent
   - Client registration
   - Mark agent for cancellation
   - Mark client for cancellation
   - Deactivate client
   - Change subscription (upgrade/downgrade)
   - Cancel subscription
   - Renew subscription
   - Query own information
   - Block/allow OAuth clients
   - View OAuth activity

3. **OAuth Features** (10+ user stories needed)
   - Authorization code flow
   - Token exchange
   - Token refresh
   - Token revocation
   - Token introspection
   - DPoP proof requirements

4. **Subscription Features** (10+ user stories needed)
   - View subscription details
   - List available tiers
   - Initiate upgrade
   - View usage statistics

5. **Shadow Claim Features** (5+ user stories needed, developer/agent docs only)
   - Initiate shadow claim
   - Complete shadow claim with payment
   - Shadow subscription management
   - Renounce shadow overseer

**Test Scenarios:**

1. **Claim Scenarios** (7+ scenarios needed)
   - Overseer claims unclaimed agent
   - Agent renounces overseer
   - Overseer ends oversight
   - Shadow claim initiation
   - Shadow claim completion with payment
   - Shadow claim fails (no payment)
   - Edge: Claim already claimed agent
   - Edge: Agent doesn't respond to claim
   - Edge: Overseer without subscription tries to claim
   - Error: Invalid claim challenge ID

2. **Registration Scenarios** (5+ scenarios needed)
   - Overseer registration with new data (success)
   - Overseer registration with duplicate email (fail)
   - Overseer registration with Paddle customer data (load data)
   - Agent registration with new data (success)
   - Agent registration with duplicate public key (fail)
   - Edge: Invalid public key format
   - Edge: Missing required fields
   - Error: Registration timeout

3. **Client Scenarios** (10+ scenarios needed)
   - Unclaimed agent can't register client
   - Claimed agent can register client
   - Shadow-claimed agent can register client
   - Overseer registers client
   - Client registration respects tier limits
   - OAuth flow with overseer's client
   - OAuth flow with agent's client
   - Free tier agent limited to 10 registrations
   - Edge: Exceed tier limit
   - Edge: Delete client and register new one
   - Error: Client registration with invalid data

4. **Edge Case Scenarios** (10+ minimum required)
   - Empty or null input fields
   - Maximum length strings
   - Invalid UUID format
   - Invalid JWT tokens
   - Expired challenge IDs
   - Rate limiting on endpoints
   - Concurrent claim attempts
   - Subscription during grace period
   - Paddle webhook delivery failures
   - Payment timeout scenarios

5. **Error Handling Scenarios** (10+ minimum required)
   - Invalid authentication
   - Expired sessions
   - Missing permissions
   - Database connection errors
   - Paddle API errors
   - Invalid request payload
   - Resource not found
   - Conflict scenarios (duplicate resources)
   - Rate limit exceeded
   - Payment failures

### Known Documentation Issues

1. **User Stories**
   - Lack WHO-WHAT-WHY format
   - No acceptance criteria
   - No related endpoints referenced
   - Inconsistent formatting

2. **Test Scenarios**
   - Simple numbered lists, no structure
   - Missing preconditions
   - No expected outcome documentation
   - No "actual behavior" section
   - Missing edge cases
   - Missing error handling scenarios
   - TODO in registration.md for proper formatting

### Documentation Gaps

1. No user stories for:
   - Key rotation
   - OAuth client registration details
   - Subscription management
   - Client cancellation/deactivation
   - Shadow claim (developer/agent docs)

2. No test scenarios for:
   - Edge cases (requirement: minimum 10)
   - Error handling (requirement: comprehensive coverage)
   - Expected vs actual behavior
   - Subscription tier changes
   - OAuth flow with various client types

### Recommended Task Structure

1. **User Story Reformulation:**
   - Review all existing user stories
   - Reformat using WHO-WHAT-WHY template
   - Add acceptance criteria (minimum 3 per story)
   - Reference related endpoints from Phase 1 audit
   - Identify missing user stories for backend features

2. **Test Scenario Enhancement:**
   - Reformulate all existing test scenarios with structured format
   - Add preconditions, steps, expected outcome, actual behavior
   - Create edge case scenarios (minimum 10)
   - Create error handling scenarios (comprehensive coverage)
   - Document expected vs actual behavior

3. **Validation:**
   - Verify all v1 features have corresponding user stories
   - Verify all test scenarios are properly formatted
   - Ensure minimum requirements met (10 edge cases, comprehensive error handling)

### Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Industry-standard user story template and test scenario formats |
| Architecture | HIGH | Based on existing documentation structure and Phase 1 findings |
| Pitfalls | HIGH | Common documentation anti-patterns well-documented |
| User Story Format | HIGH | Mountain Goat Software is authoritative source on user stories |
| Test Scenario Format | HIGH | Industry-standard structured test documentation |
| Gap Analysis | HIGH | Direct comparison of existing docs vs Phase 1 endpoint inventory |

### Ready for Planning

Research complete. Key findings:
- **40+ endpoints** from Phase 1 need user stories with acceptance criteria
- **Existing user stories** lack proper format and acceptance criteria
- **Existing test scenarios** lack structure, edge cases, error handling
- **Minimum requirements:** 10 edge case scenarios, comprehensive error handling
- **Templates provided** for consistent user story and test scenario formatting

The planner can now create PLAN.md files with specific tasks for user story reformulation, test scenario enhancement, and gap analysis.
