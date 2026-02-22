# Agent-ID Identity Platform

## What This Is

An identity web app for LLM agents with OAuth2 provider capabilities, Ed25519 cryptographic authentication, and overseer management. It enables agents to authenticate via challenge-response signing and supports third-party OAuth flows with PKCE and DPoP.

## Core Value

Users can trust that the Agent-ID platform correctly handles authentication, authorization, and subscription management with accurate documentation and comprehensive test coverage.

---

## Current Milestone: v2.2 Demo Scripts

**Goal:** Create runnable Python demo scripts that demonstrate all agent and client capabilities against the backend API.

**Target features:**
- Agent demo script with all agent-facing API operations
- Client demo script with all OAuth client operations
- Comprehensive error handling with clear error messages
- Local .env configuration management
- Cryptographic operations (Ed25519, DPoP, PKCE)

**Previous Milestone:** v2.1 Comprehensive Testing (In Progress)

---

## Requirements

### Validated (Existing Capabilities)

- ✓ OAuth2 Authorization Code Flow with PKCE and DPoP
- ✓ Agent authentication via Ed25519 challenge-response
- ✓ Agent claim procedure with cryptographic verification
- ✓ Client registration and OAuth token management
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

### Active (This Milestone)

#### Agent Demo Script
- [ ] Configuration management (.env file)
- [ ] Ed25519 key generation
- [ ] Agent registration (two-step challenge flow)
- [ ] Agent login (DPoP authentication)
- [ ] Agent logout
- [ ] Query agent info
- [ ] OAuth history query
- [ ] Overseer info query
- [ ] Claim completion
- [ ] Overseer revocation
- [ ] Key rotation (dual-signature flow)
- [ ] Client registration as agent
- [ ] OAuth authorization

#### Client Demo Script
- [ ] Configuration management (.env file)
- [ ] PKCE verifier/challenge generation
- [ ] Ed25519 key generation
- [ ] Token exchange (with HTTP callback server)
- [ ] Token refresh
- [ ] Userinfo query (DPoP-bound)
- [ ] Token revocation
- [ ] Token introspection
- [ ] OpenID discovery

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
| Python scripts | Widely used, good crypto library support | — Pending |
| .env file config | Simple, standard configuration pattern | — Pending |
| Print-only error handling | Demo scripts focus on clarity | — Pending |

---
*Last updated: 2026-02-22 after milestone initialization*
