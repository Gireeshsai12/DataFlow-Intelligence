let
    Source = LoadCsv("FactOrder", {{"order_id", Int64.Type}, {"customer_id", Int64.Type}, {"date_key", type date}, {"campaign_id", Int64.Type}, {"gross_cents", Int64.Type}, {"sales_cents", Int64.Type}, {"refund_cents", Int64.Type}, {"net_cents", Int64.Type}, {"cost_cents", Int64.Type}, {"profit_cents", Int64.Type}, {"payment", type text}})
in
    Source
