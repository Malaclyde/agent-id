# Project Roadmap

**Project:** Agent-ID Identity Platform
**Current Milestone:** Planning Next Milestone

## Overview

This roadmap tracks the evolution of the Agent-ID identity platform.

## Milestones

- ✅ **v2.2 Demo Scripts** — Phases 33-37 (shipped 2026-02-27)
- 📋 **v2.3 Platform Evolution** — Phases 38+ (planned)

## Phases

<details>
<summary>✅ v2.2 Demo Scripts (Phases 33-37) — SHIPPED 2026-02-27</summary>

- [x] Phase 33: Agent Demo - Core (5/5 plans) — completed 2026-02-22
- [x] Phase 34: Agent Demo - Extended Operations (3/3 plans) — completed 2026-02-22
- [x] Phase 35: Agent Demo - OAuth Client (2/2 plans) — completed 2026-02-22
- [x] Phase 36: Client Demo - Core (4/4 plans) — completed 2026-02-22
- [x] Phase 37: Client Demo - OAuth Operations (2/2 plans) — completed 2026-02-27

</details>

### 📋 v2.3 Platform Evolution (Planned)
### Phase 29: Backend Test Implementation
**Goal:** Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments.
**Dependencies:** Phase 28
**Requirements:** BETEST-01, BETEST-02, BETEST-03
**Plans:** 10 plans
- [x] 29-01-PLAN.md — Test Infrastructure Setup & DB/KV Helpers
- [x] 29-02-PLAN.md — Cryptographic & Data Builder Helpers
- [x] 29-03-PLAN.md — Core API & Webhook Integration Tests
- [x] 29-04-PLAN.md — Overseers & Agents Integration Tests
- [x] 29-05-PLAN.md — Clients & Subscriptions Integration Tests
- [x] 29-06-PLAN.md — OAuth API Integration Tests
- [ ] 29-07-PLAN.md — Fix Vitest Pool Configuration (Gap Closure)
- [ ] 29-08-PLAN.md — Fix Failing Unit Tests (Gap Closure)
- [ ] 29-09-PLAN.md — Fix Overseer API Tests (Gap Closure)
- [ ] 29-10-PLAN.md — Fix Agent API Tests (Gap Closure)

- [ ] Phase 38: Security Audit & Hardening
- [ ] Phase 39: Drizzle ORM Migration

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 33. Agent Demo Core | v2.2 | 5/5 | Complete | 2026-02-22 |
| 34. Agent Demo Extended | v2.2 | 3/3 | Complete | 2026-02-22 |
| 35. Agent Demo OAuth | v2.2 | 2/2 | Complete | 2026-02-22 |
| 36. Client Demo Core | v2.2 | 4/4 | Complete | 2026-02-22 |
| 37. Client Demo OAuth | v2.2 | 2/2 | Complete | 2026-02-27 |


| Phase | Goal | Requirements | Status |
|-------|------|--------------|--------|
| 28 - Audit & Test Strategy | System documentation accurately reflects current application flows and outlines a complete testing strategy. | AUDIT-01, AUDIT-02, AUDIT-03 | Complete |
| 29 - Backend Test Implementation | Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments. | BETEST-01, BETEST-02, BETEST-03 | Gap Closure |
| 30 - Frontend Test Implementation | Frontend React components and edge cases are verifiable without relying on a live backend. | FETEST-01, FETEST-02, FETEST-03 | Pending |
| 31 - End-to-End Test Implementation | Full application workflows, including real third-party integrations, are automatically verifiable. | E2ETEST-01, E2ETEST-02, E2ETEST-03 | Pending |
| 32 - Bug Discovery & Reporting | All application bugs are identified and documented for future resolution. | BUGS-01, BUGS-02 | Pending |
