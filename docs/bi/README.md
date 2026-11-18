# Excel, Power BI, Tableau and Snowflake

The reports folder contains the generated NovaCart business workbook and eight CSVs. CSV money is in integer cents. The workbook displays financial report columns in USD and leaves raw order sample values in cents.

## Excel

Open the workbook and see Instructions for Power Query import and PivotTable construction. The workbook includes tables, a revenue chart, a retention color scale, a named range, an XLOOKUP example, a schema dictionary and a 250-order sample. Excel calculates the example formulas when opened. The workbook has no native PivotTable.

## Power BI Desktop

1. Create a Text parameter named RevenueCsvPath with the absolute path to reports/Revenue.csv.
2. Create a blank query named Revenue and paste Revenue.pq in Advanced Editor. Load Summary, Segments, Cohorts, Funnel, Campaigns and Products as CSV data sources and inspect inferred types.
3. In Model view, add the Date calculated table from Measures.dax and mark it as a date table. Relate Date[Date] one-to-many to Revenue[month] with single-direction filtering. Use a month-level axis because each row is a month aggregate.
4. Add the remaining DAX definitions individually as measures. Summary, Segments and Funnel are independent snapshots for the chosen export window. Use a fresh matched set of CSVs when changing the range. Date slicers apply to Revenue.
5. Add executive cards for gross revenue and margin, revenue by month, a segment bar chart, a cohort matrix using cohort and activity month, a funnel, and a product ranking by sales before refunds.
6. For A/B results, use the A-B Testing worksheet as a separate snapshot. Use the confidence interval and sample sizes next to the lift.

For a normalized PostgreSQL model use order_facts as the order fact, items as the line fact, and customers, products and campaigns as dimensions. Derive a calendar dimension from orders. Do not join line and order facts for aggregate revenue because it repeats order totals.

## Tableau Desktop or Public

Connect to Revenue.csv for a line chart with continuous MONTH([month]) and SUM([Net Revenue USD]). Define Net Revenue USD as [net_revenue] / 100. Use Products.csv for category and product rankings, Campaigns.csv for spend versus attributed revenue, and Segments.csv for customer mix. Add Cohorts.csv as a separate data source for a highlight table with retention_pct on Color. Use the date field's ISO format and set percentage display to match pre-scaled CSV fields. For example, 31.4 in retention_pct already represents 31.4%.

## Snowflake

The optional SQL loads the monthly Revenue CSV into a Snowflake staging area. In a dedicated demo account or database, run the DDL, upload Revenue.csv with SnowSQL, and run COPY and the view statements. The X-Small compute warehouse auto-suspends after one minute. Check credits and suspend when done. The PostgreSQL analytics use generate_series for dates and filtered aggregates. Translate those to a date dimension or GENERATOR and COUNT_IF when porting individual queries. COPY load history prevents ordinary duplicate file loads. Treat a refreshed window as a replacement and clear the dedicated target before reloading a changed snapshot.

Native Power BI and Tableau workbooks and Snowflake account execution were outside this environment.
