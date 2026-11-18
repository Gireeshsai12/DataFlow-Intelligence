# Optional business-platform exercises

## Tableau Desktop or Tableau Public

Connect to FactOrder.csv and DimCustomer.csv. Relate them on customer_id at
their native grains. Use date_key at continuous month level for the revenue
trend, region to show the revenue breakdown, and date and region filters.
Define `Net Revenue USD = SUM([net_cents])/100`. Put product performance on a
separate sheet connected to FactOrderLine and DimProduct. Compare regional
results to region_revenue.csv under bi-sample/expected and save the workbook.
Use only synthetic data with a public dashboard.

## GA4 audience reporting

In a GA4 demo property available to your account, open or build a Funnel
Exploration with session_start, add_to_cart and purchase. Record the date
range, population, sequence rules and device breakdown. Save a screenshot or
permitted CSV. Compare measurement definitions with DataFlow's independent
synthetic checkout sessions. Keep the two datasets distinct.

## Salesforce report

In a Salesforce practice org and using synthetic records, create an Opportunities
report grouped by Stage and Close Date. Add Sum of Amount, a count and a
filter for open opportunities. Build a dashboard component showing pipeline by
stage. Reconcile counts with the report's ungrouped detail export.

## Power Apps and Power Automate

In a sandbox, create a SharePoint list named Report Reviews with Title,
Reporting Month, Reviewer, Status, Net Revenue USD and Review Notes. Create a
canvas app to browse reviews, edit notes and submit to Pending. Configure a
flow triggered by a list change, with a trigger condition for Pending and an
empty Approval ID. Store an approval ID before waiting on a result. Set
Approved or Rejected from the approval outcome. Exercise duplicate trigger
handling and verify both approval paths. Keep test approvals within the
sandbox and use synthetic figures.

These exercises require the relevant platform and sign-in. Complete and capture
evidence in the tool before listing platform execution or dashboard authorship.
