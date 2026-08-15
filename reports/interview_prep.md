# Interview Preparation Guide
**Solar PAYG Customer, Credit Risk & Churn Analytics**

This document contains materials to help you present this portfolio project effectively during an interview with Sun King or any other analytics role.

---

## 1. The 2-Minute Project Pitch (Elevator Pitch)
**Problem:** "PAYG solar companies face significant challenges with customer default and churn, which directly impact revenue and hardware losses. I wanted to understand the key drivers behind repayment behavior and distribution efficiency."
**Approach:** "I designed a synthetic database of 50,000 customers modeled after the PAYG industry, encompassing customer demographics, loans, monthly payment histories, and distribution logistics."
**Tools:** "I used Python (Pandas/Scikit-learn) for data cleaning, EDA, and machine learning, PostgreSQL for complex data modeling and business querying, and designed an Excel management report and Power BI dashboard for executive visibility."
**Analysis:** "I performed K-Means clustering to segment customers based on repayment reliability, and built a Random Forest classifier to predict churn probability based on early payment behavior and demographics."
**Key Finding:** "The most actionable finding was that delays exceeding 30 days almost always lead to default. Furthermore, customers who faced delivery delays had significantly lower initial collection rates."
**Business Impact:** "I recommended implementing an early-warning intervention at 14 days rather than 30, and digitizing the distribution channel, which could potentially lower Customer Acquisition Cost (CAC) by 50% while improving collection rates."

---

## 2. Resume Bullets
* Designed and executed an end-to-end data analytics project simulating a PAYG solar energy business model with 50,000+ customers and 500,000+ payment records.
* Engineered a relational PostgreSQL database (6 tables) and wrote 25+ complex SQL queries (CTEs, Window Functions, JOINs) to extract insights on collection rates, CAC, and delivery efficiency.
* Developed a K-Means clustering model in Python to segment customers into 4 distinct risk profiles, identifying a 'Premium Reliable' segment for targeted upsell campaigns.
* Trained a Random Forest classification model to predict customer churn with 94% accuracy (0.74 F1 Score), identifying average days late as the primary driver of default.
* Authored a strategic business recommendation report and an automated Excel Management Report (via Pandas/XlsxWriter) to translate technical findings into actionable operational improvements.

---

## 3. Technical Interview Questions & Answers

**Q1: Why did you use a Random Forest model for churn prediction instead of Logistic Regression?**
*Answer:* I chose Random Forest because it handles non-linear relationships and interactions between features well without requiring extensive feature scaling or transformation. It also provides a clear 'feature importance' output, which is crucial for explaining to stakeholders *why* customers are churning, not just *who* will churn.

**Q2: How did you determine the optimal number of clusters for your customer segmentation?**
*Answer:* I used the Elbow Method to plot the Within-Cluster-Sum-of-Squares (Inertia) against the number of clusters (k). I looked for the 'elbow' point where the rate of decrease sharply slows down, which occurred at k=4. I also calculated Silhouette Scores to ensure the clusters were distinct and well-separated.

**Q3: Describe a complex SQL query you wrote for this project.**
*Answer:* I wrote a query to analyze the customer acquisition cost (CAC) efficiency by channel and country. It used a CTE to aggregate total customers, average CAC, and revenue per customer for each channel. Then, in the main query, I used the `RANK() OVER (PARTITION BY country ORDER BY revenue_per_customer DESC)` window function to rank the channels' ROI within each specific country.

**Q4: How did you handle missing data in your dataset?**
*Answer:* I used Pandas for data cleaning. For missing numerical values like 'age', I imputed them using the median to avoid skewing the distribution. For categorical fields like 'payment_method', I filled missing values with an 'Unknown' category rather than dropping the rows, as dropping them would mean losing valuable loan and default information.

**Q5: What is the difference between Precision and Recall in the context of your churn model?**
*Answer:* Precision measures how many of the customers we *predicted* to churn actually did churn (avoiding false alarms). Recall measures how many of the *actual* churners our model successfully identified. In this business context, Recall is often more important because the cost of missing a churner (losing the solar product and revenue) is higher than the cost of a false alarm (sending an unnecessary SMS reminder).

---

## 4. Business & Analytics Questions

**Q6: What is the biggest business problem this project solves?**
*Answer:* It solves the problem of reactive credit management. Instead of waiting for a customer to fully default to realize there's a problem, this project provides a framework to proactively identify high-risk behavior early (e.g., at 14 days late) and intervene before the customer reaches the 'point of no return'.

**Q7: Based on your analysis, which distribution channel should the company invest more in?**
*Answer:* The company should invest more in Digital and Referral channels. While Direct Sales acquire the most raw volume, they have the highest Customer Acquisition Cost (CAC). Digital channels have a much lower CAC and a higher overall Revenue-to-CAC ratio, offering a better Return on Investment (ROI).

**Q8: How would you explain your K-Means clustering results to a non-technical Sales Manager?**
*Answer:* I would explain that we grouped our customers into four distinct 'personas' based on how they pay. For example, our 'Premium Reliable' group pays on time almost always. I would advise the Sales Manager to target this specific group with our new, larger home systems because data shows they are highly likely to pay off larger loans successfully.

**Q9: What is the relationship between delivery time and customer repayment?**
*Answer:* The data shows a clear negative correlation. Customers who experience delivery and installation delays of over 14 days have a significantly lower collection rate in their first few months. A poor onboarding experience degrades trust, making customers less willing to prioritize their payments.

**Q10: What are the limitations of your project/analysis?**
*Answer:* Because the data is synthetic, the exact numerical relationships (like the precise correlation between age and default) are simulated. In a real-world scenario, I would also want to incorporate external macroeconomic data, such as local inflation rates or agricultural harvest seasons, which heavily impact a rural customer's ability to pay.
