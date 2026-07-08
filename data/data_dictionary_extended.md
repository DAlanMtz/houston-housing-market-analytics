# Data Dictionary: `houston_housing_market_extended.csv`

This is a separate, additive dataset built on top of `houston_housing_market.csv`
(v1). It left-joins v1 with six new public sources and adds a handful of derived
columns. v1 is unchanged and still documented in `data_dictionary.md`; this file
only covers the new columns.

Grain: same as v1, one row per month per `market_area`, 2012-01 through the most
recent available month. All v1 columns are present unchanged; only the additions
are listed below.

## New source columns

| Column | Type | Unit | Source | Geography | Cadence | Description |
|---|---|---|---|---|---|---|
| `wti_oil_price_usd_bbl` | number | USD per barrel | FRED `MCOILWTICO` | National | Monthly | West Texas Intermediate crude oil spot price. Included because Houston's economy is unusually energy-linked; not a Houston-specific series. |
| `houston_unemployment_rate_pct` | number | percent | FRED `HOUS448URN` | Houston-The Woodlands-Sugar Land MSA | Monthly | Local unemployment rate. |
| `houston_nonfarm_payroll_thousands` | number | thousands of jobs | FRED `HOUS448NA` | Houston-Pasadena-The Woodlands MSA | Monthly | Total nonfarm payroll employment. |
| `employment_yoy_change` | number | fraction | derived | same as above | Monthly | Year-over-year percent change in `houston_nonfarm_payroll_thousands`. |
| `zori_rent_index` | number | USD/month | Zillow Research (ZORI) | Houston, TX metro | Monthly | Zillow Observed Rent Index, a smoothed typical asking-rent measure. Starts 2015-01; null before that. |
| `fhfa_hpi_houston_metro` | number | index (base-period = 100 at the metro's own start) | FHFA All-Transactions HPI | Houston-Pasadena-The Woodlands MSA | Quarterly, flat-filled to monthly | A repeat-sales/appraisal-based price index, methodologically independent of Redfin's median and Zillow's ZHVI. Each month within a quarter repeats that quarter's value; this is a flat-fill, not an interpolation of within-quarter movement. Null for the most recent 1-2 months where FHFA hasn't yet published the current quarter. |
| `harris_county_median_household_income_usd` | number | USD | FRED `MHITX48201A052NCEN` (Census-derived) | Harris County | Annual, forward-filled to monthly | Same annual value repeated across all 12 months of its year. Not extrapolated past the last published year (currently 2024); later months are null rather than guessed. |
| `cpi_index` | number | index (1982-84 = 100) | FRED `CPIAUCSL` | National | Monthly | Consumer Price Index for All Urban Consumers. Used to deflate nominal price and rent into constant dollars; not a Houston-specific cost-of-living measure. |

## New derived columns

| Column | Type | Unit | Description |
|---|---|---|---|
| `price_to_income_ratio` | number | ratio | `median_price / harris_county_median_household_income_usd`. Roughly, how many years of the typical Harris County household's income it would take to buy the median-priced home. A standard, simple affordability lens, distinct from the income-free, history-relative `affordability_pressure_index` in v1. Null wherever income data is unavailable (see above). |
| `price_to_annual_rent_ratio` | number | ratio | `median_price / (zori_rent_index * 12)`. A standard buy-vs-rent economics signal; higher values suggest buying is expensive relative to renting the same market. Null before 2015-01 (ZORI's start). |
| `absorption_rate_pct` | number | percent | `closed_sales / active_listings * 100`. Share of the current listing inventory that sold in the month. A more responsive, differently scaled view of supply-demand balance than `months_inventory` (roughly its inverse). |
| `new_to_closed_ratio` | number | ratio | `new_listings / closed_sales`. Above 1 means new supply is entering faster than homes are selling (building inventory pressure); below 1 means the market is absorbing supply faster than it's added. |
| `permit_single_family_share` | number | fraction | `single_family_permits / (single_family_permits + multi_family_permits)`. Share of City of Houston residential permits that are single-family, as a rough proxy for owner-occupied vs. rental-oriented new supply. Null wherever permit data is unavailable. |
| `oil_price_yoy_change` | number | fraction | Year-over-year percent change in `wti_oil_price_usd_bbl`. |
| `real_median_price` | number | USD, constant dollars of the most recent month | `median_price * (latest_cpi / cpi_index)`. Nominal median price deflated to what it would cost in the most recent month's dollars, so early- and late-period prices can be compared without inflation distorting the comparison. |
| `real_zori_rent_index` | number | USD/month, constant dollars of the most recent month | Same deflation applied to `zori_rent_index`. Null before 2015-01 (ZORI's start). |

## Why these are a separate file, not new columns bolted onto v1

`houston_housing_market.csv` (v1) is documented, cited in the case study, and used
by `market_condition_score` and `affordability_pressure_index` with fixed,
published formulas. Extending it in place would risk silently changing what a
"v1 row" means for anyone already relying on it. Keeping the extension in its own
file means v1 stays exactly as documented, while this file can evolve independently.

## Limitations specific to these columns

- **Geography varies more here than in v1.** WTI oil is national, unemployment
  and payroll are MSA-level, income is county-level (Harris County only, not the
  full metro), and rent/HPI are metro-level. None of these share an identical
  boundary with each other or with Redfin's metro definition. See
  `source_notes.md` for the full geography table.
- **Mixed native frequency.** Only oil, unemployment, payroll, and rent are
  natively monthly. HPI is quarterly (flat-filled) and income is annual
  (flat-filled). Treat month-to-month movement in `fhfa_hpi_houston_metro` and
  `harris_county_median_household_income_usd` as an artifact of the fill, not a
  real monthly change.
- **Income and HPI both lag.** Income data currently ends in 2024; HPI typically
  lags the current quarter by a quarter or more. Both are null for the most
  recent months rather than being extrapolated forward.
