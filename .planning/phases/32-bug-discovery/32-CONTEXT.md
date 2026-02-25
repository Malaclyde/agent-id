# Phase 32: Bug Discovery & Reporting - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Run all test suites (backend, frontend, E2E) across the full stack, collect failures, and produce a comprehensive bug report. Bugs are documented only — no fixes are applied. The report is discussed with the user before any resolution work begins.

</domain>

<decisions>
## Implementation Decisions

### Bug vs. test issue classification
- Distinguish between **application bugs** (code defect), **test bugs** (bad assertion/setup), and **known limitations** (skipped/acknowledged)
- 14 frontend tests already failing (182/196 passing per STATE.md) — classify each
- 3 backend unit tests skipped (per 29-12-D01) — document as known limitations, not new bugs
- If a test failure is caused by flaky setup rather than a real defect, label it as a test issue

### Report structure
- Organize by subsystem: Backend, Frontend, E2E
- Within each subsystem, group by feature area (auth, subscriptions, Paddle, clients, agents, etc.)
- Each bug entry includes: test name, file path, failure output, expected vs. actual, severity
- Summary table at top with counts by subsystem and severity

### Severity levels
- **Critical** — Breaks core flow (auth, subscription activation, payment)
- **High** — Feature doesn't work as documented but has workaround
- **Medium** — Edge case failure, non-blocking
- **Low** — Cosmetic or minor inconsistency

### Delivery for discussion
- Single comprehensive report delivered as a markdown file in the planning directory
- Report presented to user all at once for review and triage
- User decides which bugs to fix vs. defer before any resolution phase begins

### OpenCode's Discretion
- Exact report formatting and markdown structure
- Order of test suite execution (backend → frontend → E2E or otherwise)
- How to capture and format test output
- Whether to re-run flaky tests for confirmation

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 32-bug-discovery*
*Context gathered: 2026-02-25*
