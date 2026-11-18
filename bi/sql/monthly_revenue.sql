WITH monthly AS (
    SELECT d.year_month, COUNT(*) AS orders, SUM(o.net_cents) AS net_cents,
           SUM(o.profit_cents) AS profit_cents
    FROM FactOrder AS o JOIN DimDate AS d ON d.date_key = o.date_key
    GROUP BY d.year_month
)
SELECT year_month, orders, net_cents, profit_cents,
       LAG(net_cents) OVER (ORDER BY year_month) AS previous_month_net_cents
FROM monthly
ORDER BY year_month;
