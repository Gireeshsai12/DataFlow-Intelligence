let
    Source = LoadCsv("Segments", {{"segment", type text}, {"customers", Int64.Type}, {"orders", Int64.Type}, {"average_observed_value", type number}, {"repeat_customers", Int64.Type}})
in
    Source
