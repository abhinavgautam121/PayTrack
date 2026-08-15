-- ============================================================
-- CREDIT RISK ANALYSIS — 8 Business Questions
-- ============================================================

-- Q1: Which regions have the highest default rate?
SELECT
    c.country,
    c.region,
    COUNT(DISTINCT l.customer_id)                                                AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) AS defaulted_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.customer_id), 0), 2
    ) AS default_rate_pct
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.country, c.region
ORDER BY default_rate_pct DESC;


-- Q2: Default rate by customer income level
SELECT
    c.income_level,
    COUNT(DISTINCT l.customer_id)                                                AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) AS defaulted,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.customer_id), 0), 2
    ) AS default_rate_pct
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.income_level
ORDER BY default_rate_pct DESC;


-- Q3: Default rate by product — which products carry the highest risk?
SELECT
    pr.product_name,
    pr.product_category,
    COUNT(DISTINCT l.loan_id)                                                 AS total_loans,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.loan_id END) AS defaulted_loans,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.loan_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.loan_id), 0), 2
    ) AS default_rate_pct
FROM loans l
JOIN products pr ON l.product_id = pr.product_id
GROUP BY pr.product_name, pr.product_category
ORDER BY default_rate_pct DESC;


-- Q4: Customers with payment delays greater than 30 days — high risk indicator
SELECT
    c.customer_id,
    c.country,
    c.region,
    c.income_level,
    l.loan_status,
    COUNT(p.payment_id)                   AS late_payments_over_30d,
    ROUND(AVG(p.days_late), 1)            AS avg_days_late,
    ROUND(SUM(p.amount_due - p.amount_paid), 2) AS total_shortfall
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
JOIN loans l    ON p.loan_id = l.loan_id
WHERE p.days_late > 30
GROUP BY c.customer_id, c.country, c.region, c.income_level, l.loan_status
HAVING COUNT(p.payment_id) >= 3
ORDER BY late_payments_over_30d DESC
LIMIT 50;


-- Q5: Average collection rate by loan status
-- (Shows how collection rate differs between active, completed, and defaulted loans)
SELECT
    l.loan_status,
    COUNT(DISTINCT l.loan_id)                            AS total_loans,
    ROUND(AVG(
        CASE WHEN p.amount_due > 0
             THEN p.amount_paid * 100.0 / p.amount_due
             ELSE 0 END
    ), 2)                                                AS avg_collection_rate_pct,
    ROUND(AVG(p.days_late), 1)                           AS avg_days_late,
    ROUND(SUM(p.amount_due), 2)                          AS total_amount_due,
    ROUND(SUM(p.amount_paid), 2)                         AS total_amount_collected
FROM loans l
JOIN payments p ON l.loan_id = p.loan_id
GROUP BY l.loan_status
ORDER BY avg_collection_rate_pct;


-- Q6: Default rate by customer segment
SELECT
    c.customer_segment,
    COUNT(DISTINCT l.customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) AS defaulted,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.customer_id), 0), 2
    ) AS default_rate_pct,
    ROUND(AVG(l.loan_amount), 2) AS avg_loan_amount
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.customer_segment
ORDER BY default_rate_pct DESC;


-- Q7: Customers with the highest outstanding balances (top 30)
-- These represent the largest potential losses
SELECT
    c.customer_id,
    c.country,
    c.region,
    c.income_level,
    c.customer_segment,
    l.loan_amount,
    l.remaining_balance,
    l.loan_status,
    ROUND(l.remaining_balance * 100.0 / NULLIF(l.loan_amount, 0), 2) AS pct_outstanding
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
WHERE l.remaining_balance > 0
ORDER BY l.remaining_balance DESC
LIMIT 30;


-- Q8: Monthly default trend — are defaults increasing or decreasing?
WITH monthly_defaults AS (
    SELECT
        DATE_TRUNC('month', p.payment_date) AS month,
        COUNT(DISTINCT CASE WHEN p.default_flag = 1 THEN p.customer_id END) AS new_defaults,
        COUNT(DISTINCT p.customer_id) AS active_customers
    FROM payments p
    WHERE p.payment_date IS NOT NULL
    GROUP BY DATE_TRUNC('month', p.payment_date)
)
SELECT
    month,
    new_defaults,
    active_customers,
    ROUND(new_defaults * 100.0 / NULLIF(active_customers, 0), 2) AS default_rate_pct,
    SUM(new_defaults) OVER (ORDER BY month) AS cumulative_defaults
FROM monthly_defaults
ORDER BY month;
