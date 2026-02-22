# Phase 28 Context: Audit & Test Strategy

## Goal
System documentation accurately reflects current application flows and outlines a complete testing strategy.

## Decisions Made

### 1. Subscription Edge Case Coverage
- **Scope:** List all possible edge cases first (upgrades, downgrades, cancellations, resumes, payment failures, etc.) and prioritize them later.
- **Focus:** Must reason deeply about how the subscription is implemented in the codebase to uncover hidden corner cases (e.g., what happens when an overseer resumes a subscription).

### 2. Flow Documentation Structure
- **Format:** Every application flow must be documented in two formats:
  1. A shortened list of steps for a quick glance.
  2. A detailed flow description including the specific API endpoints and JSON payloads involved.
- **Visuals:** Include sequence diagrams to formalize the payment and authentication flows.

### 3. Cryptographic Authentication Edge Cases
- **Scope:** The audit must explicitly map out edge cases in the cryptographic authentication flows, including DPoP validation, Ed25519 signatures, and agent claim challenges, alongside the subscription flows.

## Guardrails
- **No Test Execution Yet:** This phase is strictly for auditing documentation and generating the strategy/scenarios. Test implementation occurs in Phases 29-31.
- **Source of Truth:** Base the audit on the existing codebase and the current `docs/v1` documentation.
