---
phase: 31-end-to-end-test-implementation
plan: 04
subsystem: E2E Testing
tags: [playwright, d1, migrations, webhooks]
requires: [31-03]
provides: [functional-e2e-infrastructure]
affects: [32-01]
tech-stack:
  added: []
  patterns: [Direct D1 migration in E2E setup]
key-files:
  created: [backend/src/routes/test-utils.ts (modified)]
  modified: [test/e2e/playwright.config.ts, test/e2e/setup/global.setup.ts, package.json]
decisions:
  - id: 31-04-D01
    decision: Align backend dev server persistence with E2E migration directory.
    rationale: Ensures that tests run against the database that was just migrated, avoiding 'no such table' or out-of-sync schema errors.
metrics:
  duration: 15m
  completed: 2026-02-23
---

# Phase 31 Plan 04: E2E Test Infrastructure Gap Closure Summary

## Substantive Changes
Fixed the E2E test infrastructure by correcting the working directory for Playwright dev servers, ensuring database migrations run automatically before tests, and implementing the missing webhook simulation endpoint.

## Key Accomplishments
- **Playwright Config Fix**: Added `cwd` to `webServer` blocks so `npm run dev` commands execute in the project root.
- **D1 Migration Automation**: Updated `global.setup.ts` to run `npm run db:migrate:test` after clearing the `.wrangler-state` directory.
- **Webhook Simulation**: Implemented `POST /v1/test-utils/simulate-webhook` in the backend to allow tests to inject Paddle webhook payloads directly into the local environment.
- **Persistence Alignment**: Configured the backend dev server in Playwright to use the same persistence directory as the migrations.

## Deviations from Plan

### Auto-fixed Issues
**1. [Rule 3 - Blocking] Missing db:migrate:test in root package.json**
- **Found during:** Task 2 verification
- **Issue:** The `global.setup.ts` tried to run `npm run db:migrate:test` but it was only defined in `backend/package.json`, not the root.
- **Fix:** Added the script to root `package.json`.
- **Commit:** c172769

**2. [Rule 3 - Blocking] Backend persistence mismatch**
- **Found during:** Task 2 verification
- **Issue:** Migrations were applied to one directory, but the dev server used another, leading to schema errors.
- **Fix:** Updated `playwright.config.ts` to use `--persist-to` for the backend server.
- **Commit:** aa61f7d

## Results & Verification
- `npx playwright test` now successfully starts dev servers and migrates the database.
- E2E tests are unblocked from infrastructure issues, though some application-level bugs (like the 400 Bad Request on registration) remain to be discovered in Phase 32.
- The `simulate-webhook` endpoint is implemented and ready for use by Paddle E2E tests.

## Next Steps
Proceed to Phase 32 to execute the full suite and document discovered bugs.
