# Requirements: Demo Scripts Milestone

**Defined:** 2026-02-22
**Core Value:** Users can demonstrate and test all agent and client API capabilities through runnable Python scripts.
**Previous Milestone:** v2.1 Comprehensive Testing (In Progress)

---

## v2.2 Requirements

### Agent Demo - Configuration (ACONF)

- [ ] **ACONF-01**: User can configure agent demo via .env file with backend URL and Ed25519 keys.
- [ ] **ACONF-02**: User can generate Ed25519 keypairs and save to .env file.
- [ ] **ACONF-03**: Script validates public key derives from private key on configuration.

### Agent Demo - Registration & Auth (AAUTH)

- [ ] **AAUTH-01**: User can register an agent with two-step challenge flow (initiate → complete with signature).
- [ ] **AAUTH-02**: User can log in an agent using DPoP proof authentication.
- [ ] **AAUTH-03**: User can log out an agent by revoking session.
- [ ] **AAUTH-04**: User can query current agent info via /agents/me endpoint.
- [ ] **AAUTH-05**: User can rotate agent keys with dual-signature verification.

### Agent Demo - Queries (AQUERY)

- [ ] **AQUERY-01**: User can query agent's OAuth authorization history.
- [ ] **AQUERY-02**: User can query agent's current overseer information.

### Agent Demo - Claim & Oversight (ACLAIM)

- [ ] **ACLAIM-01**: User can complete a claim challenge using session or DPoP auth.
- [ ] **ACLAIM-02**: User can revoke current overseer relationship.

### Agent Demo - OAuth Client (AOAUTH)

- [ ] **AOAUTH-01**: User can register an OAuth client as an agent with key generation or provision options.
- [ ] **AOAUTH-02**: User can initiate OAuth authorization for a client, receiving authorization code.

### Client Demo - Configuration (CCONF)

- [ ] **CCONF-01**: User can configure client demo via .env file with backend URL, client ID, and Ed25519 keys.
- [ ] **CCONF-02**: User can generate PKCE code verifier and challenge pair.
- [ ] **CCONF-03**: User can generate Ed25519 keypairs for client authentication.

### Client Demo - Token Flow (CTOKEN)

- [ ] **CTOKEN-01**: User can perform token exchange with HTTP callback server and client assertion JWT.
- [ ] **CTOKEN-02**: User can refresh access tokens using refresh token grant.
- [ ] **CTOKEN-03**: User can revoke access or refresh tokens.

### Client Demo - OAuth Operations (COAUTH)

- [ ] **COAUTH-01**: User can query userinfo endpoint with DPoP-bound access token.
- [ ] **COAUTH-02**: User can introspect tokens to check status and metadata.
- [ ] **COAUTH-03**: User can query OpenID discovery endpoint.

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Security hardening | Constraint: Demo scripts only, not production |
| Automated tests for demos | Constraint: Out of scope for this milestone |
| Shadow claim initiation | Constraint: Agent only completes claims, doesn't initiate |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ACONF-01 | Phase 33 | Complete |
| ACONF-02 | Phase 33 | Complete |
| ACONF-03 | Phase 33 | Complete |
| AAUTH-01 | Phase 33 | Complete |
| AAUTH-02 | Phase 33 | Complete |
| AAUTH-03 | Phase 33 | Complete |
| AAUTH-04 | Phase 33 | Complete |
| AAUTH-05 | Phase 34 | Complete |
| AQUERY-01 | Phase 34 | Complete |
| AQUERY-02 | Phase 34 | Complete |
| ACLAIM-01 | Phase 34 | Complete |
| ACLAIM-02 | Phase 34 | Complete |
| AOAUTH-01 | Phase 35 | Complete |
| AOAUTH-02 | Phase 35 | Complete |
| CCONF-01 | Phase 36 | Complete |
| CCONF-02 | Phase 36 | Complete |
| CCONF-03 | Phase 36 | Complete |
| CTOKEN-01 | Phase 36 | Complete |
| CTOKEN-02 | Phase 37 | Complete |
| CTOKEN-03 | Phase 37 | Complete |
| COAUTH-01 | Phase 37 | Complete |
| COAUTH-02 | Phase 37 | Complete |
| COAUTH-03 | Phase 37 | Complete |

**Coverage:**
- v2.2 requirements: 22 total
- Mapped to phases: 22 (100%)
- Unmapped: 0

---
*Requirements defined: 2026-02-22*
