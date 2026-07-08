# Houston Housing Market Analytics: A Descriptive Look at 2012-2026

## Question

How have Houston-area housing conditions (sales activity, pricing, inventory, days on
market, mortgage-rate context, and new construction) evolved over the past decade and
a half? And can a simple, transparent composite score meaningfully summarize whether a
given period looked relatively warmer or cooler than the rest of the market's own
history?

This is descriptive and trend analysis intended to support business intelligence and
decision-support use cases, such as understanding market cycles or tracking
affordability pressure over time. It is not a causal study and does not attempt to
isolate what drives price or sales movements.

## Data

Four public sources were combined into a single monthly dataset covering January 2012
through May 2026 for the Houston metro area:

- **Redfin Data Center**, the primary source, providing closed sales, pending sales,
  active listings, new listings, months of supply, median sale price, days on market,
  and sale-to-list ratio, all at the Houston-metro level.
- **FRED (`MORTGAGE30US`, sourced from Freddie Mac)**, the national 30-year fixed
  mortgage rate, aggregated from weekly to monthly, included as macroeconomic context.
- **City of Houston Open Data**, monthly single-family and multi-family residential
  building permit counts for the City of Houston jurisdiction, used as a supply-side
  indicator.
- **Zillow Research (ZHVI)**, a smoothed, methodologically distinct "typical home
  value" series for the Houston metro, included as a secondary price trend.

HAR's Monthly Housing Update is the most locally authoritative source for Greater
Houston MLS activity, but its terms of use do not permit redistributing its data. It is
not used as structured data anywhere in this project; any reference to HAR elsewhere in
this repository is a narrative citation to a public HAR.com page, not a dataset.

Full source detail, access method, and license notes: `data/source_notes.md`.

## Cleaning

- Redfin publishes both seasonally adjusted and non-seasonally-adjusted rows for every
  month. This project standardizes on the non-adjusted, as-reported series.
- Dates were normalized to the first of each month across all four sources before
  merging.
- The City of Houston permit workbook required minimal cleaning (year/month columns
  were already structured) beyond deriving a year-over-year percent change, which the
  source does not provide directly.
- Zillow's ZHVI file ships wide (one column per month). It was reshaped to a long,
  one-row-per-month series and filtered to the Houston metro row before merging.
- All sources were merged on month using Redfin's monthly series as the base grain.
  Every row in the final dataset corresponds to a month Redfin reported, with the other
  three sources filled in where available.

Full pipeline detail and exact code: `methodology/README.md` and
`methodology/build_dataset.py`.

## Analysis

The notebook (`notebooks/01_housing_market_analysis.ipynb`) works through the dataset
in stages: validation, source-coverage summary, sales and pending-sales trends, price
trends (Redfin median vs. Zillow ZHVI), inventory and days-on-market trends, mortgage-
rate context, permit activity, and the two composite indicators. A few things stood out:

Inventory and days on market move together closely. Across the full series, months of
supply and median days on market have a strong positive correlation, around 0.83.
Tighter inventory has consistently coincided with faster-selling homes, and looser
inventory with slower-selling homes. That's a directional co-movement observation, not
a causal claim.

Sales activity and the mortgage rate show a weak relationship at the monthly,
metro-aggregate level. The simple correlation between closed sales and the 30-year
mortgage rate over the full period sits close to zero, around -0.09. Rate effects on
transaction volume, if present, are probably mixed in with seasonal patterns, price
effects, and lag structure that a simple same-month correlation doesn't capture. That's
worth deeper, purpose-built analysis rather than reading too much into this figure
alone.

The market condition score traces two clearly distinguishable cycles: a sustained
"warmer" stretch from roughly 2013 to 2015, a long "balanced" middle period through
most of 2016 to 2020, a sharp and sustained "warmer" surge through 2020 to 2022
(consistent with the widely reported pandemic-era housing boom), and a "cooler"
stretch from late 2022 through the most recent data in early-to-mid 2026. These labels
reflect relative standing within this dataset's own history, not an external
benchmark.

Redfin's median price and Zillow's ZHVI track each other closely over the long run, as
expected given they describe the same underlying metro market. ZHVI's smoothing means
it lags and dampens the month-to-month swings visible in the median price series.

Permit activity in the City of Houston jurisdiction provides useful supply-side
context, but it should be read as directional rather than as a metro-wide construction
count, given the jurisdiction mismatch with the Redfin/Zillow metro geography.

## Findings

Over 2012 to 2026, the Houston housing market moved through recognizable cycles that a
simple, transparent composite score can trace reasonably well: a mid-2010s warm
stretch, a multi-year balanced period, a sharp pandemic-era surge, and a cooling
stretch running into 2026, marked by rising months of supply, slower days on market,
and an elevated affordability-pressure reading driven by the combination of price
levels and mortgage rates relative to the rest of the series. These patterns line up
with widely reported national housing-market narratives over the same period. That's a
reasonable sanity check on the composite scoring approach, though it isn't formal
external validation.

## Limitations

Geography mismatch across sources. Redfin and Zillow describe the Houston metro area
(MSA-based); City of Houston permits describe only the city permitting jurisdiction;
the mortgage rate is national. These are overlapping but non-identical geographies;
see `data/source_notes.md` for detail.

MLS vs. permit boundaries. Sales and listing data reflect MLS participation footprint;
permit data reflects municipal jurisdiction. The two do not describe the same
population of housing units.

Weekly vs. monthly granularity. The mortgage rate is weekly at the source and was
aggregated to a monthly average, which smooths within-month rate volatility.

No HAR-sourced structured data. HAR's terms of use do not permit redistributing its
data. Any HAR reference in this project is a narrative citation only, not a dataset
input.

Source revision risk. Redfin, FRED, and permit data are all subject to revision after
initial publication, especially for the most recent months. This dataset is a snapshot
and will drift from the live sources over time.

No causal claims. This project supports descriptive and trend analysis. Co-movement
between series (for example, inventory and days on market) is not evidence of a causal
relationship, and the composite indicators are relative-to-history summaries, not
predictive or diagnostic models.

No proprietary MLS microdata. Only public monthly summary statistics are used; no
listing-level or transaction-level MLS data is accessed or distributed.

Composite indicators are intentionally simple. `affordability_pressure_index` and
`market_condition_score` are transparent z-score blends of a handful of columns,
computed relative to this dataset's own history. They are not official, validated, or
industry-standard indices, and should not be used as inputs to real-world pricing,
lending, or investment decisions.
