"""
Database Connection Verification Script for YumSure.

Verifies PostgreSQL connectivity against the configured DATABASE_URL (Supabase or local):
- Executes 'SELECT 1;' (zero data modifications).
- Retrieves PostgreSQL server version, current database, user, and port.
- Inspects alembic_version table if present to report the active schema revision.
- Strictly masks passwords and sensitive connection parameters.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import engine


def verify_database_connection() -> int:
    """
    Executes read-only diagnostic checks against settings.DATABASE_URL.
    Returns 0 on successful verification, 1 on connection failure.
    """
    masked_app_url = settings.get_masked_database_url()
    masked_alembic_url = settings.get_masked_alembic_url()
    masked_test_url = settings.get_masked_test_url()

    print("=" * 70)
    print("  YumSure Database Connection Diagnostics")
    print("=" * 70)
    print(f"Environment         : {settings.APP_ENV}")
    print(f"Target Database URL : {masked_app_url}")
    print(f"Alembic Migration   : {masked_alembic_url}")
    print(f"Isolated Test DB    : {masked_test_url or '(Not configured - tests will be skipped)'}")
    print("-" * 70)

    try:
        print("[1/4] Establishing connection to PostgreSQL...")
        with engine.connect() as conn:
            # 1. Ping
            ping_result = conn.execute(text("SELECT 1;")).scalar()
            if ping_result != 1:
                print(f"[FAIL] Unexpected ping result: {ping_result}")
                return 1
            print("      Ping successful (SELECT 1; returned 1).")

            # 2. Server Metadata
            print("[2/4] Querying PostgreSQL server metadata...")
            version_str = conn.execute(text("SELECT version();")).scalar()
            meta = conn.execute(text("""
                SELECT 
                    current_database() AS db_name,
                    current_user AS db_user,
                    inet_server_addr() AS server_ip,
                    inet_server_port() AS server_port;
            """)).mappings().one()

            print(f"      Database Name  : {meta['db_name']}")
            print(f"      Connected User : {meta['db_user']}")
            print(f"      Remote Server  : {meta['server_ip']}:{meta['server_port']}")
            print(f"      Server Version : {version_str.split(',')[0] if version_str else 'Unknown'}")

            # 3. Alembic Revision
            print("[3/4] Checking active Alembic schema revision...")
            inspector = inspect(conn)
            tables = inspector.get_table_names()
            if "alembic_version" in tables:
                rev = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
                print(f"      Active Alembic Revision : {rev or '(No revision recorded)'}")
            else:
                print("      Alembic version table not found (unmigrated database).")

            # 4. Existing Application Tables
            app_tables = [t for t in tables if t != "alembic_version"]
            print(f"[4/4] Public schema inspection: {len(app_tables)} application table(s) discovered.")
            if app_tables:
                for t in sorted(app_tables):
                    print(f"       - {t}")

        print("-" * 70)
        print("[SUCCESS] Database connectivity verified successfully.")
        print("=" * 70)
        return 0

    except SQLAlchemyError as err:
        print("-" * 70)
        print(f"[ERROR] Database connection failed against {masked_app_url}.")
        print(f"Details : {str(err).strip()}")
        print("-" * 70)
        print("Troubleshooting Advice:")
        print(" 1. Check if database host/URL is reachable from this machine.")
        print(" 2. Confirm username and URL-encoded password in backend/.env are accurate.")
        print(" 3. For Supabase, ensure sslmode=require is permitted by your network.")
        print(" 4. If using Supabase Pooler, verify port 6543 (transaction) or 5432 (session).")
        print("=" * 70)
        return 1
    except Exception as exc:
        print(f"[ERROR] Unexpected diagnostic failure: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(verify_database_connection())

