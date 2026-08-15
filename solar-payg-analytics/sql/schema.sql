-- ============================================================
-- Solar PAYG Customer, Credit Risk & Churn Analytics
-- PostgreSQL Database Schema
-- ============================================================
-- Synthetic dataset inspired by the PAYG solar-energy
-- business model. NOT affiliated with Sun King.
-- ============================================================

-- Drop tables if they exist (for idempotent re-runs)
DROP TABLE IF EXISTS monthly_customer_metrics CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS distribution CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- ============================================================
-- 1. PRODUCTS
-- ============================================================
CREATE TABLE products (
    product_id      VARCHAR(10)    PRIMARY KEY,
    product_name    VARCHAR(50)    NOT NULL,
    product_category VARCHAR(30)   NOT NULL,
    product_price   NUMERIC(10,2)  NOT NULL CHECK (product_price > 0),
    expected_lifespan INT          NOT NULL,       -- years
    power_capacity  INT            NOT NULL        -- watts
);

-- ============================================================
-- 2. CUSTOMERS
-- ============================================================
CREATE TABLE customers (
    customer_id       VARCHAR(12)   PRIMARY KEY,
    age               INT           CHECK (age >= 18 AND age <= 100),
    gender            VARCHAR(10),
    country           VARCHAR(30)   NOT NULL,
    region            VARCHAR(30)   NOT NULL,
    income_level      VARCHAR(10)   NOT NULL,      -- Low / Medium / High
    employment_type   VARCHAR(20)   NOT NULL,
    customer_since    DATE          NOT NULL,
    customer_segment  VARCHAR(20)   NOT NULL,      -- Premium / Standard / Basic
    acquisition_channel VARCHAR(20) NOT NULL,
    sales_agent_id    VARCHAR(10)   NOT NULL,
    tenure_months     INT
);

CREATE INDEX idx_customers_country     ON customers(country);
CREATE INDEX idx_customers_region      ON customers(region);
CREATE INDEX idx_customers_income      ON customers(income_level);
CREATE INDEX idx_customers_segment     ON customers(customer_segment);
CREATE INDEX idx_customers_channel     ON customers(acquisition_channel);
CREATE INDEX idx_customers_agent       ON customers(sales_agent_id);

-- ============================================================
-- 3. LOANS
-- ============================================================
CREATE TABLE loans (
    loan_id            VARCHAR(12)   PRIMARY KEY,
    customer_id        VARCHAR(12)   NOT NULL REFERENCES customers(customer_id),
    product_id         VARCHAR(10)   NOT NULL REFERENCES products(product_id),
    loan_amount        NUMERIC(10,2) NOT NULL CHECK (loan_amount > 0),
    deposit_amount     NUMERIC(10,2) NOT NULL CHECK (deposit_amount >= 0),
    installment_amount NUMERIC(10,2) NOT NULL CHECK (installment_amount > 0),
    loan_term_months   INT           NOT NULL CHECK (loan_term_months > 0),
    loan_start_date    DATE          NOT NULL,
    loan_end_date      DATE          NOT NULL,
    remaining_balance  NUMERIC(10,2) NOT NULL DEFAULT 0,
    loan_status        VARCHAR(15)   NOT NULL DEFAULT 'Active'  -- Active / Completed / Defaulted
);

CREATE INDEX idx_loans_customer  ON loans(customer_id);
CREATE INDEX idx_loans_product   ON loans(product_id);
CREATE INDEX idx_loans_status    ON loans(loan_status);

-- ============================================================
-- 4. PAYMENTS
-- ============================================================
CREATE TABLE payments (
    payment_id          VARCHAR(16)   PRIMARY KEY,
    customer_id         VARCHAR(12)   NOT NULL REFERENCES customers(customer_id),
    loan_id             VARCHAR(12)   NOT NULL REFERENCES loans(loan_id),
    payment_date        DATE,
    amount_due          NUMERIC(10,2) NOT NULL CHECK (amount_due >= 0),
    amount_paid         NUMERIC(10,2) NOT NULL CHECK (amount_paid >= 0),
    days_late           INT           DEFAULT 0,
    payment_method      VARCHAR(20),                -- Mobile Money / Cash / Bank Transfer
    missed_payment_flag INT           DEFAULT 0 CHECK (missed_payment_flag IN (0,1)),
    default_flag        INT           DEFAULT 0 CHECK (default_flag IN (0,1)),
    payment_ratio       NUMERIC
);

CREATE INDEX idx_payments_customer  ON payments(customer_id);
CREATE INDEX idx_payments_loan      ON payments(loan_id);
CREATE INDEX idx_payments_date      ON payments(payment_date);
CREATE INDEX idx_payments_missed    ON payments(missed_payment_flag);
CREATE INDEX idx_payments_default   ON payments(default_flag);

-- ============================================================
-- 5. DISTRIBUTION
-- ============================================================
CREATE TABLE distribution (
    customer_id          VARCHAR(12)   NOT NULL REFERENCES customers(customer_id),
    sales_agent_id       VARCHAR(10)   NOT NULL,
    country              VARCHAR(30)   NOT NULL,
    region               VARCHAR(30)   NOT NULL,
    distribution_channel VARCHAR(20)   NOT NULL,     -- Direct Sales / Retail / Digital / Referral
    order_date           DATE          NOT NULL,
    delivery_date        DATE,
    installation_date    DATE,
    delivery_days        INT           DEFAULT 0,
    installation_days    INT           DEFAULT 0,
    acquisition_cost     NUMERIC(10,2) NOT NULL DEFAULT 0
);

CREATE INDEX idx_dist_customer  ON distribution(customer_id);
CREATE INDEX idx_dist_channel   ON distribution(distribution_channel);
CREATE INDEX idx_dist_country   ON distribution(country);
CREATE INDEX idx_dist_agent     ON distribution(sales_agent_id);

-- ============================================================
-- 6. MONTHLY CUSTOMER METRICS
-- ============================================================
CREATE TABLE monthly_customer_metrics (
    customer_id         VARCHAR(12)   NOT NULL REFERENCES customers(customer_id),
    month               DATE          NOT NULL,
    amount_due          NUMERIC(10,2) NOT NULL DEFAULT 0,
    amount_paid         NUMERIC(10,2) NOT NULL DEFAULT 0,
    collection_rate     NUMERIC(6,2)  DEFAULT 0,
    days_late           INT           DEFAULT 0,
    missed_payments     INT           DEFAULT 0,
    outstanding_balance NUMERIC(10,2) DEFAULT 0,
    engagement_score    NUMERIC(6,2)  DEFAULT 0,
    churn_flag          INT           DEFAULT 0 CHECK (churn_flag IN (0,1))
);

CREATE INDEX idx_mcm_customer ON monthly_customer_metrics(customer_id);
CREATE INDEX idx_mcm_month    ON monthly_customer_metrics(month);
CREATE INDEX idx_mcm_churn    ON monthly_customer_metrics(churn_flag);
