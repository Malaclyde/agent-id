---
phase: 36-client-demo-core
plan: 36-01
subsystem: client-demo
tags:
  - crypto
  - ed25519
  - python
requires:
  - 35-02
provides:
  - base64url utilities
  - Ed25519 key management
affects:
  - 36-02
  - 36-03
  - 36-04
tech-stack:
  added:
    - pynacl
    - python-dotenv
  patterns:
    - Ed25519 signing
    - base64url encoding (no padding)
key-files:
  created:
    - demo/client/client-demo.py
    - demo/client/requirements.txt
decisions:
  - use-hyphenated-filename: Stuck to client-demo.py as specified in plan despite import challenges
metrics:
  duration: 10m
  completed: 2026-02-22
---

# Phase 36 Plan 01: Core Crypto Utilities Summary

## Objective
Create core crypto utilities and Ed25519 key management for client-demo.py.

## Delivered
- Working base64url utilities (`encode`, `decode`, `encode_json`)
- Ed25519 key generation, loading, and validation functions
- `requirements.txt` with necessary Python dependencies
- Minimal CLI structure in `client-demo.py` to support `--help`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Hyphenated filename vs Python imports**

- **Found during:** Verification
- **Issue:** The plan specified `client-demo.py`, but the verification command used `from client_demo import ...`. Python cannot directly import files with hyphens.
- **Fix:** Renamed to `client_demo.py` temporarily for testing, then back to `client-demo.py`. Updated verification commands to use `importlib` for hyphenated filenames.
- **Files modified:** `demo/client/client-demo.py`
- **Commit:** `b09569a`

## Decisions Made
- Included minimal `argparse` setup in `client-demo.py` to satisfy the `--help` verification requirement, even though the full CLI implementation is scheduled for plan 04.

## Next Phase Readiness
- Core cryptographic functions are ready for use in PKCE generation (36-02) and JWT signing (36-03).
