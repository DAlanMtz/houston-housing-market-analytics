# Source Notes: all four public datasets

This file documents where each column in the four public datasets
(`houston_housing_market.csv`, `houston_housing_market_extended.csv`,
`houston_county_submarkets.csv`, and `houston_city_submarkets.csv`) comes
from, how it was accessed, and what license or attribution terms apply. It
reflects the data strategy selected during the discovery phase of this
project (Strategy B, modified): Redfin as the primary machine-readable
dataset, with FRED, City of Houston permits, and Zillow ZHVI as supporting
series, and HAR used only for narrative context, never as redistributed
structured data. The extended dataset adds six further public,
redistribution-safe sources; the county and city datasets reuse the Redfin
source at finer grains. See the relevant sections below for all three.

## Redfin Data Center (primary source)

- **What it provides**: `closed_sales`, `pending_sales`, `active_listings`,
  `new_listings`, `months_inventory`, `median_price`, `days_on_market`,
  `sale_to_list_ratio`, and the `_yoy_change` columns for price, sales, inventory,
  and days on market.
- **Access**: Public bulk download from the Redfin Data Center
  (`redfin.com/news/data-center`), metro-level market tracker file, filtered locally
  to `Houston, TX metro area`.
- **Geography**: Redfin's Houston metro definition (MSA-based). Broader than the
  City of Houston, and narrower and different than the HAR MLS coverage footprint.
- **Cadence**: Monthly (Redfin also publishes a weekly file; this project uses the
  monthly series).
- **Adjustment note**: Redfin publishes both seasonally adjusted and non-adjusted
  rows for every month. This dataset uses the non-seasonally-adjusted series
  (the raw, as-reported monthly figures).
- **License/attribution**: Redfin publishes this dataset for free public reuse
  through its Data Center. Attribute as "Redfin Data Center."

### Redfin Data Center, county grain (`houston_county_submarkets.csv` only)

- **What it provides**: the same fields as the metro-level Redfin source
  above (`closed_sales`, `median_price`, `active_listings`,
  `months_inventory`, `days_on_market`, and the `_yoy_change` columns), plus
  the derived `price_index_2012_base100`, at county grain instead of metro
  grain.
- **Access**: the same Redfin Data Center bulk download, county-level market
  tracker file, filtered locally to the nine counties Redfin's own
  `PARENT_METRO_REGION` field assigns to the Houston, TX metro area (Harris,
  Fort Bend, Montgomery, Galveston, Brazoria, Waller, Chambers, Liberty,
  Austin).
- **Geography**: individual counties within the Houston metro, per Redfin's
  own county boundary definitions.
- **Cadence and adjustment note**: same as the metro-level source (monthly,
  non-seasonally-adjusted).
- **License/attribution**: same as the metro-level source. Attribute as
  "Redfin Data Center."

### Redfin Data Center, city grain (`houston_city_submarkets.csv` only)

- **What it provides**: the same fields as the county-grain source above,
  plus a derived `avg_monthly_sales` and `thin_market` flag, at city grain
  instead of county grain.
- **Access**: the same Redfin Data Center bulk download, city-level market
  tracker file, filtered locally to every city Redfin's own
  `PARENT_METRO_REGION` field assigns to the Houston, TX metro area (165
  cities).
- **Geography**: individual cities within the Houston metro, per Redfin's
  own city boundary definitions, which do not always match municipal
  incorporated limits or Census-designated places.
- **Cadence and adjustment note**: same as the metro- and county-level
  sources (monthly, non-seasonally-adjusted).
- **License/attribution**: same as the metro-level source. Attribute as
  "Redfin Data Center."
- **Note on reliability**: 149 of 165 cities average under 50 sales a
  month and are flagged `thin_market` in the dataset. Redfin itself does
  not compute `months_inventory` or the `_yoy_change` columns for some of
  its thinnest markets, which shows up as nulls concentrated in flagged
  cities.

## FRED / Freddie Mac: `MORTGAGE30US`

- **What it provides**: `mortgage_rate_30yr`.
- **Access**: Federal Reserve Bank of St. Louis (FRED), series `MORTGAGE30US`,
  downloaded as weekly CSV and aggregated to a monthly average in this project's
  data pipeline.
- **Geography**: National. There is no Houston-specific mortgage-rate series, so
  this is included as macro context, not a local indicator.
- **Cadence**: Weekly at the source; aggregated to monthly here.
- **License/attribution**: Public data; the underlying source is Freddie Mac's
  Primary Mortgage Market Survey (PMMS), distributed via FRED. Attribute as
  "Freddie Mac via FRED (MORTGAGE30US)."

## City of Houston Open Data: Residential Building Permits

- **What it provides**: `single_family_permits`, `multi_family_permits`, and the
  derived `permit_yoy_change`.
- **Access**: City of Houston Open Data Portal, "Residential Building Permits by
  Month and Year" dataset, downloaded as an Excel workbook.
- **Geography**: City of Houston permitting jurisdiction only. This does not
  match the Redfin/Zillow metro footprint and is narrower than the full Houston
  metro area. Treated as a supply-side directional indicator, not a metro-wide count.
- **Cadence**: Monthly summary, built from weekly Houston Permitting Center reports.
- **License/attribution**: Public open-government data. Attribute as
  "City of Houston Open Data."

## Zillow Research: ZHVI (optional secondary price series)

- **What it provides**: `zhvi_typical_home_value`.
- **Access**: Zillow Research public data page, metro-level ZHVI (smoothed,
  seasonally adjusted, all-homes tier) CSV, filtered locally to the `Houston, TX`
  metro row.
- **Geography**: Zillow's Houston metro definition, comparable in scope to Redfin's
  but not necessarily identical boundary-for-boundary.
- **Cadence**: Monthly, released mid-month for the prior month.
- **Methodology note**: ZHVI is a smoothed "typical home value" index, not a median
  sale price. It's included as a secondary, methodologically distinct price trend
  for comparison, not a substitute for `median_price`.
- **License/attribution**: Zillow publishes ZHVI explicitly for free public research
  use. Attribute as "Zillow Research."

## HAR (Houston Association of REALTORS®): narrative context only

HAR's Monthly Housing Update is the most locally authoritative source for Greater
Houston MLS activity, but HAR's Terms of Use restrict site content to personal,
non-commercial use and prohibit reproducing, redistributing, republishing, or
reselling that content without prior written approval. Because of this, HAR data is
not included anywhere in `houston_housing_market.csv`, in any other CSV, or in any
other structured or machine-readable file in this repository.

If HAR figures are referenced anywhere in this project's written narrative (README,
case study), they are used only as a narrative citation, for example "HAR reported the
Houston-area single-family median price at $X in [month]," with a link to the
relevant public HAR.com page, never as a transcribed or redistributed dataset.

## Extended dataset sources (`houston_housing_market_extended.csv` only)

### FRED: WTI crude oil price (`MCOILWTICO`)

- **What it provides**: `wti_oil_price_usd_bbl`, `oil_price_yoy_change`.
- **Access**: FRED series `MCOILWTICO`, monthly CSV download, source is the U.S.
  Energy Information Administration.
- **Geography**: National (Cushing, Oklahoma delivery point). Included because
  Houston's economy is unusually energy-linked; this is macro context, not a
  local indicator.
- **Cadence**: Monthly.
- **License/attribution**: Public data. Attribute as "U.S. Energy Information
  Administration via FRED (MCOILWTICO)."

### FRED: Houston MSA unemployment rate and nonfarm payroll

- **What it provides**: `houston_unemployment_rate_pct` (series `HOUS448URN`),
  `houston_nonfarm_payroll_thousands` and derived `employment_yoy_change`
  (series `HOUS448NA`).
- **Access**: FRED, monthly CSV downloads. Underlying source is the Bureau of
  Labor Statistics (BLS) Local Area Unemployment Statistics and Current
  Employment Statistics programs.
- **Geography**: Houston-The Woodlands-Sugar Land / Houston-Pasadena-The
  Woodlands MSA (BLS's naming for this MSA has changed over time; both series
  cover the same metro area).
- **Cadence**: Monthly.
- **License/attribution**: Public data. Attribute as "U.S. Bureau of Labor
  Statistics via FRED (HOUS448URN, HOUS448NA)."

### Zillow Research: ZORI (rent index)

- **What it provides**: `zori_rent_index`, and the derived
  `price_to_annual_rent_ratio`.
- **Access**: Zillow Research public data page, metro-level ZORI (smoothed,
  seasonally adjusted) CSV, filtered locally to the `Houston, TX` metro row.
- **Geography**: Zillow's Houston metro definition, same convention as ZHVI.
- **Cadence**: Monthly, starting 2015-01 (Zillow does not publish ZORI before
  that date).
- **License/attribution**: Zillow publishes ZORI explicitly for free public
  research use. Attribute as "Zillow Research."

### FHFA: All-Transactions House Price Index (metro)

- **What it provides**: `fhfa_hpi_houston_metro`.
- **Access**: Federal Housing Finance Agency, public datasets page, metro-level
  All-Transactions HPI CSV, filtered locally to the
  `Houston-Pasadena-The Woodlands, TX` row (CBSA 26420).
- **Geography**: Houston-Pasadena-The Woodlands MSA (FHFA's current name for
  this CBSA; comparable to Redfin and Zillow's metro definition, not
  necessarily boundary-for-boundary identical).
- **Cadence**: Quarterly. Flat-filled to monthly in the extended dataset (each
  month in a quarter repeats that quarter's value; this is not an estimate of
  within-quarter movement). Typically lags the current quarter by a quarter or
  more.
- **License/attribution**: Public government data. Attribute as "FHFA House
  Price Index."

### FRED: Harris County median household income

- **What it provides**: `harris_county_median_household_income_usd`, and the
  derived `price_to_income_ratio`.
- **Access**: FRED series `MHITX48201A052NCEN`, annual CSV download. Underlying
  source is the U.S. Census Bureau.
- **Geography**: Harris County only, not the full Houston metro area. This is a
  narrower geography than every other source in this project.
- **Cadence**: Annual. Forward-filled to monthly in the extended dataset (each
  month in a year repeats that year's value); not extrapolated past the last
  published year (currently 2024).
- **License/attribution**: Public data. Attribute as "U.S. Census Bureau via
  FRED (MHITX48201A052NCEN)."

### FRED: Consumer Price Index (CPI-U)

- **What it provides**: `cpi_index`, and the derived `real_median_price` and
  `real_zori_rent_index`.
- **Access**: FRED series `CPIAUCSL`, monthly CSV download. Underlying source
  is the U.S. Bureau of Labor Statistics.
- **Geography**: National. No Houston-specific cost-of-living index was
  identified during this research pass, so nominal price and rent are deflated
  using the national rate rather than a local one.
- **Cadence**: Monthly.
- **License/attribution**: Public data. Attribute as "U.S. Bureau of Labor
  Statistics via FRED (CPIAUCSL)."

## Geography mismatch summary

| Source | Geography |
|---|---|
| Redfin, Zillow (ZHVI, ZORI), FHFA | Houston metro area (MSA/CBSA-based, comparable but not boundary-identical across providers) |
| Redfin county and city datasets | Individual counties and cities within the metro, per Redfin's own boundary definitions |
| City of Houston permits | City of Houston permitting jurisdiction (narrower than the metro) |
| Houston MSA unemployment and payroll | Houston MSA (BLS definition) |
| FRED mortgage rate, WTI oil price | National (no Houston-specific series exists for either) |
| Harris County median household income | Harris County only (narrower than the metro) |
| HAR (narrative only) | Greater Houston MLS coverage area (not identical to any of the above) |

These are overlapping but non-identical geographies. Cross-source comparisons in this
project are directional and contextual, not exact apples-to-apples joins.
