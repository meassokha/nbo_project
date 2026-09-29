"""
NBO PROJECT
Synthetic Banking Data Generator

Generates realistic-looking synthetic digital banking data
for the Next Best Offer project.

NO REAL BANK DATA IS USED.

The generator creates:

- Customers
- Accounts
- Products
- Customer product holdings
- Transactions
- Loans
- Deposits
- CBC credit reports
- Balance snapshots
- Income evidence
- Income profiles
- App events
- Offers

Database:
    ../database/nbo_demo.db
"""

from pathlib import Path
from datetime import date, timedelta
import sqlite3
import random
import calendar

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

NUM_CUSTOMERS = 1000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "nbo_demo.db"

random.seed(SEED)
np.random.seed(SEED)


END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=365)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date, end_date):
    """Generate a random date between two dates."""

    if end_date <= start_date:
        return start_date

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


def weighted_choice(items, weights):
    return random.choices(
        items,
        weights=weights,
        k=1
    )[0]


def clamp(value, minimum, maximum):
    return max(
        minimum,
        min(value, maximum)
    )


def month_end(year, month):

    last_day = calendar.monthrange(
        year,
        month
    )[1]

    return date(
        year,
        month,
        last_day
    )


def months_between(start_date, end_date):

    months = []

    current_year = start_date.year
    current_month = start_date.month

    while (
        current_year < end_date.year
        or (
            current_year == end_date.year
            and current_month <= end_date.month
        )
    ):

        months.append(
            (
                current_year,
                current_month
            )
        )

        if current_month == 12:
            current_year += 1
            current_month = 1

        else:
            current_month += 1

    return months


# ============================================================
# CONNECT TO DATABASE
# ============================================================

print("=" * 70)
print("NBO SYNTHETIC DATA GENERATOR")
print("=" * 70)

print(f"\nDatabase:")
print(DATABASE_PATH)

if not DATABASE_PATH.exists():

    raise FileNotFoundError(
        "\nDatabase does not exist.\n"
        "Please run create_database.py first."
    )


conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

cursor.execute(
    "PRAGMA foreign_keys = ON;"
)


# ============================================================
# 1. PRODUCT MASTER
# ============================================================

products = [

    (
        1,
        "Savings Account",
        "SAVINGS",
        "DEPOSIT"
    ),

    (
        2,
        "Fixed Deposit",
        "FIXED_DEPOSIT",
        "DEPOSIT"
    ),

    (
        3,
        "Personal Loan",
        "PERSONAL_LOAN",
        "CREDIT"
    ),

    (
        4,
        "Credit Card",
        "CREDIT_CARD",
        "CREDIT"
    ),

    (
        5,
        "Family Insurance",
        "INSURANCE",
        "PROTECTION"
    ),

    (
        6,
        "KHQR",
        "KHQR",
        "PAYMENT"
    ),

    (
        7,
        "Remittance",
        "REMITTANCE",
        "TRANSFER"
    )
]


cursor.executemany("""
INSERT INTO product (
    product_id,
    product_name,
    product_type,
    category
)
VALUES (?, ?, ?, ?)
""", products)


# ============================================================
# 2. OFFER MASTER
# ============================================================

offers = [

    (
        1,
        2,
        "Fixed Deposit 12 Month",
        "DEPOSIT_PROMOTION",
        1.00,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        5,
        10
    ),

    (
        2,
        3,
        "Personal Loan",
        "CREDIT_OFFER",
        1.00,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        3,
        6
    ),

    (
        3,
        4,
        "Credit Card",
        "CARD_OFFER",
        0.90,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        3,
        6
    ),

    (
        4,
        5,
        "Family Insurance",
        "INSURANCE_OFFER",
        0.80,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        3,
        6
    ),

    (
        5,
        6,
        "KHQR Cashback",
        "PAYMENT_PROMOTION",
        1.00,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        5,
        10
    ),

    (
        6,
        7,
        "Remittance Promotion",
        "REMITTANCE_PROMOTION",
        0.70,
        START_DATE.isoformat(),
        None,
        "ACTIVE",
        3,
        6
    )
]


cursor.executemany("""
INSERT INTO offer (
    offer_id,
    product_id,
    offer_name,
    offer_type,
    priority,
    start_date,
    end_date,
    status,
    max_impressions_7d,
    max_impressions_30d
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", offers)


# ============================================================
# 3. CUSTOMER ARCHETYPES
# ============================================================

archetypes = [

    "SALARIED",

    "YOUNG_DIGITAL",

    "AFFLUENT_SAVER",

    "BORROWER",

    "MERCHANT",

    "SME",

    "REMITTANCE",

    "MASS"
]


archetype_weights = [

    25,
    15,
    10,
    15,
    10,
    8,
    7,
    10
]


provinces = [

    "Phnom Penh",
    "Siem Reap",
    "Battambang",
    "Kandal",
    "Kampong Cham",
    "Prey Veng",
    "Takeo",
    "Sihanoukville"
]


province_weights = [

    45,
    10,
    8,
    8,
    7,
    7,
    5,
    10
]


# ============================================================
# 4. GENERATE CUSTOMERS
# ============================================================

customers = []

customer_profiles = {}


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    archetype = weighted_choice(
        archetypes,
        archetype_weights
    )


    # ----------------------------
    # AGE
    # ----------------------------

    if archetype == "YOUNG_DIGITAL":

        age = random.randint(
            18,
            30
        )

    elif archetype == "AFFLUENT_SAVER":

        age = random.randint(
            30,
            60
        )

    elif archetype == "SME":

        age = random.randint(
            30,
            60
        )

    else:

        age = random.randint(
            20,
            65
        )


    gender = random.choice(
        ["M", "F"]
    )


    province = weighted_choice(
        provinces,
        province_weights
    )


    # ----------------------------
    # SEGMENT
    # ----------------------------

    if archetype == "SALARIED":

        segment = "SALARIED"

    elif archetype == "YOUNG_DIGITAL":

        segment = "MASS"

    elif archetype == "AFFLUENT_SAVER":

        segment = "AFFLUENT"

    elif archetype == "BORROWER":

        segment = "MASS"

    elif archetype == "MERCHANT":

        segment = "MERCHANT"

    elif archetype == "SME":

        segment = "SME"

    elif archetype == "REMITTANCE":

        segment = "MASS"

    else:

        segment = random.choice([
            "MASS",
            "SALARIED",
            "STUDENT"
        ])


    # ----------------------------
    # KYC
    # ----------------------------

    kyc_level = weighted_choice(
        [1, 2, 3],
        [5, 25, 70]
    )


    customer_since = random_date(
        date(2021, 1, 1),
        START_DATE
    )


    customers.append((

        customer_id,

        gender,

        age,

        province,

        segment,

        kyc_level,

        customer_since.isoformat(),

        archetype
    ))


    # Store hidden simulation characteristics
    customer_profiles[customer_id] = {

        "archetype": archetype,

        "age": age,

        "segment": segment,

        "base_income": None,

        "income_source": None,

        "salary": 0.0,

        "business_income": 0.0,

        "declared_income": 0.0,

        "income_confidence": "NONE"
    }


# ============================================================
# INSERT CUSTOMERS
# ============================================================

cursor.executemany("""
INSERT INTO customer (
    customer_id,
    gender,
    age,
    province,
    segment,
    kyc_level,
    customer_since,
    archetype
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", customers)


# ============================================================
# 5. ACCOUNTS
# ============================================================

accounts = []

account_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    open_date = random_date(
        date(2021, 1, 1),
        START_DATE
    )


    accounts.append((

        account_id,

        customer_id,

        "SAVINGS",

        open_date.isoformat(),

        "ACTIVE"
    ))


    account_id += 1


cursor.executemany("""
INSERT INTO account (
    account_id,
    customer_id,
    account_type,
    open_date,
    status
)
VALUES (?, ?, ?, ?, ?)
""", accounts)


# Map customer → account
customer_account = {

    row[1]: row[0]

    for row in accounts
}


# ============================================================
# 6. CUSTOMER PRODUCT HOLDINGS
# ============================================================

customer_products = []


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    # Everyone has savings
    owned_products = {1}


    # ----------------------------
    # Fixed Deposit
    # ----------------------------

    if archetype == "AFFLUENT_SAVER":

        if random.random() < 0.65:

            owned_products.add(2)


    # ----------------------------
    # Loan
    # ----------------------------

    if archetype == "BORROWER":

        if random.random() < 0.80:

            owned_products.add(3)


    # ----------------------------
    # KHQR
    # ----------------------------

    if archetype in [
        "MERCHANT",
        "SME"
    ]:

        if random.random() < 0.90:

            owned_products.add(6)


    elif archetype == "YOUNG_DIGITAL":

        if random.random() < 0.45:

            owned_products.add(6)


    # ----------------------------
    # Remittance
    # ----------------------------

    if archetype == "REMITTANCE":

        if random.random() < 0.80:

            owned_products.add(7)


    # ----------------------------
    # Insurance
    # ----------------------------

    if (
        profile["age"] > 30
        and random.random() < 0.20
    ):

        owned_products.add(5)


    # ----------------------------
    # Credit card
    # ----------------------------

    if (
        profile["age"] > 22
        and random.random() < 0.25
    ):

        owned_products.add(4)


    for product_id in owned_products:

        customer_products.append((

            customer_id,

            product_id,

            random_date(
                date(2022, 1, 1),
                END_DATE
            ).isoformat(),

            "ACTIVE"
        ))


cursor.executemany("""
INSERT INTO customer_product (
    customer_id,
    product_id,
    start_date,
    status
)
VALUES (?, ?, ?, ?)
""", customer_products)


# ============================================================
# 7. LOANS
# ============================================================

loans = []

loan_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    if archetype != "BORROWER":

        continue


    if random.random() >= 0.80:

        continue


    principal = round(
        random.uniform(
            1000,
            15000
        ),
        2
    )


    outstanding = round(
        principal
        * random.uniform(
            0.20,
            0.90
        ),
        2
    )


    interest_rate = round(
        random.uniform(
            8,
            18
        ),
        2
    )


    monthly_payment = round(
        outstanding
        * random.uniform(
            0.025,
            0.06
        ),
        2
    )


    start_date = random_date(
        date(2023, 1, 1),
        END_DATE - timedelta(
            days=90
        )
    )


    repayment_status = weighted_choice(

        [
            "CURRENT",
            "LATE",
            "DEFAULT"
        ],

        [
            80,
            15,
            5
        ]
    )


    loans.append((

        loan_id,

        customer_id,

        "PERSONAL_LOAN",

        principal,

        outstanding,

        interest_rate,

        monthly_payment,

        start_date.isoformat(),

        None,

        "ACTIVE",

        repayment_status
    ))


    loan_id += 1


cursor.executemany("""
INSERT INTO loan (
    loan_id,
    customer_id,
    loan_type,
    principal,
    outstanding,
    interest_rate,
    monthly_payment,
    start_date,
    end_date,
    status,
    repayment_status
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", loans)


# ============================================================
# 8. DEPOSITS
# ============================================================

deposits = []

deposit_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    if archetype != "AFFLUENT_SAVER":

        continue


    if random.random() >= 0.65:

        continue


    principal = round(
        random.uniform(
            2000,
            30000
        ),
        2
    )


    interest_rate = round(
        random.uniform(
            3,
            6
        ),
        2
    )


    start_date = random_date(
        date(2024, 1, 1),
        END_DATE - timedelta(
            days=30
        )
    )


    maturity_date = (
        start_date
        + timedelta(
            days=random.choice([
                90,
                180,
                365
            ])
        )
    )


    deposits.append((

        deposit_id,

        customer_id,

        principal,

        interest_rate,

        start_date.isoformat(),

        maturity_date.isoformat(),

        "ACTIVE"
    ))


    deposit_id += 1


cursor.executemany("""
INSERT INTO deposit (
    deposit_id,
    customer_id,
    principal,
    interest_rate,
    start_date,
    maturity_date,
    status
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", deposits)


# ============================================================
# 9. TRANSACTIONS
# ============================================================

transactions = []

transaction_id = 1


# Store salary transaction IDs for income evidence
salary_transactions = []

business_transactions = []


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    # --------------------------------------------------------
    # Determine income profile
    # --------------------------------------------------------

    if archetype == "SALARIED":

        salary = random.uniform(
            500,
            1800
        )

        profile["salary"] = salary

        profile["income_source"] = "PAYROLL"

        profile["income_confidence"] = "HIGH"


    elif archetype == "AFFLUENT_SAVER":

        salary = random.uniform(
            1500,
            5000
        )

        profile["salary"] = salary

        profile["income_source"] = "PAYROLL"

        profile["income_confidence"] = "HIGH"


    elif archetype == "YOUNG_DIGITAL":

        # Some young customers have payroll,
        # others do not.
        if random.random() < 0.35:

            salary = random.uniform(
                400,
                1000
            )

            profile["salary"] = salary

            profile["income_source"] = "PAYROLL"

            profile["income_confidence"] = "HIGH"

        else:

            profile["income_source"] = "UNKNOWN"

            profile["income_confidence"] = "NONE"


    elif archetype == "MERCHANT":

        business_income = random.uniform(
            1500,
            6000
        )

        profile["business_income"] = (
            business_income
        )

        profile["income_source"] = "BUSINESS_INFLOW"

        profile["income_confidence"] = "MEDIUM"


    elif archetype == "SME":

        business_income = random.uniform(
            3000,
            15000
        )

        profile["business_income"] = (
            business_income
        )

        profile["income_source"] = "BUSINESS_INFLOW"

        profile["income_confidence"] = "MEDIUM"


    elif archetype == "REMITTANCE":

        profile["income_source"] = "REMITTANCE"

        profile["income_confidence"] = "MEDIUM"


    elif archetype == "BORROWER":

        if random.random() < 0.60:

            salary = random.uniform(
                700,
                2500
            )

            profile["salary"] = salary

            profile["income_source"] = "PAYROLL"

            profile["income_confidence"] = "HIGH"

        else:

            declared_income = random.uniform(
                700,
                2500
            )

            profile["declared_income"] = (
                declared_income
            )

            profile["income_source"] = "DECLARED"

            profile["income_confidence"] = "LOW"


    else:

        # Some mass customers have declared income
        if random.random() < 0.30:

            declared_income = random.uniform(
                300,
                1200
            )

            profile["declared_income"] = (
                declared_income
            )

            profile["income_source"] = "DECLARED"

            profile["income_confidence"] = "LOW"

        else:

            profile["income_source"] = "UNKNOWN"

            profile["income_confidence"] = "NONE"


    # --------------------------------------------------------
    # Transaction volume
    # --------------------------------------------------------

    if archetype == "MERCHANT":

        number_transactions = random.randint(
            250,
            500
        )

    elif archetype == "SME":

        number_transactions = random.randint(
            200,
            450
        )

    elif archetype == "YOUNG_DIGITAL":

        number_transactions = random.randint(
            100,
            250
        )

    elif archetype == "REMITTANCE":

        number_transactions = random.randint(
            70,
            160
        )

    else:

        number_transactions = random.randint(
            40,
            150
        )


    # --------------------------------------------------------
    # Generate ordinary transactions
    # --------------------------------------------------------

    for _ in range(
        number_transactions
    ):

        txn_date = random_date(
            START_DATE,
            END_DATE
        )


        r = random.random()


        # -----------------------------------------
        # Salary
        # -----------------------------------------

        if (
            profile["salary"] > 0
            and r < 0.08
        ):

            amount = round(
                profile["salary"]
                * random.uniform(
                    0.95,
                    1.05
                ),
                2
            )

            txn_type = "SALARY"

            channel = "BANK_TRANSFER"

            merchant_category = "EMPLOYER"

            description = "Monthly salary"


        # -----------------------------------------
        # Business inflow
        # -----------------------------------------

        elif (
            profile["business_income"] > 0
            and r < 0.30
        ):

            amount = round(
                profile["business_income"]
                * random.uniform(
                    0.01,
                    0.08
                ),
                2
            )

            txn_type = "TRANSFER_IN"

            channel = "KHQR"

            merchant_category = "BUSINESS"

            description = "Business inflow"


        # -----------------------------------------
        # Remittance
        # -----------------------------------------

        elif (
            archetype == "REMITTANCE"
            and r < 0.25
        ):

            amount = round(
                random.uniform(
                    100,
                    1000
                ),
                2
            )

            txn_type = "REMITTANCE_IN"

            channel = "MOBILE_APP"

            merchant_category = "REMITTANCE"

            description = "Incoming remittance"


        # -----------------------------------------
        # KHQR
        # -----------------------------------------

        elif r < 0.50:

            amount = round(
                random.uniform(
                    2,
                    80
                ),
                2
            )

            txn_type = "KHQR_PAYMENT"

            channel = "KHQR"

            merchant_category = random.choice([

                "FOOD",
                "GROCERY",
                "SHOPPING",
                "FUEL",
                "RESTAURANT",
                "RETAIL"
            ])

            description = "KHQR payment"


        # -----------------------------------------
        # Bill payment
        # -----------------------------------------

        elif r < 0.60:

            amount = round(
                random.uniform(
                    5,
                    150
                ),
                2
            )

            txn_type = "BILL_PAYMENT"

            channel = "MOBILE_APP"

            merchant_category = random.choice([

                "ELECTRICITY",
                "WATER",
                "PHONE",
                "INTERNET",
                "SCHOOL"
            ])

            description = "Bill payment"


        # -----------------------------------------
        # Cash withdrawal
        # -----------------------------------------

        elif r < 0.72:

            amount = round(
                random.uniform(
                    20,
                    300
                ),
                2
            )

            txn_type = "CASH_WITHDRAWAL"

            channel = "ATM"

            merchant_category = "CASH"

            description = "ATM withdrawal"


        # -----------------------------------------
        # Cash deposit
        # -----------------------------------------

        elif r < 0.78:

            amount = round(
                random.uniform(
                    20,
                    500
                ),
                2
            )

            txn_type = "CASH_DEPOSIT"

            channel = "BRANCH"

            merchant_category = "CASH"

            description = "Cash deposit"


        # -----------------------------------------
        # Transfer out
        # -----------------------------------------

        else:

            amount = round(
                random.uniform(
                    20,
                    500
                ),
                2
            )

            txn_type = "TRANSFER_OUT"

            channel = random.choice([

                "MOBILE_APP",
                "BANK_TRANSFER"
            ])

            merchant_category = "TRANSFER"

            description = "Outgoing transfer"


        transactions.append((

            transaction_id,

            customer_id,

            customer_account[customer_id],

            txn_date.isoformat(),

            txn_type,

            amount,

            channel,

            merchant_category,

            description
        ))


        # Store salary transactions
        if txn_type == "SALARY":

            salary_transactions.append({

                "transaction_id":
                    transaction_id,

                "customer_id":
                    customer_id,

                "date":
                    txn_date,

                "amount":
                    amount
            })


        if (
            txn_type == "TRANSFER_IN"
            and merchant_category == "BUSINESS"
        ):

            business_transactions.append({

                "transaction_id":
                    transaction_id,

                "customer_id":
                    customer_id,

                "date":
                    txn_date,

                "amount":
                    amount
            })


        transaction_id += 1


# ============================================================
# INSERT TRANSACTIONS
# ============================================================

cursor.executemany("""
INSERT INTO bank_transaction (
    transaction_id,
    customer_id,
    account_id,
    transaction_date,
    transaction_type,
    amount,
    channel,
    merchant_category,
    description
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [

    (
        row[0],
        row[1],
        row[2],
        row[3],
        row[4],
        row[5],
        row[6],
        row[7],
        row[8]
    )

    for row in transactions
])


# ============================================================
# 10. CBC CREDIT HISTORY
# ============================================================

cbc_reports = []

cbc_report_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    # --------------------------------------------------------
    # Some customers have no CBC history
    # --------------------------------------------------------

    if random.random() < 0.15:

        cbc_status = "NO_HISTORY"

        cbc_score = None

        external_debt = 0.0


    else:

        # -----------------------------------------
        # Status distribution
        # -----------------------------------------

        if archetype == "BORROWER":

            cbc_status = weighted_choice(

                [
                    "CLEAN",
                    "LATE",
                    "DEFAULT"
                ],

                [
                    70,
                    22,
                    8
                ]
            )


        elif archetype == "AFFLUENT_SAVER":

            cbc_status = weighted_choice(

                [
                    "CLEAN",
                    "LATE",
                    "DEFAULT"
                ],

                [
                    88,
                    10,
                    2
                ]
            )


        elif archetype in [
            "SALARIED",
            "SME"
        ]:

            cbc_status = weighted_choice(

                [
                    "CLEAN",
                    "LATE",
                    "DEFAULT"
                ],

                [
                    78,
                    18,
                    4
                ]
            )


        else:

            cbc_status = weighted_choice(

                [
                    "CLEAN",
                    "LATE",
                    "DEFAULT"
                ],

                [
                    72,
                    22,
                    6
                ]
            )


        # -----------------------------------------
        # CBC score
        # -----------------------------------------

        if cbc_status == "CLEAN":

            cbc_score = random.randint(
                650,
                850
            )

            external_debt = round(
                random.uniform(
                    0,
                    350
                ),
                2
            )


        elif cbc_status == "LATE":

            cbc_score = random.randint(
                500,
                649
            )

            external_debt = round(
                random.uniform(
                    50,
                    500
                ),
                2
            )


        else:

            cbc_score = random.randint(
                300,
                499
            )

            external_debt = round(
                random.uniform(
                    100,
                    800
                ),
                2
            )


    # --------------------------------------------------------
    # CBC report date
    # --------------------------------------------------------

    report_date = END_DATE - timedelta(
        days=random.randint(
            0,
            30
        )
    )


    cbc_reports.append((

        cbc_report_id,

        customer_id,

        report_date.isoformat(),

        cbc_status,

        external_debt,

        cbc_score
    ))


    cbc_report_id += 1


cursor.executemany("""
INSERT INTO cbc (
    cbc_report_id,
    customer_id,
    report_date,
    cbc_status,
    external_debt_monthly,
    cbc_score
)
VALUES (?, ?, ?, ?, ?, ?)
""", cbc_reports)


# ============================================================
# 11. BALANCE SNAPSHOTS
# ============================================================

balance_snapshots = []

balance_snapshot_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    # Starting balance based on customer type

    if archetype == "AFFLUENT_SAVER":

        base_balance = random.uniform(
            5000,
            30000
        )

    elif archetype == "SME":

        base_balance = random.uniform(
            3000,
            15000
        )

    elif archetype == "MERCHANT":

        base_balance = random.uniform(
            1000,
            8000
        )

    elif archetype == "SALARIED":

        base_balance = random.uniform(
            300,
            2500
        )

    elif archetype == "BORROWER":

        base_balance = random.uniform(
            100,
            1500
        )

    else:

        base_balance = random.uniform(
            50,
            1000
        )


    account_id_for_customer = (
        customer_account[customer_id]
    )


    # Generate monthly snapshots
    # for approximately 12 months.

    for year, month in months_between(
        START_DATE,
        END_DATE
    ):

        snapshot_date = month_end(
            year,
            month
        )

        # Balance changes over time
        change = random.uniform(
            -0.15,
            0.20
        )

        base_balance *= (
            1 + change
        )

        base_balance = max(
            0,
            base_balance
        )


        balance_snapshots.append((

            balance_snapshot_id,

            customer_id,

            account_id_for_customer,

            snapshot_date.isoformat(),

            round(
                base_balance,
                2
            )
        ))


        balance_snapshot_id += 1


cursor.executemany("""
INSERT INTO balance_snapshot (
    balance_snapshot_id,
    customer_id,
    account_id,
    snapshot_date,
    balance
)
VALUES (?, ?, ?, ?, ?)
""", balance_snapshots)


# ============================================================
# 12. INCOME EVIDENCE
# ============================================================

income_evidence = []

income_evidence_id = 1


# ----------------------------
# Payroll evidence
# ----------------------------

for row in salary_transactions:

    income_evidence.append((

        income_evidence_id,

        row["customer_id"],

        row["date"].isoformat(),

        "PAYROLL",

        row["amount"],

        row["transaction_id"],

        "Observed salary transaction"
    ))

    income_evidence_id += 1


# ----------------------------
# Business inflow evidence
# ----------------------------

for row in business_transactions:

    income_evidence.append((

        income_evidence_id,

        row["customer_id"],

        row["date"].isoformat(),

        "BUSINESS_INFLOW",

        row["amount"],

        row["transaction_id"],

        "Observed business inflow"
    ))

    income_evidence_id += 1


# ----------------------------
# Declared income evidence
# ----------------------------

for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]


    if profile["declared_income"] <= 0:

        continue


    income_evidence.append((

        income_evidence_id,

        customer_id,

        END_DATE.isoformat(),

        "DECLARED",

        round(
            profile["declared_income"],
            2
        ),

        None,

        "Customer declared income"
    ))

    income_evidence_id += 1


cursor.executemany("""
INSERT INTO income_evidence (
    income_evidence_id,
    customer_id,
    evidence_date,
    evidence_type,
    amount,
    source_transaction_id,
    description
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", income_evidence)


# ============================================================
# 13. INCOME PROFILE
# ============================================================

income_profiles = []


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]


    salary = profile[
        "salary"
    ]

    declared = profile[
        "declared_income"
    ]

    business = profile[
        "business_income"
    ]

    source = profile[
        "income_source"
    ]

    confidence = profile[
        "income_confidence"
    ]


    # --------------------------------------------------------
    # Determine estimated income
    # --------------------------------------------------------

    if source == "PAYROLL":

        estimated_income = salary


    elif source == "BUSINESS_INFLOW":

        # We don't treat gross business inflow
        # as personal income.
        #
        # For the prototype we assume a portion
        # is potentially available personal income.

        estimated_income = business * 0.25


    elif source == "DECLARED":

        estimated_income = declared


    elif source == "REMITTANCE":

        # Remittance is not automatically classified
        # as salary/income.
        #
        # For now we leave estimated income unknown.

        estimated_income = None


    else:

        estimated_income = None


    # --------------------------------------------------------
    # Observed months
    # --------------------------------------------------------

    if source == "PAYROLL":

        observed_months = random.randint(
            3,
            12
        )

        regularity = round(
            random.uniform(
                0.80,
                1.00
            ),
            2
        )


    elif source == "BUSINESS_INFLOW":

        observed_months = random.randint(
            4,
            12
        )

        regularity = round(
            random.uniform(
                0.55,
                0.90
            ),
            2
        )


    elif source == "DECLARED":

        observed_months = 0

        regularity = None


    else:

        observed_months = 0

        regularity = None


    # --------------------------------------------------------
    # Last income date
    # --------------------------------------------------------

    if source == "PAYROLL":

        last_income_date = END_DATE.isoformat()

    else:

        last_income_date = None


    income_profiles.append((

        customer_id,

        END_DATE.isoformat(),

        (
            round(
                estimated_income,
                2
            )
            if estimated_income is not None
            else None
        ),

        (
            round(
                salary,
                2
            )
            if salary > 0
            else None
        ),

        (
            round(
                declared,
                2
            )
            if declared > 0
            else None
        ),

        None,

        (
            round(
                business,
                2
            )
            if business > 0
            else None
        ),

        None,

        source,

        confidence,

        observed_months,

        regularity,

        last_income_date
    ))


cursor.executemany("""
INSERT INTO income_profile (
    customer_id,
    assessment_date,
    estimated_monthly_income,
    payroll_income,
    declared_income,
    recurring_transfer_income,
    business_inflow,
    other_income,
    income_source,
    income_confidence,
    income_observed_months,
    income_regularity,
    last_income_date
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", income_profiles)


# ============================================================
# 14. APP EVENTS
# ============================================================

app_events = []

event_id = 1


for customer_id in range(
    1,
    NUM_CUSTOMERS + 1
):

    profile = customer_profiles[
        customer_id
    ]

    archetype = profile[
        "archetype"
    ]


    # Digital engagement

    if archetype == "YOUNG_DIGITAL":

        number_events = random.randint(
            40,
            100
        )

    elif archetype in [
        "MERCHANT",
        "SME"
    ]:

        number_events = random.randint(
            20,
            70
        )

    elif archetype == "AFFLUENT_SAVER":

        number_events = random.randint(
            15,
            50
        )

    else:

        number_events = random.randint(
            5,
            40
        )


    for _ in range(
        number_events
    ):

        event_date = random_date(
            START_DATE,
            END_DATE
        )


        event_type = random.choice([

            "LOGIN",

            "PRODUCT_VIEW",

            "TRANSFER",

            "KHQR_VIEW",

            "BILL_PAYMENT_VIEW",

            "LOAN_VIEW",

            "DEPOSIT_VIEW",

            "INSURANCE_VIEW"
        ])


        product_id = None


        if event_type == "LOAN_VIEW":

            product_id = 3

        elif event_type == "DEPOSIT_VIEW":

            product_id = 2

        elif event_type == "INSURANCE_VIEW":

            product_id = 5

        elif event_type == "KHQR_VIEW":

            product_id = 6


        app_events.append((

            event_id,

            customer_id,

            event_date.isoformat(),

            event_type,

            product_id
        ))


        event_id += 1


cursor.executemany("""
INSERT INTO app_event (
    event_id,
    customer_id,
    event_time,
    event_type,
    product_id
)
VALUES (?, ?, ?, ?, ?)
""", app_events)


# ============================================================
# 15. COMMIT
# ============================================================

conn.commit()


# ============================================================
# 16. DATABASE SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("SYNTHETIC DATA GENERATION COMPLETE")
print("=" * 70)


tables = [

    "customer",
    "account",
    "bank_transaction",
    "product",
    "customer_product",
    "loan",
    "deposit",
    "cbc",
    "balance_snapshot",
    "income_evidence",
    "income_profile",
    "app_event",
    "offer",
    "offer_event"
]


for table in tables:

    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]


    print(
        f"{table:25s}: {count:>10,} rows"
    )


# ============================================================
# 17. CUSTOMER ARCHETYPE SUMMARY
# ============================================================

print("\n")
print("Customer archetypes:")

archetype_summary = cursor.execute("""
SELECT
    archetype,
    COUNT(*) AS customers
FROM customer
GROUP BY archetype
ORDER BY customers DESC;
""").fetchall()


for row in archetype_summary:

    print(
        f"  {row[0]:20s} : {row[1]:>6,}"
    )


# ============================================================
# 18. CBC SUMMARY
# ============================================================

print("\n")
print("CBC status:")

cbc_summary = cursor.execute("""
SELECT
    cbc_status,
    COUNT(*) AS customers,
    ROUND(AVG(cbc_score), 0) AS avg_score,
    ROUND(AVG(external_debt_monthly), 2)
        AS avg_external_debt
FROM cbc
GROUP BY cbc_status
ORDER BY customers DESC;
""").fetchall()


for row in cbc_summary:

    print(
        f"  {row[0]:15s}"
        f" Customers={row[1]:>5,}"
        f" AvgScore={str(row[2]):>6}"
        f" AvgExtDebt=${row[3]:>8.2f}"
    )


# ============================================================
# 19. INCOME SUMMARY
# ============================================================

print("\n")
print("Income source:")

income_summary = cursor.execute("""
SELECT
    income_source,
    income_confidence,
    COUNT(*) AS customers,
    ROUND(
        AVG(estimated_monthly_income),
        2
    ) AS avg_estimated_income
FROM income_profile
GROUP BY
    income_source,
    income_confidence
ORDER BY customers DESC;
""").fetchall()


for row in income_summary:

    avg_income = (
        f"${row[3]:,.2f}"
        if row[3] is not None
        else "N/A"
    )


    print(
        f"  {row[0]:20s}"
        f" Confidence={row[1]:8s}"
        f" Customers={row[2]:>5,}"
        f" AvgIncome={avg_income}"
    )


conn.close()


print("\n")
print("=" * 70)
print("DATABASE READY")
print("=" * 70)

print(f"\nSQLite database:")
print(DATABASE_PATH)

print("\nYou can now open this database in DBeaver.")