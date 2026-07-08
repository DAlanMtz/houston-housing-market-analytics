# Data Dictionary: `houston_county_submarkets.csv`

A third, additive dataset. Same source and property-type scope as v1 (Redfin
Data Center, All Residential, non-seasonally-adjusted), but at the county
grain instead of the metro grain, for the nine counties Redfin assigns to the
Houston, TX metro area. Does not modify v1 or the extended dataset.

Grain: one row per month per `county`, 2012-01 through the most recent
available month, for Harris, Fort Bend, Montgomery, Galveston, Brazoria,
Waller, Chambers, Liberty, and Austin counties.

| Column | Type | Unit | Description |
|---|---|---|---|
| `month` | date | `YYYY-MM-01` | First day of the reporting month. |
| `county` | text | | County name, e.g. `"Harris County"`. |
| `closed_sales` | number | count | Homes sold in the county that month. |
| `median_price` | number | USD | Median sale price for the county that month. |
| `active_listings` | number | count | Active for-sale listings at month end. |
| `months_inventory` | number | months | Months of supply at the current sales pace. |
| `days_on_market` | number | days | Median days from listing to sale. |
| `price_yoy_change` | number | fraction | Year-over-year change in `median_price`, as published directly by Redfin. |
| `sales_yoy_change` | number | fraction | Year-over-year change in `closed_sales`. |
| `price_index_2012_base100` | number | index | `median_price` rebased so each county's own January 2012 value equals 100. Makes counties with very different price levels comparable on relative appreciation. |

## Why a separate file

Same reasoning as the extended dataset: v1 is documented and cited with fixed
column meanings, so a different grain (county instead of metro) goes in its
own file rather than changing what a v1 row means.

## Limitations

- Four of the nine counties (Waller, Chambers, Liberty, Austin) average
  under 80 sales a month across the full period. Month-to-month figures for
  these counties are noisy; `price_index_2012_base100` in particular can
  swing to extreme values for these counties from ordinary small-sample
  variation, not real appreciation. See
  `case-study/county_submarkets_and_forecast.md` for a concrete example
  (Liberty County reaches an index value of 421.9 in the most recent month).
- Same source limitations as v1: non-seasonally-adjusted Redfin data,
  Redfin's own county boundary definitions, and revision risk on recent
  months. Full detail: `source_notes.md`.
- No causal claims. This dataset describes differences between counties; it
  does not explain why they exist.
