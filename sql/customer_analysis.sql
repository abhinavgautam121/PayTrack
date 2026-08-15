-- ============================================================
-- CUSTOMER ANALYSIS — 10 Business Questions
-- ============================================================

-- Q1: Total customers by country and their percentage share
SELECT
    country,
    COUNT(*)                                              AS total_customers,
    ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER(), 2)      AS pct_share
FROM customers
GROUP BY country
ORDER BY total_customers DESC;


-- Q2: Customer growth trend — new customers per quarter
SELECT
    DATE_TRUNC('quarter', customer_since)  AS quarter,
    COUNT(*)                               AS new_customers,
    SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('quarter', customer_since)) AS cumulative_customers
FROM customers
GROUP BY DATE_TRUNC('quarter', customer_since)
ORDER BY quarter;


-- Q3: Customer demographics — age distribution by income level
SELECT
    income_level,
    COUNT(*)                        AS customers,
    ROUND(AVG(age), 1)              AS avg_age,
    MIN(age)                        AS min_age,
    MAX(age)                        AS max_age,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY age) AS median_age
FROM customers
WHERE age IS NOT NULL
GROUP BY income_level
ORDER BY customers DESC;


-- Q4: Which customer segments generate the highest total revenue?
SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id)                           AS customers,
    ROUND(SUM(p.amount_paid), 2)                            AS total_revenue,
    ROUND(SUM(p.amount_paid) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;


-- Q5: Which acquisition channels bring the most customers and at what cost?
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id)           AS total_customers,
    ROUND(AVG(d.acquisition_cost), 2)       AS avg_cac,
    ROUND(SUM(p.amount_paid), 2)            AS total_revenue,
    ROUND(SUM(p.amount_paid) / NULLIF(SUM(d.acquisition_cost), 0), 2) AS revenue_to_cac_ratio
FROM customers c
JOIN distribution d ON c.customer_id = d.customer_id
JOIN payments p     ON c.customer_id = p.customer_id
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;


-- Q6: What percentage of customers have had at least one missed payment?
SELECT
    ROUND(
        COUNT(DISTINCT CASE WHEN missed_payment_flag = 1 THEN customer_id END) * 100.0
        / COUNT(DISTINCT customer_id), 2
    ) AS pct_with_missed_payments
FROM payments;


-- Q7: Customer tenure analysis — average tenure in months by segment
SELECT
    customer_segment,
    ROUND(AVG(
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, customer_since)) * 12
      + EXTRACT(MONTH FROM AGE(CURRENT_DATE, customer_since))
    ), 1) AS avg_tenure_months,
    COUNT(*) AS customers
FROM customers
GROUP BY customer_segment
ORDER BY avg_tenure_months DESC;


-- Q8: Top 10 sales agents by number of customers acquired
SELECT
    sales_agent_id,
    COUNT(*)                                    AS customers_acquired,
    COUNT(DISTINCT country)                     AS countries_served
FROM customers
GROUP BY sales_agent_id
ORDER BY customers_acquired DESC
LIMIT 10;


-- Q9: Customers with the highest lifetime payment value (top 20)
SELECT
    c.customer_id,
    c.country,
    c.region,
    c.customer_segment,
    c.income_level,
    ROUND(SUM(p.amount_paid), 2) AS total_paid,
    COUNT(p.payment_id)          AS total_payments
FROM customers c
JOIN payments p ON c.customer_id = p.customer_id
GROUP BY c.customer_id, c.country, c.region, c.customer_segment, c.income_level
ORDER BY total_paid DESC
LIMIT 20;


-- Q10: Regional customer distribution with average income mix
SELECT
    country,
    region,
    COUNT(*)                                                     AS total_customers,
    ROUND(COUNT(CASE WHEN income_level='Low' THEN 1 END)*100.0 / COUNT(*), 1)    AS pct_low_income,
    ROUND(COUNT(CASE WHEN income_level='Medium' THEN 1 END)*100.0 / COUNT(*), 1) AS pct_medium_income,
    ROUND(COUNT(CASE WHEN income_level='High' THEN 1 END)*100.0 / COUNT(*), 1)   AS pct_high_income
FROM customers
GROUP BY country, region
ORDER BY total_customers DESC;
