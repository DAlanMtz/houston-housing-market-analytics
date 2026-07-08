"""
Build data/houston_housing_market.csv from raw research sources.

Sources (all in housing-market-data-research/raw/):
- redfin_houston_metro_all_residential.tsv  -> primary monthly grain (Redfin metro)
- fred_mortgage30us.csv                     -> weekly 30yr mortgage rate, aggregated to monthly avg
- houston_residential_permits.xlsx          -> City of Houston monthly permit counts
- zillow_zhvi_houston_metro.csv             -> wide monthly ZHVI, reshaped to long

Output grain: one row per month for "Houston, TX metro area" (Redfin's metro definition).
HAR is not used as structured data anywhere in this script (see data/source_notes.md).

This repo ships the finished CSV (data/houston_housing_market.csv), not the raw
source files, to keep the repo small and avoid redistributing large upstream
files unnecessarily. To re-run this script from scratch, download the four raw
files listed above per the instructions in data/source_notes.md, place them in
a local `raw/` folder, and point RAW at that folder (run from methodology/, or
adjust the relative paths below to your own layout).
"""
import pandas as pd
import numpy as np
import openpyxl

RAW = "../../housing-market-data-research/raw"  # local raw-file folder, see docstring above
OUT = "../data/houston_housing_market.csv"

# ---------------------------------------------------------------------------
# 1-3. Redfin: load, normalize month, rename to project column names
# ---------------------------------------------------------------------------
redfin = pd.read_csv(f"{RAW}/redfin_houston_metro_all_residential.tsv", sep="\t")
# Redfin publishes both seasonally-adjusted and non-adjusted rows for every
# month; keep the non-adjusted (raw, reported) series for consistency with
# how HAR and most public dashboards report monthly figures.
redfin = redfin[redfin["IS_SEASONALLY_ADJUSTED"] == False].copy()
redfin["month"] = pd.to_datetime(redfin["PERIOD_BEGIN"]).values.astype("datetime64[M]")

redfin = redfin.rename(columns={
    "HOMES_SOLD": "closed_sales",
    "PENDING_SALES": "pending_sales",
    "INVENTORY": "active_listings",
    "NEW_LISTINGS": "new_listings",
    "MONTHS_OF_SUPPLY": "months_inventory",
    "MEDIAN_SALE_PRICE": "median_price",
    "MEDIAN_DOM": "days_on_market",
    "AVG_SALE_TO_LIST": "sale_to_list_ratio",
    "MEDIAN_SALE_PRICE_YOY": "price_yoy_change",
    "HOMES_SOLD_YOY": "sales_yoy_change",
    "INVENTORY_YOY": "inventory_yoy_change",
    "MEDIAN_DOM_YOY": "dom_yoy_change",
})
redfin["market_area"] = "Houston, TX metro area"

redfin_cols = [
    "month", "market_area", "closed_sales", "pending_sales", "active_listings",
    "new_listings", "months_inventory", "median_price", "days_on_market",
    "sale_to_list_ratio", "price_yoy_change", "sales_yoy_change",
    "inventory_yoy_change", "dom_yoy_change",
]
redfin = redfin[redfin_cols].sort_values("month").reset_index(drop=True)

# ---------------------------------------------------------------------------
# 4-5. FRED: load weekly, aggregate to monthly average
# ---------------------------------------------------------------------------
fred = pd.read_csv(f"{RAW}/fred_mortgage30us.csv")
fred["observation_date"] = pd.to_datetime(fred["observation_date"])
fred["MORTGAGE30US"] = pd.to_numeric(fred["MORTGAGE30US"], errors="coerce")
fred["month"] = fred["observation_date"].values.astype("datetime64[M]")
fred_monthly = (
    fred.groupby("month", as_index=False)["MORTGAGE30US"]
    .mean()
    .rename(columns={"MORTGAGE30US": "mortgage_rate_30yr"})
)
fred_monthly["mortgage_rate_30yr"] = fred_monthly["mortgage_rate_30yr"].round(3)

# ---------------------------------------------------------------------------
# 6-7. City of Houston permits: load, clean, monthly counts, YoY
# ---------------------------------------------------------------------------
wb = openpyxl.load_workbook(f"{RAW}/houston_residential_permits.xlsx", data_only=True)
ws = wb["Permits"]
rows = list(ws.iter_rows(values_only=True))
header, body = rows[0], rows[1:]
permits = pd.DataFrame(body, columns=header)
permits = permits.rename(columns={
    "Year": "year", "Month": "month_num",
    "Single Family": "single_family_permits", "Multi-Family": "multi_family_permits",
})
permits = permits.dropna(subset=["year", "month_num"])
permits["month"] = pd.to_datetime(
    dict(year=permits["year"].astype(int), month=permits["month_num"].astype(int), day=1)
)
permits = permits[["month", "single_family_permits", "multi_family_permits"]].sort_values("month")
permits["total_residential_permits"] = (
    permits["single_family_permits"] + permits["multi_family_permits"]
)
permits["permit_yoy_change"] = permits["total_residential_permits"].pct_change(periods=12).round(4)
permits = permits.drop(columns=["total_residential_permits"])

# ---------------------------------------------------------------------------
# 8-9. Zillow ZHVI: load wide, reshape to long, keep monthly value
# ---------------------------------------------------------------------------
zhvi_wide = pd.read_csv(f"{RAW}/zillow_zhvi_houston_metro.csv")
date_cols = [c for c in zhvi_wide.columns if c[:2] in ("19", "20")]
zhvi_long = zhvi_wide.melt(
    id_vars=["RegionName"], value_vars=date_cols,
    var_name="raw_date", value_name="zhvi_typical_home_value",
)
zhvi_long["month"] = pd.to_datetime(zhvi_long["raw_date"]).values.astype("datetime64[M]")
zhvi_long = zhvi_long[["month", "zhvi_typical_home_value"]].sort_values("month").reset_index(drop=True)

# ---------------------------------------------------------------------------
# 10-11. Merge all sources on month, Redfin metro is the base/main grain
# ---------------------------------------------------------------------------
df = redfin.merge(fred_monthly, on="month", how="left")
df = df.merge(permits, on="month", how="left")
df = df.merge(zhvi_long, on="month", how="left")

# ---------------------------------------------------------------------------
# 13. Composite metrics
# ---------------------------------------------------------------------------
def zscore(s):
    return (s - s.mean(skipna=True)) / s.std(skipna=True)

# Affordability pressure index: relative-to-own-history z-score blend of
# median price and mortgage rate. Higher = homes are relatively more
# expensive to finance compared to the rest of this dataset's own history.
# This is NOT a standardized/official affordability index.
z_price = zscore(df["median_price"])
z_rate = zscore(df["mortgage_rate_30yr"])
df["affordability_pressure_index"] = ((z_price + z_rate) / 2).round(3)

# Market condition score: simple, transparent composite of five standardized
# signals. Positive = indicators point toward a relatively warmer (more
# seller-favorable) market than this dataset's own history; negative =
# relatively cooler (more buyer-favorable). Not an official/industry index.
z_inv = zscore(df["months_inventory"])
z_dom = zscore(df["days_on_market"])
z_price_yoy = zscore(df["price_yoy_change"])
z_sales_yoy = zscore(df["sales_yoy_change"])
z_inv_yoy = zscore(df["inventory_yoy_change"])

df["market_condition_score"] = (
    (z_price_yoy + z_sales_yoy - z_inv - z_dom - z_inv_yoy) / 5
).round(3)

def label_condition(score):
    if pd.isna(score):
        return np.nan
    if score >= 0.5:
        return "warmer"
    if score <= -0.5:
        return "cooler"
    return "balanced"

df["market_condition_label"] = df["market_condition_score"].apply(label_condition)

# ---------------------------------------------------------------------------
# Final column order per proposed v1 schema
# ---------------------------------------------------------------------------
final_cols = [
    "month", "market_area", "closed_sales", "pending_sales", "active_listings",
    "new_listings", "months_inventory", "median_price", "days_on_market",
    "sale_to_list_ratio", "single_family_permits", "multi_family_permits",
    "mortgage_rate_30yr", "zhvi_typical_home_value", "price_yoy_change",
    "sales_yoy_change", "inventory_yoy_change", "dom_yoy_change",
    "permit_yoy_change", "affordability_pressure_index", "market_condition_score",
    "market_condition_label",
]
df = df[final_cols].sort_values("month").reset_index(drop=True)

round2 = ["median_price", "months_inventory", "days_on_market", "zhvi_typical_home_value"]
round4 = [
    "sale_to_list_ratio", "price_yoy_change", "sales_yoy_change",
    "inventory_yoy_change", "permit_yoy_change",
]
for c in round2:
    df[c] = df[c].round(2)
for c in round4:
    df[c] = df[c].round(4)
df["dom_yoy_change"] = df["dom_yoy_change"].round(0)

df["month"] = df["month"].dt.strftime("%Y-%m-%d")

df.to_csv(OUT, index=False)
print("Wrote", OUT)
print("Shape:", df.shape)
print("Date range:", df["month"].min(), "to", df["month"].max())
print(df.isna().sum())
