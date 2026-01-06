

# 🛍️ Customer 360 Intelligence Platform

### *Turning Raw Transactions into Actionable Marketing Personas*

## 📌 1. The Business Problem

Marketing teams often face the **"One-Size-Fits-All"** dilemma. By treating every customer the same, they waste budget on low-value users and fail to nurture high-value VIPs, leading to:

* **High Churn Rates:** No early warning system for at-risk users.
* **Wasted Ad Spend:** Marketing to "one-time" buyers who never return.
* **Lower LTV:** Failing to turn "Loyalists" into brand "Advocates."

## 🚀 2. The Solution

An automated **Customer 360 Pipeline** that transforms raw order data into behavioral segments using the **RFM Framework** (Recency, Frequency, Monetary). The system identifies:

* **🏆 VIPs:** The top 1% driving the most profit.
* **🔄 Loyalists:** Frequent shoppers ready for referral programs.
* **🛒 Casual Shoppers:** The mass market with upsell potential.
* **⚠️ At Risk:** Dormant users requiring urgent win-back campaigns.

## 🛠️ 3. Tech Stack & Architecture

This project follows a professional production architecture:

* **Database:** PostgreSQL (Core storage & relational mapping).
* **Feature Engineering:** Advanced SQL (Window functions, CTEs, and Type casting).
* **Machine Learning:** Scikit-Learn (Unsupervised K-Means Clustering + Standard Scaling).
* **Data Ingestion:** Python/Pandas ETL pipeline.
* **Interactive UI:** Streamlit with Plotly (Real-time filtering & data export).

## 📁 4. Data Source

This project uses the [Retail Orders Dataset from Kaggle](https://www.kaggle.com/datasets/ankitbansal06/retail-orders), containing approximately 10,000 transaction records including order dates, profits, and product categories.

## 📊 5. Workflow

1. **ETL Phase:** Raw CSV data is cleaned and loaded into PostgreSQL.
2. **SQL Feature Engineering:** A heavy-lift SQL query calculates RFM metrics per customer and handles synthetic ID generation.
3. **Clustering Engine:** Python pulls SQL-processed data, scales the features, and applies K-Means to identify 4 distinct clusters.
4. **Intelligence Dashboard:** An interactive dashboard allows marketers to filter by segment, view behavioral trends, and export targeted email lists.

## 🏗️ 6. Project Structure

```text
customer_360_platform/
├── app/             # Streamlit Dashboard (Home.py)
├── src/             # ETL & ML Scripts (ingestion.py, clustering.py)
├── sql/             # Data cleaning and Feature Engineering Layer (schema.sql, rfm_analysis.sql)
├── data/            # Raw Transaction Data
├── .env             # Database Credentials (Secure)
└── requirements.txt # Dependencies

```

## 📈 7. Key Features

* **Interactive Plotly Visualization:** Explore customer density with zoom/hover capabilities.
* **Dynamic KPI Cards:** Metrics that change color based on the selected customer segment.
* **SaaS-style Strategy Engine:** The dashboard automatically suggests a marketing action plan based on the active segment.
* **One-Click Export:** Download target customer lists directly to CSV for CRM integration.


## 🔍 8. Key Findings & Business Inference

After executing the K-Means clustering on the Retail dataset, the following patterns were identified:

### **The Pareto Principle in Action**

* **The "Whale" Effect:** Cluster 2 (VIPs) consists of only **~1% of the customer base** (10 users), yet their average profit contribution is **$11,000+ per user**.
* **Inference:** The business is highly dependent on a small group of elite spenders. A "Concierge" service or exclusive loyalty rewards for this group is mandatory to prevent them from moving to a competitor.

### **The "Loyalty Trap"**

* **Frequency vs. Profit:** Cluster 3 (Loyalists) has the highest purchase frequency (**13.3 orders**) but generates significantly less profit per order than VIPs.
* **Inference:** These users are "habitual" but price-sensitive. They likely wait for sales or buy lower-margin items. The strategy here should be **Upselling** (moving them to premium versions of products they already buy).

### **The Churn Warning**

* **The Ghost Town:** Cluster 0 as an average recency of **208 days**.
* **Inference:** These customers are effectively lost. However, since their historical frequency was ~7 orders, they clearly found value in the brand once. A **Win-Back campaign** (deep discounts for "return" purchases) is the most cost-effective way to reactivate this dormant revenue.

### **Growth Opportunity**

* **The Casual Majority:** Cluster 1 represents the largest portion of the database.
* **Inference:** This is the "Engine Room." Even a 5% increase in their average order frequency would result in a massive total revenue spike compared to focusing on any other group. This group should be the primary target for **"Bundle & Save"** marketing.

---