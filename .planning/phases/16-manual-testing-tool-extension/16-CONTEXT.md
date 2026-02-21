# Phase 16: Manual Testing Tool Extension - Context

**Gathered:** 2026-02-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend the manual testing tool (frontend + Python notebook):
1. **Frontend:** Add new section in agents pane for overseer actions (respond to custom claim URL, revoke overseer)
2. **Python Notebook:** Create `/test/manual-script/agent-notebook.ipynb` for agent/client simulation

</domain>

<decisions>
## Implementation Decisions

### Frontend UI - Overseer Actions Section

**Location:**
- At the bottom of the agents pane (after existing agent list)

**Inputs:**
- Custom agent ID (optional) - if not selecting from the list
- Custom claim URL (text input)
- Overseer ID (text input)

**Agent Selection:**
- Primary: Select agent from existing list in the app
- Fallback: Option to enter custom agent ID (text input)

**Result Display:**
- Inline display (show response directly in the UI)

**Actions:**
- Respond to custom claim URL button
- Revoke overseer button

### Python Notebook Structure

**Organization:**
- Separate cells for each function
- Results saved in variables for reuse across cells

**Error Handling:**
- Return error dicts with full info (not raise exceptions)

**Self-Contained:**
- Fully self-contained - no external dependencies beyond requests and cryptography

### Python Notebook - OAuth Flow

**Setup Cell:**
- Save necessary info in variables: client_id, client_secret, base_url, claims, etc.
- Generate code_verifier and code_challenge based on client private key
- Leave placeholders for user to fill in manually

**Authorization Cell:**
- Calculate JWT for the chosen agent
- Send request to /authorize endpoint
- Authorization code returned in response

**Token Cell:**
- Calculate JWT for client based on client private key
- Include code_verifier in request
- Simultaneously start listening on localhost:8789
- Receive and capture access_token and refresh_token from callback

### Python Notebook - DPoP Implementation

**Key Generation:**
- Use `cryptography` library for ED25519 key generation
- Dedicated function in separate cell
- Reference backend implementation for correct structure

**DPoP JWT:**
- Dedicated function in separate cell
- Include htu (HTTP target URI) and htm (HTTP method) claims
- Reference backend dpop.ts implementation

### Python Notebook - Additional Features

**Agent Client Registration:**
- Add separate cell for agent to register a new client
- Include all necessary parameters (name, public_key, redirect_uris, etc.)

**UserInfo Query:**
- Add function to query /userinfo with retrieved access token

**Token Refresh:**
- Add function to refresh access token using refresh token

</decisions>

<specifics>
## Specific Ideas

- **Frontend:** "at the bottom of the agents pane; custom agent ID (if not selected from the list), custom claim URL, overseerID; inline; the agent should be primarily selected from the list, but add an option to use a custom agent id"
- **Notebook:** "separate cells for each functions, save results in variables; fully self contained; return error dicts with full info"
- **OAuth Flow:** "we assume that the notebook is both the client and the agent, first we save the necessary info... in variables (generate the code verifier and challenge based on the client private key)... the notebook sends the request to /authorize... authorization code is returned; then (in another cell), the notebook sends the authorization code... while simultaneously starting listening for requests at localhost:8789"
- **DPoP:** "choose the library you find best; dedicated function in a separate cell; see backend implementation and documentation"
- **Client Registration:** "add a cell for an agent to register a client"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 16-manual-testing-tool-extension*
*Context gathered: 2026-02-16*
