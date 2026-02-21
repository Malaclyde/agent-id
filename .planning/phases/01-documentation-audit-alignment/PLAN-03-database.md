---
phase: 01 - Documentation Audit & Alignment
plan: PLAN-03-database
type: implementation
wave: 2
depends_on: [PLAN-01-audit]
files_modified: []
autonomous: false
must_haves:
  - All database tables documented in docs/v1/database/
  - Complete schema overview with ER diagram
  - Column types, constraints, and defaults documented
  - All indexes and their purposes documented
  - Table relationships mapped
  - Documentation derived from actual migration files
---

# Plan 3: Database Documentation

## Objective
Create comprehensive database documentation derived from migration files, documenting all 10+ tables, their columns, constraints, relationships, and indexes.

## Context
No database documentation currently exists (docs/v1/database/ doesn't exist). The database schema is defined in:
- backend/migrations/0001_initial.sql (main schema)
- backend/migrations/0004_add_oauth_client_disabled_fields.sql
- backend/migrations/0005_create_subscription_tiers.sql

We need to extract and document all tables, columns, types, constraints, indexes, and relationships.

---

## Tasks

<task type="auto">
  <name>Document Core Tables</name>
  <files>
    <file>docs/v1/database/tables/agents.md</file>
    <file>docs/v1/database/tables/overseers.md</file>
    <file>docs/v1/database/tables/oversights.md</file>
    <file>docs/v1/database/tables/oauth_clients.md</file>
    <file>backend/migrations/0001_initial.sql</file>
    <file>backend/migrations/0004_add_oauth_client_disabled_fields.sql</file>
  </files>
  <action>
    Create database documentation for the core identity tables:
    
    1. Create docs/v1/database/tables/agents.md:
       - Document the agents table from 0001_initial.sql
       - Columns: id, name, public_key, description, created_at, updated_at, oauth_count, billing_period_end
       - Primary key, UNIQUE constraints
       - Index: idx_agents_public_key
       - Purpose: Stores registered agent identities with Ed25519 keys
    
    2. Create docs/v1/database/tables/overseers.md:
       - Document the overseers table
       - Columns: id, name, email, password_hash, paddle_subscription_id, paddle_customer_id, created_at, updated_at
       - Primary key, UNIQUE on email
       - Indexes: idx_overseers_email, idx_overseers_paddle_subscription, idx_overseers_paddle_customer
       - Purpose: Human users who manage agents
    
    3. Create docs/v1/database/tables/oversights.md:
       - Document the oversights table (agent-overseer relationships)
       - Columns: id, overseer_id, agent_id, active, marked_for_cancellation, created_at, updated_at
       - Foreign key: agent_id -> agents.id (CASCADE DELETE)
       - Indexes: idx_oversights_overseer, idx_oversights_agent, idx_oversights_active
       - Unique: idx_oversights_overseer_agent
       - Purpose: Tracks which overseers manage which agents
    
    4. Create docs/v1/database/tables/oauth_clients.md:
       - Document the oauth_clients table
       - Include migration 0004 updates (marked_for_cancellation)
       - Columns: id, owner_type, owner_id, client_secret_hash, name, redirect_uris, token_endpoint_auth_method, application_type, scope, public_key, created_at, updated_at, marked_for_cancellation
       - Indexes: idx_oauth_clients_owner, idx_oauth_clients_marked_for_cancellation
       - Purpose: OAuth client applications
    
    Use the table documentation template from research findings with proper markdown tables showing column details.
  </action>
  <verify>
    - agents.md documents all columns with types and constraints
    - overseers.md documents all columns and indexes
    - oversights.md documents foreign keys and cascade behaviors
    - oauth_clients.md includes migration 0004 fields
    - All tables have purpose descriptions
    - Column details include types, defaults, constraints
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Document OAuth and Session Tables</name>
  <files>
    <file>docs/v1/database/tables/oauth_requests.md</file>
    <file>docs/v1/database/tables/client_blocks.md</file>
    <file>docs/v1/database/tables/sessions.md</file>
    <file>docs/v1/database/tables/challenges.md</file>
    <file>docs/v1/database/tables/subscription_tiers.md</file>
    <file>backend/migrations/0001_initial.sql</file>
    <file>backend/migrations/0005_create_subscription_tiers.sql</file>
  </files>
  <action>
    Create database documentation for OAuth flow and session tables:
    
    1. Create docs/v1/database/tables/oauth_requests.md:
       - Columns: id, agent_id, client_id, scopes, status, created_at
       - Foreign key: agent_id -> agents.id (CASCADE DELETE)
       - Indexes: idx_oauth_requests_agent, idx_oauth_requests_created
       - Purpose: Records of OAuth authorization requests
    
    2. Create docs/v1/database/tables/client_blocks.md:
       - Columns: id, agent_id, overseer_id, client_id, created_at
       - Foreign keys: agent_id -> agents.id, overseer_id -> overseers.id
       - Unique: (agent_id, client_id)
       - Index: idx_client_blocks_agent
       - Purpose: Tracks blocked OAuth clients per agent
    
    3. Create docs/v1/database/tables/sessions.md:
       - Columns: id, entity_type, entity_id, expires_at, created_at
       - Check constraint: entity_type IN ('agent', 'overseer')
       - Indexes: idx_sessions_entity, idx_sessions_expires
       - Purpose: Session tokens for authenticated entities
    
    4. Create docs/v1/database/tables/challenges.md:
       - Columns: id, challenge_type, entity_id, expires_at, challenge_data, created_at
       - Check constraint: challenge_type IN ('dpop', 'claim', 'key_rotation', 'shadow_claim')
       - Indexes: idx_challenges_entity, idx_challenges_expires
       - Purpose: Challenge data for cryptographic operations
    
    5. Create docs/v1/database/tables/subscription_tiers.md:
       - From migration 0005_create_subscription_tiers.sql
       - Columns: tier, max_agents, max_clients, max_oauth_per_period, price, is_hidden, created_at
       - Primary key: tier
       - Purpose: Subscription tier configurations
    
    Document each with full column specifications, constraints, and usage context.
  </action>
  <verify>
    - oauth_requests.md documents OAuth request records
    - client_blocks.md documents client blocking with foreign keys
    - sessions.md documents entity_type check constraint
    - challenges.md documents challenge_type check constraint
    - subscription_tiers.md derived from migration 0005
    - All tables have complete column specifications
    - All constraints and indexes documented
  </verify>
  <done></done>
</task>

<task type="auto">
  <name>Document Token Tables and Create Schema Overview</name>
  <files>
    <file>docs/v1/database/tables/authorization_codes.md</file>
    <file>docs/v1/database/tables/access_tokens.md</file>
    <file>docs/v1/database/tables/revoked_tokens.md</file>
    <file>docs/v1/database/schema.md</file>
    <file>docs/v1/database/relationships.md</file>
    <file>backend/migrations/0001_initial.sql</file>
    <file>backend/src/db/schema/*.ts</file>
  </files>
  <action>
    Create documentation for token-related tables and comprehensive schema overview:
    
    1. Create docs/v1/database/tables/authorization_codes.md:
       - Columns: id, agent_id, client_id, code_challenge, code_challenge_method, scopes, nonce, expires_at, used, created_at
       - Foreign key: agent_id -> agents.id (CASCADE DELETE)
       - Indexes: idx_auth_codes_agent, idx_auth_codes_expires
       - Purpose: OAuth authorization codes (PKCE)
    
    2. Create docs/v1/database/tables/access_tokens.md:
       - Columns: id, agent_id, client_id, scopes, access_token_hash, refresh_token_hash, expires_at, created_at, revoked
       - Foreign key: agent_id -> agents.id (CASCADE DELETE)
       - Indexes: idx_access_tokens_agent, idx_access_tokens_expires
       - Purpose: OAuth access and refresh tokens
    
    3. Create docs/v1/database/tables/revoked_tokens.md:
       - Columns: id, jti, token_type, expires_at, created_at
       - Check constraint: token_type IN ('access', 'refresh')
       - Unique: jti
       - Indexes: idx_revoked_tokens_jti, idx_revoked_tokens_expires
       - Purpose: Token revocation list
    
    4. Create docs/v1/database/schema.md:
       - Overview of all 10+ tables
       - Summary table with table names and purposes
       - Database technology (SQLite on D1)
       - Migration strategy notes
       - Key design decisions (why no FK on overseer_id in oversights, etc.)
    
    5. Create docs/v1/database/relationships.md:
       - Mermaid ER diagram showing all tables and relationships
       - Relationship descriptions (1:N, N:M, etc.)
       - Cascade delete behaviors
       - Indexes summary table
    
    Reference all migration files and backend/src/db/schema/ TypeScript files for complete picture.
  </action>
  <verify>
    - authorization_codes.md documents PKCE fields
    - access_tokens.md documents token hashes and revocation status
    - revoked_tokens.md documents jti uniqueness constraint
    - schema.md provides overview of all 10+ tables
    - relationships.md contains Mermaid ER diagram
    - All cascade behaviors documented
    - Indexes summary included
  </verify>
  <done></done>
</task>

---

## Verification
- All tasks completed with verify criteria met
- All 10+ database tables documented
- Schema overview with ER diagram created
- All columns, constraints, and indexes documented

## Success Criteria
- docs/v1/database/tables/ directory contains documentation for all tables
- schema.md provides complete schema overview
- relationships.md contains ER diagram
- All documentation derived from actual migration files
- Column types, constraints, defaults, and indexes fully documented

## Output
- docs/v1/database/tables/*.md (10+ table documentation files)
- docs/v1/database/schema.md
- docs/v1/database/relationships.md
