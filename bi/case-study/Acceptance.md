# NovaCart requirements and acceptance criteria

Scenario: a simulated business review for a synthetic retailer. Roles below
are personas used to define the review. No client or production impact is implied.

| User story | Acceptance criteria | Evidence |
|---|---|---|
| As a finance analyst, I need monthly net revenue by region to explain changes. | Full snapshot shows 2,500 orders and $1,378,385.95 net revenue. Regional slices sum to overall revenue. | manifest.json and expected/region_revenue.csv |
| As a product analyst, I need checkout completion by experiment arm to assess the redesign. | Session counts and conversions match both arms. Show absolute lift in percentage points and the confidence interval. | ExperimentArms.csv and Experiment.csv |
| As a retention analyst, I need a matrix that shows repeat purchase behavior by first order month. | Month zero is 100 percent, empty periods are zero only where elapsed, and the visual explains its denominator. | Cohorts.csv and expected/cohort_activity.csv |
| As a reporting owner, I need a repeatable refreshed export. | The CLI re-exports data, validates each grain and key and matches order totals. | python -m app.bi export and check |

For user acceptance testing, ask a reviewer to extract December revenue and
identify the larger checkout conversion rate without coaching. Record the tool,
steps, expected result, actual result, reviewer feedback and pass/fail. Test
slicers and a snapshot refresh after building the native Power BI and Excel
files. Local automated checks and reviewer UAT are separate evidence.
