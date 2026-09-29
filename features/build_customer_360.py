from pathlib import Path
import sqlite3


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "nbo_demo.db"
)

SQL_PATH = (
    PROJECT_ROOT
    / "sql"
    / "customer_360.sql"
)


# ------------------------------------------------------------
# Connect
# ------------------------------------------------------------

conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()


# ------------------------------------------------------------
# Read SQL
# ------------------------------------------------------------

with open(
    SQL_PATH,
    "r",
    encoding="utf-8"
) as file:

    sql = file.read()


# ------------------------------------------------------------
# Execute
# ------------------------------------------------------------

cursor.executescript(sql)

conn.commit()


# ------------------------------------------------------------
# Validate
# ------------------------------------------------------------

count = cursor.execute("""
SELECT COUNT(*)
FROM customer_360
""").fetchone()[0]


print("=" * 60)
print("CUSTOMER 360 CREATED")
print("=" * 60)

print(f"Customers in Customer 360: {count:,}")


# ------------------------------------------------------------
# Show sample
# ------------------------------------------------------------

rows = cursor.execute("""
SELECT
    customer_id,
    archetype,
    estimated_monthly_income,
    income_source,
    income_confidence,
    avg_balance_90d,
    khqr_count_30d,
    has_loan,
    cbc_status,
    cbc_score
FROM customer_360
LIMIT 10
""").fetchall()


print("\nSample records:\n")

for row in rows:

    print(row)


conn.close()