# Phase 17: Manual Test Console Backend API Fix - Context

**Gathered:** 2026-02-17
**Status:** Ready for execution

<domain>
## Phase Boundary

Update the manual test console (test/manual-console/) to use correct /v1/* API endpoints. Verify endpoints exist in backend. No new backend endpoints.

</domain>

<decisions>
## Implementation Decisions

### Endpoint migration
- Update all API calls in test/manual-console/ to use /v1/* prefix
- Verify each endpoint exists in backend before updating
- Do NOT add new endpoints to backend — consult first if needed

### Authentication
- Use existing authentication mechanism in the console
- Ensure auth headers/cookies work with /v1/* endpoints

### Scope
- Focus on test console only (frontend)
- Backend changes require discussion first

</decisions>

<specifics>
## Specific Ideas

- All /api/* calls need to become /v1/*
- Must verify endpoint exists in backend, not just add prefix
- Revoke overseer specifically needs logged-in agent session (per prior work)

</specifics>

<deferred>
## Deferred Ideas

None — all work is within phase scope

</deferred>

---

*Phase: 17-manual-test-console-backend-api-fix*
*Context gathered: 2026-02-17*
