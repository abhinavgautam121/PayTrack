-- ============================================================
-- DISTRIBUTION ANALYTICS — 7 Business Questions
-- ============================================================

-- Q1: Average delivery and installation time by distribution channel
-- Business question: Which channel is fastest from order to operational product?
SELECT
    distribution_channel,
    COUNT(*)                             AS total_orders,
    ROUND(AVG(delivery_days), 1)         AS avg_delivery_days,
    ROUND(AVG(installation_days), 1)     AS avg_installation_days,
    ROUND(AVG(delivery_days + installation_days), 1) AS avg_total_days,
    ROUND(AVG(acquisition_cost), 2)      AS avg_cac
FROM distribution
GROUP BY distribution_channel
ORDER BY avg_total_days;


-- Q2: Revenue and cost efficiency by distribution channel
-- Business question: Which channels offer the best ROI?
SELECT
    d.distribution_channel,
    COUNT(DISTINCT d.customer_id)                             AS total_customers,
    ROUND(SUM(d.acquisition_cost), 2)                         AS total_cac,
    ROUND(SUM(p.amount_paid), 2)                              AS total_revenue,
    ROUND(SUM(p.amount_paid) / NULLIF(SUM(d.acquisition_cost), 0), 2) AS revenue_to_cac_ratio,
    ROUND(SUM(p.amount_paid) / NULLIF(COUNT(DISTINCT d.customer_id), 0), 2) AS revenue_per_customer
FROM distribution d
JOIN payments p ON d.customer_id = p.customer_id
GROUP BY d.distribution_channel
ORDER BY revenue_to_cac_ratio DESC;


-- Q3: Top 20 sales agents by revenue performance
SELECT
    d.sales_agent_id,
    d.distribution_channel,
    COUNT(DISTINCT d.customer_id)           AS customers_served,
    ROUND(SUM(p.amount_paid), 2)            AS total_revenue,
    ROUND(SUM(p.amount_paid) / NULLIF(COUNT(DISTINCT d.customer_id), 0), 2) AS revenue_per_customer,
    ROUND(AVG(d.delivery_days), 1)          AS avg_delivery_days
FROM distribution d
JOIN payments p ON d.customer_id = p.customer_id
GROUP BY d.sales_agent_id, d.distribution_channel
HAVING COUNT(DISTINCT d.customer_id) >= 10   -- agents with at least 10 customers
ORDER BY total_revenue DESC
LIMIT 20;


-- Q4: Regional distribution performance
-- Business question: Which regions have the slowest delivery?
SELECT
    d.country,
    d.region,
    COUNT(*)                                 AS total_orders,
    ROUND(AVG(d.delivery_days), 1)           AS avg_delivery_days,
    ROUND(AVG(d.installation_days), 1)       AS avg_installation_days,
    ROUND(AVG(d.acquisition_cost), 2)        AS avg_cac,
    ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY d.delivery_days)::numeric, 1) AS p90_delivery_days
FROM distribution d
GROUP BY d.country, d.region
ORDER BY avg_delivery_days DESC;


-- Q5: Does delivery time affect customer repayment?
-- Business question: Do customers who wait longer for delivery pay worse?
WITH customer_delivery AS (
    SELECT
        d.customer_id,
        d.delivery_days,
        CASE
            WHEN d.delivery_days <= 3  THEN '0-3 days'
            WHEN d.delivery_days <= 7  THEN '4-7 days'
            WHEN d.delivery_days <= 14 THEN '8-14 days'
            ELSE '15+ days'
        END AS delivery_bucket
    FROM distribution d
)
SELECT
    cd.delivery_bucket,
    COUNT(DISTINCT cd.customer_id)                         AS total_customers,
    ROUND(AVG(p.amount_paid * 100.0 / NULLIF(p.amount_due, 0)), 2) AS avg_collection_rate,
    ROUND(AVG(p.days_late), 1)                              AS avg_payment_delay,
    COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN cd.customer_id END) AS defaulted_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN l.loan_status = 'Defaulted' THEN cd.customer_id END) * 100.0
        / NULLIF(COUNT(DISTINCT cd.customer_id), 0), 2
    ) AS default_rate_pct
FROM customer_delivery cd
JOIN payments p ON cd.customer_id = p.customer_id
JOIN loans l    ON p.loan_id = l.loan_id
GROUP BY cd.delivery_bucket
ORDER BY cd.delivery_bucket;


-- Q6: Distribution channel mix by country
SELECT
    country,
    COUNT(*)                                                                     AS total_orders,
    ROUND(COUNT(CASE WHEN distribution_channel='Direct Sales' THEN 1 END)*100.0 / COUNT(*), 1) AS pct_direct_sales,
    ROUND(COUNT(CASE WHEN distribution_channel='Retail' THEN 1 END)*100.0 / COUNT(*), 1)       AS pct_retail,
    ROUND(COUNT(CASE WHEN distribution_channel='Digital' THEN 1 END)*100.0 / COUNT(*), 1)      AS pct_digital,
    ROUND(COUNT(CASE WHEN distribution_channel='Referral' THEN 1 END)*100.0 / COUNT(*), 1)     AS pct_referral
FROM distribution
GROUP BY country
ORDER BY total_orders DESC;


-- Q7: Customer acquisition cost efficiency — ranking channels within each country
WITH channel_perf AS (
    SELECT
        d.country,
        d.distribution_channel,
        COUNT(DISTINCT d.customer_id) AS customers,
        ROUND(AVG(d.acquisition_cost), 2) AS avg_cac,
        ROUND(SUM(p.amount_paid) / NULLIF(COUNT(DISTINCT d.customer_id), 0), 2) AS revenue_per_customer
    FROM distribution d
    JOIN payments p ON d.customer_id = p.customer_id
    GROUP BY d.country, d.distribution_channel
)
SELECT
    country,
    distribution_channel,
    customers,
    avg_cac,
    revenue_per_customer,
    RANK() OVER (PARTITION BY country ORDER BY revenue_per_customer DESC) AS revenue_rank,
    RANK() OVER (PARTITION BY country ORDER BY avg_cac ASC)              AS cost_rank
FROM channel_perf
ORDER BY country, revenue_rank;
