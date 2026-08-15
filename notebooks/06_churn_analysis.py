"""
06 - Churn Analysis
=====================================
Solar PAYG Customer, Credit Risk & Churn Analytics

This script analyzes churn (default) drivers and builds a 
Random Forest classification model to predict churn probability.
"""

import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data', 'processed')
REPORT_DIR = os.path.join(BASE_DIR, '..', 'reports')

print("Loading cleaned datasets...")
customers  = pd.read_csv(os.path.join(DATA_DIR, 'customers_clean.csv'))
loans      = pd.read_csv(os.path.join(DATA_DIR, 'loans_clean.csv'))
payments   = pd.read_csv(os.path.join(DATA_DIR, 'payments_clean.csv'))
dist       = pd.read_csv(os.path.join(DATA_DIR, 'distribution_clean.csv'))

# ============================================================
# 1. PREPARE DATASET FOR MODELING
# ============================================================
print("Preparing dataset for Churn Prediction...")

# Define churn as loan_status == 'Defaulted'
loans['is_churned'] = (loans['loan_status'] == 'Defaulted').astype(int)

# Aggregate payment history
cust_payments = payments.groupby('customer_id').agg(
    avg_days_late=('days_late', 'mean'),
    missed_payments=('missed_payment_flag', 'sum'),
    total_due=('amount_due', 'sum'),
    total_paid=('amount_paid', 'sum')
).reset_index()
cust_payments['collection_rate'] = np.where(cust_payments['total_due'] > 0, cust_payments['total_paid'] / cust_payments['total_due'], 0)

# Merge datasets
model_df = loans[['customer_id', 'loan_amount', 'remaining_balance', 'is_churned']].copy()
model_df = model_df.merge(customers[['customer_id', 'age', 'income_level', 'customer_segment', 'tenure_months']], on='customer_id')
model_df = model_df.merge(cust_payments, on='customer_id')
model_df = model_df.merge(dist[['customer_id', 'delivery_days', 'acquisition_cost']], on='customer_id')

# Convert categorical features to dummy variables
categorical_cols = ['income_level', 'customer_segment']
model_df = pd.get_dummies(model_df, columns=categorical_cols, drop_first=True)

# Select features
features = [col for col in model_df.columns if col not in ['customer_id', 'is_churned', 'total_due', 'total_paid']]
X = model_df[features].fillna(0)
y = model_df['is_churned']

print(f"Features used: {features}")

# ============================================================
# 2. TRAIN-TEST SPLIT
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set: {X_test.shape[0]} samples")

# ============================================================
# 3. TRAIN RANDOM FOREST CLASSIFIER
# ============================================================
print("Training Random Forest model...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# ============================================================
# 4. MODEL EVALUATION
# ============================================================
print("\nEvaluating Model...")
y_pred = rf_model.predict(X_test)
y_prob = rf_model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f} (When we predict churn, we are correct {prec*100:.1f}% of the time)")
print(f"Recall:    {rec:.4f} (We catch {rec*100:.1f}% of all actual churners)")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")
print("\nConfusion Matrix:")
print(f"True Negatives:  {conf_matrix[0][0]} | False Positives: {conf_matrix[0][1]}")
print(f"False Negatives: {conf_matrix[1][0]}  | True Positives:  {conf_matrix[1][1]}")

# ============================================================
# 5. FEATURE IMPORTANCE
# ============================================================
print("\nFeature Importance:")
importances = rf_model.feature_importances_
feature_imp_df = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values(by='Importance', ascending=False)
print(feature_imp_df.head(10))

# Plot Feature Importance
plt.figure(figsize=(10, 6))
plt.barh(feature_imp_df['Feature'][:10][::-1], feature_imp_df['Importance'][:10][::-1], color='#3F51B5')
plt.title('Top 10 Drivers of Churn (Random Forest Feature Importance)')
plt.xlabel('Relative Importance')
plt.tight_layout()
plt.savefig(os.path.join(REPORT_DIR, 'churn_feature_importance.png'))
print(f"Saved feature importance chart to {REPORT_DIR}/churn_feature_importance.png")

print("\nCHURN ANALYSIS COMPLETE")
