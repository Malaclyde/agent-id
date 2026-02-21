# Phase 8: API Prefix to /v1 Prefix - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Restructure all API paths from `/api` to `/v1` prefix for proper API versioning. This includes all backend routes: main API endpoints, webhooks, and OAuth endpoints. Update all related documentation. No backward compatibility required - immediate switch since app has never been deployed and has no customers.

</domain>

<decisions>
## Implementation Decisions

### Migration Strategy
- Immediate switch: All `/api/*` routes become `/v1/*` in one change
- No gradual rollout or dual-serving period
- Same applies to `/webhooks/*` → `/v1/webhooks/*`
- Same applies to `/oauth/*` → `/v1/oauth/*`

### Backward Compatibility
- **None required** - no existing customers, app not deployed
- Do NOT keep old `/api` routes
- Pure replacement, not addition

### Client Communication
- Not applicable - no customers to notify
- No deprecation timeline needed

### Documentation Approach
- Update ALL existing documentation to reflect `/v1` prefix
- Add info about the prefix in documentation (e.g., API introduction section)
- Document that this is v1 of the API

### Scope (All Affected)
- Main API endpoints: `/api/*` → `/v1/*`
- Webhooks: `/webhooks` → `/v1/webhooks`
- OAuth: `/oauth` → `/v1/oauth`

</decisions>

<specifics>
## Specific Ideas

- All three route groups (API, webhooks, OAuth) should follow consistent versioning pattern
- Current structure: `/api/*`, `/webhooks`, `/oauth` - researcher to confirm why webhooks and oauth don't have `/api` prefix (may have been added separately or as a convention choice)

</specifics>

<deferred>
## Deferred Ideas

None - all decisions captured

</deferred>

---

*Phase: 08-api-prefix-to-v1-prefix*
*Context gathered: 2026-02-15*
