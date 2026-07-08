# Data Dictionary: `houston_city_submarkets.csv`

A fourth, independent dataset. Same source and property-type scope as v1 and
the county dataset (Redfin Data Center, All Residential, non-seasonally-
adjusted), at city grain instead of metro or county grain, for every city
Redfin assigns to the Houston, TX metro area. Does not modify v1, the
extended dataset, or the county dataset.

Grain: one row per month per `city`, 2012-01 through the most recent
available month, for 165 cities.

| Column | Type | Unit | Description |
|---|---|---|---|
| `month` | date | `YYYY-MM-01` | First day of the reporting month. |
| `city` | text | | City name, e.g. `"Houston"`, `"Katy"`. Redfin's own city boundary, not necessarily identical to municipal or Census city limits. |
| `closed_sales` | number | count | Homes sold in the city that month. |
| `median_price` | number | USD | Median sale price for the city that month. |
| `active_listings` | number | count | Active for-sale listings at month end. |
| `months_inventory` | number | months | Months of supply at the current sales pace. Null for some low-volume city-months; see Limitations. |
| `days_on_market` | number | days | Median days from listing to sale. |
| `price_yoy_change` | number | fraction | Year-over-year change in `median_price`, as published directly by Redfin. Null where Redfin does not compute it for a thin market. |
| `sales_yoy_change` | number | fraction | Year-over-year change in `closed_sales`. Same null pattern as above. |
| `price_index_2012_base100` | number | index | `median_price` rebased so each city's own first observed month equals 100. Makes cities at very different price levels comparable on relative appreciation. |
| `avg_monthly_sales` | number | count | Each city's average `closed_sales` across its full history. A fixed reference value repeated on every row for that city, used to build the `thin_market` flag. |
| `thin_market` | boolean | | `true` when `avg_monthly_sales` is below 50. 149 of the 165 cities are flagged. Flagged cities are included in the dataset for completeness but are unreliable for month-to-month reading; see the case study for a concrete illustration. |

## Why a separate file

Same reasoning as the county dataset: v1 is documented and cited with fixed
column meanings, so a finer grain goes in its own file rather than changing
what a v1 row means.

## Limitations

- 149 of 165 cities (90%) are flagged `thin_market`. Redfin itself does not
  always compute `months_inventory`, `price_yoy_change`, or `sales_yoy_change`
  for its thinnest markets, which is why those columns have nulls
  concentrated almost entirely in flagged cities.
- Redfin's city boundaries are its own definitions and do not always match
  municipal incorporated limits or Census-designated places.
- Same source limitations as v1 and the county dataset: non-seasonally-
  adjusted Redfin data and revision risk on recent months. Full detail:
  `source_notes.md`.
- No causal claims. This dataset describes differences between cities; it
  does not explain why they exist.
