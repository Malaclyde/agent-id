# Phase 34: Agent Demo - Extended Operations - Research

**Researched:** Sun Feb 22 2026
**Domain:** Python CLI Tooling, External API Integration, Ed25519 Cryptography
**Confidence:** HIGH

## Summary

The goal of this phase is to construct a resilient, fail-fast Python CLI script that handles querying API records, generating/verifying Ed25519 claims, managing overseer relationships, and executing automatic key rotation without manual intervention.

To strictly comply with architectural decisions from the phase context, the solution emphasizes the Python standard library (`argparse`, `urllib.request`, `json`, `shutil`) to minimize external dependencies. External libraries are limited to `PyNaCl` (for Ed25519 cryptography) and `python-dotenv` (for `.env` mutations). The design must emphasize explicit developer-centric behavior, specifically favoring raw API logs over formatted error messages, and eliminating paginations or confirmation prompts completely.

**Primary recommendation:** Use `argparse.ArgumentParser` to define a subcommand-based CLI that utilizes `urllib.request` for un-intercepted API calls and `python-dotenv`'s `set_key` alongside `shutil.copy2` for atomic `.env` rotation.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `argparse` | built-in | CLI Subcommands & Flags | Built-in solution for strict subcommand modeling and flag parsing (`--challenge-id`, `--overseer-id`). |
| `urllib.request` | built-in | HTTP Requests | Standard library selection for REST API interactions, avoiding third-party client bloat. |
| `json` | built-in | Serialization | Generates raw, pretty-printed outputs with `json.dumps(obj, indent=2)`. |
| `shutil` | built-in | File Operations | Standard library tool for generating backups like `.env.bak`. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `python-dotenv` | current | Environment Variables | Reading configuration and safely mutating the `.env` file via `set_key()` while preserving comments. |
| `PyNaCl` | current | Cryptography | `SigningKey` generation, Ed25519 signature creation for payloads and claim construction (matches `@noble/ed25519`). |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `urllib.request` | `requests` / `httpx` | `requests` provides a friendlier API but introduces unnecessary external dependencies, violating prior architectural decisions to minimize bloat. |
| Custom file parsing | `dotenv.set_key` | Regex-based file rewriting is error-prone. `set_key` flawlessly handles quoted strings and preserves adjacent comments. |

**Installation:**
```bash
# Based on existing python dependencies
pip install pynacl python-dotenv
```

## Architecture Patterns

### Recommended CLI Structure
A monolithic Python script organized linearly into functional responsibilities:
```
agent_demo.py
├── Configuration Loading (load_dotenv)
├── HTTP Request Wrapper (urllib.request + error handling)
├── Subcommand Handlers
│   ├── handle_query()
│   ├── handle_claim()
│   ├── handle_overseer()
│   └── handle_rotate_keys()
└── Main Entrypoint (argparse setup & dispatch)
```

### Pattern 1: Fail-Fast HTTP Client
**What:** A unified wrapper for API requests that fires `urllib.request.urlopen` and catches `urllib.error.HTTPError`, forcefully printing the unadulterated response body string.
**When to use:** All network-bound operations (queries, claims, revocation).
**Example:**
```python
import urllib.request
import urllib.error
import sys

def make_request(url, headers, data=None):
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        # CONTEXT MANDATE: Output raw API error response, fail fast
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)
```

### Pattern 2: Atomic Zero-Prompt File Mutation
**What:** A function for key rotation that strictly calls `shutil.copy2` then `dotenv.set_key` sequentially.
**When to use:** Post-successful key rotation API response.
**Example:**
```python
import shutil
import dotenv

def rotate_env_keys(env_path, new_public_key, new_private_key):
    # CONTEXT MANDATE: Create/overwrite .env.bak
    shutil.copy2(env_path, f"{env_path}.bak")
    
    # CONTEXT MANDATE: Auto-overwrite existing .env without prompting
    dotenv.set_key(env_path, "AGENT_PUBLIC_KEY", new_public_key)
    dotenv.set_key(env_path, "AGENT_PRIVATE_KEY", new_private_key)
```

### Anti-Patterns to Avoid
- **Confirmation Prompts:** Accidental usage of `input("[y/N]")` before executing destructive actions like overseer revocation. Execute destructive actions immediately.
- **Error Obfuscation:** Catching `HTTPError` and re-raising or logging generic summaries (`"HTTP Error 401: Unauthorized"`). `HTTPError` contains the raw JSON body and MUST be dumped via `.read().decode()`.
- **Auto Re-authentication:** Attempting to trap `401 Unauthorized` responses and re-running the token exchange. Fail and crash immediately instead.

## Don't Hand-Roll

Problems that look simple but have existing robust solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Environment updates | Custom `open().write()` | `dotenv.set_key` | Handles edge cases with quoted strings, missing newlines, and preserves existing `# comments` perfectly. |
| CLI Argument parsing | `sys.argv` looping | `argparse` | Subparsers and specific flag constraints (`--challenge-id`) are difficult to validate comprehensively using raw `argv`. |
| File Backup logic | Reading and writing file chunks | `shutil.copy2` | `shutil.copy2` natively handles "overwrite if exists" out of the box and preserves file metadata natively. |

**Key insight:** The user context explicitly dictates formatting outputs using raw, pretty-printed JSON. Use `json.dumps(obj, indent=2)` over manual table generation.

## Common Pitfalls

### Pitfall 1: Failing to Read the HTTPError Body
**What goes wrong:** The CLI prints `<HTTPError 400: Bad Request>` rather than the actual API error message, obscuring why the request failed.
**Why it happens:** In `urllib.request`, an `HTTPError` is an exception, but it is *also* a file-like response object. Developers often print the exception object directly.
**How to avoid:** Always call `e.read().decode('utf-8')` on the exception before exiting.
**Warning signs:** Developer logs showing standard HTTP status codes but no application-specific error details.

### Pitfall 2: Appending Instead of Overwriting Backups
**What goes wrong:** Generating `.env.bak`, `.env.bak.1`, `.env.bak.2`, or failing to rotate keys the second time because `.env.bak` already exists.
**Why it happens:** Over-engineering the backup process or utilizing strict file-creation modes (`open(..., 'x')`).
**How to avoid:** `shutil.copy2('.env', '.env.bak')` automatically performs a destructive overwrite if the destination already exists, guaranteeing a single backup.

### Pitfall 3: Subparser Flag Omission
**What goes wrong:** The CLI relies on positional arguments instead of flags for explicit parameters like the challenge ID.
**Why it happens:** Defaulting to `parser.add_argument('challenge_id')` instead of `--challenge-id`.
**How to avoid:** Explicitly prefix the flag names when defining arguments in the `claim` subparser: `parser.add_argument('--challenge-id', required=True)`.

## Code Examples

Verified patterns mapped directly to Context Decisions:

### Argparse Subcommands with Explicit Flags
```python
import argparse

parser = argparse.ArgumentParser(description="Agent Extended Operations CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: claim
claim_parser = subparsers.add_parser("claim")
claim_parser.add_argument("--challenge-id", required=True, help="The ID of the claim challenge")
claim_parser.add_argument("--overseer-id", required=True, help="The ID of the overseer")

# Subcommand: query
query_parser = subparsers.add_parser("query")
query_parser.add_argument("target", choices=["history", "overseers"])
```

### Raw Output & Pretty-Printing JSON
```python
import json

def print_output(response_string):
    # Parse the incoming string (from API) into a Python dict, then dump
    # using indentation to satisfy the "pretty-printed for readability" requirement.
    # We DO NOT paginate or truncate.
    data = json.loads(response_string)
    print(json.dumps(data, indent=2))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Multi-step manual key rotation | Automated in-place file mutation | Discuss Phase | Removes human error; forces developers to handle `.env.bak` state safely within the script. |
| Interactive CLI Prompts (`inquirer`) | Pure un-prompted CLI execution | Discuss Phase | Enforces predictable, CI/CD-friendly operations. No destructive operations will block on STDIN. |

## Open Questions

None. The technical path forward is fully mapped and constrained effectively by standard library components.

## Sources

### Primary (HIGH confidence)
- `34-CONTEXT.md` - Required implementation directives (Output formatting, interaction patterns, fail-fast operations).
- Python Standard Library Documentation (`urllib.request`, `argparse`, `shutil`, `json`) - Recommended for the strict constraint against bloat.
- PyPI `python-dotenv` Documentation - Source of truth for programmatic `.env` mutation using `dotenv.set_key`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Directly aligns with user context requests (`argparse`, `urllib.request`) and python fundamentals.
- Architecture: HIGH - Adheres to explicit fail-fast, unprompted mandates from `CONTEXT.md`.
- Pitfalls: HIGH - Common problems encountered specifically with `urllib` HTTPError handling and `shutil` overwrites.

**Research date:** Sun Feb 22 2026
**Valid until:** Sun Mar 22 2026
