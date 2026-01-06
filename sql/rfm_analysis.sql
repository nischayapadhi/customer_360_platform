/*
  Project: Customer 360 Intelligence Platform
  Step: Feature Engineering (RFM Metrics)
  
  Logic:
  1. Calculate Profit per line item.
  2. rfm_aggregation: Aggregate data by Customer to get:
     - Recency (Days since last order)
     - Frequency (Total unique orders)
     - Monetary (Total Profit generated)
*/

WITH profite AS (
    SELECT 
        *,
        (
            (list_price * (1 - discount_percent * 0.01) * quantity) - 
            (cost_price * quantity)
        ) as profit_generated
    FROM retail_orders
),

rfm_aggregation AS (
    SELECT 
        customer_id,
        (SELECT MAX(order_date) FROM retail_orders) - MAX(order_date) as recency_days,
        COUNT(DISTINCT order_id) as frequency_orders,
        SUM(profit_generated) as monetary_profit,
        ROUND(AVG(quantity)) as avg_basket_size
    FROM profite
    GROUP BY customer_id
)
SELECT * FROM rfm_aggregation
WHERE monetary_profit IS NOT NULL;