"""
Build data/houston_city_submarkets.csv: city-level cut of the same Redfin
market tracker used for the metro-level (v1) and county-level datasets, for
every city Redfin assigns to the Houston, TX metro area.

Source: housing-market-data-research/raw/redfin_houston_cities_all_residential.tsv
(already filtered from Redfin's national city_market_tracker.tsv000.gz to
Houston-metro cities, All Residential property type, non-seasonally-adjusted).

This is a fourth, independent dataset. It does not modify v1, the extended
dataset, or the county dataset.
"""
import pandas as pd

RAW = "../../housing-market-data-research/raw"
OUT = "../data/houston_city_submarkets.csv"

THIN_THRESHOLD = 50  # avg monthly closed sales below this = flagged thin

df = pd.read_csv(f"{RAW}/redfin_houston_cities_all_residential.tsv", sep="\t")
df["month"] = pd.to_datetime(df["PERIOD_BEGIN"]).values.astype("datetime64[M]")

df = df.rename(columns={
    "REGION": "city",
    "HOMES_SOLD": "closed_sales",
    "MEDIAN_SALE_PRICE": "median_price",
    "MEDIAN_DOM": "days_on_market",
    "INVENTORY": "active_listings",
    "MONTHS_OF_SUPPLY": "months_inventory",
    "MEDIAN_SALE_PRICE_YOY": "price_yoy_change",
    "HOMES_SOLD_YOY": "sales_yoy_change",
})
df["city"] = df["city"].str.replace(", TX", "", regex=False)

cols = [
    "month", "city", "closed_sales", "median_price", "active_listings",
    "months_inventory", "days_on_market", "price_yoy_change", "sales_yoy_change",
]
df = df[cols].sort_values(["city", "month"]).reset_index(drop=True)

# Price index (Jan 2012 = 100) per city, so cities with very different price
# levels can be compared on the same scale for relative appreciation.
def index_from_start(group):
    base = group.sort_values("month")["median_price"].iloc[0]
    group = group.copy()
    group["price_index_2012_base100"] = (group["median_price"] / base * 100).round(1)
    return group

df = df.groupby("city", group_keys=False)[df.columns].apply(index_from_start)

# Flag cities too thin to read month-to-month reliably, same convention used
# for the county dataset's Waller/Chambers/Liberty/Austin caveat, but computed
# explicitly here as a column since there are 165 cities, not 9.
avg_sales = df.groupby("city")["closed_sales"].transform("mean")
df["avg_monthly_sales"] = avg_sales.round(1)
df["thin_market"] = avg_sales < THIN_THRESHOLD

df = df.sort_values(["city", "month"]).reset_index(drop=True)
df["month"] = df["month"].dt.strftime("%Y-%m-%d")
df.to_csv(OUT, index=False)

print("Wrote", OUT)
print("Shape:", df.shape)
print("Cities:", df["city"].nunique())
print("Thin cities (avg < {} sales/mo):".format(THIN_THRESHOLD), df.groupby("city")["thin_market"].first().sum())
print("Date range:", df["month"].min(), "to", df["month"].max())
