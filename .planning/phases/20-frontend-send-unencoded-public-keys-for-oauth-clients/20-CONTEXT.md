# Phase 20: Frontend Send Unencoded Public Keys for OAuth Clients - Context

**Gathered:** 2026-02-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix OAuth client registration to properly handle public key encoding:
- Frontend converts raw public key from input field to base64url before sending to backend
- Backend validates public key is base64url encoded and returns clear error if not

This is a bugfix phase - backend validation already exists but frontend doesn't convert keys.

</domain>

<decisions>
## Implementation Decisions

### Public Key Handling
- User pastes raw (unencoded) public key in the input field
- Frontend converts the input value to base64url format before sending to backend
- This applies to: generated keys AND manually pasted keys

### Backend Validation
- Backend already validates public key format via `validateEd25519PublicKey()`
- Must return clear error message when validation fails: "Invalid Ed25519 public key format. Expected base64url-encoded key."
- Error should be returned during OAuth client registration (not later during JWT verification)

### Frontend Changes
- Modify `registerOAuthClient` API call to convert `public_key` to base64url using existing `formatPublicKey()` method
- Apply same conversion to `updateOAuthClientKey` method

### Documentation Update
- Update input placeholder text from "Base64-encoded" to "Base64url-encoded Ed25519 public key"

</decisions>

<specifics>
## Specific Requirements

**Frontend files to modify:**
- `frontend/src/api/client.ts` - Convert public_key to base64url in registerOAuthClient and updateOAuthClientKey

**Backend behavior:**
- Already validates via `validateEd25519PublicKey()` in `oauth-client.ts`
- Returns: `{ success: false, error: 'Invalid Ed25519 public key format' }` (already implemented)

**Verification:**
- Register client with non-base64url key → should get clear error
- Register client with valid base64url key → should succeed

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 20-frontend-send-unencoded-public-keys-for-oauth-clients*
*Context gathered: 2026-02-17*
