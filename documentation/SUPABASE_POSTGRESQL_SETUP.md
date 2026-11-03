# YumSure — Supabase Shared PostgreSQL & Backend Integration Guide

**Role & Audience**: Technical Guide for Backend Engineers (Tejas & Abhishek)  
**Architecture**: Flutter &rarr; FastAPI &rarr; SQLAlchemy 2.0 (Psycopg 3) &rarr; Shared PostgreSQL (Supabase)  
**Database Driver**: Psycopg 3 (`postgresql+psycopg://`)  
**Migration Tool**: Alembic (Tejas is the designated Migration Owner)

---

## 1. Overview & Architecture Principles

YumSure utilizes a shared Supabase PostgreSQL database for collaborative team development between Tejas and Abhishek. 

### Core Architectural Guarantees:
1. **Single Access Layer**: FastAPI and SQLAlchemy communicate with PostgreSQL using synchronous Psycopg 3. No Supabase client libraries (JavaScript/Python SDK) or Supabase Auth are introduced into the backend.
2. **Alembic Exclusivity**: All database schema changes are managed exclusively through versioned Alembic migrations. Direct table creation or GUI-driven schema edits in Supabase are strictly prohibited.
3. **Migration Ownership**: **Tejas is the sole migration executor**. Abhishek develops DTOs, engines, and migration scripts, but migrations against the shared Supabase database must be executed only by Tejas.
4. **Isolated Test Isolation**: Automated test suites are strictly prohibited from touching the shared Supabase development database. Integration tests require a dedicated local test database (`TEST_DATABASE_URL`).

---

## 2. Supabase Connection Modes: Direct vs. Pooler

Supabase provides two primary connection endpoints in your Project Settings (**Project Settings &rarr; Database &rarr; Connection string**):

| Connection Mode | Port | URL Hostname Pattern | Purpose in YumSure | Recommended URL Key |
|---|---|---|---|---|
| **Direct Connection** | `5432` | `db.<ref>.supabase.co:5432` | Transactional DDL, schema migrations, table creation, locks | `ALEMBIC_DATABASE_URL` (Required for Alembic migrations if using transaction pooler for app) |
| **Session Pooler** | `5432` | `aws-0-<region>.pooler.supabase.com:5432` | Long-lived persistent backend connections with full session support | `DATABASE_URL` (Alternative for FastAPI) |
| **Transaction Pooler** | `6543` | `aws-0-<region>.pooler.supabase.com:6543` | Ephemeral serverless connections, high-concurrency read/write | `DATABASE_URL` (FastAPI backend; does NOT support Alembic DDL) |

> [!WARNING]
> **Alembic Pooler Restriction**:
> Alembic executes transactional DDL, acquires table locks, and queries session parameters. If `DATABASE_URL` uses the **Transaction Pooler (port 6543)**, Alembic migrations **WILL FAIL** with `prepared statement does not exist` or lock timeout errors.
> **Rule**: Point `ALEMBIC_DATABASE_URL` to **Direct Connection (port 5432)** or **Session Pooler (port 5432)**.

---

## 3. Environment Configuration (`backend/.env`)

Copy `backend/.env.example` to `backend/.env`:

```powershell
Copy-Item backend/.env.example backend/.env
```

Configure the environment variables in `backend/.env`:

```ini
# ==============================================================================
# YumSure Backend Configuration — Environment Variables
# ==============================================================================
APP_NAME=YumSure
APP_ENV=development
API_V1_STR=/api/v1

# 1. FastAPI Application Database Connection (Supabase Session Pooler or Direct)
# Dialect: postgresql+psycopg://
# SSL: sslmode=require is automatically appended by config loader if missing
DATABASE_URL=postgresql+psycopg://postgres.<project_ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require

# 2. Alembic Migration Connection (Direct Connection on Port 5432)
# Required for transactional DDL; falls back to DATABASE_URL if not set
ALEMBIC_DATABASE_URL=postgresql+psycopg://postgres:<password>@db.<project_ref>.supabase.co:5432/postgres?sslmode=require

# 3. Dedicated Isolated Test Database (STRICTLY LOCAL — NEVER SUPABASE)
# Used by integration tests; must contain 'test' in database name
TEST_DATABASE_URL=postgresql+psycopg://postgres:your_local_password@localhost:5432/yumsure_test

# 4. Connection Pool Parameters (FastAPI Application)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
```

### Password Encoding Rules
If your database password contains special characters like `@`, `#`, `:`, `/`, or `%`, you **must URL-encode** them:
- `@` &rarr; `%40`
- `#` &rarr; `%23`
- `!` &rarr; `%21`
- `$` &rarr; `%24`

*(Example: `MyPass@123` becomes `MyPass%40123`)*

---

## 4. Safe Connection Verification

Before running FastAPI or Alembic, verify connectivity using the built-in diagnostic tool:

```powershell
.\backend\venv\Scripts\python.exe backend/app/db/verify_connection.py
```

### What this command does:
1. Tests physical connectivity using `SELECT 1;`.
2. Inspects remote PostgreSQL server version and connected database name.
3. Checks if `alembic_version` exists and reports the active schema revision.
4. **Never exposes credentials** in terminal output or logs.
5. **Zero data modification**: Executes 100% read-only queries.

---

## 5. Running the FastAPI Application

To launch the local development API server:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger UI Documentation: `http://127.0.0.1:8000/docs`
- OpenAPI JSON Schema: `http://127.0.0.1:8000/openapi.json`
- Healthcheck Endpoint: `http://127.0.0.1:8000/api/v1/health`

---

## 6. Inspecting Alembic Migrations

To view the active schema state on the shared database:

```powershell
cd backend

# Check current applied revision in the database
.\venv\Scripts\python.exe -m alembic -c alembic.ini current

# Inspect migration history chain
.\venv\Scripts\python.exe -m alembic -c alembic.ini history

# Check target repository head
.\venv\Scripts\python.exe -m alembic -c alembic.ini heads

# Review offline generated SQL without modifying the database
.\venv\Scripts\python.exe -m alembic -c alembic.ini upgrade 0002_enhance_rules:0003_seed_verified_rule_data --sql
```

---

## 7. Migration Ownership & Team Workflow Rules

### Role Separation:
- **Abhishek**:
  - Researches regulatory thresholds and standards.
  - Implements deterministic engines in `backend/app/domain/engines/`.
  - Authors seed data in `backend/app/data/seeds/`.
  - Prepares migration scripts in `backend/alembic/versions/`.
  - Tests models and engines using unit tests and mock simulators.
- **Tejas (Owner)**:
  - Audits migration scripts and generated SQL.
  - Reviews ownership tracking and foreign key rollback safety.
  - Executes `alembic upgrade head` against Supabase.
  - Maintains repository interfaces and FastAPI endpoint integration.

### Team Safety Rules:
1. **Never Run `alembic upgrade` Automatically**: Schema changes to the shared development database must be communicated and reviewed before execution.
2. **Never Execute Migrations in CI/CD without Approval**: Migrations must run on designated maintenance windows.
3. **Never Touch `migration_seed_ownership` Manually**: The tracking table is managed automatically by Alembic migration scripts.

---

## 8. Test Database Isolation

All unit and integration tests are strictly isolated from the shared database:

```powershell
# Run full test suite with discovery
.\backend\venv\Scripts\python.exe -m unittest discover -s backend/tests -v
```

### Test Isolation Guardrails:
- **`TEST_DATABASE_URL` Mandate**: Integration tests in `test_product_repository.py` strictly require `TEST_DATABASE_URL`. If unset, tests skip cleanly.
- **Supabase Cloud Rejection**: If `TEST_DATABASE_URL` points to `supabase.co` or `supabase.com`, tests **refuse to execute** and raise `SkipTest`.
- **Database Name Filter**: Target database name must contain `'test'` (e.g. `yumsure_test`).
- **Transactional Rollback**: Every test executes within `connection.begin()` and issues `transaction.rollback()` in `tearDown()`. Exactly 0 records persist.

---

## 9. Secret Handling & Version Control Rules

1. **`.env` is Git-Ignored**: `.gitignore` strictly blocks all `.env` files. Verify using:
   ```powershell
   git check-ignore backend/.env
   ```
2. **Never Commit Secrets**: Check Git staging before committing:
   ```powershell
   git status --short
   git diff --staged
   ```
3. **Log Sanitization**: Always use `settings.get_masked_database_url()` when logging database endpoints.

