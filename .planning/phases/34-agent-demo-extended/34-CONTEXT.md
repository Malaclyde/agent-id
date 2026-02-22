# Phase 34: Agent Demo - Extended Operations
# Implementation Context

This document captures implementation decisions made during the discuss-phase workflow. Downstream agents (researcher, planner, executor) must honor these locked decisions.

## 1. Output Formatting for Queries
* **Decision:** The CLI must output raw JSON, but pretty-printed for readability.
* **Details:** 
  * Do not parse the JSON into custom tables or summaries.
  * When querying OAuth history or overseers, dump the entire JSON response at once (no pagination, limits, or "press any key to continue" prompts by default).

## 2. CLI Interaction Pattern for Key Rotation
* **Decision:** The script must automatically overwrite the `.env` file with new keys upon a successful key rotation operation.
* **Details:**
  * Before overwriting `.env`, create a single backup file named `.env.bak`.
  * If `.env.bak` already exists, overwrite it so there is only ever one backup copy at a time.
  * Do not prompt the user to manually update their keys in the console.

## 3. Claim Challenge Input Method
* **Decision:** The user will provide the required IDs via explicit CLI flags.
* **Details:** 
  * Use `--challenge-id` and `--overseer-id` to pass the necessary identifiers.
  * The script will construct the claim challenge payload using these user-provided IDs combined with existing configuration data found in the `.env` file.

## 4. Safeguards & Error Handling
* **Decision:** The CLI will favor a fast, explicit, "fail-fast" approach with minimal hand-holding.
* **Details:**
  * **Revocation:** No confirmation prompt (`[y/N]`) before revoking an overseer relationship. Execute the destructive action immediately.
  * **Authentication:** No automatic re-authentication if a session expires or a request fails due to authentication errors.
  * **API Errors:** If an API request fails (e.g., 401 Unauthorized), the CLI must output the raw API error response rather than catching it and displaying a custom, friendly error message.