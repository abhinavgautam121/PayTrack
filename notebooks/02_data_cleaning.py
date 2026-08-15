"""
02 - Data Cleaning Pipeline
============================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script inspects the raw dataset, identifies quality issues,
and produces clean CSV files in data/processed/.

Synthetic dataset inspired by the PAYG solar-energy business model.
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, '..', 'data', 'raw')
PROC_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
os.makedirs(PROC_DIR, exist_ok=True)

# ============================================================
# 1. LOAD RAW DATA
# ============================================================
print("=" * 60)
print("PHASE 1: LOADING RAW DATA")
print("=" * 60)

customers = pd.read_csv(os.path.join(RAW_DIR, 'customers.csv'))
products  = pd.read_csv(os.path.join(RAW_DIR, 'products.csv'))
loans     = pd.read_csv(os.path.join(RAW_DIR, 'loans.csv'))
payments  = pd.read_csv(os.path.join(RAW_DIR, 'payments.csv'))
distribution = pd.read_csv(os.path.join(RAW_DIR, 'distribution.csv'))
monthly  = pd.read_csv(os.path.join(RAW_DIR, 'monthly_customer_metrics.csv'))

datasets = {
    'customers': customers, 'products': products, 'loans': loans,
    'payments': payments, 'distribution': distribution, 'monthly_metrics': monthly
}

for name, df in datasets.items():
    print(f"\n{name}: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"  Columns: {list(df.columns)}")

# ============================================================
# 2. INSPECT DATA TYPES
# ============================================================
print("\n" + "=" * 60)
print("PHASE 2: DATA TYPE INSPECTION")
print("=" * 60)

for name, df in datasets.items():
    print(f"\n--- {name} ---")
    print(df.dtypes)

# ============================================================
# 3. MISSING VALUES
# ============================================================
print("\n" + "=" * 60)
print("PHASE 3: MISSING VALUE ANALYSIS")
print("=" * 60)

for name, df in datasets.items():
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(f"\n--- {name} ---")
        print(missing)
        print(f"  Total missing cells: {df.isnull().sum().sum()}")
    else:
        print(f"\n--- {name} --- No missing values")

# ============================================================
# 4. DUPLICATE DETECTION
# ============================================================
print("\n" + "=" * 60)
print("PHASE 4: DUPLICATE DETECTION")
print("=" * 60)

dup_customers = customers.duplicated(subset=['customer_id']).sum()
print(f"Duplicate customer_ids in customers: {dup_customers}")
print(f"  Decision: Remove duplicates, keep first occurrence.")

dup_payments = payments.duplicated().sum()
print(f"Fully duplicate rows in payments: {dup_payments}")

# ============================================================
# 5. CLEANING — CUSTOMERS
# ============================================================
print("\n" + "=" * 60)
print("PHASE 5: CLEANING CUSTOMERS")
print("=" * 60)

# 5a. Remove duplicates
customers_clean = customers.drop_duplicates(subset=['customer_id'], keep='first').copy()
print(f"Removed {len(customers) - len(customers_clean)} duplicate customer records.")

# 5b. Standardize gender
# Raw data has: M, F, Male, Female, male, female
gender_map = {
    'M': 'Male', 'F': 'Female',
    'Male': 'Male', 'Female': 'Female',
    'male': 'Male', 'female': 'Female'
}
customers_clean['gender'] = customers_clean['gender'].map(gender_map)
print(f"Standardized gender values: {customers_clean['gender'].value_counts().to_dict()}")

# 5c. Handle missing ages — fill with median age
median_age = customers_clean['age'].median()
missing_ages = customers_clean['age'].isnull().sum()
customers_clean['age'] = customers_clean['age'].fillna(median_age).astype(int)
print(f"Filled {missing_ages} missing ages with median: {median_age}")

# 5d. Convert customer_since to datetime
customers_clean['customer_since'] = pd.to_datetime(customers_clean['customer_since'])
print(f"Converted customer_since to datetime.")

# 5e. Create derived column: customer_tenure_months
reference_date = pd.Timestamp('2024-02-01')
customers_clean['tenure_months'] = (
    (reference_date.year - customers_clean['customer_since'].dt.year) * 12
    + (reference_date.month - customers_clean['customer_since'].dt.month)
)
print(f"Created tenure_months column. Range: {customers_clean['tenure_months'].min()}-{customers_clean['tenure_months'].max()}")

# 5f. Validate age range
invalid_ages = ((customers_clean['age'] < 18) | (customers_clean['age'] > 100)).sum()
print(f"Invalid ages (outside 18-100): {invalid_ages}")

print(f"\nCleaned customers: {len(customers_clean)} rows")

# ============================================================
# 6. CLEANING — LOANS
# ============================================================
print("\n" + "=" * 60)
print("PHASE 6: CLEANING LOANS")
print("=" * 60)

loans_clean = loans.copy()
loans_clean['loan_start_date'] = pd.to_datetime(loans_clean['loan_start_date'])
loans_clean['loan_end_date'] = pd.to_datetime(loans_clean['loan_end_date'])
# Clip negative remaining_balance to 0
neg_bal = (loans_clean['remaining_balance'] < 0).sum()
loans_clean['remaining_balance'] = loans_clean['remaining_balance'].clip(lower=0)
print(f"Fixed {neg_bal} negative remaining_balance values (clipped to 0).")
print(f"Loan status distribution:\n{loans_clean['loan_status'].value_counts()}")

# ============================================================
# 7. CLEANING — PAYMENTS
# ============================================================
print("\n" + "=" * 60)
print("PHASE 7: CLEANING PAYMENTS")
print("=" * 60)

payments_clean = payments.copy()
payments_clean['payment_date'] = pd.to_datetime(payments_clean['payment_date'])

# Fill missing payment_method with 'Unknown'
missing_pm = payments_clean['payment_method'].isnull().sum()
payments_clean['payment_method'] = payments_clean['payment_method'].fillna('Unknown')
print(f"Filled {missing_pm} missing payment_method values with 'Unknown'.")

# Clip days_late to 0 minimum
payments_clean['days_late'] = payments_clean['days_late'].clip(lower=0)

# Create derived: payment_ratio
payments_clean['payment_ratio'] = np.where(
    payments_clean['amount_due'] > 0,
    payments_clean['amount_paid'] / payments_clean['amount_due'],
    0
)
print(f"Created payment_ratio column.")
print(f"Cleaned payments: {len(payments_clean)} rows")

# ============================================================
# 8. CLEANING — DISTRIBUTION
# ============================================================
print("\n" + "=" * 60)
print("PHASE 8: CLEANING DISTRIBUTION")
print("=" * 60)

dist_clean = distribution.copy()
for col in ['order_date', 'delivery_date', 'installation_date']:
    dist_clean[col] = pd.to_datetime(dist_clean[col])

# Clip negative acquisition_cost
neg_cac = (dist_clean['acquisition_cost'] < 0).sum()
dist_clean['acquisition_cost'] = dist_clean['acquisition_cost'].clip(lower=0)
print(f"Fixed {neg_cac} negative acquisition_cost values.")
print(f"Cleaned distribution: {len(dist_clean)} rows")

# ============================================================
# 9. CLEANING — MONTHLY METRICS
# ============================================================
print("\n" + "=" * 60)
print("PHASE 9: CLEANING MONTHLY METRICS")
print("=" * 60)

monthly_clean = monthly.copy()
monthly_clean['month'] = pd.to_datetime(monthly_clean['month'])
print(f"Cleaned monthly_metrics: {len(monthly_clean)} rows")

# ============================================================
# 10. OUTLIER DETECTION
# ============================================================
print("\n" + "=" * 60)
print("PHASE 10: OUTLIER DETECTION")
print("=" * 60)

# Check for extreme outliers in payment amounts
q99 = payments_clean['amount_paid'].quantile(0.99)
q01 = payments_clean['amount_paid'].quantile(0.01)
print(f"Payment amount_paid — 1st percentile: {q01:.2f}, 99th percentile: {q99:.2f}")

# Check loan amounts
q99_loan = loans_clean['loan_amount'].quantile(0.99)
print(f"Loan amount — 99th percentile: {q99_loan:.2f}")

# Check delivery days
q99_del = dist_clean['delivery_days'].quantile(0.99)
print(f"Delivery days — 99th percentile: {q99_del:.0f}")

# ============================================================
# 11. SAVE CLEANED DATA
# ============================================================
print("\n" + "=" * 60)
print("PHASE 11: SAVING CLEANED DATA")
print("=" * 60)

customers_clean.to_csv(os.path.join(PROC_DIR, 'customers_clean.csv'), index=False)
products.to_csv(os.path.join(PROC_DIR, 'products_clean.csv'), index=False)
loans_clean.to_csv(os.path.join(PROC_DIR, 'loans_clean.csv'), index=False)
payments_clean.to_csv(os.path.join(PROC_DIR, 'payments_clean.csv'), index=False)
dist_clean.to_csv(os.path.join(PROC_DIR, 'distribution_clean.csv'), index=False)
monthly_clean.to_csv(os.path.join(PROC_DIR, 'monthly_metrics_clean.csv'), index=False)

print("All cleaned datasets saved to data/processed/")
print("\n✅ DATA CLEANING PIPELINE COMPLETE")
