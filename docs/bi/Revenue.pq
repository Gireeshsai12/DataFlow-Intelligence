let
    Source = Csv.Document(File.Contents(RevenueCsvPath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"month", type date}, {"net_revenue", Int64.Type},
        {"mom_pct", type number}, {"yoy_pct", type number}, {"rolling_3_month_revenue", Int64.Type}}, "en-US")
in
    Typed
