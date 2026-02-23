# Phase 37: Client Demo - OAuth Operations — Context

## Phase Boundary

**Goal:** Client demo script handles token refresh, userinfo, revocation, and introspection.
**Requirements:** CTOKEN-02, CTOKEN-03, COAUTH-01, COAUTH-02, COAUTH-03
**Modifies:** `demo/client/client-demo.py`
**Dependencies:** Phase 36 (Client Demo - Core)

---

## Decisions

### 1. Token Persistence & Refresh Lifecycle

**Decision:** Tokens are auto-saved to `.env` on both initial exchange and refresh. Refresh silently overwrites old tokens.

- **Storage keys:** `AGENT_<agent-id>_ACCESS_TOKEN` and `AGENT_<agent-id>_REFRESH_TOKEN` — user provides `--agent-id` to identify which token set to use.
- **Retroactive fix required:** Phase 36's `token-exchange` subcommand currently only prints tokens to stdout. This phase MUST update it to also auto-save tokens to `.env` using the `AGENT_<agent-id>_*` namespace. The `token-exchange` subcommand needs an `--agent-id` flag added.
- **Refresh token rotation:** When server issues a new refresh token alongside the new access token, silently overwrite the old refresh token in `.env`. No logging of rotation.
- **Stdout behavior:** After saving tokens to `.env`, still print the full token JSON to stdout so the user can see what was saved.

### 2. Endpoint Discovery Strategy

**Decision:** Always fetch `/.well-known/openid-configuration` dynamically. No caching, no fallbacks.

- **No caching:** Fetch the discovery document fresh on every subcommand invocation.
- **Fail-fast:** If the well-known endpoint is unreachable or returns an error, fail immediately via `sys.exit(1)` (consistent with `make_request` pattern). No fallback to hardcoded paths.
- **Endpoints available from backend:** `token_endpoint`, `userinfo_endpoint`, `revocation_endpoint`, `introspection_endpoint`, `authorization_endpoint` — all present in the well-known response. No hardcoding needed.
- **`discover` subcommand:** Add a `discover` subcommand that fetches and prints the full well-known JSON via `print_output` (raw JSON, consistent with other query commands).

### 3. Userinfo DPoP Request Mechanics

**Decision:** Script auto-generates DPoP JWT from `.env` values. User only provides `--agent-id`.

- **Key source:** Use the client's Ed25519 keypair already in `.env` (`CLIENT_PRIVATE_KEY` / `CLIENT_PUBLIC_KEY`) — same keys used for `private_key_jwt` client authentication.
- **Access token source:** Read from `AGENT_<agent-id>_ACCESS_TOKEN` in `.env`. User passes `--agent-id` flag to identify which agent's token to use.
- **DPoP proof generation:** Script constructs DPoP JWT with claims required by the backend's `validateDPoPProof` function. Researcher should verify exact required claims (`htm`, `htu`, `ath`, `jti`, `iat`, etc.) from the backend implementation.
- **Request format:** `Authorization: DPoP <access_token>` header + `DPoP: <proof_jwt>` header on a GET request.

### 4. Revocation & Introspection Auth

**Decision:** Both use `private_key_jwt` client authentication (NOT DPoP). Token type hint included but cosmetic.

- **Auth method:** `revoke` and `introspect` both send `client_id` + `client_assertion` (private_key_jwt). No DPoP required.
- **JWT `aud` claim:** Must match the specific endpoint URL (e.g., `{baseUrl}/v1/oauth/revoke` for revoke, `{baseUrl}/v1/oauth/introspect` for introspect). Backend validates this strictly.
- **Token type hint flag:** Include `--access` / `--refresh` flag on `revoke` subcommand. Send as `token_type_hint` parameter. Add code comment that backend currently ignores this hint.
- **Token source for revoke:** Require `--agent-id` flag. Auto-pull token from `AGENT_<agent-id>_ACCESS_TOKEN` or `AGENT_<agent-id>_REFRESH_TOKEN` based on `--access` / `--refresh` flag.
- **No post-revocation cleanup:** Do NOT remove tokens from `.env` after successful revocation.
- **Token source for introspect:** Same pattern — require `--agent-id` and `--access` / `--refresh` to identify which token to introspect.
- **Introspect output:** Print raw JSON response via `print_output`. No formatting.

---

## Subcommand Summary

| Subcommand | Auth Method | Key Flags | Output |
|------------|-------------|-----------|--------|
| `token-exchange` | private_key_jwt | `--agent-id` (NEW) | JSON to stdout + auto-save to .env |
| `refresh` | private_key_jwt | `--agent-id` | JSON to stdout + auto-save to .env |
| `userinfo` | DPoP (access token + proof) | `--agent-id` | Raw JSON via print_output |
| `revoke` | private_key_jwt | `--agent-id`, `--access`/`--refresh` | Raw JSON via print_output |
| `introspect` | private_key_jwt | `--agent-id`, `--access`/`--refresh` | Raw JSON via print_output |
| `discover` | None | None | Raw JSON via print_output |

---

## Research Directives

The researcher MUST verify:
1. **DPoP proof claims:** Exact claims required by `validateDPoPProof` in the backend (`htm`, `htu`, `ath`, `jti`, `iat`, `typ` header, `jwk` header, etc.).
2. **Token endpoint refresh grant:** Exact body parameters for `grant_type=refresh_token` request at the token endpoint — does it also require `private_key_jwt` auth?
3. **Client assertion JWT structure:** Confirm the `aud` claim must include the `/v1/` prefix (e.g., `{baseUrl}/v1/oauth/revoke` vs `{baseUrl}/oauth/revoke`).

---

## Deferred Ideas

None.

---

*Created: 2026-02-23*
