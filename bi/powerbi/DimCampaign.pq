let
    Source = LoadCsv("DimCampaign", {{"campaign_id", Int64.Type}, {"channel", type text}, {"spend", Int64.Type}, {"impressions", Int64.Type}, {"clicks", Int64.Type}})
in
    Source
