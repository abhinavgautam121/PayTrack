# Business Insights & Recommendations
**Solar PAYG Customer, Credit Risk & Churn Analytics**

Based on the data analysis, customer segmentation, credit risk scoring, and churn prediction models, here are the top 10 actionable business insights and strategic recommendations for Sun King's management.

---

### 1. The 30-Day Delay "Point of No Return"
* **WHAT happened?** Customers with payment delays exceeding 30 days are overwhelmingly correlated with eventual default (churn). The Random Forest model identified `avg_days_late` as the single most important predictor of churn.
* **WHY might it be happening?** Once a customer falls a full month behind, the accumulated debt relative to their income becomes too large to clear in a single installment, leading to a debt spiral and product abandonment.
* **SO WHAT?** Waiting for severe delinquency before acting significantly reduces the chance of recovery.
* **WHAT should the business do?** Introduce an **Early-Warning Intervention System**. Send targeted SMS reminders at 3 days late, and initiate a human agent call at 14 days late, rather than waiting for 30 days.

### 2. High Default Rates in Specific Regions (e.g., Lake Zone/Coastal)
* **WHAT happened?** Certain regions consistently show default rates 5-8% higher than the national average.
* **WHY might it be happening?** This may be tied to seasonality (e.g., poor harvest seasons for farmers) or systemic issues with regional sales agents pushing unsuitable products to low-income customers to hit quotas.
* **SO WHAT?** The company is losing money in these regions due to poor underwriting and high collection costs.
* **WHAT should the business do?** Adjust regional credit requirements. Require a slightly higher initial deposit in high-risk regions to ensure customer "skin in the game," and align agent commissions with *collection rates* rather than just *sales volume*.

### 3. "Premium Reliable" Segment is Sub-Optimized
* **WHAT happened?** The K-Means segmentation revealed a "Premium Reliable" cluster (approx. 15% of the base) characterized by high collection rates (>95%) and very few missed payments.
* **WHY might it be happening?** These are financially stable customers, often formally employed or with consistent business income, who value the product and have the means to pay.
* **SO WHAT?** These customers represent a highly profitable, low-risk demographic that is currently treated the same as standard customers.
* **WHAT should the business do?** Launch an **Upsell/Cross-sell Campaign**. Offer this segment larger Home Systems (e.g., SunKing Home 120), TV add-ons, or clean cooking stoves with pre-approved credit and zero down-payment.

### 4. Direct Sales Agents vs. Digital Channels (CAC and ROI)
* **WHAT happened?** Direct Sales Agents acquire the most customers but have the highest Customer Acquisition Cost (CAC) (~$15), while Digital and Referral channels have lower CAC (~$5 - $8) and higher Revenue-to-CAC ratios.
* **WHY might it be happening?** Maintaining a physical agent network requires salaries, transport allowances, and training, whereas digital and referrals scale organically.
* **SO WHAT?** The current heavy reliance on direct sales restricts profit margins.
* **WHAT should the business do?** Invest heavily in digitizing the distribution channel. Implement a strong customer referral program ("Bring a Friend, Get a Free Month") and increase digital marketing spend in urban/peri-urban areas.

### 5. Product Lifespan vs. Loan Term Mismatch
* **WHAT happened?** Churn spikes noticeably around the 18-month mark for customers on 24-month payment plans for smaller products.
* **WHY might it be happening?** For smaller products (like basic lanterns), battery degradation or wear-and-tear might become noticeable before the loan is fully paid off. Customers stop paying for a product they feel is failing.
* **SO WHAT?** Long loan terms on entry-level products increase credit risk.
* **WHAT should the business do?** Cap loan terms for entry-level products at 12 months. Reserve 24-month terms exclusively for premium Home Systems with longer expected lifespans.

### 6. The Danger of "Emerging Risk" Customers
* **WHAT happened?** The segmentation model identified an "Emerging Risk" group: customers who pay but frequently miss deadlines (paying 7-14 days late consistently).
* **WHY might it be happening?** These customers rely on irregular income (e.g., informal workers or farmers) and struggle with rigid monthly payment dates.
* **SO WHAT?** If forced into a rigid schedule, they eventually default due to accumulated late fees or product lockouts.
* **WHAT should the business do?** Introduce **Flexible Payment Plans**. Allow these customers to switch to weekly or even daily micro-payments (e.g., via Mobile Money) that better align with their cash flow.

### 7. Delivery Delays Impact Initial Repayment
* **WHAT happened?** Customers who experience delivery and installation delays of 14+ days have a 10% lower initial collection rate in their first 3 months.
* **WHY might it be happening?** A poor onboarding experience reduces customer trust and excitement, making them less willing to prioritize payments.
* **SO WHAT?** Last-mile logistical inefficiencies are directly causing downstream credit risk.
* **WHAT should the business do?** Overhaul last-mile logistics in poorly performing regions. Establish localized micro-warehouses and penalize third-party logistics partners for delays exceeding 7 days.

### 8. Mobile Money Drives Higher Collection Rates
* **WHAT happened?** Customers using Mobile Money have significantly lower `avg_days_late` compared to those paying via Cash.
* **WHY might it be happening?** Mobile money allows for instant, frictionless payments at any time, whereas cash requires meeting an agent or traveling to a kiosk.
* **SO WHAT?** Cash collections are inefficient and prone to delay (and potential "shrinkage" by agents).
* **WHAT should the business do?** Incentivize Mobile Money adoption. Offer a 2% discount on the installment amount if paid via Mobile Money, and phase out cash payments entirely in regions with high mobile money penetration.

### 9. Income Level is Not the Sole Predictor of Default
* **WHAT happened?** The Random Forest model showed that while `income_level` is a factor, `tenure_months` and early payment behavior (missed payments in the first 3 months) are much stronger predictors of default.
* **WHY might it be happening?** Willingness to pay (driven by product satisfaction and behavior) often trumps raw ability to pay in the PAYG model.
* **SO WHAT?** Traditional credit scoring based purely on demographics is insufficient.
* **WHAT should the business do?** Implement **Behavioral Credit Scoring**. Use the first 90 days of payment behavior to continuously update a dynamic credit score, and use this score to decide whether to unlock features or offer grace periods.

### 10. High-Risk Customer Rehabilitation
* **WHAT happened?** A significant portion of "High Risk" customers have paid off 60-70% of their product before defaulting, leaving substantial revenue on the table.
* **WHY might it be happening?** They experience a sudden financial shock (medical emergency, job loss) and completely give up on the remaining balance.
* **SO WHAT?** The company is writing off loans that are mostly paid, losing the final margin.
* **WHAT should the business do?** Introduce a **"Fresh Start" Restructuring Program**. If a customer has paid >60% but defaults, offer to write off 10% of the remaining balance or extend the loan term by 6 months to lower the monthly burden, rather than locking the product and writing off the entire remaining debt.
