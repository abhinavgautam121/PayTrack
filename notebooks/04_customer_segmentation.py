"""
04 - Customer Segmentation
=====================================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script uses K-Means clustering on aggregated customer features
to identify distinct customer segments based on repayment behavior.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
REPORT_DIR = os.path.join(BASE_DIR, '..', 'reports')

# ============================================================
# 1. LOAD CLEANED DATA
# ============================================================
print("Loading cleaned datasets...")
customers  = pd.read_csv(os.path.join(DATA_DIR, 'customers_clean.csv'))
loans      = pd.read_csv(os.path.join(DATA_DIR, 'loans_clean.csv'))
payments   = pd.read_csv(os.path.join(DATA_DIR, 'payments_clean.csv'))

# ============================================================
# 2. FEATURE ENGINEERING FOR CLUSTERING
# ============================================================
print("Aggregating customer features...")
# Group payments by customer
cust_payments = payments.groupby('customer_id').agg(
    total_paid=('amount_paid', 'sum'),
    total_due=('amount_due', 'sum'),
    avg_days_late=('days_late', 'mean'),
    missed_count=('missed_payment_flag', 'sum'),
    payment_count=('payment_id', 'count')
).reset_index()

# Merge loan details
cust_loans = loans[['customer_id', 'loan_amount', 'remaining_balance']].copy()

# Merge all
features = cust_payments.merge(cust_loans, on='customer_id')

# Calculate derived features
features['collection_rate'] = np.where(features['total_due'] > 0, features['total_paid'] / features['total_due'], 0)
features['pct_balance_remaining'] = np.where(features['loan_amount'] > 0, features['remaining_balance'] / features['loan_amount'], 0)

# Select features for clustering
cluster_cols = ['total_paid', 'avg_days_late', 'missed_count', 'collection_rate', 'pct_balance_remaining', 'loan_amount']
X = features[cluster_cols].fillna(0)

# Scale features
print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================
# 3. K-MEANS CLUSTERING & ELBOW METHOD
# ============================================================
print("Determining optimal clusters (Elbow Method)...")
inertia = []
K = range(2, 8)
# We limit silhouette calculation to a sample for performance
sample_size = min(10000, X_scaled.shape[0])
X_sample = X_scaled[:sample_size]

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)
    
    # Calculate silhouette score on sample
    labels = kmeans.predict(X_sample)
    sil_score = silhouette_score(X_sample, labels)
    print(f"  k={k} | Inertia: {kmeans.inertia_:.2f} | Silhouette: {sil_score:.4f}")

# Plot Elbow Curve
plt.figure(figsize=(8, 5))
plt.plot(K, inertia, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Customer Segmentation')
plt.grid(True)
plt.savefig(os.path.join(REPORT_DIR, 'elbow_curve.png'))

# ============================================================
# 4. FINAL MODEL (K=4)
# ============================================================
print("Fitting final K-Means model with k=4...")
kmeans_final = KMeans(n_clusters=4, random_state=42, n_init=10)
features['cluster'] = kmeans_final.fit_predict(X_scaled)

# ============================================================
# 5. CLUSTER PROFILING
# ============================================================
print("Profiling clusters...")
cluster_summary = features.groupby('cluster')[cluster_cols].mean().round(2)
cluster_summary['customer_count'] = features['cluster'].value_counts()
print(cluster_summary)

# Define business names based on characteristics
# This is a heuristic based on synthetic data patterns
def assign_segment_name(row):
    if row['collection_rate'] > 0.9 and row['avg_days_late'] < 5:
        return 'Reliable High-Value'
    elif row['missed_count'] > 3 and row['avg_days_late'] > 20:
        return 'High Risk'
    elif row['collection_rate'] < 0.5:
        return 'Critical Risk'
    else:
        return 'Consistent Low-Value'

# Map standard names to clusters based on logic or index. 
# We'll use a simple sorted mapping based on collection rate for consistent names.
sorted_clusters = cluster_summary.sort_values(by='collection_rate', ascending=False).index
name_mapping = {
    sorted_clusters[0]: 'Premium Reliable',
    sorted_clusters[1]: 'Standard Consistent',
    sorted_clusters[2]: 'Emerging Risk',
    sorted_clusters[3]: 'High Risk/Default'
}

features['segment_name'] = features['cluster'].map(name_mapping)

print("\nFinal Segments:")
print(features['segment_name'].value_counts())

# Save results
features.to_csv(os.path.join(DATA_DIR, 'customer_segments.csv'), index=False)
print("Saved segments to data/processed/customer_segments.csv")
print("✅ CUSTOMER SEGMENTATION COMPLETE")
