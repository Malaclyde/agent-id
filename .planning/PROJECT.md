# Agent-ID Identity Platform

## What This Is

An identity web app for LLM agents with OAuth2 provider capabilities, Ed25519 cryptographic authentication, and overseer management. It enables agents to authenticate via challenge-response signing and supports third-party OAuth flows with PKCE and DPoP.

## Core Value

Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.

---

## Current Milestone: Planning Next Milestone (v2.3)

**Goal:** Evolve the Agent-ID platform based on demo script feedback and security audit findings.

---

## Requirements

### Validated (Existing Capabilities)

- ✓ OAuth2 Authorization Code Flow with PKCE and DPoP — v2.2
- ✓ Agent authentication via Ed25519 challenge-response — v2.2
- ✓ Agent claim procedure with cryptographic verification — v2.2
- ✓ Client registration and OAuth token management — v2.2
- ✓ Basic subscription tier structure (FREE, BASIC, PRO, etc.)
- ✓ Overseer-agent oversight relationships
- ✓ Paddle payment integration with webhook handling
- ✓ Shadow overseer cryptographic ID generation
- ✓ Comprehensive documentation and test suite
- ✓ Unify shadow claim with standard claim challenge system
- ✓ Agent confirmation step before payment processing
- ✓ Proper state management (initiated → awaiting-payment → completed)
- ✓ Paddle `transaction.completed` webhook handling for one-time payments
- ✓ Comprehensive test coverage for shadow claim flows
- ✓ Comprehensive testing suite (backend, frontend, E2E)
- ✓ Python Agent Demo CLI (Full API coverage) — v2.2
- ✓ Python Client Demo CLI (Full OAuth coverage) — v2.2

### Active

- [ ] Security audit of DPoP and key rotation flows
- [ ] Database migration to Drizzle ORM
- [ ] Repository redesign (public/private split)

### Out of Scope

- Security hardening (demo scripts only)
- Production deployment of scripts
- Automated testing of demo scripts
- Database migration to Drizzle ORM (deferred to future milestone)
- Repository redesign (public/private split) (deferred)
- Admin features and company registration (deferred)
- OAuth providers beyond current implementation (Google, Apple, GitHub) (deferred)
- OpenAPI/Swagger documentation (deferred)
- Real-time chat or video features (never)
- Mobile native apps (never for v1)

## Context

**Current State:**
- Backend: Cloudflare Workers + Hono + D1 (SQLite) + KV
- Frontend: React SPA for GitHub Pages
- Payment: Paddle Billing integration (working)
- Documentation: Complete and accurate
- Testing: Comprehensive test suite in place

**Technical Debt:**
- Large route files (agents.ts: 876 lines)
- 67+ TypeScript `any` types
- Complex SQL joins without query builder

## Constraints

- **Compatibility:** Cannot break existing OAuth/agent flows
- **Python Version:** Python 3.x with standard library preferred
- **Dependencies:** Minimize external dependencies

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python scripts | Widely used, good crypto library support | ✓ Good (Milestone v2.2) |
| .env file config | Simple, standard configuration pattern | ✓ Good (Milestone v2.2) |
| Print-only error handling | Demo scripts focus on clarity | ✓ Good (Milestone v2.2) |
| Dual-signature rotation | Enhanced security for key rotation | ✓ Good (Milestone v2.2) |
| private_key_jwt | RFC 7523 compliant client auth | ✓ Good (Milestone v2.2) |
| DPoP proof binding | RFC 9449 compliant token binding | ✓ Good (Milestone v2.2) |

---
*Last updated: 2026-02-27 after v2.2 milestone*
