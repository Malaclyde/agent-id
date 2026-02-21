# Phase 4: Test Implementation - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Write comprehensive test suite covering backend, frontend, integration, and end-to-end scenarios. Tests verify all functionality documented in Phase 2 test scenarios. Does not include bug fixing — that's Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Test organization
- Separate `backend/test/` and `frontend/test/` folders (not colocated with source)
- Subfolders: `unit/` and `integration/` within each
- E2E tests in root-level `test/e2e/` directory
- Example structure:
  ```
  backend/test/unit/
  backend/test/integration/
  frontend/test/unit/
  frontend/test/integration/
  test/e2e/
  ```

### Mocking strategy
- **Unit & Integration tests:** Mock Paddle entirely (no real API calls)
- **E2E tests:** Use real Paddle sandbox for realistic payment flow testing
- Mock other external services as appropriate for test speed and reliability

### Coverage expectations
- Target >80% code coverage for backend and frontend
- Can go higher where practical
- Critical paths (auth, subscription, OAuth) should have highest coverage

### E2E test scope
- Full user flows: registration → subscription → OAuth
- Chromium browser only
- Use Playwright for E2E testing

### Claude's Discretion
- Test file naming conventions
- Specific mock implementations
- Test utilities and helpers structure
- CI integration approach

</decisions>

<specifics>
## Specific Ideas

No specific references provided — open to standard testing approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-test-implementation*
*Context gathered: 2026-02-15*
