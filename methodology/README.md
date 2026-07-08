# Methodology

This document explains how `data/houston_housing_market.csv` was built and how its
two composite indicators are calculated, so that every derived number in this project
is traceable back to a public source.

## 1. Data pipeline overview

Source: [`build_dataset.py`](build_dataset.py) in this folder, a documented,
step-by-step script (not run automatically as part of the notebook) that produces
the primary CSV from the four raw source files described in
[`../data/source_notes.md`](../data/source_notes.md).

Pipeline steps:

1. Load the Redfin Houston-metro "All Residential" monthly file.
2. Keep only the non-seasonally-adjusted rows (Redfin publishes both SA and
   non-SA versions of every month; this project standardizes on non-SA, as-reported
   figures).
3. Normalize `PERIOD_BEGIN` to a first-of-month date and rename Redfin's raw column
   names to the project's clean schema (see `../data/data_dictionary.md`).
4. Load the FRED `MORTGAGE30US` weekly series and aggregate to a monthly average.
5. Load the City of Houston residential permits workbook, clean the year/month
   fields, and derive a 12-month percent change (`permit_yoy_change`).
6. Load the Zillow ZHVI metro file (wide format, one column per month) and reshape
   it to a long, one-row-per-month series for the Houston metro.
7. Merge all four sources on `month`, using the Redfin monthly series as the base
   grain: a left join, so every row in the final dataset corresponds to a
   Redfin-reported month, with the other three sources filled in where available.
8. Compute the two composite indicators (below).
9. Round numeric columns for readability and write the final CSV.

Geography differences between sources (metro vs. city jurisdiction vs. national) are
not reconciled. They're documented in `../data/source_notes.md` and should be kept
in mind when interpreting any cross-source comparison.

## 2. Composite indicators: design principles

Both composite indicators in this dataset are intentionally simple and fully
disclosed:

- They are z-score blends of a small number of existing columns. There is no hidden
  weighting scheme and no proprietary methodology.
- They are computed relative to this dataset's own 2012-present history, not
  against any external benchmark, national index, or industry-standard scale.
  A score of 0 means "about average for this series." It does not mean "healthy"
  or "average nationally."
- They are not presented as official, industry-standard, or validated indices.
  They exist to support descriptive, at-a-glance trend reading, not as inputs to
  any real-world pricing or lending decision.

### `affordability_pressure_index`

Intuition: affordability pressure rises when home prices and mortgage rates are both
elevated relative to their own recent history, since both drive the effective cost of
financing a home purchase.

```
z_price = zscore(median_price)
z_rate  = zscore(mortgage_rate_30yr)
affordability_pressure_index = mean(z_price, z_rate)
```

### `market_condition_score`

Intuition: a market leans "warmer" (more seller-favorable) when prices and sales are
growing year-over-year while inventory and days-on-market are shrinking, and it leans
"cooler" (more buyer-favorable) in the opposite case.

```
z_inv       = zscore(months_inventory)
z_dom       = zscore(days_on_market)
z_price_yoy = zscore(price_yoy_change)
z_sales_yoy = zscore(sales_yoy_change)
z_inv_yoy   = zscore(inventory_yoy_change)

market_condition_score = mean(z_price_yoy, z_sales_yoy, -z_inv, -z_dom, -z_inv_yoy)
```

`market_condition_label` bins the score conservatively and symmetrically:

- `score >= 0.5` -> `warmer`
- `score <= -0.5` -> `cooler`
- otherwise -> `balanced`

## 3. What this methodology does and does not support

Supports: descriptive analysis, trend analysis, and relative market-condition
comparison across months within this dataset's own history.

Does not support: causal claims about what drives price, sales, or inventory
changes; predictions about future market direction; or comparisons against other
metros without rebuilding the z-scores on a combined dataset.

Revision risk: source data, especially recent months, is subject to revision
after initial publication. A given snapshot of this dataset will drift from the
live sources over time. Rebuild from fresh downloads for the most current figures.

## 4. Extended dataset: macro and affordability context

Source: [`build_extended_dataset.py`](build_extended_dataset.py), which loads
the already-built v1 CSV and left-joins six additional public sources, adding
macro and affordability context that v1 intentionally left out. v1 itself is
never modified; the result is written to
`data/houston_housing_market_extended.csv`. Column-by-column detail is in
[`../data/data_dictionary_extended.md`](../data/data_dictionary_extended.md)
and source access/license detail is in
[`../data/source_notes.md`](../data/source_notes.md).

Why these six: the v1 dataset can show market conditions moving, but has
little to explain why. Houston's economy is unusually energy-linked, so oil
price and local employment are natural demand-side additions; a second,
methodologically independent price index (FHFA) checks whether v1's price
trends could be a mix-shift artifact; income and rent data turn the existing
history-relative affordability index into something with a real denominator;
and CPI separates how much of the price trend is inflation versus real
appreciation.

Pipeline steps:

1. Load `data/houston_housing_market.csv` (v1) as the base.
2. Load the WTI oil price (FRED `MCOILWTICO`), a national monthly series.
3. Load Houston MSA unemployment rate and nonfarm payroll (FRED `HOUS448URN`,
   `HOUS448NA`), both monthly, and derive `employment_yoy_change`.
4. Load Zillow's ZORI rent index (Houston metro), reshape from wide to long,
   same pattern as v1's ZHVI handling.
5. Load the FHFA All-Transactions House Price Index (Houston metro), quarterly,
   and flat-fill it to monthly (each month in a quarter repeats that quarter's
   value; this is not an estimate of within-quarter movement).
6. Load Harris County median household income (FRED `MHITX48201A052NCEN`),
   annual, and forward-fill it to monthly within each observed year only, with
   no extrapolation past the last published year.
7. Load the national CPI-U (FRED `CPIAUCSL`), monthly.
8. Left-join all six onto the v1 base on `month`.
9. Compute derived columns: `price_to_income_ratio`, `price_to_annual_rent_ratio`,
   `absorption_rate_pct`, `new_to_closed_ratio`, `permit_single_family_share`,
   `oil_price_yoy_change`, `real_median_price`, `real_zori_rent_index`.
10. Round and write the extended CSV.

### New derived formulas

```
price_to_income_ratio = median_price / harris_county_median_household_income_usd
price_to_annual_rent_ratio = median_price / (zori_rent_index * 12)
absorption_rate_pct = closed_sales / active_listings * 100
new_to_closed_ratio = new_listings / closed_sales
permit_single_family_share = single_family_permits / (single_family_permits + multi_family_permits)
real_median_price = median_price * (latest_cpi_index / cpi_index)
real_zori_rent_index = zori_rent_index * (latest_cpi_index / cpi_index)
```

`real_median_price` and `real_zori_rent_index` deflate nominal price and rent
to constant dollars of the most recent month in the dataset, using national
CPI-U. This isolates how much of a nominal increase is inflation versus real
appreciation. No Houston-specific cost-of-living index was identified during
this research pass, so the deflator is national, not local.

`price_to_income_ratio` and `price_to_annual_rent_ratio` are standard, widely
used affordability lenses (years-of-income-to-buy, and price-relative-to-rent).
Unlike v1's `affordability_pressure_index`, they have real-world units and a
genuine denominator, at the cost of coarser update frequency (income is annual)
and a narrower geography (Harris County, not the full metro) for the income
figure specifically.

`absorption_rate_pct` and `new_to_closed_ratio` are not new indices, just
different arithmetic views of columns already in v1 (`closed_sales`,
`active_listings`, `new_listings`), included because they respond faster
month-to-month than `months_inventory`.

### What the extended dataset does and does not support

Supports: everything v1 supports, plus checking v1's price and market-condition
trends against an independent price index (FHFA), local employment context, and
income/rent-based affordability, instead of only history-relative measures.

Does not support: causal claims linking oil, employment, or rate changes to
housing outcomes. Co-movement between series (for example, oil price and sales
activity around 2015-2016) is a descriptive observation, not evidence that one
caused the other.

Extra limitations beyond v1: mixed source frequency (monthly, quarterly, and
annual sources are blended via flat-fill, not true interpolation), a narrower
geography for the income column (Harris County only), and two additional
sources (FHFA, income) that lag the current month more than v1's sources do.
Full detail: [`../data/data_dictionary_extended.md`](../data/data_dictionary_extended.md).

## 5. Formal causality testing and baseline forecast (R)

Source: [`r_analysis/granger_causality.R`](r_analysis/granger_causality.R)
and [`r_analysis/forecast_baseline.R`](r_analysis/forecast_baseline.R). This
is the one part of the project that uses R instead of Python, because
`lmtest::grangertest`, `tseries::adf.test`, and `forecast::ets` are the
standard, well-tested tools for these specific time-series tasks in applied
econometrics, with cleaner default output than the closest Python
equivalents. It's a small, self-contained addition, not a switch away from
Python for the rest of the project.

`granger_causality.R` tests whether the mortgage rate, oil price, or local
employment growth Granger-cause `sales_yoy_change`, at lag orders of 3, 6,
and 12 months. None of the four series involved passed a stationarity test
in their original form, so the headline results come from first-differenced
versions of each series, which all pass.

`forecast_baseline.R` produces a naive six-month-ahead ETS forecast of
`closed_sales` and `median_price`, with prediction intervals, as the
project's one deliberate exception to its otherwise descriptive-only stance.
It has no access to any of the macro variables studied elsewhere in this
project and is a mechanical baseline, not a business recommendation.

Full write-up, results tables, and interpretation caveats for both scripts:
[`r_analysis/README.md`](r_analysis/README.md).

To reproduce: `cd methodology/r_analysis && Rscript install_packages.R &&
Rscript granger_causality.R && Rscript forecast_baseline.R`.

## 6. County-level submarket dataset

Source: [`build_county_dataset.py`](build_county_dataset.py), which loads
the same Redfin bulk source used for v1, at county grain instead of metro
grain, filtered to the nine counties Redfin assigns to the Houston metro.
Writes `data/houston_county_submarkets.csv`. This does not touch v1 or the
extended dataset; it's a third, independent file built from the same
primary source.

Pipeline steps:

1. Load the Redfin county-level market tracker, filtered during research to
   Houston-metro counties, All Residential property type, non-seasonally-
   adjusted (same filtering convention as v1).
2. Rename columns to match v1's naming where the same concept applies.
3. Compute `price_index_2012_base100`: each county's `median_price` rebased
   to 100 in its own first observed month, so counties with very different
   price levels can be compared on relative appreciation.

Column detail: [`../data/data_dictionary_county.md`](../data/data_dictionary_county.md).
