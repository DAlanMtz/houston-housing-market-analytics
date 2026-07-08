# Houston Metro: City-Level Submarket Variation

*This is a fourth, additive case study. It extends the county-level analysis
in `county_submarkets_and_forecast.md` one grain finer, using the same Redfin
source, and does not change any findings in the other three case studies. No
HAR data is used here.*

## Question

The county-level case study found that Harris County alone drives roughly
three-quarters of metro sales volume and that price appreciation genuinely
diverges by county. Does that same pattern hold, or sharpen, at the city
level within those counties? And just as importantly: at what point does
slicing the data finer stop being informative and start being noise?

This is descriptive and trend analysis for business intelligence and
decision support. It does not make causal claims.

## Data

**Redfin Data Center, city grain**: the same source and property-type scope
as v1 and the county dataset (All Residential, non-seasonally-adjusted),
pulled at the city level for the 165 cities Redfin assigns to the Houston
metro area, producing `data/houston_city_submarkets.csv`. No new external
source; this is a finer cut of data already in use elsewhere in the project.

Full source detail: `data/source_notes.md`. Column detail:
`data/data_dictionary_city.md`.

## Cleaning

- The city-level Redfin file was filtered to rows where `PARENT_METRO_REGION`
  matches Houston, All Residential property type, and the non-seasonally-
  adjusted series, the same convention used for v1 and the county dataset.
- Column names were aligned to the established naming convention.
- `price_index_2012_base100` was computed per city, same method as the
  county dataset: each city's own first observed month rebased to 100.
- A new step not needed at the county level: `avg_monthly_sales` and a
  `thin_market` flag were computed for every city, since 165 cities span an
  enormous range of sales volume, from Houston itself (1,845 sales a month
  on average) down to cities with barely more than one sale a month. Cities
  averaging under 50 sales a month (149 of 165) are flagged.

## Analysis

The notebook (`notebooks/04_city_submarket_variation.ipynb`) works through
sales volume by city, indexed price appreciation, recent year-over-year
price change, and months of inventory, restricted almost entirely to the 16
cities above the thin-market threshold.

The city of Houston accounts for about 37% of total metro-city sales volume
across all 165 tracked cities, more than three times the next-largest city
(Katy) by average monthly sales. That's a large plurality, not a majority:
the remaining 63% of activity is spread across 164 other cities, most of
them individually small. This is a more precise version of the county-level
finding that Harris County dominates the metro number; at the city level,
that dominance is concentrated further still in Houston proper, within
Harris County.

Of the 165 cities Redfin tracks, only 16 average at least 50 sales a month.
The other 149, roughly 90% of all tracked cities, are too thin to read
reliably. Some of these thin cities are not obscure: they include
recognizable suburbs and communities, not just rural fringe areas. Their
statistics carry real risk of the same small-sample distortion already
documented at the county level (where Liberty County's price index reached
421.9 on about 60 sales a month), and in several cases Redfin itself does
not compute months-of-inventory or year-over-year figures for these
thinnest markets, leaving those cells null in the source data.

Even among the 16 reliable cities, price appreciation and current inventory
pressure vary meaningfully. This holds even within a single county: Katy,
The Woodlands, and Conroe, for instance, are all in counties already shown
to diverge from each other, and they show further variation among
themselves.

## Findings

Slicing Houston's housing market finer keeps revealing more internal
variation, not less: metro masks county-level differences, and county masks
city-level differences within it. But this finding has a boundary. Once the
data gets thin enough, roughly 90% of cities in this specific dataset, the
"variation" being observed is increasingly sampling noise rather than a real
market signal. The useful takeaway is not "go as granular as possible," it's
"check the sample size before trusting a granular number," which is exactly
why this dataset ships with an explicit `thin_market` flag rather than
leaving that judgment to whoever opens the file.

## Limitations

149 of 165 cities (90%) are flagged `thin_market` and excluded from every
chart in the notebook, though they remain in the underlying CSV for
completeness. Redfin itself does not always compute `months_inventory`,
`price_yoy_change`, or `sales_yoy_change` for its thinnest markets, which
shows up as nulls concentrated almost entirely in flagged cities.

Redfin's city boundaries are its own definitions and do not always match
municipal incorporated limits or Census-designated places, so "Houston" or
"Katy" in this dataset may not exactly match how those names are used
elsewhere.

The 50-sales-a-month thin-market threshold is a judgment call made for this
project, not a Redfin-published or industry-standard cutoff. A different
threshold would move some cities across the line.

Same source limitations as v1 and the county dataset: non-seasonally-
adjusted Redfin data and revision risk on recent months.

No causal claims are made anywhere in this analysis. Differences between
cities are described, not explained.

As with the other three case studies, no HAR data is used anywhere in this
analysis.
