# Project Roadmap

**Project:** Agent-ID Identity Platform
**Current Milestone:** v2.2 Demo Scripts
**Goal:** Create runnable Python demo scripts that demonstrate all agent and client capabilities against the backend API.

## Overview
This roadmap details the implementation of Python demo scripts for the Agent-ID platform. The milestone consists of agent demo script with full API coverage and client demo script with OAuth flow support.

---

## Phases

### Phase 33: Agent Demo - Core
**Goal:** Agent demo script handles configuration, key generation, registration, and basic authentication.
**Dependencies:** None
**Requirements:** ACONF-01, ACONF-02, ACONF-03, AAUTH-01, AAUTH-02, AAUTH-03, AAUTH-04
**Plans:** 5 plans

**Success Criteria:**
1. User can configure .env file with backend URL and keys via command line.
2. User can generate Ed25519 keypairs and save to .env.
3. User can register a new agent with two-step challenge flow.
4. User can log in using DPoP proof and receive session.
5. User can log out and query agent info.

**Plan List:**
- [x] 33-01-PLAN.md — Crypto utilities and Ed25519 key management
- [x] 33-02-PLAN.md — Configuration management with .env handling
- [x] 33-03-PLAN.md — Registration flow with challenge-response
- [x] 33-04-PLAN.md — Authentication operations (login, logout, info)
- [x] 33-05-PLAN.md — CLI implementation and end-to-end verification

---

### Phase 34: Agent Demo - Extended Operations
**Goal:** Agent demo script handles queries, claims, oversight, and key rotation.
**Dependencies:** Phase 33
**Requirements:** AAUTH-05, AQUERY-01, AQUERY-02, ACLAIM-01, ACLAIM-02
**Plans:** 3 plans

**Success Criteria:**
1. User can rotate agent keys with dual-signature verification.
2. User can query OAuth history and overseer info.
3. User can complete claim challenges with session or DPoP.
4. User can revoke overseer relationship.

**Plan List:**
- [ ] 34-01-PLAN.md — Query subcommand and fail-fast HTTP wrapper
- [ ] 34-02-PLAN.md — Claim challenges and overseer revocation
- [ ] 34-03-PLAN.md — Key rotation with dual-signature and .env backup

---

### Phase 35: Agent Demo - OAuth Client
**Goal:** Agent demo script handles OAuth client registration and authorization.
**Dependencies:** Phase 33
**Requirements:** AOAUTH-01, AOAUTH-02

**Success Criteria:**
1. User can register OAuth clients with three key provision options.
2. User can initiate OAuth authorization and receive authorization code.

---

### Phase 36: Client Demo - Core
**Goal:** Client demo script handles configuration, PKCE, key generation, and token exchange.
**Dependencies:** None
**Requirements:** CCONF-01, CCONF-02, CCONF-03, CTOKEN-01

**Success Criteria:**
1. User can configure .env file with client credentials.
2. User can generate PKCE verifier/challenge pairs.
3. User can generate Ed25519 keypairs for client auth.
4. User can perform token exchange with blocking HTTP callback server.

---

### Phase 37: Client Demo - OAuth Operations
**Goal:** Client demo script handles token refresh, userinfo, revocation, and introspection.
**Dependencies:** Phase 36
**Requirements:** CTOKEN-02, CTOKEN-03, COAUTH-01, COAUTH-02, COAUTH-03

**Success Criteria:**
1. User can refresh access tokens with refresh token grant.
2. User can revoke access or refresh tokens.
3. User can query userinfo with DPoP-bound access token.
4. User can introspect tokens for status and metadata.
5. User can query OpenID discovery endpoint.

---

## Progress

| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 33 - Agent Demo Core | Agent demo script handles configuration, key generation, registration, and basic authentication. | ACONF-01, ACONF-02, ACONF-03, AAUTH-01, AAUTH-02, AAUTH-03, AAUTH-04 | Complete |
| 34 - Agent Demo Extended | Agent demo script handles queries, claims, oversight, and key rotation. | AAUTH-05, AQUERY-01, AQUERY-02, ACLAIM-01, ACLAIM-02 | Pending |
| 35 - Agent Demo OAuth | Agent demo script handles OAuth client registration and authorization. | AOAUTH-01, AOAUTH-02 | Pending |
| 36 - Client Demo Core | Client demo script handles configuration, PKCE, key generation, and token exchange. | CCONF-01, CCONF-02, CCONF-03, CTOKEN-01 | Pending |
| 37 - Client Demo OAuth | Client demo script handles token refresh, userinfo, revocation, and introspection. | CTOKEN-02, CTOKEN-03, COAUTH-01, COAUTH-02, COAUTH-03 | Pending |
