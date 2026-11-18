# Advanced Excel workbook

With Microsoft 365 Excel for Windows installed and closed, run from the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\bi\excel\New-NovaCartWorkbook.ps1
```

The script uses local Excel automation to create live Power Query imports, formulas, a monthly PivotTable, a payment slicer and a chart. Keep the snapshot folder available so Excel can refresh the queries. To refresh data, run bi-export.ps1, then create the workbook with -Snapshot pointing to bi-output. In Excel choose Data → Refresh All. Verify the net revenue and order count after refresh, change the customer ID to test XLOOKUP, and use the payment slicer to check the pivot. The workbook generator requires desktop Excel with Power Query and XLOOKUP. Execution is unverified here.

If your Excel policy blocks automation, import FactOrder.csv and DimCustomer.csv with Data → Get Data → From Text/CSV. In the order query, type order_id and net_cents as whole numbers, date_key as date, and add month = Date.ToText([date_key], "yyyy-MM") and net_usd = [net_cents]/100. Load both queries as tables. Create a PivotTable from orders with month on rows, Sum of net_usd in values, and a payment slicer. Use XLOOKUP to retrieve region from the customer table. The original generated Excel workbook is available in reports as an immediately readable baseline.
