"""
03 - Exploratory Data Analysis (EDA)
=====================================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script performs comprehensive EDA on the cleaned data
and generates visualizations saved to reports/.

Synthetic dataset inspired by the PAYG solar-energy business model.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
REPORT_DIR = os.path.join(BASE_DIR, '..', 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)

# ============================================================
# LOAD CLEANED DATA
# ============================================================
print("Loading cleaned datasets...")
customers  = pd.read_csv(os.path.join(DATA_DIR, 'customers_clean.csv'), parse_dates=['customer_since'])
products   = pd.read_csv(os.path.join(DATA_DIR, 'products_clean.csv'))
loans      = pd.read_csv(os.path.join(DATA_DIR, 'loans_clean.csv'), parse_dates=['loan_start_date','loan_end_date'])
payments   = pd.read_csv(os.path.join(DATA_DIR, 'payments_clean.csv'), parse_dates=['payment_date'])
dist       = pd.read_csv(os.path.join(DATA_DIR, 'distribution_clean.csv'), parse_dates=['order_date','delivery_date','installation_date'])
monthly    = pd.read_csv(os.path.join(DATA_DIR, 'monthly_metrics_clean.csv'), parse_dates=['month'])

# ============================================================
# 1. KPI CALCULATIONS
# ============================================================
print("\n" + "=" * 60)
print("BUSINESS KPIs")
print("=" * 60)

total_customers = len(customers)
active_customers = len(loans[loans['loan_status'] == 'Active'])
defaulted_customers = len(loans[loans['loan_status'] == 'Defaulted'])
completed_customers = len(loans[loans['loan_status'] == 'Completed'])

total_revenue = payments['amount_paid'].sum()
total_amount_due = payments['amount_due'].sum()
collection_rate = (total_revenue / total_amount_due) * 100 if total_amount_due > 0 else 0
default_rate = (defaulted_customers / total_customers) * 100
churn_rate = default_rate  # Using default as proxy for churn
avg_days_late = payments['days_late'].mean()
avg_outstanding = loans['remaining_balance'].mean()
avg_loan_value = loans['loan_amount'].mean()
avg_cac = dist['acquisition_cost'].mean()
revenue_per_customer = total_revenue / total_customers
on_time_rate = (payments[payments['days_late'] == 0].shape[0] / len(payments)) * 100
missed_rate = (payments[payments['missed_payment_flag'] == 1].shape[0] / len(payments)) * 100
avg_delivery_time = dist['delivery_days'].mean()
avg_install_time = dist['installation_days'].mean()

kpis = {
    'Total Customers': f"{total_customers:,}",
    'Active Customers': f"{active_customers:,}",
    'Completed Customers': f"{completed_customers:,}",
    'Defaulted Customers': f"{defaulted_customers:,}",
    'Total Revenue ($)': f"${total_revenue:,.2f}",
    'Total Amount Due ($)': f"${total_amount_due:,.2f}",
    'Collection Rate (%)': f"{collection_rate:.2f}%",
    'Default Rate (%)': f"{default_rate:.2f}%",
    'Churn Rate (%)': f"{churn_rate:.2f}%",
    'Avg Days Late': f"{avg_days_late:.1f}",
    'Avg Outstanding Balance ($)': f"${avg_outstanding:,.2f}",
    'Avg Loan Value ($)': f"${avg_loan_value:,.2f}",
    'Customer Acquisition Cost ($)': f"${avg_cac:.2f}",
    'Revenue per Customer ($)': f"${revenue_per_customer:,.2f}",
    'On-Time Payment Rate (%)': f"{on_time_rate:.2f}%",
    'Missed Payment Rate (%)': f"{missed_rate:.2f}%",
    'Avg Delivery Time (days)': f"{avg_delivery_time:.1f}",
    'Avg Installation Time (days)': f"{avg_install_time:.1f}",
}

for k, v in kpis.items():
    print(f"  {k:40s} {v}")

# ============================================================
# 2. CUSTOMER DEMOGRAPHICS
# ============================================================
print("\n" + "=" * 60)
print("CUSTOMER DEMOGRAPHICS")
print("=" * 60)

print("\nGender Distribution:")
print(customers['gender'].value_counts())

print("\nIncome Level Distribution:")
print(customers['income_level'].value_counts())

print("\nEmployment Type Distribution:")
print(customers['employment_type'].value_counts())

print("\nCountry Distribution:")
print(customers['country'].value_counts())

print("\nCustomer Segment Distribution:")
print(customers['customer_segment'].value_counts())

print("\nAcquisition Channel Distribution:")
print(customers['acquisition_channel'].value_counts())

# ============================================================
# 3. LOAN STATUS ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("LOAN STATUS ANALYSIS")
print("=" * 60)

print("\nLoan Status Distribution:")
print(loans['loan_status'].value_counts())
print(f"\nLoan Status Percentages:")
print(loans['loan_status'].value_counts(normalize=True).mul(100).round(2))

print("\nLoan Amount Statistics:")
print(loans['loan_amount'].describe().round(2))

# ============================================================
# 4. PAYMENT BEHAVIOR ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("PAYMENT BEHAVIOR")
print("=" * 60)

print("\nPayment Method Distribution:")
print(payments['payment_method'].value_counts())

print("\nDays Late Statistics:")
print(payments['days_late'].describe().round(2))

print("\nPayment Ratio Statistics (amount_paid / amount_due):")
print(payments['payment_ratio'].describe().round(4))

# ============================================================
# 5. DISTRIBUTION ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("DISTRIBUTION CHANNEL ANALYSIS")
print("=" * 60)

channel_stats = dist.groupby('distribution_channel').agg(
    total_customers=('customer_id', 'count'),
    avg_delivery_days=('delivery_days', 'mean'),
    avg_install_days=('installation_days', 'mean'),
    avg_cac=('acquisition_cost', 'mean')
).round(2)
print(channel_stats)

# ============================================================
# 6. CORRELATION ANALYSIS
# ============================================================
print("\n" + "=" * 60)
print("CORRELATION ANALYSIS")
print("=" * 60)

# Merge key metrics per customer
cust_metrics = payments.groupby('customer_id').agg(
    total_paid=('amount_paid', 'sum'),
    total_due=('amount_due', 'sum'),
    avg_days_late=('days_late', 'mean'),
    missed_count=('missed_payment_flag', 'sum'),
    payment_count=('payment_id', 'count')
).reset_index()

cust_metrics = cust_metrics.merge(loans[['customer_id', 'loan_amount', 'remaining_balance', 'loan_status']], on='customer_id')
cust_metrics = cust_metrics.merge(customers[['customer_id', 'age', 'tenure_months']], on='customer_id')
cust_metrics['collection_rate'] = np.where(cust_metrics['total_due'] > 0, cust_metrics['total_paid'] / cust_metrics['total_due'], 0)
cust_metrics['is_defaulted'] = (cust_metrics['loan_status'] == 'Defaulted').astype(int)

corr_cols = ['total_paid', 'avg_days_late', 'missed_count', 'loan_amount', 'remaining_balance', 'age', 'tenure_months', 'collection_rate', 'is_defaulted']
corr_matrix = cust_metrics[corr_cols].corr()

print("\nKey correlations with Default:")
print(corr_matrix['is_defaulted'].sort_values(ascending=False).round(4))

print("\nKey correlations with Collection Rate:")
print(corr_matrix['collection_rate'].sort_values(ascending=False).round(4))

# ============================================================
# 7. GENERATE CHARTS
# ============================================================
print("\n" + "=" * 60)
print("GENERATING CHARTS")
print("=" * 60)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Solar PAYG Analytics — EDA Overview', fontsize=16, fontweight='bold')

# Chart 1: Customer Growth
customers.set_index('customer_since').resample('QE')['customer_id'].count().cumsum().plot(
    ax=axes[0,0], color='#2196F3', linewidth=2)
axes[0,0].set_title('Cumulative Customer Growth', fontweight='bold')
axes[0,0].set_ylabel('Customers')

# Chart 2: Loan Status
loans['loan_status'].value_counts().plot(kind='bar', ax=axes[0,1], color=['#4CAF50','#FF9800','#F44336'])
axes[0,1].set_title('Loan Status Distribution', fontweight='bold')
axes[0,1].tick_params(axis='x', rotation=0)

# Chart 3: Revenue by Country
payments.merge(customers[['customer_id','country']], on='customer_id').groupby('country')['amount_paid'].sum().sort_values().plot(
    kind='barh', ax=axes[0,2], color='#9C27B0')
axes[0,2].set_title('Revenue by Country', fontweight='bold')

# Chart 4: Collection Rate by Channel
pay_dist = payments.merge(dist[['customer_id','distribution_channel']], on='customer_id')
channel_cr = pay_dist.groupby('distribution_channel').apply(
    lambda x: (x['amount_paid'].sum() / x['amount_due'].sum()) * 100).sort_values()
channel_cr.plot(kind='barh', ax=axes[1,0], color='#FF5722')
axes[1,0].set_title('Collection Rate by Channel (%)', fontweight='bold')

# Chart 5: Default Rate by Income
def_by_income = loans.merge(customers[['customer_id','income_level']], on='customer_id')
def_by_income = def_by_income.groupby('income_level').apply(
    lambda x: (x['loan_status']=='Defaulted').mean()*100)
def_by_income.plot(kind='bar', ax=axes[1,1], color='#E91E63')
axes[1,1].set_title('Default Rate by Income Level (%)', fontweight='bold')
axes[1,1].tick_params(axis='x', rotation=0)

# Chart 6: Payment Delay Distribution
payments['days_late'].clip(upper=60).hist(ax=axes[1,2], bins=30, color='#009688', edgecolor='white')
axes[1,2].set_title('Payment Delay Distribution (days)', fontweight='bold')

plt.tight_layout()
chart_path = os.path.join(REPORT_DIR, 'eda_overview.png')
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
print(f"Saved EDA overview chart to {chart_path}")

# Save KPIs to a text file
kpi_path = os.path.join(REPORT_DIR, 'kpis.txt')
with open(kpi_path, 'w') as f:
    f.write("Solar PAYG Analytics — Key Performance Indicators\n")
    f.write("=" * 60 + "\n\n")
    for k, v in kpis.items():
        f.write(f"{k:40s} {v}\n")
print(f"Saved KPIs to {kpi_path}")

print("\n✅ EDA COMPLETE")
