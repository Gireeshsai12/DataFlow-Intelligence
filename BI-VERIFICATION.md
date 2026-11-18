# BI Edition verification

## Passed in this workspace

- Production frontend build from `npm ci` and `npm run build`.
- Six Python tests and five dbt data tests.
- Live PostgreSQL and FastAPI smoke checks covering 10 analytics routes, revenue reconciliation, data quality, the original Excel workbook and eight CSV exports.
- Live refresh authorization, background refresh, contention, pagination and restoration of the default dataset.
- Ten dashboard screens checked with Playwright, including date filters, the mobile viewport and Excel download.
- BI exporter at the default 2,500 orders and at 25,000 orders. Independent SQLite validation checked fact and dimension keys, accounting reconciliation, and checkout totals. Five SQL queries agreed across SQLite and PostgreSQL at both scales.
- The default snapshot was reloaded after the scale test. Bundled totals include 2,500 orders, $1,378,385.95 net revenue, 497 active customers, 6,000 synthetic sessions and 662 conversions.
- The five-slide briefing was exported to PPTX, rendered for visual review, and checked for slide and chart parts.
- Unix script syntax, YAML parsing, ZIP CRC and extracted snapshot checks.

The app ran natively on Linux for this revision. Docker Compose and PowerShell were unavailable here. The earlier release passed Docker Compose on Windows in the user's environment. Run the BI Edition's Docker smoke and export commands from its README to validate the new container path.

## External platforms

The Power BI Desktop deliverables are typed M queries, DAX, model design and report construction steps. A saved native PBIX is pending. The advanced Excel workbook generator requires desktop Excel and its local Power Query provider. The existing generated Excel workbook was verified in the API smoke check. The new native Excel script and workbook refresh are pending a Windows Excel run.

Tableau, Google Sheets, SQL Server, Snowflake, BigQuery, SAS, SPSS, Salesforce, GA4, Power Apps and Power Automate have exercises, scripts or import specs. Execution on those platforms is pending access to the corresponding applications or accounts. The NovaCart stakeholder case is simulated. Reviewer UAT is still a project task.
