# Reproduce the analytics in other SQL engines

Run the statements in this directory against the seven fact and dimension tables.
Run each statement separately. Check results against the locally generated
`bi-sample/expected` CSVs. Dates use ISO text on disk. Use DATE columns in
warehouse imports and BIGINT for IDs, counts and cents, to preserve accuracy.

## SQL Server / T-SQL

In SSMS, create a scratch database. Import the fact and dimension CSVs from
`bi-sample` via the Import Flat File wizard. Name each table exactly after the
CSV stem, choose nullable customer_id for FactSession and nullable campaign_id
for FactOrder, and check the types against the Power Query files in ../powerbi.
Use dbo and the scratch database when running the queries. Compare the revenue,
cohort, product, region and experiment outputs to the expected CSVs. For a T-SQL
exercise, use `TRY_CONVERT(date, date_key, 23)` on a text staging table and check
that the count of rejected date keys is zero. For the optional larger run,
compare actual execution plans and `SET STATISTICS IO ON` before and after an
index on FactOrder(date_key, customer_id) INCLUDE (net_cents, profit_cents).

## Snowflake

In a sandbox with an approved warehouse and an existing database/schema, use
Snowsight Load Data or the provided optional stage example in
`warehouse/snowflake/setup.sql`. Load the CSVs to tables named after the file
stems. Use NUMBER(19,0) for cents, DATE for date keys, and explicit types for
empty values. Select your scratch schema and a small auto-suspending warehouse.
Run the shared SQL and compare to expected outputs. The original stage example
is for the monthly Revenue.csv export.

## BigQuery

In a scratch dataset, upload the CSVs using Create table. Specify the schema
explicitly or verify CSV schema detection. Represent cents as INT64 and dates
as DATE. Qualify table references with your project/dataset, or set the dataset
as default. Run the shared SQL and compare to expected outputs. Check bytes
processed before running queries if billing is enabled.

All five queries were run locally against the same snapshot in SQLite and
PostgreSQL. SQL Server, Snowflake and BigQuery execution requires a target
environment.
