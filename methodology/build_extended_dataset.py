"""
Build data/houston_housing_market_extended.csv on top of the v1 dataset.

This script does not modify data/houston_housing_market.csv (v1). It loads that
file as a base and left-joins six additional public sources (seven raw files,
since Houston unemployment and payroll are two separate FRED series), then
computes a few new derived columns. v1 stays exactly as documented; this is an
additive, separately versioned dataset for macro/context analysis.

New raw sources (all in housing-market-data-research/raw/):
- wti_oil_monthly.csv                    -> FRED MCOILWTICO, national, monthly
- houston_unemployment_rate.csv          -> FRED HOUS448URN, Houston MSA, monthly
- houston_nonfarm_payroll.csv            -> FRED HOUS448NA, Houston MSA, monthly (thousands of jobs)
- zillow_zori_houston_metro.csv          -> Zillow Observed Rent Index, Houston metro, monthly
- fhfa_hpi_houston_metro.csv             -> FHFA All-Transactions HPI, Houston metro, quarterly
- harris_county_median_household_income.csv -> FRED MHITX48201A052NCEN, Harris County, annual
- cpi_all_urban.csv                       -> FRED CPIAUCSL, national, monthly

As with build_dataset.py, this repo ships the finished CSV, not the raw source
files. To re-run this script, download the seven raw files above per
data/source_notes.md, place them in a local raw/ folder, and point RAW at it.
"""
import pandas as pd
import numpy as np

RAW = "../../housing-market-data-research/raw"  # local raw-file folder, see docstring above
BASE = "../data/houston_housing_market.csv"
OUT = "../data/houston_housing_market_extended.csv"

df = pd.read_csv(BASE, parse_dates=["month"])

# ---------------------------------------------------------------------------
# WTI oil price (national, monthly)
# ---------------------------------------------------------------------------
oil = pd.read_csv(f"{RAW}/wti_oil_monthly.csv")
oil["month"] = pd.to_datetime(oil["observation_date"]).values.astype("datetime64[M]")
oil = oil.rename(columns={"MCOILWTICO": "wti_oil_price_usd_bbl"})[["month", "wti_oil_price_usd_bbl"]]

# ---------------------------------------------------------------------------
# Houston MSA unemployment rate and nonfarm payroll (monthly)
# ---------------------------------------------------------------------------
unemp = pd.read_csv(f"{RAW}/houston_unemployment_rate.csv")
unemp["month"] = pd.to_datetime(unemp["observation_date"]).values.astype("datetime64[M]")
unemp = unemp.rename(columns={"HOUS448URN": "houston_unemployment_rate_pct"})[["month", "houston_unemployment_rate_pct"]]

payroll = pd.read_csv(f"{RAW}/houston_nonfarm_payroll.csv")
payroll["month"] = pd.to_datetime(payroll["observation_date"]).values.astype("datetime64[M]")
payroll = payroll.rename(columns={"HOUS448NA": "houston_nonfarm_payroll_thousands"})[["month", "houston_nonfarm_payroll_thousands"]]
payroll = payroll.sort_values("month")
payroll["employment_yoy_change"] = payroll["houston_nonfarm_payroll_thousands"].pct_change(periods=12).round(4)

# ---------------------------------------------------------------------------
# Zillow ZORI rent index (Houston metro, monthly, wide -> long)
# ---------------------------------------------------------------------------
zori_wide = pd.read_csv(f"{RAW}/zillow_zori_houston_metro.csv")
date_cols = [c for c in zori_wide.columns if c[:2] in ("19", "20")]
zori_long = zori_wide.melt(id_vars=["RegionName"], value_vars=date_cols, var_name="raw_date", value_name="zori_rent_index")
zori_long["month"] = pd.to_datetime(zori_long["raw_date"]).values.astype("datetime64[M]")
zori_long = zori_long[["month", "zori_rent_index"]].sort_values("month").reset_index(drop=True)

# ---------------------------------------------------------------------------
# FHFA All-Transactions HPI (Houston metro, quarterly -> monthly, forward-filled)
#
# The index is only observed once per quarter. Each month within a quarter is
# assigned that quarter's value rather than interpolated, since FHFA does not
# publish a within-quarter trajectory. This is a deliberate flat-fill, not an
# estimate of monthly movement.
# ---------------------------------------------------------------------------
fhfa = pd.read_csv(
    f"{RAW}/fhfa_hpi_houston_metro.csv",
    header=None,
    names=["metro_name", "cbsa", "year", "quarter", "hpi_index_nsa", "standard_error"],
)
fhfa["hpi_index_nsa"] = pd.to_numeric(fhfa["hpi_index_nsa"], errors="coerce")
fhfa["quarter_start_month"] = (fhfa["quarter"].astype(int) - 1) * 3 + 1
fhfa["quarter_start"] = pd.to_datetime(dict(year=fhfa["year"], month=fhfa["quarter_start_month"], day=1))

fhfa_monthly_rows = []
for _, row in fhfa.iterrows():
    if pd.isna(row["hpi_index_nsa"]):
        continue
    for m_offset in range(3):
        month = row["quarter_start"] + pd.DateOffset(months=m_offset)
        fhfa_monthly_rows.append({"month": month, "fhfa_hpi_houston_metro": row["hpi_index_nsa"]})
fhfa_monthly = pd.DataFrame(fhfa_monthly_rows)

# ---------------------------------------------------------------------------
# Harris County median household income (annual -> monthly, forward-filled
# within the observed year only; not extrapolated past the last known year)
# ---------------------------------------------------------------------------
income = pd.read_csv(f"{RAW}/harris_county_median_household_income.csv")
income["year"] = pd.to_datetime(income["observation_date"]).dt.year
income = income.rename(columns={"MHITX48201A052NCEN": "harris_county_median_household_income_usd"})
income = income.dropna(subset=["harris_county_median_household_income_usd"])

income_monthly_rows = []
for _, row in income.iterrows():
    for m in range(1, 13):
        income_monthly_rows.append({
            "month": pd.Timestamp(year=int(row["year"]), month=m, day=1),
            "harris_county_median_household_income_usd": row["harris_county_median_household_income_usd"],
        })
income_monthly = pd.DataFrame(income_monthly_rows)

# ---------------------------------------------------------------------------
# CPI-U (national, monthly), used to deflate nominal price and rent into
# constant dollars of the most recent month in the dataset.
# ---------------------------------------------------------------------------
cpi = pd.read_csv(f"{RAW}/cpi_all_urban.csv")
cpi["month"] = pd.to_datetime(cpi["observation_date"]).values.astype("datetime64[M]")
cpi = cpi.rename(columns={"CPIAUCSL": "cpi_index"})[["month", "cpi_index"]]

# ---------------------------------------------------------------------------
# Merge everything onto the v1 base (left join, v1's monthly grain preserved)
# ---------------------------------------------------------------------------
df = df.merge(oil, on="month", how="left")
df = df.merge(unemp, on="month", how="left")
df = df.merge(payroll, on="month", how="left")
df = df.merge(zori_long, on="month", how="left")
df = df.merge(fhfa_monthly, on="month", how="left")
df = df.merge(income_monthly, on="month", how="left")
df = df.merge(cpi, on="month", how="left")

# ---------------------------------------------------------------------------
# Derived columns
# ---------------------------------------------------------------------------
# Price-to-income ratio: how many years of the typical Harris County household
# income it would take to buy the median-priced home. A standard, simple
# affordability lens, distinct from the existing (history-relative,
# income-free) affordability_pressure_index in the v1 dataset.
df["price_to_income_ratio"] = (df["median_price"] / df["harris_county_median_household_income_usd"]).round(2)

# Price-to-annual-rent ratio: a standard buy-vs-rent economics signal.
df["price_to_annual_rent_ratio"] = (df["median_price"] / (df["zori_rent_index"] * 12)).round(2)

# Absorption rate: share of active listings sold in the month. A more
# responsive supply-demand read than months_inventory (its rough inverse).
df["absorption_rate_pct"] = (df["closed_sales"] / df["active_listings"] * 100).round(2)

# New-to-closed ratio: how much new supply is entering relative to what's
# closing. Above 1 means new listings are outpacing sales (building inventory
# pressure); below 1 means the market is absorbing supply faster than it's added.
df["new_to_closed_ratio"] = (df["new_listings"] / df["closed_sales"]).round(3)

# Single-family share of total residential permits issued that month.
permit_total = df["single_family_permits"] + df["multi_family_permits"]
df["permit_single_family_share"] = (df["single_family_permits"] / permit_total).round(4)

# WTI oil price year-over-year change, for comparison against Houston-specific
# employment and sales cycles (Houston's economy is energy-linked).
df = df.sort_values("month").reset_index(drop=True)
df["oil_price_yoy_change"] = df["wti_oil_price_usd_bbl"].pct_change(periods=12).round(4)

# Real (inflation-adjusted) price and rent, deflated to constant dollars of
# the most recent month with a known CPI reading. Answers "how much of the
# nominal price/rent increase is inflation, versus a real increase" without
# needing a separate base-year convention.
latest_cpi = df.loc[df["cpi_index"].notna(), "cpi_index"].iloc[-1]
df["real_median_price"] = (df["median_price"] * (latest_cpi / df["cpi_index"])).round(2)
df["real_zori_rent_index"] = (df["zori_rent_index"] * (latest_cpi / df["cpi_index"])).round(2)

final_cols = list(df.columns)
# keep month first, everything else in the order it was built
df = df[final_cols].sort_values("month").reset_index(drop=True)

round2 = ["wti_oil_price_usd_bbl", "houston_nonfarm_payroll_thousands", "zori_rent_index", "fhfa_hpi_houston_metro", "cpi_index"]
for c in round2:
    df[c] = df[c].round(2)

df["month"] = df["month"].dt.strftime("%Y-%m-%d")
df.to_csv(OUT, index=False)

print("Wrote", OUT)
print("Shape:", df.shape)
print("Date range:", df["month"].min(), "to", df["month"].max())
new_cols = [
    "wti_oil_price_usd_bbl", "houston_unemployment_rate_pct", "houston_nonfarm_payroll_thousands",
    "employment_yoy_change", "zori_rent_index", "fhfa_hpi_houston_metro",
    "harris_county_median_household_income_usd", "price_to_income_ratio",
    "price_to_annual_rent_ratio", "absorption_rate_pct", "new_to_closed_ratio",
    "permit_single_family_share", "oil_price_yoy_change", "cpi_index",
    "real_median_price", "real_zori_rent_index",
]
print(df[new_cols].isna().sum())
