SELECT p.category, SUM(l.quantity) AS units, SUM(l.sales_cents) AS sales_cents,
       SUM(l.sales_cents-l.cost_cents) AS profit_before_refunds_cents
FROM FactOrderLine AS l JOIN DimProduct AS p ON p.product_id = l.product_id
GROUP BY p.category
ORDER BY sales_cents DESC, p.category;
