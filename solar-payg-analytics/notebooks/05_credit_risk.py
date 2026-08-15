"""
05 - Credit Risk Analysis
=====================================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script builds a simple credit risk scoring model
and analyzes the characteristics of high-risk customers.
"""

import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
REPORT_DIR = os.path.join(BASE_DIR, '..', 'reports')

print("Loading cleaned datasets...")
customers  = pd.read_csv(os.path.join(DATA_DIR, 'customers_clean.csv'))
loans      = pd.read_csv(os.path.join(DATA_DIR, 'loans_clean.csv'))
payments   = pd.read_csv(os.path.join(DATA_DIR, 'payments_clean.csv'))

# ============================================================
# 1. FEATURE ENGINEERING
# ============================================================
print("Engineering risk features...")
cust_risk = payments.groupby('customer_id').agg(
    avg_days_late=('days_late', 'mean'),
    max_days_late=('days_late', 'max'),
    missed_payments=('missed_payment_flag', 'sum'),
    total_due=('amount_due', 'sum'),
    total_paid=('amount_paid', 'sum')
).reset_index()

cust_risk['collection_rate'] = np.where(cust_risk['total_due'] > 0, cust_risk['total_paid'] / cust_risk['total_due'], 0)

cust_loans = loans[['customer_id', 'loan_amount', 'remaining_balance', 'loan_status']].copy()
cust_risk = cust_risk.merge(cust_loans, on='customer_id')

# ============================================================
# 2. CREDIT RISK SCORING MODEL
# ============================================================
print("Calculating Credit Risk Score...")
# Base Score = 100
# - 5 points per average day late
# - 15 points per missed payment
# + (collection_rate * 50)
cust_risk['risk_score'] = 100 - (cust_risk['avg_days_late'] * 5) - (cust_risk['missed_payments'] * 15) + (cust_risk['collection_rate'] * 50)
cust_risk['risk_score'] = cust_risk['risk_score'].clip(lower=0, upper=100)

def assign_risk_category(score):
    if score >= 80: return 'Low Risk'
    elif score >= 50: return 'Medium Risk'
    elif score >= 30: return 'High Risk'
    else: return 'Critical Risk'

cust_risk['risk_category'] = cust_risk['risk_score'].apply(assign_risk_category)

print("\nRisk Category Distribution:")
print(cust_risk['risk_category'].value_counts())

# ============================================================
# 3. RISK ANALYSIS
# ============================================================
print("\nRisk Analysis by Default Rate:")
# Check actual default rate by risk category
risk_defaults = cust_risk.groupby('risk_category').agg(
    total_customers=('customer_id', 'count'),
    defaulted_customers=('loan_status', lambda x: (x == 'Defaulted').sum())
)
risk_defaults['default_rate'] = (risk_defaults['defaulted_customers'] / risk_defaults['total_customers'] * 100).round(2)
print(risk_defaults.sort_values(by='default_rate'))

# Save risk scores
cust_risk.to_csv(os.path.join(DATA_DIR, 'credit_risk_scores.csv'), index=False)
print("\nSaved credit_risk_scores.csv")
print("✅ CREDIT RISK ANALYSIS COMPLETE")
