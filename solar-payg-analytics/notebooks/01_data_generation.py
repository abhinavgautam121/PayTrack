import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import string

np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, '..', 'data', 'raw')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("Starting Data Generation...")

# 1. Products
products_data = [
    {'product_id': 'PRD-001', 'product_name': 'SunKing Pico', 'product_category': 'Lantern', 'product_price': 20.0, 'expected_lifespan': 3, 'power_capacity': 5},
    {'product_id': 'PRD-002', 'product_name': 'SunKing Pro', 'product_category': 'Lantern+Phone Charger', 'product_price': 45.0, 'expected_lifespan': 4, 'power_capacity': 10},
    {'product_id': 'PRD-003', 'product_name': 'SunKing Home 40Z', 'product_category': 'Home System', 'product_price': 150.0, 'expected_lifespan': 5, 'power_capacity': 40},
    {'product_id': 'PRD-004', 'product_name': 'SunKing Home 120', 'product_category': 'Home System', 'product_price': 300.0, 'expected_lifespan': 5, 'power_capacity': 120},
    {'product_id': 'PRD-005', 'product_name': 'SunKing Boom', 'product_category': 'Entertainment', 'product_price': 80.0, 'expected_lifespan': 4, 'power_capacity': 15}
]
products_df = pd.DataFrame(products_data)
products_df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)
print("products.csv generated.")

# 2. Customers
customer_ids = [f"CUS-{str(i).zfill(6)}" for i in range(1, NUM_CUSTOMERS + 1)]
ages = np.random.normal(38, 12, NUM_CUSTOMERS)
ages = np.clip(ages, 18, 85).astype(int)

# Introduce missing ages and inconsistent genders
genders = np.random.choice(['M', 'F', 'Male', 'Female', 'female', 'male'], NUM_CUSTOMERS, p=[0.3, 0.3, 0.15, 0.15, 0.05, 0.05])
countries = np.random.choice(['Kenya', 'Nigeria', 'Uganda', 'Tanzania', 'Zambia'], NUM_CUSTOMERS, p=[0.4, 0.3, 0.15, 0.1, 0.05])

regions = []
for c in countries:
    if c == 'Kenya': regions.append(np.random.choice(['Nairobi', 'Rift Valley', 'Central', 'Coast']))
    elif c == 'Nigeria': regions.append(np.random.choice(['Lagos', 'Kano', 'Abuja', 'Rivers']))
    elif c == 'Uganda': regions.append(np.random.choice(['Central', 'Western', 'Eastern', 'Northern']))
    elif c == 'Tanzania': regions.append(np.random.choice(['Dar es Salaam', 'Mwanza', 'Arusha']))
    else: regions.append(np.random.choice(['Lusaka', 'Copperbelt']))

income_levels = np.random.choice(['Low', 'Medium', 'High'], NUM_CUSTOMERS, p=[0.6, 0.3, 0.1])
employment_types = np.random.choice(['Informal', 'Formal', 'Farmer', 'Unemployed'], NUM_CUSTOMERS, p=[0.4, 0.3, 0.25, 0.05])

# Customer Since Date (Last 3 years)
start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)
date_diff = (end_date - start_date).days
customer_since = [start_date + timedelta(days=random.randint(0, date_diff)) for _ in range(NUM_CUSTOMERS)]

customer_segments = np.random.choice(['Premium', 'Standard', 'Basic'], NUM_CUSTOMERS, p=[0.15, 0.6, 0.25])
acquisition_channels = np.random.choice(['Direct Sales', 'Retail', 'Digital', 'Referral'], NUM_CUSTOMERS, p=[0.5, 0.3, 0.1, 0.1])
sales_agent_ids = [f"AGT-{str(random.randint(1, 1000)).zfill(4)}" for _ in range(NUM_CUSTOMERS)]

customers_df = pd.DataFrame({
    'customer_id': customer_ids,
    'age': ages,
    'gender': genders,
    'country': countries,
    'region': regions,
    'income_level': income_levels,
    'employment_type': employment_types,
    'customer_since': customer_since,
    'customer_segment': customer_segments,
    'acquisition_channel': acquisition_channels,
    'sales_agent_id': sales_agent_ids
})

# Imperfections: missing ages
customers_df.loc[customers_df.sample(frac=0.03).index, 'age'] = np.nan
# Imperfections: duplicates
duplicates = customers_df.sample(n=200)
customers_df = pd.concat([customers_df, duplicates], ignore_index=True)
customers_df.to_csv(os.path.join(OUTPUT_DIR, 'customers.csv'), index=False)
print("customers.csv generated.")
# Remove duplicates for internal references
customers_df = customers_df.drop_duplicates(subset=['customer_id'])

# 3. Loans
product_ids_assigned = np.random.choice(products_df['product_id'], NUM_CUSTOMERS, p=[0.3, 0.2, 0.2, 0.1, 0.2])
loan_df = pd.DataFrame({'customer_id': customers_df['customer_id'], 'product_id': product_ids_assigned})
loan_df = loan_df.merge(products_df[['product_id', 'product_price']], on='product_id')
loan_df['loan_id'] = [f"L-{str(i).zfill(6)}" for i in range(1, NUM_CUSTOMERS + 1)]
loan_df['loan_amount'] = loan_df['product_price'] * np.random.uniform(1.2, 1.5, NUM_CUSTOMERS) # with interest
loan_df['deposit_amount'] = loan_df['loan_amount'] * np.random.uniform(0.1, 0.2, NUM_CUSTOMERS)
loan_df['loan_term_months'] = np.random.choice([6, 12, 24], NUM_CUSTOMERS, p=[0.2, 0.5, 0.3])
loan_df['installment_amount'] = (loan_df['loan_amount'] - loan_df['deposit_amount']) / loan_df['loan_term_months']
loan_df['loan_start_date'] = customers_df['customer_since'].values
loan_df['loan_end_date'] = [
    pd.to_datetime(start) + pd.DateOffset(months=term)
    for start, term in zip(loan_df['loan_start_date'], loan_df['loan_term_months'])
]
loan_df['remaining_balance'] = loan_df['loan_amount'] - loan_df['deposit_amount']

# Determine behavior (hidden risk score based on income and employment)
risk_base = np.zeros(NUM_CUSTOMERS)
risk_base[customers_df['income_level'] == 'Low'] += 0.3
risk_base[customers_df['employment_type'] == 'Unemployed'] += 0.4
risk_base[customers_df['employment_type'] == 'Informal'] += 0.2
risk_base += np.random.uniform(0, 0.4, NUM_CUSTOMERS)
loan_df['risk_score'] = risk_base

# 4. Payments and Monthly Metrics
payments_list = []
monthly_metrics = []

print("Generating payments and metrics...")
# Vectorized/fast approach for payments
# For each customer, simulate month by month payments
# Generate array of months since start
current_date = datetime(2024, 2, 1)

payment_id_counter = 1
for row in loan_df.itertuples():
    cust_id = row.customer_id
    l_id = row.loan_id
    term = row.loan_term_months
    installment = row.installment_amount
    start = row.loan_start_date
    risk = row.risk_score
    rem_bal = row.remaining_balance
    
    # how many months have passed since start
    months_passed = min(term, (current_date.year - start.year)*12 + current_date.month - start.month)
    if months_passed <= 0: continue
        
    consecutive_misses = 0
    defaulted = False
    
    for m in range(1, months_passed + 1):
        if defaulted:
            break
        
        due_date = start + pd.DateOffset(months=m)
        if due_date > current_date:
            break
            
        amount_due = min(installment, rem_bal)
        if amount_due <= 0:
            break
            
        # Payment behavior based on risk
        miss_prob = min(0.9, risk * 0.5)
        is_missed = random.random() < miss_prob
        
        if is_missed:
            amount_paid = 0
            days_late = 30
            consecutive_misses += 1
            missed_flag = 1
        else:
            # Partial or full payment
            if random.random() < (risk * 0.3):
                amount_paid = amount_due * random.uniform(0.1, 0.9) # partial
                days_late = random.randint(1, 29)
            else:
                amount_paid = amount_due
                days_late = 0
            consecutive_misses = 0
            missed_flag = 0
            
        rem_bal -= amount_paid
        default_flag = 1 if consecutive_misses >= 3 else 0
        if default_flag == 1:
            defaulted = True
            
        payments_list.append({
            'payment_id': f"PAY-{str(payment_id_counter).zfill(8)}",
            'customer_id': cust_id,
            'loan_id': l_id,
            'payment_date': due_date + pd.DateOffset(days=days_late) if amount_paid > 0 else due_date,
            'amount_due': round(amount_due, 2),
            'amount_paid': round(amount_paid, 2),
            'days_late': days_late,
            'payment_method': random.choice(['Mobile Money', 'Cash', 'Bank Transfer']),
            'missed_payment_flag': missed_flag,
            'default_flag': default_flag
        })
        payment_id_counter += 1
        
        monthly_metrics.append({
            'customer_id': cust_id,
            'month': datetime(due_date.year, due_date.month, 1),
            'amount_due': round(amount_due, 2),
            'amount_paid': round(amount_paid, 2),
            'collection_rate': round((amount_paid/amount_due)*100, 2) if amount_due > 0 else 0,
            'days_late': days_late,
            'missed_payments': missed_flag,
            'outstanding_balance': round(rem_bal, 2),
            'engagement_score': round(100 - (days_late + missed_flag*20), 2),
            'churn_flag': default_flag
        })
        
    loan_df.at[row.Index, 'remaining_balance'] = max(0, rem_bal)
    loan_df.at[row.Index, 'loan_status'] = 'Defaulted' if defaulted else ('Completed' if rem_bal <= 0 else 'Active')

loan_df.drop(columns=['risk_score', 'product_price']).to_csv(os.path.join(OUTPUT_DIR, 'loans.csv'), index=False)
print("loans.csv generated.")

payments_df = pd.DataFrame(payments_list)
# Add some imperfections to payments
if len(payments_df) > 0:
    payments_df.loc[payments_df.sample(frac=0.01).index, 'payment_method'] = np.nan
payments_df.to_csv(os.path.join(OUTPUT_DIR, 'payments.csv'), index=False)
print("payments.csv generated.")

monthly_df = pd.DataFrame(monthly_metrics)
monthly_df.to_csv(os.path.join(OUTPUT_DIR, 'monthly_customer_metrics.csv'), index=False)
print("monthly_customer_metrics.csv generated.")

# 5. Distribution
dist_df = customers_df[['customer_id', 'sales_agent_id', 'country', 'region', 'acquisition_channel']].copy()
dist_df.rename(columns={'acquisition_channel': 'distribution_channel'}, inplace=True)
dist_df['order_date'] = customers_df['customer_since']

delivery_delays = np.random.gamma(2, 2, NUM_CUSTOMERS).astype(int)
install_delays = np.random.gamma(1.5, 2, NUM_CUSTOMERS).astype(int)
dist_df['delivery_days'] = delivery_delays
dist_df['installation_days'] = install_delays
dist_df['delivery_date'] = dist_df['order_date'] + pd.to_timedelta(delivery_delays, unit='d')
dist_df['installation_date'] = dist_df['delivery_date'] + pd.to_timedelta(install_delays, unit='d')

# Cost depends on channel
cac_map = {'Direct Sales': 15, 'Retail': 10, 'Digital': 5, 'Referral': 8}
dist_df['acquisition_cost'] = dist_df['distribution_channel'].map(cac_map) + np.random.normal(0, 2, NUM_CUSTOMERS)
dist_df['acquisition_cost'] = dist_df['acquisition_cost'].round(2)

dist_df.to_csv(os.path.join(OUTPUT_DIR, 'distribution.csv'), index=False)
print("distribution.csv generated.")

print("All synthetic datasets generated successfully in data/raw/")
