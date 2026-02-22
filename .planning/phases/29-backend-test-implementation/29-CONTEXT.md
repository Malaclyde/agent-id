# Phase 29 Context: Backend Test Implementation

## Goal
Backend APIs and cryptographic utilities are fully verifiable in isolated, ephemeral environments without network overhead.

## Decisions Made

### 1. Ephemeral Data Architecture
- **Relationship Initialization:** Use an in-memory builder pattern inside tests to construct complex agent/overseer relationships, rather than a dynamic API or static fixtures.
- **Data Consistency:** Implement strict setup/teardown hooks (`beforeEach`/`afterEach`) to completely reset the mock database state and prevent pollution across tests.
- **Verification:** Verify relationships and states via direct mock queries (`Direct Mock Queries`), bypassing the public API (`SELF.fetch()`) for internal relationship verification.
- **Invalid State:** Test the backend's resilience to corrupted or invalid data by relying on API payload validation rather than mocking corrupted database states.

### 2. Time & Webhook Simulation
- **Time Simulation:** Use Vitest's `vi.useFakeTimers()` to artificially advance time for testing token expiry and webhook retry delays.
- **Webhook Events:** Inject mock webhook payloads directly via `SELF.fetch()` to simulate asynchronous events like Paddle webhooks.
- **Webhook Retries:** Implement mock server failures to automatically trigger and verify the retry mechanism.
- **Signature Validation:** Generate valid test signatures using a known test secret for the injected payloads, rather than bypassing validation or mocking the function.

### 3. Cryptographic Key Strategy
- **Key Generation:** Generate a unique Ed25519 keypair and DPoP signature for each individual test to ensure absolute isolation.
- **Key Distribution:** Distribute the necessary keys (public/private) to the test setup via dependency injection rather than shared global state or temporary files.
- **Key Rotation:** Simulate key rotation by manually updating the database mock with a new key and verifying that the old key fails.
- **Invalid Signatures:** Verify the backend correctly rejects tampered payloads by intentionally generating invalid signatures (e.g., using incorrect keys or algorithms).

### 4. Mock Isolation Boundaries
- **D1/KV Isolation:** Create a new D1/KV mock instance per test file (suite) to balance test speed with preventing cross-test data pollution.
- **Teardown Strategy:** Ensure the mock database is completely clean for the next test execution by dropping and recreating all tables using `afterEach` hooks.
- **Concurrency:** Run tests concurrently with completely isolated D1/KV instances per Vitest worker.
- **KV Implementation:** Use a simple in-memory JavaScript Map or Object to mock the KV namespace, prioritizing speed and simplicity over a dedicated local store.

## Guardrails
- **Scope:** This phase focuses exclusively on backend (API and database) testing using ephemeral D1/KV mocks and `@cloudflare/vitest-pool-workers`. Frontend and E2E testing belong to subsequent phases.
- **Fidelity:** Prioritize exact Web Crypto API parity by strictly mandating `@cloudflare/vitest-pool-workers` for all cryptographic tests.
