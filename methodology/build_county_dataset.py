"""
Build data/houston_county_submarkets.csv: county-level cut of the same Redfin
market tracker used for the metro-level v1 dataset, for the nine counties
Redfin assigns to the Houston, TX metro area.

Source: housing-market-data-research/raw/redfin_houston_counties_all_residential.tsv
(already filtered from Redfin's national county_market_tracker.tsv000.gz to
Houston-metro counties, All Residential property type, non-seasonally-adjusted).
"""
import pandas as pd

RAW = "../../housing-market-data-research/raw"
OUT = "../data/houston_county_submarkets.csv"

df = pd.read_csv(f"{RAW}/redfin_houston_counties_all_residential.tsv", sep="\t")
df["month"] = pd.to_datetime(df["PERIOD_BEGIN"]).values.astype("datetime64[M]")

df = df.rename(columns={
    "REGION": "county",
    "HOMES_SOLD": "closed_sales",
    "MEDIAN_SALE_PRICE": "median_price",
    "MEDIAN_DOM": "days_on_market",
    "INVENTORY": "active_listings",
    "MONTHS_OF_SUPPLY": "months_inventory",
    "MEDIAN_SALE_PRICE_YOY": "price_yoy_change",
    "HOMES_SOLD_YOY": "sales_yoy_change",
})
df["county"] = df["county"].str.replace(", TX", "", regex=False)

cols = [
    "month", "county", "closed_sales", "median_price", "active_listings",
    "months_inventory", "days_on_market", "price_yoy_change", "sales_yoy_change",
]
df = df[cols].sort_values(["county", "month"]).reset_index(drop=True)

# Price index (Jan 2012 = 100) per county, so counties with very different
# price levels (e.g. Harris vs. Austin County) can be compared on the same
# scale for relative appreciation.
def index_from_start(group):
    base = group.sort_values("month")["median_price"].iloc[0]
    group = group.copy()
    group["price_index_2012_base100"] = (group["median_price"] / base * 100).round(1)
    return group

df = df.groupby("county", group_keys=False)[df.columns].apply(index_from_start)
df = df.sort_values(["county", "month"]).reset_index(drop=True)

df["month"] = df["month"].dt.strftime("%Y-%m-%d")
df.to_csv(OUT, index=False)

print("Wrote", OUT)
print("Shape:", df.shape)
print("Counties:", sorted(df["county"].unique()))
print("Date range:", df["month"].min(), "to", df["month"].max())
