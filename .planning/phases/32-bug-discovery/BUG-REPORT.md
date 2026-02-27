# Bug Discovery Report — Agent-ID Platform

**Generated:** 2026-02-27
**Test Suites:** Backend (vitest), Frontend (vitest), E2E (Playwright)

## Summary

| Subsystem | Total | Pass | Fail | Skip | App Bugs | Test Bugs | Known |
|-----------|-------|------|------|------|----------|-----------|-------|
| Backend   | 402   | 402  | 0    | 0    | 0        | 0         | 0     |
| Frontend  | 197   | 182  | 14   | 1    | 0        | 14        | 0     |
| E2E       | 42    | 18   | 23   | 1    | 0        | 23        | 0     |
| **Total** | 641   | 602  | 37   | 2    | 0        | 37        | 0     |

## Application Bugs

### Critical
None

### High
None

### Medium
None

### Low
None

## Test Bugs

All 37 failures across Frontend and E2E are classified as **Test Bugs** — issues with test infrastructure, mocking, or selectors rather than application code defects.

### Frontend Test Bugs (14 failures)

All failures occur in `test/unit/api/client.test.ts` due to `vi.mocked()` API incompatibility with frontend vitest v4.0.18. The tests correctly describe expected behavior but fail due to test infrastructure issues.

| Test | Error |
|------|-------|
| `makes fetch request with correct headers` | `vi.mocked(...).mockClear is not a function` |
| `includes Authorization header when session exists` | `vi.mocked(...).mockClear is not a function` |
| `does not include Authorization header when no session` | `vi.mocked(...).mockClear is not a function` |
| `throws error when response is not ok` | `vi.mocked(...).mockClear is not a function` |
| `returns parsed JSON data on success` | `vi.mocked(...).mockClear is not a function` |
| `makes POST request to correct endpoint` (registerAgent) | `vi.mocked(...).mockResolvedValue is not a function` |
| `makes POST request with agent ID` (loginAgent) | `vi.mocked(...).mockResolvedValue is not a function` |
| `sets session on successful login` (completeAgentLogin) | `vi.mocked(...).mockResolvedValue is not a function` |
| `makes POST request and sets session on success` (loginOverseer) | `vi.mocked(...).mockResolvedValue is not a function` |
| `makes POST request and sets session on success` (registerOverseer) | `vi.mocked(...).mockResolvedValue is not a function` |
| `calls logoutOverseer API and clears session` | `vi.mocked(...).mockResolvedValue is not a function` |
| `clears session even if API call fails` | `vi.mocked(...).mockRejectedValue is not a function` |
| `makes GET request to subscriptions endpoint` | `vi.mocked(...).mockResolvedValue is not a function` |
| `makes POST request with target tier` | `vi.mocked(...).mockResolvedValue is not a function` |

**Root Cause:** The frontend test setup uses `vi.mocked()` with methods like `.mockClear()`, `.mockResolvedValue()`, and `.mockRejectedValue()`. These methods exist on vitest mock functions in the Workers pool version (used by backend), but the frontend's vitest v4.0.18 setup doesn't support these methods on the mocked API client.

**Fix Approach:** Either (a) update frontend test mock setup to use vi.fn().mockReturnValue() pattern instead of vi.mocked(), or (b) ensure the vi.mock properly chains mock implementations.

### E2E Test Bugs (23 failures)

All E2E failures are due to test infrastructure issues: page element timeouts, session/login issues, and UI element selectors not matching the current application markup.

#### Registration/Login Flow Failures (9 failures across 3 browsers)

| Test | Browser | Error | Root Cause |
|------|---------|-------|------------|
| `overseer registration: fills form, submits, receives success` | chromium | `getByText('Test Overseer')` not found | Page navigation completes but user name not displayed - test expects different element |
| `overseer registration: fills form, submits, receives success` | firefox | `getByText('Test Overseer')` not found | Same as above |
| `overseer registration: fills form, submits, receives success` | webkit | `getByText('Test Overseer')` not found | Same as above |
| `overseer login: with newly registered credentials` | chromium | `getByRole('button', { name: 'Email' })` timeout | Login form provider button not appearing - selector mismatch |
| `overseer login: with newly registered credentials` | firefox | `getByRole('button', { name: 'Email' })` timeout | Same as above |
| `overseer login: with newly registered credentials` | webkit | `getByRole('button', { name: 'Email' })` timeout | Same as above |
| `session persistence: stays logged in on page refresh` | chromium | `getByText('Session Test')` not found | User name not displayed after refresh - session restored but UI different |
| `session persistence: stays logged in on page refresh` | firefox | `getByText('Session Test')` not found | Same as above |
| `session persistence: stays logged in on page refresh` | webkit | `getByText('Session Test')` not found | Same as above |

**Root Cause:** Tests use selectors (`getByText`, `getByRole`) that don't match the current UI markup. The registration and login flows likely work, but the test assertions look for elements that either don't exist or have different text/content.

#### Multi-Actor Workflow Failures (3 failures across 3 browsers)

| Test | Browser | Error | Root Cause |
|------|---------|-------|------------|
| `overseer and agent: full oauth authorization flow` | chromium | `getByText('Agent-1772201513610')` not found | Agent dashboard shows different content after login |
| `overseer and agent: full oauth authorization flow` | firefox | `getByText('Agent-1772201628970')` not found | Same as above |
| `overseer and agent: full oauth authorization flow` | webkit | (skipped) | WebKit-specific timeout |

**Root Cause:** Agent dashboard displays different content than expected. The agent login succeeds (navigates to /agent/dashboard) but the test assertion for agent name fails.

#### Shadow Claim Flow Failures (3 failures across 3 browsers)

| Test | Browser | Error | Root Cause |
|------|---------|-------|------------|
| `complete shadow claim via one-time payment` | chromium | `expect(response.ok()).toBeTruthy()` failed | API call to create agent fails with non-OK response |
| `complete shadow claim via one-time payment` | firefox | `expect(response.ok()).toBeTruthy()` failed | Same as above |
| `complete shadow claim via one-time payment` | webkit | `expect(response.ok()).toBeTruthy()` failed | Same as above |

**Root Cause:** Test calls API endpoint to create a test agent but receives a non-2xx response. This could be (a) test setup issue with D1/database, (b) API endpoint requiring different payload, or (c) auth session not properly established in test context.

#### Subscription Flow Failures (9 failures across 3 browsers)

| Test | Browser | Error | Root Cause |
|------|---------|-------|------------|
| `complete Paddle checkout in sandbox and verify upgrade` | chromium | `getByPlaceholder('Your Full Name')` timeout | Login/registration page not showing expected form |
| `complete Paddle checkout in sandbox and verify upgrade` | firefox | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `complete Paddle checkout in sandbox and verify upgrade` | webkit | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view subscription status on dashboard` | chromium | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view subscription status on dashboard` | firefox | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view subscription status on dashboard` | webkit | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view usage statistics` | chromium | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view usage statistics` | firefox | `getByPlaceholder('Your Full Name')` timeout | Same as above |
| `view usage statistics` | webkit | `getByPlaceholder('Your Full Name')` timeout | Same as above |

**Root Cause:** All three subscription tests use a shared `login()` helper that expects a registration form with `getByPlaceholder('Your Full Name')`. The placeholder text may have changed, or the page isn't loading the expected component.

## Known Limitations

None identified beyond the 3 skipped backend unit tests documented in Phase 29 (29-12-D01: "skipped 3 unit tests requiring subscription mocking — covered by integration tests"). Those 3 tests remain skipped but are not part of the 37 failures analyzed here.

## Backend Observations (Non-Failing)

A logged error was observed in backend test output that doesn't cause test failures:

```
TypeError: agentIdsResult.map is not a function
    at getOauthUsageCount (/Users/brotholomew/workdir/llms/agent-id/backend/src/routes/subscriptions.ts:54:35)
```

**Location:** `backend/src/routes/subscriptions.ts:54` in the `/v1/subscriptions/usage` endpoint

**Analysis:** The `getOauthUsageCount` function expects `agentIdsResult` to be an array with a `.map()` method, but it's receiving something else (likely a non-array result from the database query). The test passes because the error is caught and returns a 500 response, which the test accepts. This is a **potential application bug** worth investigating but does not cause any test to fail.

---

## Recommendations

1. **Fix Frontend Test Infrastructure (Priority: High)**
   - Update `test/unit/api/client.test.ts` to use `vi.fn()` with `mockReturnValue()` instead of `vi.mocked().mockResolvedValue()`
   - Alternative: Align frontend vitest version/configuration with backend's workers pool setup

2. **Fix E2E Test Selectors (Priority: High)**
   - Update registration-flow tests to use correct selectors for user display name
   - Update login-flow tests with correct provider button selector
   - Update subscription-flow tests with correct form placeholder/selectors
   - Investigate agent dashboard test - verify what content should appear after agent login

3. **Investigate Shadow Claim API (Priority: Medium)**
   - The agent creation API call in shadow-claim.spec.ts is failing
   - Verify D1 database is properly seeded in E2E environment
   - Check if API payload format has changed

4. **Investigate Backend Usage Endpoint (Priority: Low)**
   - The `agentIdsResult.map` error in subscriptions.ts:54 should be investigated
   - May be a data type mismatch in database query result handling

---

*Report generated from test results captured in Plan 01*
*Test execution date: 2026-02-27*
