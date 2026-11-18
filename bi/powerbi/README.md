# Build the native Power BI report

1. In Power BI Desktop, open a blank report and select **Transform data**. Create a Text parameter named SnapshotFolder with the absolute path to bi-sample (or a refreshed bi-output directory). Use the supplied LoadCsv.pq in a blank query named LoadCsv. Then paste each remaining .pq file into a query named after the file. Apply changes.
2. In Model view, add the relationships below as one-to-many with single direction from the dimension. Mark DimDate as a date table using date_key. Hide foreign keys and cents columns from the report view once measures exist.
3. Add each expression in Measures.dax individually as a measure using **New measure**. Format USD as currency and ratios as percentages. Set the date hierarchy explicitly or use year_month sorted ascending.
4. Build the pages below. Save as NovaCart.pbix and reopen before calling the Desktop build verified.

| Dimension key | Fact keys |
|---|---|
| DimDate[date_key] | FactOrder[date_key], FactOrderLine[date_key], FactSession[date_key] |
| DimCustomer[customer_id] | FactOrder[customer_id], FactOrderLine[customer_id], FactSession[customer_id] |
| DimProduct[product_id] | FactOrderLine[product_id] |
| DimCampaign[campaign_id] | FactOrder[campaign_id] |

| Page | Visuals and filters |
|---|---|
| Executive Sales | Net Revenue, Orders, Average Order Value and Gross Margin cards. Monthly revenue and MoM Growth. Date and region slicers scoped to applicable visuals. |
| Retention | Cohort month and activity month matrix with Cohort Retention and conditional formatting. Suppress totals. This snapshot has its own cohort filters. |
| Checkout Funnel | Sessions, Carts, Conversions and Cart Abandonment Rate cards. Compare Conversion Rate by variant. Use date and device as filters. |
| RFM | Customer and repeat-rate cards with customers by segment. This snapshot has its own segment filter. |
| Products | Line Sales Before Refunds and Units Sold by category. Category and date slicers. |

FactOrder is one row per order. FactOrderLine is one row per order/product and is used for product performance before refunds. Sessions contain anonymous traffic. A customer slicer excludes anonymous sessions while active. Cohorts and Segments are precomputed snapshots and should remain disconnected. Select full calendar months for MoM and YoY comparisons.

For acceptance, compare the default Excel and Power BI totals to bi-sample/manifest.json, check a regional slice using the cross-platform SQL exercise, compare conversion counts by variant, and confirm that the date filter does not change disconnected snapshot visuals. Test one refresh after changing SnapshotFolder to a regenerated export. Save screenshots of the checks. The package supplies model data, M queries, DAX and these build steps. Power BI Desktop execution is pending.
