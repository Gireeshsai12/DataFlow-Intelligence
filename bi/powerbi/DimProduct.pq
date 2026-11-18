let
    Source = LoadCsv("DimProduct", {{"product_id", Int64.Type}, {"name", type text}, {"category", type text}, {"price", Int64.Type}, {"cost", Int64.Type}, {"stock", Int64.Type}})
in
    Source
