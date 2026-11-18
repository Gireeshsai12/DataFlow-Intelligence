"""Shared read models. Revenue and cost use integer US cents."""
QUERIES = {
    "dashboard/summary": """
        SELECT count(*) AS orders, count(DISTINCT customer_id) AS active_customers,
        coalesce(sum(gross),0) AS gross_revenue, coalesce(sum(sales-refund),0) AS net_revenue,
        coalesce(sum(refund),0) AS refunds, coalesce(sum(sales-refund-cost),0) AS gross_profit,
        round(avg(sales-refund),0) AS average_order_value,
        round(100*sum(sales-refund-cost)/nullif(sum(sales-refund),0),2) AS margin_pct,
        round(100*sum(refund)/nullif(sum(sales),0),2) AS refund_pct
        FROM order_facts WHERE ordered BETWEEN %(start)s AND %(end)s
    """,
    "revenue/trends": """
        WITH months AS (
          SELECT d::date AS month, coalesce(sum(sales-refund),0) AS net_revenue
          FROM generate_series(date_trunc('month',%(start)s::timestamp),
            date_trunc('month',%(end)s::timestamp), '1 month') d
          LEFT JOIN order_facts ON ordered >= d AND ordered < d + interval '1 month'
            AND ordered BETWEEN %(start)s AND %(end)s GROUP BY d
        )
        SELECT month,net_revenue,
         round(100*(net_revenue-lag(net_revenue) OVER series)/
           nullif(lag(net_revenue) OVER series,0),2) AS mom_pct,
         round(100*(net_revenue-lag(net_revenue,12) OVER series)/
           nullif(lag(net_revenue,12) OVER series,0),2) AS yoy_pct,
         round(avg(net_revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW))
           AS rolling_3_month_revenue
        FROM months WINDOW series AS (ORDER BY month) ORDER BY month
    """,
    "customers/segments": """
        WITH rfm AS (
          SELECT customer_id, %(end)s::date-max(ordered) AS recency,
          count(*) AS orders, sum(sales-refund) AS value FROM order_facts
          WHERE ordered BETWEEN %(start)s AND %(end)s GROUP BY customer_id
        ), classified AS (
          SELECT *, CASE WHEN recency>90 THEN 'At risk'
             WHEN orders>=5 AND value>=100000 THEN 'Champions'
             WHEN orders>=2 THEN 'Repeat' ELSE 'New or occasional' END AS segment FROM rfm
        )
        SELECT segment,count(*) AS customers,sum(orders) AS orders,
          round(avg(value)) AS average_observed_value, count(*) FILTER(WHERE orders>=2) AS repeat_customers
        FROM classified GROUP BY segment ORDER BY customers DESC,segment
    """,
    "customers/cohorts": """
        WITH activity AS (
          SELECT DISTINCT customer_id,date_trunc('month',ordered)::date AS month
          FROM orders WHERE ordered <= %(end)s
        ), first_order AS (
          SELECT customer_id,min(month) AS cohort FROM activity GROUP BY customer_id
        ), sizes AS (
          SELECT cohort,count(*) AS cohort_size FROM first_order GROUP BY cohort
        ), counts AS (
          SELECT cohort,month,count(*) AS retained FROM first_order JOIN activity USING(customer_id)
          GROUP BY cohort,month
        )
        SELECT s.cohort, d.month::date AS activity_month, s.cohort_size,
          coalesce(c.retained,0) AS retained,
          round(100.0*coalesce(c.retained,0)/s.cohort_size,1) AS retention_pct
        FROM sizes s CROSS JOIN LATERAL generate_series(s.cohort::timestamp,
            date_trunc('month',%(end)s::timestamp),'1 month') AS d(month)
        LEFT JOIN counts c ON c.cohort=s.cohort AND c.month=d.month
        WHERE s.cohort>=date_trunc('month',%(start)s::timestamp)
        ORDER BY s.cohort,d.month
    """,
    "marketing/funnel": """
        SELECT count(*) AS sessions,count(*) FILTER(WHERE cart) AS carts,
          count(*) FILTER(WHERE converted) AS conversions,
          round(100.0*count(*) FILTER(WHERE converted)/nullif(count(*),0),2) AS conversion_pct,
          round(100.0*count(*) FILTER(WHERE cart AND NOT converted)/
            nullif(count(*) FILTER(WHERE cart),0),2) AS cart_abandonment_pct
        FROM sessions WHERE visited BETWEEN %(start)s AND %(end)s
    """,
    "marketing/campaigns": """
        SELECT c.id,c.channel,c.impressions,c.clicks,c.spend,count(f.id) AS orders,
          coalesce(sum(f.sales-f.refund),0) AS attributed_revenue,
          round(coalesce(sum(f.sales-f.refund),0)/nullif(c.spend,0),2) AS roas
        FROM campaigns c LEFT JOIN order_facts f ON c.id=f.campaign_id
          AND f.ordered BETWEEN %(start)s AND %(end)s
        GROUP BY c.id ORDER BY attributed_revenue DESC,c.id
    """,
    "products/performance": """
        SELECT p.id,p.name,p.category,p.stock,
           coalesce(sum(i.quantity),0) AS units,
           coalesce(sum(i.quantity::bigint*(i.unit_price-i.discount)),0) AS sales_before_refunds,
           coalesce(sum(i.quantity::bigint*(i.unit_price-i.discount-i.unit_cost)),0) AS profit_before_refunds
        FROM products p LEFT JOIN (
           SELECT items.* FROM items JOIN orders ON orders.id=items.order_id
           WHERE ordered BETWEEN %(start)s AND %(end)s
        ) i ON p.id=i.product_id
        GROUP BY p.id ORDER BY sales_before_refunds DESC,p.id
    """,
    "quality": """
        SELECT 'Order precedes signup' AS check_name, count(*) AS failures
        FROM orders o JOIN customers c ON c.id=o.customer_id WHERE o.ordered<c.signup
        UNION ALL SELECT 'Refund exceeds sales',count(*) FROM order_facts WHERE refund>sales
        UNION ALL SELECT 'Order missing line items',count(*) FROM orders o
          WHERE NOT EXISTS(SELECT 1 FROM items WHERE order_id=o.id)
        UNION ALL SELECT 'Session precedes signup', count(*) FROM sessions s
          JOIN customers c ON c.id=s.customer_id WHERE s.visited<c.signup
    """,
    "pipelines/runs": "SELECT * FROM pipeline_runs ORDER BY id DESC",
}
