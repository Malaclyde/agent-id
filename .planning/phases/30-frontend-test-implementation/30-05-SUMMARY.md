---
phase: 30-frontend-test-implementation
plan: 05
subsystem: frontend-testing
tags:
  - vitest
  - testing-library
  - render-helpers
  - component-tests
requires:
  - 30-01
  - 30-02
  - 30-03
  - 30-04
provides:
  - Updated Home page tests using renderWithRouter
  - Updated Header component tests using renderWithRouter and mock factories
affects:
  - Other frontend component tests (reference pattern)
---

# Phase 30 Plan 05: Update Home and Header Tests with Render Helpers

## Summary

Updated existing Home page and Header component tests to use render helpers from `test/utils/render-helpers.tsx`, establishing consistent testing patterns across the frontend test suite.

## Tasks Completed

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Update Home page tests with render helpers | e7345e4 | test/unit/pages/home.test.tsx |
| 2 | Update Header component tests with render helpers | e7345e4 | test/unit/components/header.test.tsx |

## Key Changes

### Home Page Tests (test/unit/pages/home.test.tsx)

- Replaced custom `renderWithRouter` function with `renderWithRouter` from `test/utils/render-helpers.tsx`
- Updated imports to use centralized render helpers
- All 16 existing tests continue to pass
- Tests cover: initial render, human flow, agent flow, navigation

### Header Component Tests (test/unit/components/header.test.tsx)

- Uses `renderWithRouter` from render-helpers for routing
- Uses mock `useAuth` hook (via vi.mock) for auth state simulation
- Uses `createMockOverseer` and `createMockAgent` from factories for test data
- All 13 tests pass covering:
  - Unauthenticated state (login link visible)
  - Authenticated overseer state (dashboard, name, logout)
  - Authenticated agent state (dashboard, name, logout)
  - Logout functionality
  - Loading state

## Tech Stack Additions

- **Patterns established:**
  - `renderWithRouter` from test/utils/render-helpers.tsx
  - Factory functions (createMockOverseer, createMockAgent)
  - Mocked AuthContext via vi.mock

## File Tracking

**Key files created/modified:**
- `frontend/test/unit/pages/home.test.tsx` - Updated
- `frontend/test/unit/components/header.test.tsx` - Updated
- `frontend/test/utils/render-helpers.tsx` - Referenced (already existed)
- `frontend/test/factories/` - Referenced (already existed)

## Decisions Made

1. **Used renderWithRouter instead of renderWithAllProviders**: Header component uses useAuth hook which is mocked, so AuthProvider isn't needed. renderWithRouter provides routing context only.

2. **Kept useAuth mock instead of switching to MSW**: The Header reads auth state from context rather than making API calls. MSW handlers would require additional context mocking layer that's more complex than direct mock.

## Verification

- Home tests: 16/16 passing ✓
- Header tests: 13/13 passing ✓

## Deviations from Plan

**None** - Plan executed exactly as written.

Note: Pre-existing test failures in other test files (client.test.tsx, overseer-auth.test.tsx, subscription-*.test.tsx) are unrelated to this plan. They have import issues with `vi.mocked` that existed before this work.
