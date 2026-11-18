SELECT c.region, COUNT(*) AS orders, COUNT(DISTINCT o.customer_id) AS active_customers,
       SUM(o.net_cents) AS net_cents, SUM(o.profit_cents) AS profit_cents
FROM FactOrder AS o JOIN DimCustomer AS c ON c.customer_id = o.customer_id
GROUP BY c.region
ORDER BY net_cents DESC, c.region;
