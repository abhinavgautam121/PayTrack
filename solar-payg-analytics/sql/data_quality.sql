-- ============================================================
-- DATA QUALITY CHECKS
-- Run after loading CSVs into PostgreSQL
-- ============================================================

-- Q1: Check for duplicate customers
SELECT customer_id, COUNT(*) AS cnt
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- Q2: Check for NULL ages
SELECT COUNT(*) AS missing_ages
FROM customers
WHERE age IS NULL;

-- Q3: Check for inconsistent gender values
SELECT gender, COUNT(*) AS cnt
FROM customers
GROUP BY gender
ORDER BY cnt DESC;

-- Q4: Check for NULL payment_method in payments
SELECT COUNT(*) AS missing_payment_method
FROM payments
WHERE payment_method IS NULL;

-- Q5: Check for payments where amount_paid > amount_due (overpayments/errors)
SELECT COUNT(*) AS overpayments
FROM payments
WHERE amount_paid > amount_due;

-- Q6: Check for negative remaining_balance in loans
SELECT COUNT(*) AS negative_balance
FROM loans
WHERE remaining_balance < 0;

-- Q7: Check for loans where loan_end_date < loan_start_date
SELECT COUNT(*) AS invalid_dates
FROM loans
WHERE loan_end_date < loan_start_date;

-- Q8: Check distribution for delivery_date before order_date
SELECT COUNT(*) AS invalid_delivery
FROM distribution
WHERE delivery_date < order_date;

-- Q9: Verify loan_status distribution
SELECT loan_status, COUNT(*) AS cnt,
       ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM loans
GROUP BY loan_status
ORDER BY cnt DESC;

-- Q10: Summary statistics — row counts per table
SELECT 'customers' AS tbl, COUNT(*) AS rows FROM customers
UNION ALL
SELECT 'products',  COUNT(*) FROM products
UNION ALL
SELECT 'loans',     COUNT(*) FROM loans
UNION ALL
SELECT 'payments',  COUNT(*) FROM payments
UNION ALL
SELECT 'distribution', COUNT(*) FROM distribution
UNION ALL
SELECT 'monthly_customer_metrics', COUNT(*) FROM monthly_customer_metrics;
