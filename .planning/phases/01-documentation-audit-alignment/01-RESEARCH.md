# Phase 1: Documentation Audit & Alignment - Research

**Researched:** 2026-02-14
**Domain:** Documentation audit, API documentation, database schema documentation
**Confidence:** HIGH

## Summary

This research investigates how to effectively plan Phase 1: Documentation Audit & Alignment for the Agent-ID project. The phase requires auditing all v1 documentation, verifying it against the actual implementation, and creating comprehensive endpoint and database documentation.

**Current State Analysis:**
- v1 documentation exists but has gaps and known outdated sections
- OAuth2/DPoP documentation is believed accurate (per project roadmap)
- Subscription documentation is explicitly marked as outdated with warnings
- No structured endpoint documentation exists (docs/v1/endpoints/ is empty)
- No database schema documentation exists (docs/v1/database/ doesn't exist)
- Backend implements more features than currently documented (shadow claims, Paddle webhooks, key rotation)

**Primary recommendation:** Use a systematic audit approach comparing documentation against implementation code, prioritize OpenAPI-style endpoint documentation, and create database documentation derived directly from migration files.

## Standard Stack

### Core Documentation Tools

| Tool/Standard | Purpose | Why Standard |
|---------------|---------|--------------|
| OpenAPI 3.0 | API specification standard | Industry standard, machine-readable, generates interactive docs |
| Markdown | Human-readable documentation | Universal, version-controlled, works with GitHub |
| Mermaid | Diagrams in markdown | Native GitHub support, text-based (version controlled) |
| YAML/JSON | Structured data formats | OpenAPI, configuration files |

### Documentation Audit Approach

| Method | Purpose | When to Use |
|--------|---------|-------------|
| Code-to-Doc Comparison | Verify accuracy | For each documented endpoint/feature |
| Migration-to-Schema Doc | Database documentation | Auto-generate from SQL files |
| Route Extraction | Endpoint inventory | Scan backend route files |
| Warning Tag System | Track outdated docs | Mark known outdated sections |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| OpenAPI | API Blueprint | OpenAPI has better tooling ecosystem |
| Markdown | reStructuredText | Markdown is simpler, more common |
| Manual docs | Auto-generated only | Manual provides context auto-gen misses |
| Separate DB docs | Inline comments | Separate docs are easier to navigate |

## Architecture Patterns

### Recommended Documentation Structure

```
docs/v1/
├── endpoints/           # API endpoint documentation
│   ├── agents.md       # Agent endpoints
│   ├── overseers.md    # Overseer endpoints
│   ├── oauth.md        # OAuth2/DPoP endpoints
│   ├── clients.md      # OAuth client endpoints
│   ├── subscriptions.md # Subscription endpoints
│   └── webhooks.md     # Webhook endpoints
├── database/           # Database documentation
│   ├── schema.md       # Complete schema overview
│   ├── tables/         # Individual table docs
│   └── relationships.md # ER diagram and relationships
├── flows/              # User/technical flows (existing)
├── requirements/       # Requirements docs (existing)
└── test-scenarios/     # Test scenarios (existing)
```

### Pattern 1: Endpoint Documentation Template
**What:** Standardized format for documenting each endpoint
**When to use:** All API endpoints

**Template:**
```markdown
### POST /api/endpoint/path
**Description:** What this endpoint does

**Authentication:** Required/Optional - Type (Bearer/DPoP)

**Request Body:**
```json
{
  "field": "type - description"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": "response structure"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found

**Implementation Location:** `backend/src/routes/filename.ts:line_number`
```

### Pattern 2: Documentation Audit Checklist
**What:** Systematic verification process
**When to use:** For each document being audited

**Checklist:**
- [ ] Verify all documented endpoints exist in code
- [ ] Verify endpoint paths match implementation
- [ ] Verify HTTP methods match implementation
- [ ] Verify request/response schemas match
- [ ] Verify authentication requirements match
- [ ] Check for undocumented features
- [ ] Mark outdated sections with [OUTDATED] tag
- [ ] Add [VERIFIED] tag to confirmed sections

### Pattern 3: Database Documentation from Migrations
**What:** Deriving documentation from migration files
**When to use:** Creating database documentation

**Process:**
1. Read migration files in order (0001_initial.sql, etc.)
2. Extract CREATE TABLE statements
3. Document columns with types, constraints, defaults
4. Document indexes and foreign keys
5. Create Mermaid ER diagram
6. Note which tables are for which features

### Anti-Patterns to Avoid

- **Duplicating code in docs:** Don't copy entire function implementations
- **Storing secrets in docs:** Never document actual keys/secrets
- **Hardcoding URLs:** Use `{SERVICE_URL}` placeholders
- **Version drift:** Don't document v0 when implementing v1
- **Orphaned docs:** Delete or archive docs for removed features

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API documentation | Manual markdown only | OpenAPI spec + tools | Auto-validation, client generation, interactive docs |
| Database diagrams | Drawing tools | Mermaid ER diagrams | Version controlled, auto-generated from schema |
| Doc accuracy tracking | Memory/spreadsheets | Inline [VERIFIED]/[OUTDATED] tags | Visible in source, tied to content |
| Endpoint inventory | Manual list | Route file scanning | Always up-to-date with code |
| Schema documentation | Manual table docs | Extract from migrations | Single source of truth |

**Key insight:** Documentation should be as maintainable as code. Manual processes for keeping docs in sync will fail.

## Common Pitfalls

### Pitfall 1: The "Documentation is Correct" Assumption
**What goes wrong:** Trusting that existing docs reflect current implementation
**Why it happens:** Code evolves faster than docs; developers forget to update
**How to avoid:** Always verify against actual code; assume docs are outdated until proven otherwise
**Warning signs:** No [VERIFIED] tags; last update > 3 months ago; warnings in docs

### Pitfall 2: Writing Docs Before Finalizing Implementation
**What goes wrong:** Docs written for planned features that change during implementation
**Why it happens:** Parallel doc/development; changing requirements
**How to avoid:** Document what IS implemented, not what WILL be implemented
**Warning signs:** Todos in code for "update docs"; docs reference unimplemented features

### Pitfall 3: Scattered Documentation
**What goes wrong:** Docs spread across multiple locations (v0, v1, outdated/, etc.)
**Why it happens:** Refactoring without cleanup; fear of deleting
**How to avoid:** Single source of truth per version; archive, don't duplicate
**Warning signs:** Same topic in multiple files; conflicting information

### Pitfall 4: Missing Context for Future Developers
**What goes wrong:** Docs describe "what" but not "why"
**Why it happens:** Authors know context; forget to write it down
**How to avoid:** Document design decisions, tradeoffs, and rationale
**Warning signs:** "Why does it work this way?" questions; tribal knowledge

### Pitfall 5: Over-Documentation
**What goes wrong:** Documenting implementation details that change frequently
**Why it happens:** Desire for completeness; copy-pasting code into docs
**How to avoid:** Document interfaces and behavior, not internal implementation
**Warning signs:** Docs longer than code; outdated internal details

## Code Examples

### Endpoint Documentation Example

```markdown
### POST /api/agents/register/initiate
**Description:** Initiates agent registration by creating a challenge.

**Authentication:** None - this is the first step

**Request Body:**
```json
{
  "name": "string - Agent display name (required)",
  "public_key": "string - Ed25519 public key in base64url (required)",
  "description": "string - Optional agent description"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "challenge_id": "uuid - Challenge identifier",
  "expires_at": "ISO8601 - Challenge expiration",
  "challenge_data": "string - Canonicalized data to sign"
}
```

**Error Responses:**
- `400` - Missing required fields or invalid public key
- `409` - Public key already registered

**Implementation:** `backend/src/routes/agents.ts:51-101`
```

### Database Table Documentation Example

```markdown
### agents
Stores registered agent identities with Ed25519 cryptographic keys.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique agent UUID |
| name | TEXT | NOT NULL | Display name |
| public_key | TEXT | NOT NULL, UNIQUE | Ed25519 public key (base64url) |
| description | TEXT | nullable | Optional description |
| created_at | TEXT | NOT NULL, DEFAULT now() | Creation timestamp |
| updated_at | TEXT | NOT NULL, DEFAULT now() | Last update timestamp |
| oauth_count | INTEGER | NOT NULL, DEFAULT 0 | OAuth requests this period |
| billing_period_end | TEXT | NOT NULL, DEFAULT +1 month | Period reset date |

**Indexes:**
- `idx_agents_public_key` - Fast lookup by public key

**Related Tables:**
- oversights.agent_id -> agents.id (CASCADE DELETE)
- oauth_requests.agent_id -> agents.id (CASCADE DELETE)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual API docs | OpenAPI specs | 2020+ | Machine-readable, auto-generation |
| Wiki-based docs | Git-based markdown | 2015+ | Version control, PR review |
| Drawn diagrams | Mermaid/PlantUML | 2018+ | Text-based, version controlled |
| Separate doc teams | Dev-written docs | 2020+ | Accuracy, context |
| Monolithic docs | Docs-as-code | 2019+ | CI/CD integration |

**Deprecated/outdated:**
- Word/PDF documentation (not version controlled)
- Wiki without version control (lose history)
- Swagger 2.0 (use OpenAPI 3.0)
- Manual API testing docs (use automated tests as docs)

## Open Questions

1. **OpenAPI Specification Adoption**
   - What we know: Standard format, good tooling
   - What's unclear: Whether to invest time in OpenAPI vs markdown
   - Recommendation: Use markdown for now, consider OpenAPI for Phase 2 if needed

2. **Documentation Maintenance Process**
   - What we know: Need to keep docs in sync
   - What's unclear: Process for updating docs when code changes
   - Recommendation: Add "Update docs" to PR checklist; review docs quarterly

3. **Shadow Claim Documentation**
   - What we know: Feature exists in code, partially documented
   - What's unclear: How much to document (hidden feature)
   - Recommendation: Document for developers/agents, not for overseers

## Implementation Inventory

Based on backend/src/routes/ analysis:

### Agents Routes (backend/src/routes/agents.ts)
- POST /api/agents/register/initiate - Start registration
- POST /api/agents/register/complete/:challengeId - Complete registration
- POST /api/agents/login - Login with DPoP
- POST /api/agents/logout - Logout
- POST /api/agents/rotate-key/initiate - Initiate key rotation
- POST /api/agents/rotate-key/complete/:challengeId - Complete key rotation
- GET /api/agents/me - Get current agent
- GET /api/agents/me/oauth-history - Get OAuth history
- GET /api/agents/me/overseer - Get overseer info
- POST /api/agents/claim/initiate - Initiate claim (overseer)
- POST /api/agents/claim/complete/:challengeId - Complete claim (agent)
- GET /api/agents/claim/status/:challengeId - Check claim status
- POST /api/agents/revoke-overseer - Revoke overseer
- POST /api/agents/malice/:agentId - Initiate shadow claim
- GET /api/agents/malice/:agentId/payment/:paymentChallengeId - Payment page
- POST /api/agents/malice/:agentId/complete - Complete shadow payment
- POST /api/agents/declaim/:agentId - Declaim agent (overseer)

### Overseers Routes (backend/src/routes/overseers.ts)
- POST /api/overseers/register - Register overseer
- POST /api/overseers/login - Login
- POST /api/overseers/logout - Logout
- GET /api/overseers/me - Get current overseer
- GET /api/overseers/me/agents - Get claimed agents
- POST /api/overseers/agents/:agentId/block-client - Block client
- DELETE /api/overseers/agents/:agentId/block-client/:clientId - Unblock client
- GET /api/overseers/agents/:agentId/blocked-clients - List blocked clients
- GET /api/overseers/me/subscription - Get subscription
- GET /api/overseers/me/usage - Get usage stats
- GET /api/overseers/:id/agents - List overseer's agents (detailed)
- PUT /api/overseers/:id/agents/:agentId/cancellation - Toggle agent cancellation
- GET /api/overseers/:id/clients - List overseer's clients
- PUT /api/overseers/:id/clients/:clientId/cancellation - Toggle client cancellation

### OAuth Routes (backend/src/routes/oauth.ts)
- POST /oauth/authorize - OAuth2 authorization
- POST /oauth/token - Token exchange (auth code & refresh)
- GET /oauth/userinfo - Get user info (with DPoP)
- POST /oauth/revoke - Revoke token
- POST /oauth/introspect - Introspect token
- GET /oauth/.well-known/openid-configuration - OIDC discovery

### Clients Routes (backend/src/routes/clients.ts)
- POST /api/clients/register/:owner_type - Register OAuth client
- GET /api/clients/list/:owner_type - List clients
- PUT /api/clients/:client_id/key - Rotate client key
- DELETE /api/clients/:client_id - Delete client

### Subscriptions Routes (backend/src/routes/subscriptions.ts)
- GET /api/subscriptions/me - Get subscription
- GET /api/subscriptions/tiers - List tiers
- POST /api/subscriptions/upgrade - Initiate upgrade
- GET /api/subscriptions/usage - Get usage

### Webhooks Routes (backend/src/routes/webhooks.ts)
- POST /webhooks/paddle - Paddle webhook handler

## Sources

### Primary (HIGH confidence)
- Backend route files: `backend/src/routes/*.ts` - Source of truth for endpoints
- Database migrations: `backend/migrations/*.sql` - Source of truth for schema
- Existing v1 docs: `docs/v1/**/*.md` - Current documentation state

### Secondary (MEDIUM confidence)
- Implementation audit: `docs/outdated documentation/subscription/implementation-audit.md` - Previous audit results
- CLAUDE.md: Root level - Project overview and architecture

### Tertiary (LOW confidence)
- None required for documentation audit

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Industry standard practices
- Architecture: HIGH - Based on actual codebase analysis
- Pitfalls: HIGH - Common documentation anti-patterns

**Research date:** 2026-02-14
**Valid until:** 2026-03-14 (30 days for stable domain)

## Key Findings for Planner

### Must Document (Critical Path)
1. **All 40+ API endpoints** across 6 route files
2. **10 database tables** with relationships
3. **OAuth2/DPoP flow** (verify accuracy)
4. **Agent claim procedure** (verify accuracy)
5. **Subscription system** (mark as outdated, plan rewrite)

### Known Documentation Issues
1. **Subscription docs** explicitly marked outdated in 2 files
2. **Endpoint docs** directory is empty (docs/v1/endpoints/)
3. **Database docs** don't exist (docs/v1/database/)
4. **Shadow claim** partially documented but needs developer docs
5. **Key rotation** not documented in flows

### Documentation Gaps
1. No comprehensive endpoint reference
2. No database schema documentation
3. No rate limiting documentation
4. No error code reference
5. No webhook payload documentation

### Recommended Task Structure
1. **Audit Phase:** Review each v1 doc, verify against code, tag [VERIFIED] or [OUTDATED]
2. **Endpoint Documentation:** Document all 40+ endpoints with standard template
3. **Database Documentation:** Extract from migrations, create ER diagram
4. **Verification Phase:** Cross-check all docs against implementation

### Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Industry standard practices well-established |
| Architecture | HIGH | Based on direct codebase analysis |
| Pitfalls | HIGH | Common patterns, well-documented anti-patterns |
| Endpoint Inventory | HIGH | Direct extraction from route files |
| Database Schema | HIGH | Direct extraction from migration files |
| Doc Accuracy | MEDIUM | Some docs claim accuracy, others warn of outdated content |

### Open Questions for Planning

1. **Documentation Scope:** Should shadow claim be fully documented or kept minimal since it is a hidden feature?
2. **Documentation Format:** Should we invest in OpenAPI specs or stick to markdown for now?
3. **Maintenance Process:** How to ensure docs stay updated after Phase 1?
4. **Subscription Docs:** Should we mark as outdated or completely rewrite during this phase?

### Ready for Planning

Research complete. Key findings:
- **40+ endpoints** need documentation across 6 route files
- **10 database tables** need schema documentation
- **2 major docs** (subscription) are explicitly marked outdated
- **OAuth/DPoP** believed accurate but needs verification
- **Standard templates** provided for consistent documentation

The planner can now create PLAN.md files with specific tasks for documentation audit, endpoint documentation, and database documentation.