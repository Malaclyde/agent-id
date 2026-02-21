# Phase 12: Frontend Fixes - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix 7 specific frontend issues in the React application:
1. Client registration UI improvements
2. Subscription tier limit displays
3. Account management (logout + delete button)
4. Subscription termination functionality
5. Remove tier comparison table
6. Testing and documentation

</domain>

<decisions>
## Implementation Decisions

### 1. Client Registration - Token Endpoint Auth Method
- **REMOVE** the token endpoint auth method picker entirely
- **ALWAYS DISPLAY** the public key input field
- **ALWAYS DISPLAY** the "Generate Keys" button
- Backend only supports "private_key" - picker is unnecessary

### 2. Subscription Tier Limits Display
- **BASIC tier:** 10 client registrations, unlimited OAuth requests
- **PRO tier:** unlimited clients, unlimited OAuth requests  
- **PREMIUM tier:** unlimited clients, unlimited OAuth requests
- **FIX** slider displays to show correct limits
- **FIX** remaining clients/agents count in dashboard panes

### 3. Logout Functionality
- **ADD** logout option in UI header/menu
- **ENSURE** session is invalidated in backend (revoke session endpoint)
- Already exists at POST /v1/overseers/logout

### 4. Delete Account Button
- **ADD** disabled button with "Coming Soon" tooltip on hover
- Button should be visible but not clickable
- Feature will be implemented in next milestone
- Tooltip text: "Coming in next milestone"

### 5. Remove Tier Comparison Table
- **REMOVE** the tier comparison table from subscription pane
- Keep the current subscription display only

### 6. Subscription Termination
- **ADD** "Cancel Subscription" / "Downgrade to FREE" option
- Subscription continues until end of current billing period
- **ADD** backend endpoint: POST /v1/subscriptions/cancel
- Must integrate with Paddle API for proper subscription cancellation

### 7. Testing and Documentation
- Test each change functionality
- Add new tests to test suites if necessary
- Update documentation in docs/v1/

</decisions>

<specifics>
## Specific Implementation Details

### Files to Modify
- Frontend: `RegisteredClients.tsx` (client registration)
- Frontend: `SubscriptionManagement.tsx` (tier display, termination)
- Frontend: `AgentDashboard.tsx`, `OverseerDashboard.tsx` (counts)
- Frontend: `Header.tsx` or similar (logout button)
- Backend: May need new endpoint for subscription cancellation
- Documentation: Various files in docs/v1/

### API Endpoints Needed
- POST /v1/subscriptions/cancel - Cancel subscription (Paddle integration)

</specifics>

<deferred>
## Deferred Ideas

- Delete account functionality - implemented as disabled button with tooltip (next milestone)
- Full account deletion workflow - next milestone

</deferred>

---

*Phase: 12-frontend-fixes*
*Context gathered: 2026-02-16*
