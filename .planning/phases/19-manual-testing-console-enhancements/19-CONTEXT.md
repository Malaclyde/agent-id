# Phase 19: Manual Testing Console Enhancements - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Add client key restoration feature to the OAuth clients pane in test/manual-console. Users can add missing public/private key pairs to clients fetched from the database. Other enhancements can be added in future phases.

</domain>

<decisions>
## Implementation Decisions

### Feature: Add Keys to Fetched Clients

**What:**
- In the OAuth clients pane, when clients are fetched from the database but lack private/public keys in local state
- Add an action to the existing client actions dropdown: "Add Keys"
- This opens an input form where user can provide public_key and private_key
- Keys are saved to localStorage/state for the console to use

**UI Flow:**
1. User clicks "Actions" dropdown next to a fetched client
2. Selects "Add Keys" option
3. Input fields appear for public_key and private_key
4. User pastes both keys
5. Click "Save Keys" button
6. Keys stored in console's local state
7. Console can now sign challenges with the private key

**Location:**
- File: test/manual-console/public/js/panes/oauth.js
- Existing action pattern: Similar to "Delete Client" action in the dropdown

**Behavior:**
- Only show "Add Keys" option for clients that DON'T have keys in local state
- Client with keys in local state should show "Keys Loaded" indicator instead
- Keys stored in localStorage under client ID key
- No DB write needed - console reads from localStorage

### Claude's Discretion
- Exact UI/UX of the input form (modal, inline, etc.)
- How to validate key format
- Whether to show keys as plain text or masked input

</decisions>

<specifics>
## Specific Ideas

- "I create a client in the browser, test console fetches it but doesn't have the private key to sign challenges"
- Need to manually add the key pair so the console can sign DPoP challenges
- Similar to how you might "import" keys into a wallet app

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 19-manual-testing-console-enhancements*
*Context gathered: 2026-02-17*
