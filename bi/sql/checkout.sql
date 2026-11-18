SELECT variant, COUNT(*) AS sessions, SUM(carts) AS carts, SUM(conversions) AS conversions
FROM FactSession
GROUP BY variant
ORDER BY variant;
