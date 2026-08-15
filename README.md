# PayTrack -  PAYG Customer, Credit Risk & Churn Analytics
*A professional portfolio project targeted toward the Sun King Analytics & Technology team.*

> **Disclaimer:** This project uses a completely synthetic dataset inspired by the PAYG (Pay-As-You-Go) solar-energy business model. It is not affiliated with, nor does it contain any confidential data from, Sun King.

## 📌 Project Overview
This project demonstrates an end-to-end data analytics workflow for a fictional PAYG solar energy company. It tackles three of the most critical challenges in the PAYG industry:
1. **Credit Risk Management:** Predicting which customers are likely to default on their solar loans.
2. **Churn Prevention:** Understanding the drivers that cause customers to stop paying.
3. **Distribution Channel Optimization:** Evaluating the efficiency of last-mile delivery and acquisition channels.

## 🎯 Business Problem & Objectives
PAYG solar companies provide off-grid solar products via affordable installment plans. The core business problem is maximizing revenue collection while minimizing defaults and customer churn in an unbanked, off-grid customer base.

## 🗄️ Data Architecture & Tools
* **Synthetic Data Generation:** Python (Pandas, NumPy) — 50,000+ customers, 500,000+ payment records.
* **Data Storage & ETL:** PostgreSQL / Python (Pandas)
* **Exploratory Data Analysis (EDA):** Python (Matplotlib)
* **Machine Learning:** Scikit-Learn (K-Means Clustering, Random Forest Classifier)
* **Reporting & Visualization:** Power BI (Template) & Excel

## 📁 Repository Structure
```
PayTrack/
│
├── data/                   # (Not tracked in Git to save space)
│   ├── raw/                # Generated synthetic CSVs
│   └── processed/          # Cleaned CSVs used for ML and dashboards
│
├── notebooks/              # Python scripts for data generation, EDA, and ML
│   ├── 01_data_generation.py
│   ├── 02_data_cleaning.py
│   ├── 03_eda.py
│   ├── 04_customer_segmentation.py
│   ├── 05_credit_risk.py
│   └── 06_churn_analysis.py
│
├── sql/                    # PostgreSQL Schema & Analytical Queries
│   ├── schema.sql
│   ├── data_quality.sql
│   ├── customer_analysis.sql
│   ├── credit_risk.sql
│   ├── churn_analysis.sql
│   └── distribution_analysis.sql
│
├── powerbi/                # Power BI Dashboard file
│   └── Solar_PAYG_Analytics.pbix
│
├── excel/                  # Excel Management Report
│   └── Management_Report.xlsx
│
├── reports/                # Generated charts, KPIs, and recommendations
│   ├── business_recommendations.md
│   └── (various .png charts)
│
├── requirements.txt
├── run_analytics.py
├── run_sql.py
└── README.md
```

## 🚀 Key Insights & Business Recommendations
Here are a few high-level insights generated from the analysis (see `reports/business_recommendations.md` for the full list):

1. **The 30-Day Delay "Point of No Return":** Customers exceeding 30 days late almost inevitably default. **Recommendation:** Implement an early-warning intervention at 14 days rather than waiting for severe delinquency.
2. **"Premium Reliable" Sub-Optimization:** 15% of the customer base pays on time with >95% collection rates. **Recommendation:** Launch an aggressive cross-sell campaign (e.g., larger TV systems) for this low-risk segment with zero down-payment.
3. **Digital Channels Outperform Direct Sales on ROI:** Direct sales acquire the most customers but have the highest CAC (~$15). Digital/Referral channels have lower CAC (~$5-$8) and higher Revenue-to-CAC ratios. **Recommendation:** Shift marketing spend toward referral programs and digital acquisition.
4. **Behavior > Income:** Initial payment behavior in the first 90 days is a stronger predictor of default than the customer's reported income level. **Recommendation:** Shift from static demographic credit scoring to dynamic behavioral credit scoring.

## 🛠️ How to Run the Project
1. **Clone the repository:** `git clone https://github.com/abhinavgautam121/PayTrack.git`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Generate Data:** Run `python notebooks/01_data_generation.py` to create the 50,000+ customer dataset.
4. **Run Pipeline:** Execute scripts `02` through `06` sequentially to clean data, run EDA, and train the ML models.
5. **Database:** Execute the SQL scripts in a PostgreSQL instance to recreate the data warehouse and run the analytical queries.

## 🔮 Future Improvements
* Integrate external macroeconomic data (e.g., inflation rates, rainfall data for farmers) to improve churn predictions.
* Deploy the Random Forest model via a Flask/FastAPI REST API to provide real-time credit scoring for new loan applications.
* Automate the data pipeline using Apache Airflow.
