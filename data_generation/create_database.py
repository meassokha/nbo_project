"""
NBO PROJECT
Database Schema Creation

Creates the SQLite database structure for the synthetic
digital banking / Next Best Offer project.

No real bank data is used.

Database:
    ../database/nbo_demo.db
"""

from pathlib import Path
import sqlite3


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "nbo_demo.db"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONNECT
# ============================================================

print("=" * 70)
print("NBO DATABASE CREATION")
print("=" * 70)

print(f"\nDatabase path:")
print(DATABASE_PATH)

conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

# Enable foreign-key enforcement
cursor.execute("PRAGMA foreign_keys = ON;")


# ============================================================
# DROP EXISTING TABLES
# ============================================================

print("\nRemoving old tables...")

tables = [
    "offer_event",
    "offer",
    "app_event",
    "income_profile",
    "income_evidence",
    "customer_product",
    "deposit",
    "loan",
    "cbc",
    "balance_snapshot",
    "bank_transaction",
    "account",
    "product",
    "customer"
]

for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")


# ============================================================
# 1. CUSTOMER
# ============================================================

cursor.execute("""
CREATE TABLE customer (

    customer_id INTEGER PRIMARY KEY,

    gender TEXT NOT NULL,

    age INTEGER NOT NULL,

    province TEXT NOT NULL,

    segment TEXT NOT NULL,

    kyc_level INTEGER NOT NULL,

    customer_since TEXT NOT NULL,

    archetype TEXT NOT NULL,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")


# ============================================================
# 2. ACCOUNT
# ============================================================

cursor.execute("""
CREATE TABLE account (

    account_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    account_type TEXT NOT NULL,

    open_date TEXT NOT NULL,

    status TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);
""")


# ============================================================
# 3. BANK TRANSACTION
# ============================================================

cursor.execute("""
CREATE TABLE bank_transaction (

    transaction_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    account_id INTEGER NOT NULL,

    transaction_date TEXT NOT NULL,

    transaction_type TEXT NOT NULL,

    amount REAL NOT NULL,

    channel TEXT NOT NULL,

    merchant_category TEXT,

    description TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (account_id)
        REFERENCES account(account_id)
);
""")


# ============================================================
# 4. PRODUCT
# ============================================================

cursor.execute("""
CREATE TABLE product (

    product_id INTEGER PRIMARY KEY,

    product_name TEXT NOT NULL,

    product_type TEXT NOT NULL,

    category TEXT,

    active INTEGER DEFAULT 1
);
""")


# ============================================================
# 5. CUSTOMER PRODUCT
# ============================================================

cursor.execute("""
CREATE TABLE customer_product (

    customer_product_id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id INTEGER NOT NULL,

    product_id INTEGER NOT NULL,

    start_date TEXT NOT NULL,

    status TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);
""")


# ============================================================
# 6. LOAN
# ============================================================

cursor.execute("""
CREATE TABLE loan (

    loan_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    loan_type TEXT NOT NULL,

    principal REAL NOT NULL,

    outstanding REAL NOT NULL,

    interest_rate REAL NOT NULL,

    monthly_payment REAL,

    start_date TEXT NOT NULL,

    end_date TEXT,

    status TEXT NOT NULL,

    repayment_status TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);
""")


# ============================================================
# 7. DEPOSIT
# ============================================================

cursor.execute("""
CREATE TABLE deposit (

    deposit_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    principal REAL NOT NULL,

    interest_rate REAL NOT NULL,

    start_date TEXT NOT NULL,

    maturity_date TEXT NOT NULL,

    status TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);
""")


# ============================================================
# 8. CBC
# ============================================================

cursor.execute("""
CREATE TABLE cbc (

    cbc_report_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    report_date TEXT NOT NULL,

    cbc_status TEXT NOT NULL,

    external_debt_monthly REAL NOT NULL,

    cbc_score INTEGER,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);
""")


# ============================================================
# 9. BALANCE SNAPSHOT
# ============================================================

cursor.execute("""
CREATE TABLE balance_snapshot (

    balance_snapshot_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    account_id INTEGER NOT NULL,

    snapshot_date TEXT NOT NULL,

    balance REAL NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (account_id)
        REFERENCES account(account_id)
);
""")


# ============================================================
# 10. INCOME EVIDENCE
# ============================================================

cursor.execute("""
CREATE TABLE income_evidence (

    income_evidence_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    evidence_date TEXT NOT NULL,

    evidence_type TEXT NOT NULL,

    amount REAL NOT NULL,

    source_transaction_id INTEGER,

    description TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (source_transaction_id)
        REFERENCES bank_transaction(transaction_id)
);
""")


# ============================================================
# 11. INCOME PROFILE
# ============================================================

cursor.execute("""
CREATE TABLE income_profile (

    customer_id INTEGER PRIMARY KEY,

    assessment_date TEXT NOT NULL,

    estimated_monthly_income REAL,

    payroll_income REAL,

    declared_income REAL,

    recurring_transfer_income REAL,

    business_inflow REAL,

    other_income REAL,

    income_source TEXT NOT NULL,

    income_confidence TEXT NOT NULL,

    income_observed_months INTEGER NOT NULL,

    income_regularity REAL,

    last_income_date TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
);
""")


# ============================================================
# 12. APP EVENTS
# ============================================================

cursor.execute("""
CREATE TABLE app_event (

    event_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    event_time TEXT NOT NULL,

    event_type TEXT NOT NULL,

    product_id INTEGER,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);
""")


# ============================================================
# 13. OFFER
# ============================================================

cursor.execute("""
CREATE TABLE offer (

    offer_id INTEGER PRIMARY KEY,

    product_id INTEGER NOT NULL,

    offer_name TEXT NOT NULL,

    offer_type TEXT,

    priority REAL NOT NULL,

    start_date TEXT NOT NULL,

    end_date TEXT,

    status TEXT NOT NULL,

    max_impressions_7d INTEGER,

    max_impressions_30d INTEGER,

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
);
""")


# ============================================================
# 14. OFFER EVENTS
# ============================================================

cursor.execute("""
CREATE TABLE offer_event (

    event_id INTEGER PRIMARY KEY,

    customer_id INTEGER NOT NULL,

    offer_id INTEGER NOT NULL,

    event_time TEXT NOT NULL,

    event_type TEXT NOT NULL,

    channel TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id),

    FOREIGN KEY (offer_id)
        REFERENCES offer(offer_id)
);
""")


# ============================================================
# INDEXES
# ============================================================

print("\nCreating indexes...")


indexes = [

    """
    CREATE INDEX idx_account_customer
    ON account(customer_id)
    """,

    """
    CREATE INDEX idx_transaction_customer_date
    ON bank_transaction(customer_id, transaction_date)
    """,

    """
    CREATE INDEX idx_transaction_type
    ON bank_transaction(transaction_type)
    """,

    """
    CREATE INDEX idx_customer_product_customer
    ON customer_product(customer_id)
    """,

    """
    CREATE INDEX idx_loan_customer
    ON loan(customer_id)
    """,

    """
    CREATE INDEX idx_deposit_customer
    ON deposit(customer_id)
    """,

    """
    CREATE INDEX idx_cbc_customer_date
    ON cbc(customer_id, report_date)
    """,

    """
    CREATE INDEX idx_balance_customer_date
    ON balance_snapshot(customer_id, snapshot_date)
    """,

    """
    CREATE INDEX idx_income_evidence_customer_date
    ON income_evidence(customer_id, evidence_date)
    """,

    """
    CREATE INDEX idx_app_event_customer_date
    ON app_event(customer_id, event_time)
    """,

    """
    CREATE INDEX idx_offer_event_customer_date
    ON offer_event(customer_id, event_time)
    """
]


for index_sql in indexes:
    cursor.execute(index_sql)


# ============================================================
# COMMIT
# ============================================================

conn.commit()


# ============================================================
# SHOW TABLES
# ============================================================

print("\nTables created:")

result = cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
""").fetchall()

for row in result:
    print(f"  - {row[0]}")


conn.close()


print("\n" + "=" * 70)
print("DATABASE CREATED SUCCESSFULLY")
print("=" * 70)

print(f"\nDatabase:")
print(DATABASE_PATH)