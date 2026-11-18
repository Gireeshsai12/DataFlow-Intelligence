SELECT date_trunc('month',ordered)::date AS month,
       count(*) AS orders,
       sum(gross) AS gross_revenue_cents,
       sum(sales-refund) AS net_revenue_cents,
       sum(sales-refund-cost) AS gross_profit_cents
FROM {{ source('public','order_facts') }}
GROUP BY 1
