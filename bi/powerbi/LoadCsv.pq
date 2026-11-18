// Create a blank Power Query named LoadCsv. Create SnapshotFolder as a Text parameter.
(name as text, columnTypes as list) as table =>
let
    Path = SnapshotFolder & (if Text.EndsWith(SnapshotFolder, "\") then "" else "\") & name & ".csv",
    Csv = Csv.Document(File.Contents(Path), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),
    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(Nulls, columnTypes, "en-US")
in
    Typed
