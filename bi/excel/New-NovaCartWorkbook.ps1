param(
    [string]$Snapshot = (Join-Path $PSScriptRoot '../../bi-sample'),
    [string]$Output = (Join-Path $PWD 'NovaCart-Advanced.xlsx')
)
$ErrorActionPreference = 'Stop'
$Snapshot = (Resolve-Path $Snapshot).Path
$Output = [IO.Path]::GetFullPath($Output)
if (Test-Path $Output) { throw "Output already exists. Supply a different -Output path." }
$excel = $null
$book = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.DisplayAlerts = $false
    $book = $excel.Workbooks.Add(-4167) # xlWBATWorksheet
    $summary = $book.Worksheets.Item(1)
    $summary.Name = 'KPI Summary'
    $prefix = $Snapshot.Replace('"','""') + [IO.Path]::DirectorySeparatorChar
    foreach ($spec in @(
        @{ Name='Orders'; Csv='FactOrder'; Types='{"order_id", Int64.Type},{"date_key", type date},{"customer_id", Int64.Type},{"net_cents", Int64.Type},{"profit_cents", Int64.Type}' },
        @{ Name='Customers'; Csv='DimCustomer'; Types='{"customer_id", Int64.Type},{"region", type text}' }
    )) {
        $name = $spec.Name
        $csv = $spec.Csv
        $types = $spec.Types
        $m = 'let Raw = Csv.Document(File.Contents("' + $prefix + $csv + '.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), Headers = Table.PromoteHeaders(Raw,[PromoteAllScalars=true]), Typed = Table.TransformColumnTypes(Headers, {' + $types + '}, "en-US")' + $(if ($name -eq 'Orders') { ', WithMonth = Table.AddColumn(Typed, "month", each Date.ToText([date_key], "yyyy-MM"), type text), WithUsd = Table.AddColumn(WithMonth,"net_usd",each [net_cents]/100, Currency.Type) in WithUsd' } else { ' in Typed' })
        $null = $book.Queries.Add($name,$m)
        $sheet = $book.Worksheets.Add()
        $sheet.Name = $name
        $source = 'OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=' + $name + ';Extended Properties=""'
        $table = $sheet.ListObjects.Add(0,$source,$null,1,$sheet.Range('A1'))
        $table.Name = $name + 'Data'
        $table.QueryTable.CommandType = 2
        $table.QueryTable.CommandText = 'SELECT * FROM [' + $name + ']'
        $null = $table.QueryTable.Refresh($false)
    }
    $summary.Range('A1').Value2 = 'NovaCart business review'
    $summary.Range('A3').Value2 = 'Orders'
    $summary.Range('B3').Formula2 = '=ROWS(OrdersData[order_id])'
    $summary.Range('A4').Value2 = 'Net revenue (USD)'
    $summary.Range('B4').Formula2 = '=SUM(OrdersData[net_cents])/100'
    $summary.Range('A5').Value2 = 'Gross profit (USD)'
    $summary.Range('B5').Formula2 = '=SUM(OrdersData[profit_cents])/100'
    $summary.Range('A7').Value2 = 'Look up customer ID'
    $summary.Range('B7').Value2 = 1.0
    $summary.Range('A8').Value2 = 'Customer region'
    $summary.Range('B8').Formula2 = '=XLOOKUP(B7,CustomersData[customer_id],CustomersData[region],"Unknown")'
    $summary.Range('B4:B5').NumberFormat = '"$"#,##0.00'
    $summary.Range('A1').Font.Bold = $true
    $summary.Range('A:A').ColumnWidth = 27
    $summary.Range('B:B').ColumnWidth = 18
    $pivotSheet = $book.Worksheets.Add()
    $pivotSheet.Name = 'Monthly Pivot'
    $cache = $book.PivotCaches().Create(1,'OrdersData')
    $pivot = $cache.CreatePivotTable($pivotSheet.Range('A3'),'MonthlyRevenue')
    $pivot.PivotFields('month').Orientation = 1
    $measure = $pivot.AddDataField($pivot.PivotFields('net_usd'),'Net revenue (USD)',-4157)
    $measure.NumberFormat = '"$"#,##0.00'
    $slicerCache = $book.SlicerCaches.Add2($pivot,'payment')
    $null = $slicerCache.Slicers.Add($pivotSheet,[Type]::Missing,'PaymentFilter','Payment',16,250,150,135)
    $chartBox = $pivotSheet.ChartObjects().Add(425,16,500,280)
    $chartBox.Chart.SetSourceData($pivot.TableRange1)
    $chartBox.Chart.ChartType = 4
    $chartBox.Chart.HasTitle = $true
    $chartBox.Chart.ChartTitle.Text = 'Monthly net revenue'
    $excel.CalculateFull()
    $manifest = Get-Content (Join-Path $Snapshot 'manifest.json') -Raw | ConvertFrom-Json
    if ([long]$summary.Range('B3').Value2 -ne [long]$manifest.totals.orders -or
        [math]::Round($summary.Range('B4').Value2 * 100) -ne $manifest.totals.net_cents) {
        throw 'Workbook order count or net revenue did not match the snapshot manifest.'
    }
    $null = $summary.Activate()
    $book.SaveAs($Output,51)
    Write-Output "Saved reconciled native workbook to $Output"
} finally {
    if ($null -ne $book) { $book.Close($false) }
    if ($null -ne $excel) { $excel.Quit() }
}
