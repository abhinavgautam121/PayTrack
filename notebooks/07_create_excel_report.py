"""
07 - Excel Management Report Generator
=====================================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script uses Pandas and XlsxWriter to generate a formatted
Excel Management Report containing KPIs, Customer Segments,
and Regional Risk summaries.
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
EXCEL_DIR = os.path.join(BASE_DIR, '..', 'excel')
os.makedirs(EXCEL_DIR, exist_ok=True)

print("Loading processed datasets...")
customers = pd.read_csv(os.path.join(DATA_DIR, 'customers_clean.csv'))
loans = pd.read_csv(os.path.join(DATA_DIR, 'loans_clean.csv'))
payments = pd.read_csv(os.path.join(DATA_DIR, 'payments_clean.csv'))
segments = pd.read_csv(os.path.join(DATA_DIR, 'customer_segments.csv'))

# ============================================================
# 1. PREPARE DATA FOR EXCEL
# ============================================================
print("Preparing data summaries...")

# Executive Summary
total_cust = len(customers)
active_loans = len(loans[loans['loan_status'] == 'Active'])
default_rate = len(loans[loans['loan_status'] == 'Defaulted']) / total_cust
collection_rate = payments['amount_paid'].sum() / payments['amount_due'].sum()

exec_summary = pd.DataFrame({
    'Metric': ['Total Customers', 'Active Loans', 'Overall Default Rate', 'Overall Collection Rate', 'Total Revenue Collected'],
    'Value': [total_cust, active_loans, f"{default_rate*100:.1f}%", f"{collection_rate*100:.1f}%", f"${payments['amount_paid'].sum():,.2f}"]
})

# Segment Summary
segment_summary = segments.groupby('segment_name').agg(
    Customers=('customer_id', 'count'),
    Avg_Collection_Rate=('collection_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Avg_Days_Late=('avg_days_late', lambda x: f"{x.mean():.1f}"),
    Avg_Loan_Amount=('loan_amount', lambda x: f"${x.mean():,.2f}")
).reset_index()

# Regional Summary
regional_summary = customers.merge(loans[['customer_id', 'loan_status']], on='customer_id')
regional_summary = regional_summary.groupby('region').agg(
    Customers=('customer_id', 'count'),
    Defaults=('loan_status', lambda x: (x == 'Defaulted').sum())
).reset_index()
regional_summary['Default_Rate'] = (regional_summary['Defaults'] / regional_summary['Customers'] * 100).round(1).astype(str) + '%'

# ============================================================
# 2. WRITE TO EXCEL WITH FORMATTING
# ============================================================
print("Writing to Excel...")
excel_path = os.path.join(EXCEL_DIR, 'Management_Report.xlsx')

with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    workbook = writer.book
    
    # Formats
    header_format = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'top',
        'fg_color': '#D7E4BC', 'border': 1
    })
    title_format = workbook.add_format({
        'bold': True, 'font_size': 14, 'valign': 'vcenter'
    })
    
    # --- Sheet 1: Executive Summary ---
    exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False, startrow=2)
    worksheet1 = writer.sheets['Executive Summary']
    worksheet1.write('A1', 'Solar PAYG - Executive KPI Summary', title_format)
    for col_num, value in enumerate(exec_summary.columns.values):
        worksheet1.write(2, col_num, value, header_format)
    worksheet1.set_column('A:A', 25)
    worksheet1.set_column('B:B', 20)
    
    # --- Sheet 2: Customer Segments ---
    segment_summary.to_excel(writer, sheet_name='Customer Segments', index=False, startrow=2)
    worksheet2 = writer.sheets['Customer Segments']
    worksheet2.write('A1', 'Customer Segmentation Analysis', title_format)
    for col_num, value in enumerate(segment_summary.columns.values):
        worksheet2.write(2, col_num, value.replace('_', ' '), header_format)
    worksheet2.set_column('A:E', 20)
    
    # --- Sheet 3: Regional Risk ---
    regional_summary.to_excel(writer, sheet_name='Regional Risk', index=False, startrow=2)
    worksheet3 = writer.sheets['Regional Risk']
    worksheet3.write('A1', 'Regional Default Risk Analysis', title_format)
    for col_num, value in enumerate(regional_summary.columns.values):
        worksheet3.write(2, col_num, value.replace('_', ' '), header_format)
    worksheet3.set_column('A:D', 15)
    
    # --- Sheet 4: Raw Data Export (Sample) ---
    customers.head(1000).to_excel(writer, sheet_name='Customer Data (Sample)', index=False)

print(f"✅ Excel Management Report generated at: {excel_path}")
