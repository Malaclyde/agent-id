# Project State

## Project Reference
**Project:** Agent-ID Identity Platform
**Core Value:** Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.
**Current Focus:** v2.2 Demo Scripts - Creating Python demo scripts for agent and client operations.

## Current Position
- **Phase:** 35-agent-demo-oauth (Agent Demo - OAuth Client)
- **Plan:** 01 of 02
- **Status:** In progress
- **Last activity:** 2026-02-22 — Completed 35-01-PLAN.md (register-client subcommand)
- **Progress:** [████████████░░░░░░░░░░░░░] 50% (1 of 2 Phase 35 Plans Complete)

## Performance Metrics
- **Velocity:** N/A
- **Quality:** N/A

## Accumulated Context
**Architecture Decisions:**
- Prioritizing `@cloudflare/vitest-pool-workers` for exact Web Crypto API parity.
- Utilizing ephemeral D1 instances for backend testing to simulate production.
- `@playwright/test` selected over Cypress for native multi-context and iframe support.
- Using PyNaCl for Ed25519 (matches backend @noble/ed25519).
- Using python-dotenv for configuration management.
- Using urllib.request for HTTP requests (standard library).
- Using argparse for CLI to minimize external dependencies.
- Fail-fast HTTP wrapper (make_request) exits via sys.exit(1) on HTTPError, printing raw response body to stderr.
- Raw JSON output via print_output for all query results (no pagination or truncation).
- Dual auth pattern: claim subcommand auto-selects Bearer (session) vs DPoP based on config state.
- No confirmation prompts on destructive actions (revoke-overseer executes immediately).
- Dual-signature key rotation: DPoP proof with old key + body signature with new key, no Bearer on complete step.
- Atomic .env backup via shutil.copy2 before save_config for recoverability.

**Active Blockers:**
- None.

**Next Steps:**
- Proceed to Phase 35 (Agent Demo - OAuth Client) for client registration and authorization

## Session Continuity
**Last session:** 2026-02-22
**Stopped at:** Completed 34-03-PLAN.md — Phase 34 complete
**Resume file:** None


---
*Updated: 2026-02-22*
