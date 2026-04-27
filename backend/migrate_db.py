"""
Database migration script - creates all missing tables and seeds initial data.
Run once: python migrate_db.py
"""
import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'gaokao.db')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'backend', 'scripts')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute_sql_file(filename):
    """Execute a SQL file against the database."""
    filepath = os.path.join(SCRIPTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filename} not found at {filepath}")
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
        print(f"  [OK] {filename}")
        return True
    except Exception as e:
        print(f"  [FAIL] {filename}: {e}")
        return False
    finally:
        conn.close()


def table_exists(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def main():
    print("Database Migration Tool")
    print(f"  DB path: {DB_PATH}")
    print(f"  Scripts: {SCRIPTS_DIR}")

    missing = []

    # Check which tables are missing
    required_tables = [
        'yunnan_physics_scores',
        'yunnan_physics_score_segments',
        'yunnan_b_segment_plans',
    ]

    for table in required_tables:
        if table_exists(table):
            print(f"\n{table}: already exists")
        else:
            print(f"\n{table}: MISSING - creating...")
            missing.append(table)

    if not missing:
        print("\nAll tables present. Nothing to migrate.")
        return

    # Create missing tables
    print("\n--- Creating tables ---")
    for table in missing:
        if table == 'yunnan_physics_scores':
            execute_sql_file('create_yunnan_physics_scores.sql')
        elif table == 'yunnan_physics_score_segments':
            execute_sql_file('create_score_segments_table.sql')
        elif table == 'yunnan_b_segment_plans':
            execute_sql_file('create_b_segment_plans.sql')

    # Also ensure province_subjects and import_logs exist
    if not table_exists('province_subjects') or not table_exists('import_logs'):
        print("\n--- Creating auxiliary tables ---")
        execute_sql_file('create_admission_tables.sql')

    # Verify
    print("\n--- Verification ---")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    for row in cursor.fetchall():
        cursor2 = conn.cursor()
        cursor2.execute(f"SELECT COUNT(*) FROM \"{row['name']}\"")
        count = cursor2.fetchone()[0]
        print(f"  {row['name']}: {count} rows")
    conn.close()

    print("\nMigration complete.")


if __name__ == '__main__':
    main()
