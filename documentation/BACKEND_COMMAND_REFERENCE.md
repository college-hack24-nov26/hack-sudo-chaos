# YumSure Backend Command Reference

A quick-reference guide for terminal commands used in backend development, database migrations, and operational debugging.

---

## 1. Python Environment Commands

| Command | Purpose | Example / Notes |
|---|---|---|
| `& "D:\conda_envs\dev\python.exe" -V` | Print active Python version | Verifies Python interpreter (Python 3.13) |
| `& "D:\conda_envs\dev\python.exe" -m venv <path>` | Create an isolated virtual environment | `python -m venv backend/venv` |
| `.\backend\venv\Scripts\Activate.ps1` | Activate virtual environment in PowerShell | Requires script execution policy |

---

## 2. Dependency Management Commands

| Command | Purpose | Example / Notes |
|---|---|---|
| `python -m pip install -r requirements.txt` | Install all pinned dependencies | Installs FastAPI, SQLAlchemy, Psycopg 3, Alembic |
| `python -m pip list` | List all installed packages and versions | Audits installed environment |
| `python -m pip show <package>` | Show details of a specific package | `python -m pip show sqlalchemy` |

---

## 3. PostgreSQL Server Commands (Windows)

| Command | Purpose | Example / Notes |
|---|---|---|
| `Get-Process -Name *postgres*` | Check if PostgreSQL server processes are active | Returns process list or empty if stopped |
| `net start postgresql-x64-18` | Start PostgreSQL 18 service (Admin cmd) | Starts background database daemon |
| `net stop postgresql-x64-18` | Stop PostgreSQL 18 service (Admin cmd) | Stops background database daemon |

---

## 4. Database Connection Commands (`psql`)

| Command | Purpose | Example / Notes |
|---|---|---|
| `psql -U postgres -h localhost -p 5432 -c "\l"` | List all databases | Tests server authentication |
| `psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE yumsure_db;"` | Create application database | Prepares target DB for YumSure |
| `psql -U postgres -d yumsure_db -c "\dt"` | List all tables in YumSure database | Inspects tables created by migrations |

---

## 5. Alembic Database Migration Commands

| Command | Purpose | Example / Notes |
|---|---|---|
| `alembic init alembic` | Initialize Alembic migration environment | Creates `alembic.ini` and `alembic/` folder |
| `alembic revision --autogenerate -m "description"` | Generate migration script by comparing models to DB | `alembic revision --autogenerate -m "Initial schema"` |
| `alembic upgrade head` | Apply all pending migrations to database | Updates database schema to latest version |
| `alembic current` | Display current applied migration revision | Verifies synchronization state |
| `alembic history` | Show migration history tree | Traces sequence of revisions |

---

## 6. FastAPI Runtime Commands

| Command | Purpose | Example / Notes |
|---|---|---|
| `uvicorn app.main:app --reload --port 8000` | Start local development server with auto-reload | Launches API at http://localhost:8000 |
| `python -c "import app.core.config; print('OK')"` | Verify application configuration syntax | Smoke-test settings loading |

---

## 7. Troubleshooting Commands

| Command | Purpose | Example / Notes |
|---|---|---|
| `Test-NetConnection -ComputerName 127.0.0.1 -Port 5432` | Test if PostgreSQL TCP port is open | Checks network listener without auth |
| `python -c "import psycopg; print(psycopg.__version__)"` | Verify Psycopg 3 C-extension/binary driver | Validates DB driver |

