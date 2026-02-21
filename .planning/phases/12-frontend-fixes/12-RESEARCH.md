# Phase 12: Frontend Fixes - Research

**Researched:** 2026-02-16
**Domain:** React frontend + Cloudflare Workers backend
**Confidence:** HIGH

## Summary

This phase addresses 7 specific frontend fixes in an existing React application with a Cloudflare Workers backend using Drizzle ORM and Paddle for subscriptions. Each fix requires coordinated changes between frontend components and backend API endpoints where applicable.

**Primary recommendation:** Focus on the frontend changes first (items 1, 2, 3, 4, 5), then implement the subscription cancellation backend endpoint (item 6), and complete with testing (item 7).

---

## User Constraints (<user_constraints>
from CONTEXT.md)

### Locked Decisions

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

### Specific Implementation Details

#### Files to Modify
- Frontend: `RegisteredClients.tsx` (client registration)
- Frontend: `SubscriptionManagement.tsx` (tier display, termination)
- Frontend: `AgentDashboard.tsx`, `OverseerDashboard.tsx` (counts)
- Frontend: `Header.tsx` or similar (logout button)
- Backend: May need new endpoint for subscription cancellation
- Documentation: Various files in docs/v1/

#### API Endpoints Needed
- POST /v1/subscriptions/cancel - Cancel subscription (Paddle integration)

### Deferred Ideas
- Delete account functionality - implemented as disabled button with tooltip (next milestone)
- Full account deletion workflow - next milestone
</user_constraints>

---

## Current State Analysis

### What Already Exists

| Fix # | Feature | Status |
|-------|---------|--------|
| 1 | Token endpoint picker | **EXISTS** - needs removal |
| 2 | Subscription tier display | **PARTIAL** - needs fixes |
| 3 | Logout button | **EXISTS** - already in Header.tsx |
| 4 | Delete account button | **MISSING** - needs implementation |
| 5 | Tier comparison table | **EXISTS** - needs removal |
| 6 | Subscription cancellation | **MISSING** - endpoint not exposed |
| 7 | Testing | N/A |

### Backend API Status

**Existing endpoints:**
- `POST /v1/overseers/logout` - Session revocation (line 96-110, overseers.ts)
- `cancelSubscription()` function exists in paddle-api.ts (line 257-269) but NOT exposed as HTTP endpoint

---

## Standard Stack

### Frontend
| Library | Version | Purpose |
|---------|---------|---------|
| React | 18.x | UI framework |
| React Router | Latest | Client-side routing |
| TypeScript | 5.x | Type safety |

### Backend
| Library | Version | Purpose |
|---------|---------|---------|
| Hono | Latest | HTTP framework |
| Drizzle ORM | Latest | Database ORM |
| Paddle SDK | Latest | Subscription management |

---

## Architecture Patterns

### Frontend Component Structure

```
frontend/src/pages/
├── RegisteredClients.tsx      # OAuth client management
├── SubscriptionManagement.tsx # Tier display & upgrade
├── AgentDashboard.tsx         # Agent stats
├── OverseerDashboard.tsx     # Agent/client counts
└── components/
    └── Header.tsx             # Navigation with logout
```

### Backend Route Structure

```
backend/src/routes/
├── subscriptions.ts  # GET /me, GET /tiers, POST /upgrade, GET /usage
└── overseers.ts     # POST /logout (existing)
```

---

## Implementation Details

### Fix 1: Remove Token Endpoint Auth Picker

**Current state (RegisteredClients.tsx lines 206-244):**
- Dropdown selector for auth method (client_secret_basic, client_secret_post, private_key_jwt)
- Public key field shows conditionally ONLY when private_key_jwt selected

**Required changes:**
1. Remove `<select>` for token_endpoint_auth_method (lines 206-217)
2. Remove conditional rendering `{newClient.token_endpoint_auth_method === 'private_key_jwt' && (` (line 219)
3. Always display public key input field and "Generate Keys" button
4. Remove `token_endpoint_auth_method` from form submission or hardcode to `private_key_jwt`

**Code reference:** RegisteredClients.tsx lines 20, 95-98, 101-108

### Fix 2: Subscription Tier Limits Display

**Current config (subscription-config.ts lines 25-30):**
```typescript
BASIC: {
  max_agents: 1,
  max_clients: 10,
  max_oauth_per_period: -1, // unlimited
  price: 5
}
```

This already matches the requirements! The frontend displays are correct.

**What to verify:**
- CurrentSubscriptionCard (SubscriptionManagement.tsx) displays correct values
- RegisteredClients.tsx line 159 shows correct client count
- OverseerDashboard.tsx line 287 shows correct agent count

### Fix 3: Logout Button

**Already implemented in Header.tsx (lines 20-22, 31-33):**
```tsx
<button className="btn btn-secondary" onClick={logout}>
  Logout
</button>
```

**Backend endpoint exists:** POST /v1/overseers/logout (overseers.ts lines 96-110)
- Takes Bearer token
- Calls `revokeSession()` to invalidate session

**Frontend already calls it:** AuthContext.tsx line 77 - `logoutOverseerAndClear()` which calls the API and clears local storage.

**Status:** No changes needed - this already works!

### Fix 4: Delete Account Button

**Required implementation:**
- Add disabled button with tooltip
- Place in UserInfo component (OverseerDashboard.tsx lines 369-398) or Header
- Use `title` attribute or a tooltip library for hover text: "Coming in next milestone"

**Example pattern:**
```tsx
<button 
  className="btn btn-danger" 
  disabled 
  title="Coming in next milestone"
>
  Delete Account
</button>
```

### Fix 5: Remove Tier Comparison Table

**Current state (SubscriptionManagement.tsx lines 214-287):**
- TierComparisonCard component exists
- Rendered at line 539: `<TierComparisonCard tiers={tiers} currentTier={subscription?.tier || 'FREE'} />`

**Required changes:**
1. Remove TierComparisonCard component (lines 214-287) OR just remove its rendering (line 539)
2. Keep CurrentSubscriptionCard and UpgradeOptionsCard

### Fix 6: Subscription Cancellation

**Backend changes required:**

1. Add new endpoint in subscriptions.ts:
```typescript
subscriptions.post('/cancel', async (c) => {
  // 1. Get overseer ID
  // 2. Get subscription from Paddle
  // 3. Call cancelSubscription() from paddle-api.ts
  // 4. Return success
});
```

2. The cancelSubscription function already exists (paddle-api.ts lines 257-269):
```typescript
export async function cancelSubscription(
  env: Env,
  subscriptionId: string
): Promise<PaddleSubscription> {
  const result = await paddleRequest(...);
  return result.data;
}
```

3. Need to get subscription ID from overseer record (paddle_subscription_id)

**Frontend changes required:**
- Add "Cancel Subscription" button in SubscriptionManagement.tsx
- Call new POST /v1/subscriptions/cancel endpoint
- Show confirmation: "Your subscription will remain active until [billing_period_end]"

### Fix 7: Testing & Documentation

**Testing:**
- Frontend tests in `frontend/test/unit/`
- Backend tests in `backend/test/`

**Documentation updates:**
- Update docs/v1/endpoints/ if new endpoint added
- Update relevant flow docs

---

## Common Pitfalls

### Pitfall 1: Subscription Cancellation Without Confirmation
**What goes wrong:** User accidentally cancels subscription
**How to avoid:** Add confirmation modal before calling cancel API

### Pitfall 2: Hardcoded Tier Limits in Frontend
**What goes wrong:** Frontend shows different limits than backend config
**How to avoid:** Always use values from GET /v1/subscriptions/me endpoint

### Pitfall 3: Deleting Session Without Revoking
**What goes wrong:** Logout clears local storage but doesn't invalidate server session
**How to avoid:** Already handled - logoutOverseer() calls POST /v1/overseers/logout first

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Tooltip | Custom tooltip component | Native `title` attribute or existing CSS |
| Paddle integration | Custom fetch to Paddle | Existing paddle-api.ts functions |
| Session management | Custom JWT handling | Existing session.ts service |

---

## Code Examples

### Add Cancel Subscription Button (SubscriptionManagement.tsx)

```tsx
// Add state for cancel modal
const [showCancelModal, setShowCancelModal] = useState(false);

// Add to CurrentSubscriptionCard, after billing info:
{subscription.is_active && subscription.tier !== 'FREE' && (
  <button 
    className="btn btn-danger" 
    style={{ marginTop: '1rem' }}
    onClick={() => setShowCancelModal(true)}
  >
    Cancel Subscription
  </button>
)}
```

### Add Delete Account Button (UserInfo component)

```tsx
<div className="form-group" style={{ marginTop: '1.5rem' }}>
  <button 
    className="btn btn-danger" 
    disabled 
    title="Coming in next milestone"
  >
    Delete Account
  </button>
</div>
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Token picker with conditional key field | Always show public key field | Simplified UI, fewer states |
| Tier comparison always visible | Removed comparison table | Cleaner subscription page |
| No cancel option | Cancel with end-of-period | Proper subscription lifecycle |

---

## Open Questions

1. **Where should the delete account button be placed?**
   - Options: Header, User Info page, Account settings page
   - Recommendation: User Info page (OverseerDashboard.tsx) next to existing user info

2. **Should tier comparison be accessible elsewhere?**
   - Could be moved to a "Pricing" page instead of being completely removed
   - Current decision: Complete removal as per requirements

---

## Sources

### Primary (HIGH confidence)
- Frontend source files analyzed in-place
- Backend source files analyzed in-place
- Existing subscription configuration matches requirements

### Secondary (MEDIUM confidence)
- Paddle API cancel endpoint documented in paddle-api.ts

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Existing codebase, no new libraries needed
- Architecture: HIGH - Clear patterns from existing code
- Pitfalls: HIGH - Known issues from codebase analysis
- Implementation: HIGH - Clear requirements from CONTEXT.md

**Research date:** 2026-02-16
**Valid until:** 90 days (these are specific frontend changes, not API changes)
