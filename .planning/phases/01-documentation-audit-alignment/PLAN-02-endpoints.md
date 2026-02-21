---
phase: 01 - Documentation Audit & Alignment
plan: PLAN-02-endpoints
type: implementation
wave: 2
depends_on: [PLAN-01-audit]
files_modified: []
autonomous: false
must_haves:
  - All 40+ endpoints documented in docs/v1/endpoints/
  - Consistent format using the standard template
  - Authentication requirements specified for each endpoint
  - Error responses documented (400, 401, 403, 500) for each endpoint
  - Rate limits documented for endpoints that have them
  - Implementation file:line references included
---

# Plan 2: Endpoint Documentation

## Objective
Create comprehensive API endpoint documentation for all 40+ endpoints across 6 route files in docs/v1/endpoints/ directory.

## Context
The docs/v1/endpoints/ directory is currently empty. We need to document:
- 17 agent endpoints
- 14 overseer endpoints  
- 6 OAuth endpoints
- 4 client endpoints
- 4 subscription endpoints
- 1 webhook endpoint

Each endpoint needs: HTTP method, path, auth requirements, request/response schemas, error codes, and implementation location.

---

## Tasks

<task type="auto">
  <name>Document Agent and OAuth Endpoints</name>
  <files>
    <file>docs/v1/endpoints/agents.md</file>
    <file>docs/v1/endpoints/oauth.md</file>
    <file>backend/src/routes/agents.ts</file>
    <file>backend/src/routes/oauth.ts</file>
  </files>
  <action>
    Create comprehensive endpoint documentation for agents and OAuth routes:
    
    1. Create docs/v1/endpoints/agents.md with all 17 agent endpoints:
       - POST /api/agents/register/initiate
       - POST /api/agents/register/complete/:challengeId
       - POST /api/agents/login
       - POST /api/agents/logout
       - POST /api/agents/rotate-key/initiate
       - POST /api/agents/rotate-key/complete/:challengeId
       - GET /api/agents/me
       - GET /api/agents/me/oauth-history
       - GET /api/agents/me/overseer
       - POST /api/agents/claim/initiate
       - POST /api/agents/claim/complete/:challengeId
       - GET /api/agents/claim/status/:challengeId
       - POST /api/agents/revoke-overseer
       - POST /api/agents/malice/:agentId (shadow claim)
       - GET /api/agents/malice/:agentId/payment/:paymentChallengeId
       - POST /api/agents/malice/:agentId/complete
       - POST /api/agents/declaim/:agentId
    
       For each endpoint include:
       - Description
       - Authentication requirements (None/Bearer/DPoP) explicitly specified
       - Request body schema with types
       - Response schemas for success and errors
       - HTTP status codes
       - Error responses (400, 401, 403, 500) documented
       - Implementation reference (file:line)
    
    2. Create docs/v1/endpoints/oauth.md with all 6 OAuth endpoints:
       - POST /oauth/authorize
       - POST /oauth/token
       - GET /oauth/userinfo
       - POST /oauth/revoke
       - POST /oauth/introspect
       - GET /oauth/.well-known/openid-configuration
    
       Include PKCE, DPoP, and client_assertion details where applicable.
       Include authentication requirements and error codes for each endpoint.
  </action>
  <verify>
    - agents.md contains all 17 agent endpoints
    - oauth.md contains all 6 OAuth endpoints
    - Authentication requirements (None/Bearer/DPoP) specified for each endpoint
    - Error responses (400, 401, 403, 500) documented for each endpoint
    - Implementation file:line references included
    - PKCE, DPoP details documented where applicable
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Document Overseer and Client Endpoints</name>
  <files>
    <file>docs/v1/endpoints/overseers.md</file>
    <file>docs/v1/endpoints/clients.md</file>
    <file>backend/src/routes/overseers.ts</file>
    <file>backend/src/routes/clients.ts</file>
  </files>
  <action>
    Create endpoint documentation for overseers and OAuth clients:
    
    1. Create docs/v1/endpoints/overseers.md with all 14 overseer endpoints:
       - POST /api/overseers/register
       - POST /api/overseers/login
       - POST /api/overseers/logout
       - GET /api/overseers/me
       - GET /api/overseers/me/agents
       - POST /api/overseers/agents/:agentId/block-client
       - DELETE /api/overseers/agents/:agentId/block-client/:clientId
       - GET /api/overseers/agents/:agentId/blocked-clients
       - GET /api/overseers/me/subscription
       - GET /api/overseers/me/usage
       - GET /api/overseers/:id/agents
       - PUT /api/overseers/:id/agents/:agentId/cancellation
       - GET /api/overseers/:id/clients
       - PUT /api/overseers/:id/clients/:clientId/cancellation
    
       Include authentication requirements, error codes, and implementation references.
    
    2. Create docs/v1/endpoints/clients.md with all 4 client endpoints:
       - POST /api/clients/register/:owner_type
       - GET /api/clients/list/:owner_type
       - PUT /api/clients/:client_id/key
       - DELETE /api/clients/:client_id
    
       Document the OAuth client registration and management endpoints with:
       - Owner type validation ('agent' or 'overseer')
       - Authentication requirements
       - Error responses
       - Key rotation process
       - Client deletion implications
  </action>
  <verify>
    - overseers.md contains all 14 overseer endpoints
    - clients.md contains all 4 client endpoints
    - Authentication requirements specified for each endpoint
    - Error responses (400, 401, 403, 500) documented for each endpoint
    - Owner type validation documented
    - Implementation references included
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Document Subscription and Webhook Endpoints</name>
  <files>
    <file>docs/v1/endpoints/subscriptions.md</file>
    <file>docs/v1/endpoints/webhooks.md</file>
    <file>docs/v1/endpoints/README.md</file>
    <file>backend/src/routes/subscriptions.ts</file>
    <file>backend/src/routes/webhooks.ts</file>
  </files>
  <action>
    Create endpoint documentation for subscriptions and webhooks:
    
    1. Create docs/v1/endpoints/subscriptions.md with all 4 subscription endpoints:
       - GET /api/subscriptions/me - Get current subscription
       - GET /api/subscriptions/tiers - List available tiers
       - POST /api/subscriptions/upgrade - Initiate upgrade
       - GET /api/subscriptions/usage - Get usage statistics
    
       Include in the documentation:
       - Authentication requirements
       - Error responses
       - Paddle integration details
       - Subscription tier structure
       - Webhook handling for Paddle events
       - Usage tracking fields
       - Mark entire file with [CURRENT] tag (not [OUTDATED] like the flow docs)
    
    2. Create docs/v1/endpoints/webhooks.md with:
       - POST /webhooks/paddle - Paddle webhook handler
       
       Document:
       - Authentication requirements (if any)
       - Error responses
       - Webhook signature validation (even though known to be broken)
       - Event types handled
       - Security considerations
       - Expected payload structure
    
    3. Create docs/v1/endpoints/README.md as an index:
       - List all endpoint files
       - Provide quick navigation
       - Summarize authentication methods used across endpoints
       - Note rate limiting (if any)
  </action>
  <verify>
    - subscriptions.md contains all 4 subscription endpoints with [CURRENT] tag
    - webhooks.md contains Paddle webhook endpoint
    - Authentication requirements specified for each endpoint
    - Error responses documented
    - README.md exists as index with navigation
    - Implementation references included
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Document Rate Limits for Endpoints</name>
  <files>
    <file>docs/v1/endpoints/README.md</file>
    <file>docs/v1/endpoints/*.md</file>
    <file>backend/src/routes/*.ts</file>
  </files>
  <action>
    Document rate limiting for all endpoints:
    
    1. Check backend code for rate limiting middleware or configurations:
       - Search for rate limit related code in backend/src/
       - Check for any rate limit headers in responses
       - Review any middleware that handles throttling
    
    2. For each endpoint documentation file:
       - Add rate limit section if rate limits exist
       - Specify rate limit values (requests per time period)
       - Document rate limit headers returned (X-RateLimit-Limit, X-RateLimit-Remaining, etc.)
       - Document error response when rate limit exceeded (429 Too Many Requests)
    
    3. If no rate limiting is implemented:
       - Add explicit note: "No rate limiting currently implemented for this endpoint"
       - Create a documentation note in docs/v1/endpoints/README.md about overall rate limit status
    
    4. Update docs/v1/endpoints/README.md to include rate limit summary section
  </action>
  <verify>
    - Each endpoint has explicit rate limit documentation OR note that none exists
    - Rate limit values documented where they exist
    - 429 error response documented where rate limiting exists
    - README.md includes rate limit summary
    - All rate limits cross-checked against implementation
  </verify>
  <done></done>
</task>

---

## Verification
- All tasks completed with verify criteria met
- All 40+ endpoints documented
- Authentication requirements specified for all endpoints
- Error responses (400, 401, 403, 500) documented for all endpoints
- Rate limits documented for all applicable endpoints

## Success Criteria
- docs/v1/endpoints/ directory contains complete documentation
- agents.md, oauth.md, overseers.md, clients.md, subscriptions.md, webhooks.md created
- README.md index file created with navigation
- Each endpoint has HTTP method, path, auth requirements, schemas, error codes
- Rate limits documented or explicitly noted as not implemented

## Output
- docs/v1/endpoints/agents.md
- docs/v1/endpoints/oauth.md
- docs/v1/endpoints/overseers.md
- docs/v1/endpoints/clients.md
- docs/v1/endpoints/subscriptions.md
- docs/v1/endpoints/webhooks.md
- docs/v1/endpoints/README.md
