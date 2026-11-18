import csv
from io import BytesIO, StringIO
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter

from app.metrics import QUERIES
from app.statistics import checkout_experiment, describe

SHEETS = {"Summary": "dashboard/summary", "Revenue": "revenue/trends",
          "Cohorts": "customers/cohorts", "Segments": "customers/segments",
          "Funnel": "marketing/funnel", "Campaigns": "marketing/campaigns",
          "Products": "products/performance", "Quality": "quality"}
MONEY = set("gross_revenue net_revenue refunds gross_profit average_order_value rolling_3_month_revenue average_observed_value spend attributed_revenue sales_before_refunds profit_before_refunds".split())


def export_rows(db, key, params):
    cursor = db.execute(QUERIES[key], params)
    return [col.name for col in cursor.description], cursor.fetchall()


def csv_data(columns, rows):
    stream = StringIO()
    writer = csv.DictWriter(stream, columns)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def workbook(db, params):
    book = Workbook()
    book.remove(book.active)
    datasets = {name: export_rows(db, key, params) for name, key in SHEETS.items()}
    arms = db.execute("""
      SELECT variant,count(*) AS n,count(*) FILTER(WHERE converted) AS x
      FROM sessions WHERE visited BETWEEN %(start)s AND %(end)s GROUP BY variant
    """,params)
    experiment = checkout_experiment({r["variant"]:(r["n"],r["x"]) for r in arms})
    datasets["A-B Testing"] = (list(experiment),[experiment])
    stats = describe([int(r["net_revenue"])/100 for r in datasets["Revenue"][1]])
    datasets["Revenue Statistics"] = (list(stats), [stats])
    raw = db.execute("""
      SELECT id AS order_id,customer_id,ordered,gross,sales,refund,cost
      FROM order_facts WHERE ordered BETWEEN %(start)s AND %(end)s ORDER BY id LIMIT 250
    """,params).fetchall()
    datasets["Raw Order Sample"] = (["order_id","customer_id","ordered","gross","sales","refund","cost"],raw)
    for name, (columns, rows) in datasets.items():
        sheet = book.create_sheet(name)
        sheet.append(columns)
        for row in rows:
            sheet.append([row[c]/Decimal(100) if c in MONEY and row[c] is not None else row[c]
                          for c in columns])
        for i, col in enumerate(columns, start=1):
            letter = get_column_letter(i)
            sheet.column_dimensions[letter].width = max(19, len(col)+3)
            cell = sheet.cell(1, i)
            cell.font = Font(color="FFFFFF", bold=True)
            cell.fill = PatternFill("solid", fgColor="17334B")
            if col in MONEY:
                for row in sheet.iter_rows(min_row=2, min_col=i, max_col=i):
                    row[0].number_format = '"$"#,##0.00'
        sheet.freeze_panes = "A2"
        if rows:
            table = Table(displayName="Data" + "".join(filter(str.isalnum,name)), ref=sheet.dimensions)
            table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
            sheet.add_table(table)
        if name == "Cohorts" and rows:
            sheet.conditional_formatting.add(f"E2:E{sheet.max_row}", ColorScaleRule(
                start_type="num",start_value=0,start_color="F4F7F5",
                end_type="num",end_value=100,end_color="56B697"))
        if name == "Revenue" and rows:
            chart = LineChart()
            chart.title = "Monthly net revenue (USD)"
            chart.add_data(Reference(sheet,min_col=2,min_row=1,max_row=sheet.max_row),titles_from_data=True)
            chart.set_categories(Reference(sheet,min_col=1,min_row=2,max_row=sheet.max_row))
            sheet.add_chart(chart,"G2")
    instructions = book.create_sheet("Instructions")
    for line in ("NovaCart Business Analysis", "Workbook analytics amounts are shown in USD.",
                 "Raw Order Sample and CSV monetary fields are integer cents.",
                 "In Excel, select Data → Get Data → From Text/CSV to import a report with Power Query.",
                 "To build a PivotTable, select the Raw Order Sample table and choose Insert → PivotTable.",
                 "Put ordered in Rows and sales in Values, then group by month.",
                 "Open in Excel to calculate the formula examples."):
        instructions.append([line])
    instructions.column_dimensions["A"].width = 95
    book.defined_names.add(DefinedName("MonthlyRevenue",attr_text=f"'Revenue'!$B$2:$B{book['Revenue'].max_row}"))
    instructions.append(["Reported monthly net revenue total", "=SUM(MonthlyRevenue)"])
    instructions.append(["Example date lookup", '=_xlfn.XLOOKUP(Revenue!A2,Revenue!A:A,Revenue!B:B,"Missing")'])
    dictionary = book.create_sheet("Data Dictionary")
    dictionary.append(["Table","Column","SQL type","Units"])
    for row in db.execute("""
      SELECT table_name,column_name,data_type FROM information_schema.columns
      WHERE table_schema='public' ORDER BY table_name,ordinal_position
    """):
        name = row["column_name"]
        units = "USD cents" if name in {"gross","sales","refund","cost","price","cents","unit_price","unit_cost","discount","spend"} else ""
        dictionary.append([row["table_name"], name, row["data_type"], units])
    for col in "ABCD":
        dictionary.column_dimensions[col].width = 24
    dictionary.freeze_panes = "A2"
    stream = BytesIO()
    book.save(stream)
    return stream.getvalue()
