# Phase 36: Client Demo - Core
# Implementation Context

This document captures implementation decisions made during the discuss-phase workflow. Downstream agents (researcher, planner, executor) must honor these locked decisions.

## 1. PKCE Output & Storage

* **Decision:** Print verifier/challenge to stdout only. No automatic .env storage.
* **Details:**
  * `generate-verifier` subcommand outputs: code_verifier, code_challenge, code_challenge_method
  * User copies values manually to use with agent-demo authorize and client-demo token-exchange
  * Follows established pattern: agent-demo also prints to stdout (no redirect/file save)

## 2. Token Exchange Callback Server

* **Decision:** Blocking HTTP server with configurable port/hostname, waits for tokens or Ctrl+C.
* **Details:**
  * Port: Read from `CLIENT_PORT` in .env, default is `8790`
  * Hostname: Read from `CLIENT_URL` in .env, default is `localhost`
  * Redirect URI: Constructed as `http://{CLIENT_URL}:{CLIENT_PORT}/callback`
  * Wait behavior: Block until request with access_token + refresh_token in body, OR user sends Ctrl+C
  * After receiving tokens: Print body/headers to stdout, save tokens to .env, stop server, exit
  * On token exchange failure: Stop server, print API error response to stderr, exit with code 1
  * Server should handle the callback request and extract tokens from query params or body

## 3. Client Configuration Namespace

* **Decision:** Single client per .env file with CLIENT_* prefix for client credentials.
* **Details:**
  * `.env` structure for client demo:
    ```
    BACKEND_URL=<backend-url>
    CLIENT_PUBLIC_KEY=...
    CLIENT_PRIVATE_KEY=...
    CLIENT_ID=...
    CLIENT_URL=localhost
    CLIENT_PORT=8790
    AGENT_<agent-id>_ACCESS_TOKEN=...
    AGENT_<agent-id>_REFRESH_TOKEN=...
    ```
  * One .env = one client (simplification for demo scripts)
  * Agent tokens stored with agent-id namespace to support multiple agent sessions
  * Keys must be validated: base64url format, public derives from private

## 4. Token Exchange Flow

* **Decision:** Two-step process: start server → call /token endpoint.
* **Details:**
  * Step 1: Start HTTP server on configured port/hostname
  * Step 2: POST to `/v1/oauth/token` with:
    * `code`: authorization token from user (--token flag)
    * `code_verifier`: from user (--code-verifier flag)
    * `redirect_uri`: `http://{CLIENT_URL}:{CLIENT_PORT}/callback`
    * `client_id`: from .env
    * `client_assertion`: JWT signed with client's private key (client assertion JWT pattern)
    * `client_assertion_type`: `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
    * `grant_type`: `authorization_code`
  * The backend will redirect to the callback URL with tokens
  * Server receives callback, extracts tokens, saves to .env under `AGENT_<agent-id>_ACCESS_TOKEN` and `AGENT_<agent-id>_REFRESH_TOKEN`

## 5. Client Assertion JWT

* **Decision:** Use private key JWT client authentication for token exchange.
* **Details:**
  * Client assertion is a JWT signed with the client's Ed25519 private key
  * JWT header: `{"alg": "EdDSA", "typ": "JWT"}`
  * JWT payload includes: `iss` (client_id), `sub` (client_id), `aud` (backend URL), `exp`, `iat`, `jti`
  * Matches the pattern used by backend for agent authentication

## 6. Default Values

* **Decision:** Provide sensible defaults for optional configuration.
* **Details:**
  * `CLIENT_URL`: default `localhost`
  * `CLIENT_PORT`: default `8790`
  * If .env doesn't exist, create it with defaults
  * If values missing from .env, use defaults
