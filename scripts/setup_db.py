#!/usr/bin/env python3
"""
Database Setup Script
======================
Runs all migrations in order and seeds the database with demo data.
Use this to reset and re-initialize the development database from scratch.

Usage:
    python scripts/setup_db.py [--seed] [--reset] [--migrations-only]

Options:
    --seed            : Also run seed data files after migrations
    --reset           : DROP and recreate the database before running migrations
    --migrations-only : Only run migrations, skip seeding
    --verify          : Run normalization and integrity checks after setup

Example:
    python scripts/setup_db.py --seed --verify
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# pyrefly: ignore [missing-import]
import asyncpg


# ── Configuration ────────────────────────────────────────────────────────────
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/smartcommerce"
)

PROJECT_ROOT = Path(__file__).parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "database" / "migrations"
SEED_DIR       = PROJECT_ROOT / "database" / "seed"

MIGRATION_FILES = [
    "V1__initial_schema.sql",
    "V2__add_views_and_functions.sql",
    "V3__add_triggers.sql",
    "V4__seed_categories_and_brands.sql",
]

SEED_FILES = [
    "01_seed_reference_data.sql",
    "02_seed_products.sql",
    "03_seed_users_and_orders.sql",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(msg: str, icon: str = "✓") -> str:
    return f"  {icon} {msg}"


async def execute_sql_file(conn: asyncpg.Connection, filepath: Path) -> None:
    """Read and execute a .sql file, logging progress."""
    print(fmt(f"Running: {filepath.name}", "→"))
    sql = filepath.read_text(encoding="utf-8")

    # Skip \i include directives (not supported by asyncpg; use direct files)
    filtered_lines = [
        line for line in sql.splitlines()
        if not line.strip().startswith(r"\i")
    ]
    sql_clean = "\n".join(filtered_lines)

    try:
        await conn.execute(sql_clean)
        print(fmt(f"Done:    {filepath.name}", "✓"))
    except Exception as exc:
        print(fmt(f"ERROR in {filepath.name}: {exc}", "✗"))
        raise


async def run_migrations(conn: asyncpg.Connection) -> None:
    print("\n📦 Running Migrations...")
    for filename in MIGRATION_FILES:
        filepath = MIGRATIONS_DIR / filename
        if not filepath.exists():
            print(fmt(f"SKIP (file not found): {filename}", "⚠"))
            continue
        await execute_sql_file(conn, filepath)


async def run_seeds(conn: asyncpg.Connection) -> None:
    print("\n🌱 Seeding Data...")
    for filename in SEED_FILES:
        filepath = SEED_DIR / filename
        if not filepath.exists():
            print(fmt(f"SKIP (file not found): {filename}", "⚠"))
            continue
        await execute_sql_file(conn, filepath)


async def run_integrity_checks(conn: asyncpg.Connection) -> None:
    """Runs the normalization validation queries to verify DB health."""
    print("\n🔍 Running Integrity Checks...")

    checks = [
        ("Orphaned Products",       "SELECT COUNT(*) FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE c.id IS NULL"),
        ("Orphaned Inventory",      "SELECT COUNT(*) FROM inventory i LEFT JOIN product_variants pv ON i.variant_id = pv.id WHERE pv.id IS NULL"),
        ("Stock Integrity Errors",  "SELECT COUNT(*) FROM inventory WHERE reserved > on_hand"),
        ("Negative Stock",          "SELECT COUNT(*) FROM inventory WHERE on_hand < 0"),
        ("Total Products",          "SELECT COUNT(*) FROM products"),
        ("Total Orders",            "SELECT COUNT(*) FROM orders"),
    ]

    all_passed = True
    for name, sql in checks:
        count = await conn.fetchval(sql)
        is_error = "Orphaned" in name or "Error" in name or "Negative" in name
        if is_error and count > 0:
            print(fmt(f"FAIL  {name}: {count} violations", "✗"))
            all_passed = False
        else:
            icon = "✓" if not is_error else "✓"
            print(fmt(f"PASS  {name}: {count}", icon))

    if all_passed:
        print("\n  ✅ All integrity checks passed!")
    else:
        print("\n  ❌ Some checks failed — review seed data.")


async def reset_database(conn: asyncpg.Connection) -> None:
    """Drops all tables. USE WITH CAUTION — destroys all data."""
    print("\n⚠️  Resetting database (DROP SCHEMA public CASCADE)...")
    await conn.execute("""
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
        GRANT ALL ON SCHEMA public TO postgres;
        GRANT ALL ON SCHEMA public TO public;
    """)
    print(fmt("Schema reset complete.", "✓"))


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(args: argparse.Namespace) -> None:
    print(f"\n🚀 SmartCommerce AI — Database Setup")
    print(f"   Connecting to: {DB_URL.split('@')[-1]}")  # Hide credentials in log

    conn = await asyncpg.connect(DB_URL)
    try:
        if args.reset:
            await reset_database(conn)

        if not args.seed_only:
            await run_migrations(conn)

        if args.seed or args.seed_only:
            await run_seeds(conn)

        if args.verify:
            await run_integrity_checks(conn)

        print("\n✅ Database setup complete!\n")

    except Exception as exc:
        print(f"\n❌ Setup failed: {exc}")
        sys.exit(1)
    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartCommerce DB Setup")
    parser.add_argument("--seed",           action="store_true", help="Also run seed data")
    parser.add_argument("--seed-only",      action="store_true", help="Only run seeds")
    parser.add_argument("--reset",          action="store_true", help="Drop schema before running")
    parser.add_argument("--verify",         action="store_true", help="Run integrity checks after setup")
    parser.add_argument("--migrations-only",action="store_true", help="Only run migrations")
    args = parser.parse_args()

    asyncio.run(main(args))
