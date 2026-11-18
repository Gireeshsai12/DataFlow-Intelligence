let
    Source = LoadCsv("FactOrderLine", {{"order_id", Int64.Type}, {"product_id", Int64.Type}, {"date_key", type date}, {"customer_id", Int64.Type}, {"quantity", Int64.Type}, {"sales_cents", Int64.Type}, {"cost_cents", Int64.Type}})
in
    Source
