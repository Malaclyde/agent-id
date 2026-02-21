---
phase: 01 - Documentation Audit & Alignment
plan: PLAN-01-audit
type: implementation
wave: 1
depends_on: []
files_modified: []
autonomous: false
must_haves:
  - All v1 documentation files reviewed and tagged
  - Outdated subscription documentation clearly marked with [OUTDATED] tags
  - OAuth2/DPoP documentation verified for accuracy
  - Agent claim procedure documentation verified
  - Gap analysis identifying undocumented features
  - Outdated sections marked with [OUTDATED] tags (actual removal of sections is out of scope for this phase)
---

# Plan 1: Documentation Audit & Verification

## Objective
Systematically audit all v1 documentation files against the actual implementation, identify outdated sections, and mark them with [OUTDATED] or [VERIFIED] tags.

## Context
The codebase has v1 documentation with known gaps:
- OAuth2/DPoP documentation is believed accurate (per roadmap)
- Subscription documentation is explicitly marked outdated
- No endpoint documentation exists (docs/v1/endpoints/ is empty)
- No database documentation exists
- Shadow claim and key rotation features exist in code but lack comprehensive docs

---

## Tasks

<task type="auto">
  <name>Audit v1 Documentation Files</name>
  <files>
    <file>docs/v1/requirements/README.md</file>
    <file>docs/v1/requirements/agent/*.md</file>
    <file>docs/v1/requirements/overseer/*.md</file>
    <file>docs/v1/flows/oauth/oauth2_flow.md</file>
    <file>docs/v1/flows/agent/agent_claim_procedure.md</file>
    <file>docs/v1/flows/agent/agent_authorization.md</file>
    <file>docs/v1/flows/client/client_app_register_workflow.md</file>
    <file>docs/v1/flows/subscription/*.md</file>
    <file>docs/v1/AUDIT_REPORT.md</file>
  </files>
  <action>
    Review all documentation files in docs/v1/ directory and compare against implementation:
    
    1. Read each v1 documentation file
    2. For each document:
       - Compare endpoints described vs backend/src/routes/*.ts
       - Compare flows described vs actual implementation
       - Check for missing features (shadow claim, key rotation)
       - Add [VERIFIED] tag to confirmed accurate sections
       - Add [OUTDATED] tag to outdated sections with explanation
    3. Create audit summary in docs/v1/AUDIT_REPORT.md with:
       - List of all documents audited
       - Status of each (VERIFIED/OUTDATED/PARTIAL)
       - List of gaps found
       - Recommendations for updates
  </action>
  <verify>
    - docs/v1/AUDIT_REPORT.md exists and contains audit summary
    - All v1 docs have been reviewed
    - [VERIFIED] or [OUTDATED] tags applied to each document
    - Gap analysis identifies all undocumented features
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Verify OAuth2/DPoP Flow Documentation</name>
  <files>
    <file>docs/v1/flows/oauth/oauth2_flow.md</file>
    <file>backend/src/routes/oauth.ts</file>
    <file>backend/src/services/oauth-flow.ts</file>
  </files>
  <action>
    Specifically verify the OAuth2/DPoP documentation accuracy:
    
    1. Read docs/v1/flows/oauth/oauth2_flow.md thoroughly
    
    2. Verify against implementation in backend/src/routes/oauth.ts:
       - All 6 endpoints documented match actual routes
       - Request/response schemas match validation logic
       - Authentication methods (Bearer vs DPoP) are correct
       - Token lifetimes match implementation
       - Scopes documented match allowed scopes
       - PKCE implementation details are accurate
       - DPoP proof requirements are correct
    
    3. Verify against backend/src/services/oauth-flow.ts:
       - Authorization code flow logic matches docs
       - Token exchange process matches docs
       - Token refresh logic matches docs
       - Revocation and introspection match docs
    
    4. Update oauth2_flow.md with [VERIFIED] tags for confirmed sections
    
    5. Document any discrepancies found with [OUTDATED] tags
  </action>
  <verify>
    - oauth2_flow.md has [VERIFIED] tags on accurate sections
    - Any discrepancies marked with [OUTDATED] tags
    - All 6 OAuth endpoints verified against implementation
    - Token lifetimes, scopes, and auth methods match code
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Mark Subscription Documentation as Outdated</name>
  <files>
    <file>docs/v1/flows/subscription/subscription-flows.md</file>
    <file>docs/v1/flows/subscription/subscription-endpoints.md</file>
    <file>docs/v1/requirements/subscription/subscription-provider.md</file>
    <file>docs/v1/requirements/subscription/subscription-model.md</file>
    <file>backend/src/routes/subscriptions.ts</file>
    <file>backend/src/services/subscription.ts</file>
    <file>backend/src/services/paddle.ts</file>
    <file>backend/migrations/0005_create_subscription_tiers.sql</file>
  </files>
  <action>
    Subscription documentation is explicitly known to be outdated. Update the relevant files:
    
    1. Read subscription documentation files
    
    2. Add prominent [OUTDATED] warning at the top of each file:
       > **⚠️ [OUTDATED] WARNING**: This documentation is outdated as of {date}.
       > The subscription system has been refactored. Current implementation uses
       > Paddle integration. This document is retained for reference but should
       > not be used for implementation. See backend/src/routes/subscriptions.ts
       > for current implementation.
    
    3. Verify current implementation in:
       - backend/src/routes/subscriptions.ts (4 endpoints)
       - backend/src/services/subscription.ts
       - backend/src/services/paddle.ts
       - backend/migrations/0005_create_subscription_tiers.sql
    
    4. Add notes about what's different in current implementation vs documented
  </action>
  <verify>
    - All 4 subscription docs have [OUTDATED] warning at top
    - Warnings include current date
    - References to current implementation files included
    - Notes about differences added
  </verify>
  <done></done>
</task>

---

## Verification
- All tasks completed with verify criteria met
- Audit report created and reviewed
- OAuth2/DPoP documentation verified
- Subscription docs marked as outdated

## Success Criteria
- docs/v1/AUDIT_REPORT.md exists with complete audit results
- All v1 documentation files have [VERIFIED] or [OUTDATED] tags
- OAuth2/DPoP flow documentation accuracy confirmed
- Subscription documentation clearly marked as outdated
- Gap analysis completed identifying undocumented features

## Output
- docs/v1/AUDIT_REPORT.md
- Updated docs/v1/flows/oauth/oauth2_flow.md with tags
- Updated subscription documentation with [OUTDATED] warnings
