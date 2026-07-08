# Data Dictionary: `houston_housing_market.csv`

Grain: one row per month per `market_area`. v1 contains a single market area
(`Houston, TX metro area`, Redfin's metro definition), 2012-01 through the most
recent available month.

| Column | Type | Unit / format | Source | Description |
|---|---|---|---|---|
| `month` | date | `YYYY-MM-01` | Redfin (base grain) | First day of the reporting month. |
| `market_area` | text | n/a | Redfin | Metro-area label; constant `"Houston, TX metro area"` in v1. |
| `closed_sales` | number | count | Redfin (`HOMES_SOLD`) | Homes sold in the month. |
| `pending_sales` | number | count | Redfin (`PENDING_SALES`) | Homes that went under contract in the month. |
| `active_listings` | number | count | Redfin (`INVENTORY`) | Active for-sale listings at month end. |
| `new_listings` | number | count | Redfin (`NEW_LISTINGS`) | New listings added during the month. |
| `months_inventory` | number | months | Redfin (`MONTHS_OF_SUPPLY`) | Months it would take to sell current inventory at the current sales pace. |
| `median_price` | number | USD | Redfin (`MEDIAN_SALE_PRICE`) | Median sale price for the month. |
| `days_on_market` | number | days | Redfin (`MEDIAN_DOM`) | Median days from listing to contract/sale. |
| `sale_to_list_ratio` | number | ratio | Redfin (`AVG_SALE_TO_LIST`) | Average sale price divided by list price (near 1.0 = selling near asking price). |
| `single_family_permits` | number | count | City of Houston Open Data | Single-family residential permits issued in the City of Houston jurisdiction that month. Null for months not yet published (see limitations). |
| `multi_family_permits` | number | count | City of Houston Open Data | Multi-family residential permits issued in the City of Houston jurisdiction that month. |
| `mortgage_rate_30yr` | number | percent | FRED `MORTGAGE30US` (Freddie Mac) | Monthly average of the weekly national 30-year fixed mortgage rate. |
| `zhvi_typical_home_value` | number | USD | Zillow Research (ZHVI) | Zillow's smoothed, seasonally adjusted typical home value for the Houston metro, distinct methodology from `median_price`. |
| `price_yoy_change` | number | fraction | Redfin (`MEDIAN_SALE_PRICE_YOY`) | Year-over-year change in `median_price`, as published directly by Redfin. |
| `sales_yoy_change` | number | fraction | Redfin (`HOMES_SOLD_YOY`) | Year-over-year change in `closed_sales`. |
| `inventory_yoy_change` | number | fraction | Redfin (`INVENTORY_YOY`) | Year-over-year change in `active_listings`. |
| `dom_yoy_change` | number | days (difference) | Redfin (`MEDIAN_DOM_YOY`) | Year-over-year change in `days_on_market`, in days. |
| `permit_yoy_change` | number | fraction | derived (City of Houston) | Year-over-year change in total residential permits (single-family + multi-family), computed as a 12-month percent change. |
| `affordability_pressure_index` | number | standardized score | derived | Composite score. See formula below. Higher = homes are relatively more expensive to finance compared to the rest of this dataset's own history. **Not an official or industry-standard index.** |
| `market_condition_score` | number | standardized score | derived | Composite score. See formula below. Positive = indicators point toward a relatively warmer (more seller-favorable) market vs. this dataset's own history; negative = relatively cooler (more buyer-favorable). **Not an official or industry-standard index.** |
| `market_condition_label` | text | `cooler` / `balanced` / `warmer` | derived | Simple, documented binning of `market_condition_score`. See thresholds below. |

## Composite metric formulas

Both composite metrics are z-score blends computed relative to this dataset's own
2012-present history. They describe how a given month compares to the rest of the
series, not to any external or industry benchmark. Full derivation and rationale are
in [`../methodology/README.md`](../methodology/README.md).

**`affordability_pressure_index`**
```
z_price = zscore(median_price)
z_rate  = zscore(mortgage_rate_30yr)
affordability_pressure_index = mean(z_price, z_rate)
```

**`market_condition_score`**
```
z_inv       = zscore(months_inventory)
z_dom       = zscore(days_on_market)
z_price_yoy = zscore(price_yoy_change)
z_sales_yoy = zscore(sales_yoy_change)
z_inv_yoy   = zscore(inventory_yoy_change)

market_condition_score = mean(z_price_yoy, z_sales_yoy, -z_inv, -z_dom, -z_inv_yoy)
```

**`market_condition_label` thresholds** (conservative, symmetric around zero):
- `score >= 0.5`  → `warmer`
- `score <= -0.5` → `cooler`
- otherwise       → `balanced`

## Known nulls

- `single_family_permits`, `multi_family_permits`, `permit_yoy_change` are null for the
  most recent months where the City of Houston permit workbook has not yet been updated
  (permits data currently runs through December 2025; Redfin data runs several months
  further). This is expected and documented, not a data-quality defect.
