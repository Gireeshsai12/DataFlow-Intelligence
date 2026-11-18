let
    Source = LoadCsv("FactSession", {{"session_id", Int64.Type}, {"customer_id", Int64.Type}, {"date_key", type date}, {"variant", type text}, {"device", type text}, {"carts", Int64.Type}, {"conversions", Int64.Type}})
in
    Source
