# Phase 35: Agent Demo - OAuth Client
# Implementation Context

This document captures implementation decisions made during the discuss-phase workflow. Downstream agents (researcher, planner, executor) must honor these locked decisions.

## 1. Client Key Storage & Multi-Client Naming
* **Decision:** Store client keys using the server-generated client ID as the namespace, not the client name.
* **Details:**
  * Save keys as `CLIENT_<client-id>_PUBLIC_KEY` and `CLIENT_<client-id>_PRIVATE_KEY` in `.env`.
  * Also save the client ID itself as `CLIENT_<client-id>_ID` (or equivalent) so the user can reference it later.
  * Client IDs are server-generated UUIDs and guaranteed unique — no collision handling needed.
  * Do NOT use the client name as the .env key namespace (names may contain spaces, special characters, or duplicates).
  * The three key provision options remain as documented in the README:
    1. `--generate` — script generates keypair, saves both to `.env` under the client ID namespace.
    2. No key flags — script reads pre-existing keys from `.env` under the client ID namespace. (Note: since client ID is only known after registration, this option applies when re-using keys for an already-registered client.)
    3. `--private-key <key> --public-key <key>` — user provides keys explicitly, script validates and saves to `.env` under the client ID namespace.

## 2. PKCE Code Challenge Input
* **Decision:** The authorize subcommand expects the user to pass the PKCE code challenge via an explicit CLI flag.
* **Details:**
  * Add a `--code-challenge` flag (required) to the `authorize` subcommand.
  * The script does NOT generate the PKCE challenge itself — the client application is responsible for generating the code_verifier and computing the S256 challenge.
  * The `code_challenge_method` is always `S256` and does not need a flag — hardcode it in the request body.
  * This mirrors real-world OAuth flows where the client generates PKCE, not the resource owner.

## 3. Authorization Code Output
* **Decision:** Print the authorization code directly to stdout. No redirect, no file save.
* **Details:**
  * After a successful `/v1/oauth/authorize` call, use `print_output()` to dump the raw JSON response (which includes `authorization_code`, `redirect_uri`, `state`, `scope`).
  * The user manually copies the authorization code and provides it to the client demo script.
  * Do NOT attempt to redirect, open a browser, or save the code to a file.
  * This is consistent with the established raw JSON output pattern from Phase 34.
