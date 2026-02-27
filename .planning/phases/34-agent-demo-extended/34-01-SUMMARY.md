---
phase: 34-agent-demo-extended
plan: 01
subsystem: api
tags: [urllib, json, cli, argparse, http-wrapper, query]

# Dependency graph
requires:
  - phase: 33-agent-demo-core
    provides: CLI framework with argparse, load_config, save_config, session management
provides:
  - Unified fail-fast HTTP wrapper (make_request) for all future network operations
  - Pretty-print JSON output utility (print_output)
  - Query subcommand with history and overseers targets
affects: [34-02, 34-03, 35-agent-demo-oauth]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fail-fast HTTP: make_request prints raw error body to stderr and exits on HTTPError"
    - "Raw JSON output: print_output dumps parsed JSON with indent=2, no pagination"

key-files:
  created: []
  modified:
    - demo/agent/agent-demo.py

key-decisions:
  - "make_request exits via sys.exit(1) on HTTPError, printing raw unadulterated response body"
  - "print_output parses and re-dumps JSON for consistent pretty-printing"
  - "query subcommand uses positional target argument with argparse choices validation"

patterns-established:
  - "Fail-fast HTTP wrapper: all new network operations should use make_request instead of raw urllib"
  - "Raw JSON output: query results printed via print_output without pagination or truncation"

# Metrics
duration: 2min
completed: 2026-02-22
---

# Phase 34 Plan 01: Query Subcommand and Fail-Fast HTTP Wrapper Summary

**Unified make_request HTTP wrapper with fail-fast error handling and query subcommand for OAuth history and overseer info**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-22T18:39:28Z
- **Completed:** 2026-02-22T18:41:30Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Unified fail-fast HTTP wrapper (make_request) that prints raw API error bodies to stderr and exits immediately
- Pretty-print JSON utility (print_output) for consistent raw output without pagination
- Query subcommand with history and overseers targets using Bearer token authentication

## Task Commits

Each task was committed atomically:

1. **Task 1: Add fail-fast HTTP wrapper** - `0414087` (feat)
2. **Task 2: Implement query subcommand** - `a88ce17` (feat)

**Plan metadata:** (pending)

## Files Created/Modified
- `demo/agent/agent-demo.py` - Added make_request, print_output, cmd_query, and query subparser registration

## Decisions Made
- make_request uses sys.exit(1) on HTTPError with raw body output to stderr — ensures API errors are never swallowed or reformatted
- print_output parses response string into dict then re-dumps with json.dumps(indent=2) — guarantees consistent formatting
- Query subcommand uses positional `target` argument with choices=["history", "overseers"] — argparse handles validation automatically

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- make_request wrapper is available for all future network operations in 34-02 (claims, overseer revocation) and 34-03 (key rotation)
- Query subcommand pattern established for adding future query targets
- No blockers for next plan

---
*Phase: 34-agent-demo-extended*
*Completed: 2026-02-22*
