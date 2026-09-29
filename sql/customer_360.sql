/*
============================================================
NBO PROJECT
Customer 360 Feature View
============================================================

Purpose:
    Transform raw banking tables into one customer-level
    analytical view for the NBO engine.

One row = one customer.

All data is synthetic.
============================================================
*/


DROP VIEW IF EXISTS customer_360;


CREATE VIEW customer_360 AS

WITH

/* ==========================================================
   CUSTOMER BASE
   ========================================================== */

customer_base AS (

    SELECT

        c.customer_id,
        c.gender,
        c.age,
        c.province,
        c.segment,
        c.kyc_level,
        c.customer_since,
        c.archetype,

        CAST(
            (
                julianday('now')
                - julianday(c.customer_since)
            ) / 30.44
            AS INTEGER
        ) AS customer_tenure_months

    FROM customer c
),


/* ==========================================================
   INCOME
   ========================================================== */

income AS (

    SELECT

        customer_id,

        estimated_monthly_income,

        payroll_income,

        declared_income,

        recurring_transfer_income,

        business_inflow,

        other_income,

        income_source,

        income_confidence,

        income_observed_months,

        income_regularity

    FROM income_profile
),


/* ==========================================================
   BALANCE
   ========================================================== */

balance AS (

    SELECT

        customer_id,

        AVG(
            CASE
                WHEN snapshot_date >= date('now', '-30 day')
                THEN balance
            END
        ) AS avg_balance_30d,

        AVG(
            CASE
                WHEN snapshot_date >= date('now', '-90 day')
                THEN balance
            END
        ) AS avg_balance_90d,

        AVG(
            CASE
                WHEN snapshot_date >= date('now', '-180 day')
                THEN balance
            END
        ) AS avg_balance_180d,

        MAX(
            CASE
                WHEN snapshot_date = (
                    SELECT MAX(snapshot_date)
                    FROM balance_snapshot b2
                    WHERE b2.customer_id =
                          balance_snapshot.customer_id
                )
                THEN balance
            END
        ) AS latest_balance

    FROM balance_snapshot

    GROUP BY customer_id
),


/* ==========================================================
   TRANSACTION FEATURES - 30 DAYS
   ========================================================== */

transaction_30d AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'KHQR_PAYMENT'
                THEN 1
                ELSE 0
            END
        ) AS khqr_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'KHQR_PAYMENT'
                THEN amount
                ELSE 0
            END
        ) AS khqr_amount_30d,

        SUM(
            CASE
                WHEN transaction_type = 'BILL_PAYMENT'
                THEN 1
                ELSE 0
            END
        ) AS bill_payment_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'REMITTANCE_IN'
                THEN 1
                ELSE 0
            END
        ) AS remittance_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'CASH_WITHDRAWAL'
                THEN 1
                ELSE 0
            END
        ) AS cash_withdrawal_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'TRANSFER_IN'
                THEN 1
                ELSE 0
            END
        ) AS transfer_in_count_30d,

        SUM(
            CASE
                WHEN transaction_type = 'TRANSFER_OUT'
                THEN 1
                ELSE 0
            END
        ) AS transfer_out_count_30d

    FROM bank_transaction

    WHERE transaction_date >= date(
        'now',
        '-30 day'
    )

    GROUP BY customer_id
),


/* ==========================================================
   TRANSACTION FEATURES - 90 DAYS
   ========================================================== */

transaction_90d AS (

    SELECT

        customer_id,

        COUNT(*) AS transaction_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'KHQR_PAYMENT'
                THEN 1
                ELSE 0
            END
        ) AS khqr_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'BILL_PAYMENT'
                THEN 1
                ELSE 0
            END
        ) AS bill_payment_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'REMITTANCE_IN'
                THEN 1
                ELSE 0
            END
        ) AS remittance_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'CASH_WITHDRAWAL'
                THEN 1
                ELSE 0
            END
        ) AS cash_withdrawal_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'TRANSFER_IN'
                THEN 1
                ELSE 0
            END
        ) AS transfer_in_count_90d,

        SUM(
            CASE
                WHEN transaction_type = 'TRANSFER_OUT'
                THEN 1
                ELSE 0
            END
        ) AS transfer_out_count_90d

    FROM bank_transaction

    WHERE transaction_date >= date(
        'now',
        '-90 day'
    )

    GROUP BY customer_id
),


/* ==========================================================
   LOAN
   ========================================================== */

loan_features AS (

    SELECT

        customer_id,

        1 AS has_loan,

        SUM(outstanding)
            AS loan_outstanding,

        SUM(monthly_payment)
            AS monthly_loan_payment,

        MAX(repayment_status)
            AS loan_repayment_status

    FROM loan

    WHERE status = 'ACTIVE'

    GROUP BY customer_id
),


/* ==========================================================
   DEPOSIT
   ========================================================== */

deposit_features AS (

    SELECT

        customer_id,

        1 AS has_fixed_deposit,

        SUM(principal)
            AS deposit_balance,

        MIN(
            julianday(maturity_date)
            - julianday('now')
        ) AS days_to_deposit_maturity

    FROM deposit

    WHERE status = 'ACTIVE'

    GROUP BY customer_id
),


/* ==========================================================
   PRODUCT HOLDINGS
   ========================================================== */

product_features AS (

    SELECT

        cp.customer_id,

        COUNT(
            DISTINCT cp.product_id
        ) AS product_count,

        MAX(
            CASE
                WHEN cp.product_id = 4
                THEN 1
                ELSE 0
            END
        ) AS has_credit_card,

        MAX(
            CASE
                WHEN cp.product_id = 5
                THEN 1
                ELSE 0
            END
        ) AS has_insurance,

        MAX(
            CASE
                WHEN cp.product_id = 6
                THEN 1
                ELSE 0
            END
        ) AS has_khqr,

        MAX(
            CASE
                WHEN cp.product_id = 7
                THEN 1
                ELSE 0
            END
        ) AS has_remittance,

        MAX(
            CASE
                WHEN cp.product_id = 2
                THEN 1
                ELSE 0
            END
        ) AS has_fixed_deposit

    FROM customer_product cp

    WHERE cp.status = 'ACTIVE'

    GROUP BY cp.customer_id
),


/* ==========================================================
   CBC
   ========================================================== */

cbc_latest AS (

    SELECT

        c.customer_id,

        c.cbc_status,

        c.cbc_score,

        c.external_debt_monthly

    FROM cbc c

    INNER JOIN (

        SELECT

            customer_id,

            MAX(report_date) AS max_report_date

        FROM cbc

        GROUP BY customer_id

    ) latest

        ON c.customer_id =
           latest.customer_id

        AND c.report_date =
            latest.max_report_date
),


/* ==========================================================
   APP ENGAGEMENT
   ========================================================== */

app_features AS (

    SELECT

        customer_id,

        COUNT(*) AS app_events_30d,

        SUM(
            CASE
                WHEN event_type = 'LOGIN'
                THEN 1
                ELSE 0
            END
        ) AS app_logins_30d,

        SUM(
            CASE
                WHEN event_type = 'PRODUCT_VIEW'
                THEN 1
                ELSE 0
            END
        ) AS product_views_30d

    FROM app_event

    WHERE event_time >= date(
        'now',
        '-30 day'
    )

    GROUP BY customer_id
)


/* ==========================================================
   FINAL CUSTOMER 360
   ========================================================== */

SELECT

    cb.customer_id,

    cb.gender,

    cb.age,

    cb.province,

    cb.segment,

    cb.kyc_level,

    cb.customer_since,

    cb.archetype,

    cb.customer_tenure_months,


    /* ------------------------
       Income
       ------------------------ */

    i.estimated_monthly_income,

    i.payroll_income,

    i.declared_income,

    i.recurring_transfer_income,

    i.business_inflow,

    i.other_income,

    i.income_source,

    i.income_confidence,

    i.income_observed_months,

    i.income_regularity,


    /* ------------------------
       Balance
       ------------------------ */

    COALESCE(
        b.avg_balance_30d,
        0
    ) AS avg_balance_30d,

    COALESCE(
        b.avg_balance_90d,
        0
    ) AS avg_balance_90d,

    COALESCE(
        b.avg_balance_180d,
        0
    ) AS avg_balance_180d,

    COALESCE(
        b.latest_balance,
        0
    ) AS latest_balance,


    /* ------------------------
       Transactions
       ------------------------ */

    COALESCE(
        t30.transaction_count_30d,
        0
    ) AS transaction_count_30d,

    COALESCE(
        t30.khqr_count_30d,
        0
    ) AS khqr_count_30d,

    COALESCE(
        t30.khqr_amount_30d,
        0
    ) AS khqr_amount_30d,

    COALESCE(
        t30.bill_payment_count_30d,
        0
    ) AS bill_payment_count_30d,

    COALESCE(
        t30.remittance_count_30d,
        0
    ) AS remittance_count_30d,

    COALESCE(
        t30.cash_withdrawal_count_30d,
        0
    ) AS cash_withdrawal_count_30d,

    COALESCE(
        t30.transfer_in_count_30d,
        0
    ) AS transfer_in_count_30d,

    COALESCE(
        t30.transfer_out_count_30d,
        0
    ) AS transfer_out_count_30d,


    COALESCE(
        t90.transaction_count_90d,
        0
    ) AS transaction_count_90d,

    COALESCE(
        t90.khqr_count_90d,
        0
    ) AS khqr_count_90d,

    COALESCE(
        t90.bill_payment_count_90d,
        0
    ) AS bill_payment_count_90d,

    COALESCE(
        t90.remittance_count_90d,
        0
    ) AS remittance_count_90d,


    /* ------------------------
       Loan
       ------------------------ */

    COALESCE(
        l.has_loan,
        0
    ) AS has_loan,

    COALESCE(
        l.loan_outstanding,
        0
    ) AS loan_outstanding,

    COALESCE(
        l.monthly_loan_payment,
        0
    ) AS monthly_loan_payment,

    COALESCE(
        l.loan_repayment_status,
        'NO_LOAN'
    ) AS loan_repayment_status,


    /* ------------------------
       Deposit
       ------------------------ */

    COALESCE(
        d.has_fixed_deposit,
        0
    ) AS has_fixed_deposit,

    COALESCE(
        d.deposit_balance,
        0
    ) AS deposit_balance,

    d.days_to_deposit_maturity,


    /* ------------------------
       Products
       ------------------------ */

    COALESCE(
        p.product_count,
        0
    ) AS product_count,

    COALESCE(
        p.has_credit_card,
        0
    ) AS has_credit_card,

    COALESCE(
        p.has_insurance,
        0
    ) AS has_insurance,

    COALESCE(
        p.has_khqr,
        0
    ) AS has_khqr,

    COALESCE(
        p.has_remittance,
        0
    ) AS has_remittance,


    /* ------------------------
       CBC
       ------------------------ */

    COALESCE(
        cbc.cbc_status,
        'NO_HISTORY'
    ) AS cbc_status,

    cbc.cbc_score,

    COALESCE(
        cbc.external_debt_monthly,
        0
    ) AS external_debt_monthly,


    /* ------------------------
       App
       ------------------------ */

    COALESCE(
        a.app_events_30d,
        0
    ) AS app_events_30d,

    COALESCE(
        a.app_logins_30d,
        0
    ) AS app_logins_30d,

    COALESCE(
        a.product_views_30d,
        0
    ) AS product_views_30d


FROM customer_base cb

LEFT JOIN income i
    ON cb.customer_id =
       i.customer_id

LEFT JOIN balance b
    ON cb.customer_id =
       b.customer_id

LEFT JOIN transaction_30d t30
    ON cb.customer_id =
       t30.customer_id

LEFT JOIN transaction_90d t90
    ON cb.customer_id =
       t90.customer_id

LEFT JOIN loan_features l
    ON cb.customer_id =
       l.customer_id

LEFT JOIN deposit_features d
    ON cb.customer_id =
       d.customer_id

LEFT JOIN product_features p
    ON cb.customer_id =
       p.customer_id

LEFT JOIN cbc_latest cbc
    ON cb.customer_id =
       cbc.customer_id

LEFT JOIN app_features a
    ON cb.customer_id =
       a.customer_id
;