let
    Source = LoadCsv("Cohorts", {{"cohort", type date}, {"activity_month", type date}, {"cohort_size", Int64.Type}, {"retained", Int64.Type}, {"retention_pct", type number}})
in
    Source
