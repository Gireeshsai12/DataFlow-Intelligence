# Google Sheets revenue and checkout tracker

Import FactOrder.csv, DimCustomer.csv, DimDate.csv and FactSession.csv as
separate sheets with those exact names. Turn on conversion to numbers and dates
during import. Add an Analysis sheet.

Place this in Analysis!A1 to group net revenue by payment type:

```
=QUERY(FactOrder!A1:K,"select K,count(A),sum(H) where A is not null group by K label K 'Payment',count(A) 'Orders',sum(H) 'Net cents'",1)
```

Put this in Analysis!D1 for a live display column, then set it to USD format:

```
={"Net revenue (USD)";ARRAYFORMULA(IF(C2:C="","",C2:C/100))}
```

Add checkout analysis on a different tab:

```
=QUERY(FactSession!A1:G,"select D,count(A),sum(F),sum(G) where A is not null group by D label count(A) 'Sessions',sum(F) 'Carts',sum(G) 'Conversions'",1)
```

Use a bar chart for net revenue by payment, and compare SUM(Analysis!D2:D)
and the order count with manifest.json. Verify 6,000 sessions and 662
conversions across the two variants for the bundled snapshot. These formulas
use English locale separators. Google Sheets execution was not performed here.
