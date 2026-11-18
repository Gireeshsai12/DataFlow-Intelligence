let
    Source = LoadCsv("DimCustomer", {{"customer_id", Int64.Type}, {"signup", type date}, {"region", type text}, {"channel", type text}, {"segment", type text}})
in
    Source
