-- ============================================================
-- CHURN ANALYSIS — 7 Business Questions
-- ============================================================

-- Q1: Overall churn rate
SELECT
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) AS churned_customers,
    COUNT(DISTINCT l.customer_id)                                                 AS total_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.customer_id), 0), 2
    ) AS churn_rate_pct
FROM loans l;


-- Q2: Churn rate by region — where are we losing customers fastest?
SELECT
    c.country,
    c.region,
    COUNT(DISTINCT c.customer_id)                                                 AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) AS churned,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2
    ) AS churn_rate_pct
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.country, c.region
ORDER BY churn_rate_pct DESC;


-- Q3: Relationship between average payment delay and churn
-- (Customers grouped by delay buckets to see the trend)
WITH customer_delay AS (
    SELECT
        p.customer_id,
        AVG(p.days_late)                                                AS avg_delay,
        MAX(CASE WHEN l.loan_status = 'Defaulted' THEN 1 ELSE 0 END)   AS is_churned
    FROM payments p
    JOIN loans l ON p.loan_id = l.loan_id
    GROUP BY p.customer_id
)
SELECT
    CASE
        WHEN avg_delay = 0               THEN '0 — On Time'
        WHEN avg_delay BETWEEN 1 AND 7   THEN '1-7 days'
        WHEN avg_delay BETWEEN 8 AND 14  THEN '8-14 days'
        WHEN avg_delay BETWEEN 15 AND 30 THEN '15-30 days'
        ELSE '30+ days'
    END AS delay_bucket,
    COUNT(*)                              AS customers,
    SUM(is_churned)                       AS churned,
    ROUND(SUM(is_churned)*100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customer_delay
GROUP BY
    CASE
        WHEN avg_delay = 0               THEN '0 — On Time'
        WHEN avg_delay BETWEEN 1 AND 7   THEN '1-7 days'
        WHEN avg_delay BETWEEN 8 AND 14  THEN '8-14 days'
        WHEN avg_delay BETWEEN 15 AND 30 THEN '15-30 days'
        ELSE '30+ days'
    END
ORDER BY churn_rate_pct;


-- Q4: Churn by product — which products have the highest churn?
SELECT
    pr.product_name,
    pr.product_category,
    pr.product_price,
    COUNT(DISTINCT l.customer_id)                                                 AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) AS churned,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN l.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT l.customer_id), 0), 2
    ) AS churn_rate_pct
FROM loans l
JOIN products pr ON l.product_id = pr.product_id
GROUP BY pr.product_name, pr.product_category, pr.product_price
ORDER BY churn_rate_pct DESC;


-- Q5: Churn by acquisition channel — do certain channels produce stickier customers?
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id)                                                 AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) AS churned,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2
    ) AS churn_rate_pct
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.acquisition_channel
ORDER BY churn_rate_pct DESC;


-- Q6: Churn by income level — does income correlate with churn?
SELECT
    c.income_level,
    COUNT(DISTINCT c.customer_id)                                                 AS total_customers,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) AS churned,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN c.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2
    ) AS churn_rate_pct,
    ROUND(AVG(l.loan_amount), 2) AS avg_loan_amount
FROM customers c
JOIN loans l ON c.customer_id = l.customer_id
GROUP BY c.income_level
ORDER BY churn_rate_pct DESC;


-- Q7: Monthly churn trend — is churn getting worse?
WITH monthly_churn AS (
    SELECT
        DATE_TRUNC('month', p.payment_date) AS month,
        COUNT(DISTINCT p.customer_id) AS active_customers,
        COUNT(DISTINCT CASE WHEN p.default_flag = 1 THEN p.customer_id END) AS churned
    FROM payments p
    WHERE p.payment_date IS NOT NULL
    GROUP BY DATE_TRUNC('month', p.payment_date)
)
SELECT
    month,
    active_customers,
    churned,
    ROUND(churned * 100.0 / NULLIF(active_customers, 0), 2) AS churn_rate_pct,
    LAG(churned) OVER (ORDER BY month) AS prev_month_churned,
    churned - LAG(churned) OVER (ORDER BY month) AS churn_change
FROM monthly_churn
ORDER BY month;
