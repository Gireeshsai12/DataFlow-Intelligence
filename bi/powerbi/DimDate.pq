let
    Source = LoadCsv("DimDate", {{"date_key", type date}, {"year", Int64.Type}, {"month_number", Int64.Type}, {"year_month", type text}})
in
    Source
