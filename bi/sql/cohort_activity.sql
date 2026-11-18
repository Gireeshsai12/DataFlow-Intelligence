WITH activity AS (
    SELECT DISTINCT o.customer_id, d.year_month
    FROM FactOrder AS o JOIN DimDate AS d ON d.date_key = o.date_key
), first_order AS (
    SELECT customer_id, MIN(year_month) AS cohort
    FROM activity GROUP BY customer_id
)
SELECT f.cohort, a.year_month AS activity_month, COUNT(*) AS retained
FROM activity AS a JOIN first_order AS f ON a.customer_id = f.customer_id
GROUP BY f.cohort, a.year_month
ORDER BY f.cohort, a.year_month;
