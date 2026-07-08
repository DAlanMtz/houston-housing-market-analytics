# Houston Housing Market: County Submarkets and a Baseline Forecast

*This is a third, additive case study. It extends the project with a
county-level cut of the existing Redfin source and one deliberate,
clearly-bounded forecast, and does not change any findings in the other two
case studies. No HAR data is used here.*

## Question

The metro-level dataset (v1) and the macro-context dataset (extended) both
describe Houston as a single number per month. Two questions follow from
that simplification: is Houston actually moving as one market, or do the
counties within the metro diverge in ways the metro-level figure hides, and
what would a simple, mechanical extrapolation of the existing trend say about
the next few months, as an explicit contrast to this project's otherwise
descriptive-only approach?

This is descriptive and trend analysis for business intelligence and
decision support. The forecast section is the one exception to the
project's no-prediction stance, and it is treated as a bounded reference
baseline, not a market call.

## Data

- **Redfin Data Center, county grain**: the same source and property-type
  scope as v1 (All Residential, non-seasonally-adjusted), pulled at the
  county level for the nine counties Redfin assigns to the Houston metro
  area, producing `data/houston_county_submarkets.csv`. No new external
  source; this is a different cut of data already in use elsewhere in the
  project.
- **v1's own history**: `closed_sales` and `median_price` from
  `houston_housing_market.csv`, used as the input to the R baseline
  forecast.

Full source detail: `data/source_notes.md`. Column detail:
`data/data_dictionary_county.md`.

## Cleaning

- The county-level Redfin file was filtered to rows where
  `PARENT_METRO_REGION` matches Houston, All Residential property type, and
  the non-seasonally-adjusted series, the same convention used for v1.
- Column names were aligned to v1's naming where the same concept applies.
- `price_index_2012_base100` was computed per county, rebasing each county's
  own January 2012 median price to 100, so counties starting at very
  different price levels can be compared on relative appreciation rather
  than raw dollars.
- For the forecast, `closed_sales` and `median_price` were converted to R
  time series objects and fit with automatic exponential smoothing
  (`forecast::ets`); no manual model selection or tuning was applied.

## Analysis

The notebook (`notebooks/03_county_submarket_variation.ipynb`) works through
sales volume by county, indexed price appreciation, recent year-over-year
divergence against the metro figure, and months of inventory by county.

Harris County dominates the metro numbers by volume, averaging roughly
three-quarters of total metro-county sales across the full period. In
practice, the metro-level v1 figures are mostly a Harris County number with
the other eight counties blended in at a much smaller weight.

The five higher-volume counties (Harris, Fort Bend, Montgomery, Galveston,
Brazoria) have appreciated at genuinely different rates since January 2012.
As of the most recent month, Galveston County's price index stands at 273.6
and Harris County's at 263.5, well above Brazoria (239.4), Fort Bend
(215.6), and Montgomery (210.1). That's a real, persistent spread across 14
years, not month-to-month noise, and it is invisible in the single
metro-level median price series.

The four thinly-traded counties (Waller, Chambers, Liberty, Austin) average
under 80 sales a month, and their price index values show it: Liberty
County's index reaches 421.9 in the most recent month, more than 150 points
above the next-highest county. That is a small-sample artifact, not a real
signal, and is the concrete reason those four counties are excluded from the
comparison charts even though they remain in the underlying dataset.

Months of inventory has moved in a broadly similar shape across the five
main counties, tightening through 2020-2022 and loosening since, which
suggests the cooling identified at the metro level in the original case
study is a genuinely metro-wide pattern, even though the underlying price
levels and appreciation rates differ by county.

The R baseline forecast (`methodology/r_analysis/forecast_baseline.R`)
extrapolates `closed_sales` and `median_price` six months forward using
automatic ETS model selection, with 80% and 95% prediction intervals. Both
series' models incorporate a damped trend and multiplicative or additive
seasonality (selected automatically), consistent with the seasonal pattern
already identified in the extended analysis's STL decomposition. The
forecast has no access to mortgage rate, oil price, or employment data, so
it should be read as a mechanical continuation of the two series' own
recent pattern, not as an informed prediction.

## Findings

Houston is not a single, uniform market once you look below the metro
level. Price appreciation genuinely diverges by county over long horizons,
Harris County's dominant sales volume means the metro-level figure is
effectively a Harris County number, and thinly-traded counties can produce
extreme, misleading statistics if read without checking sample size first.
At the same time, the broad direction of the market (tightening then
loosening inventory) does appear to be shared across the higher-volume
counties, so the metro-level trend direction from the original case study
still holds as a reasonable summary, even if the price levels underneath it
vary. The baseline forecast, read as a bounded reference point rather than a
prediction, projects a continuation of the recent softening pattern in both
sales and price over the next six months.

## Limitations

Four of the nine counties in the submarket dataset are too thin (under 80
sales a month) for reliable month-to-month reading; their inclusion in the
dataset is for completeness, not for the comparison charts.

The county-level analysis inherits every limitation of the metro-level
Redfin source: non-seasonally-adjusted figures, Redfin's own county boundary
definitions, and revision risk on recent months.

No causal claims are made about why counties appreciate at different rates;
this analysis describes the divergence, it does not explain it.

The baseline forecast is a mechanical, univariate extrapolation with no
macro context, no knowledge of the oil, employment, or rate relationships
studied in the extended case study, and no adjustment for known structural
breaks like the 2020 pandemic surge or the 2022 rate-hike cycle. Prediction
intervals reflect the model's own uncertainty about historical patterns
repeating, not uncertainty about real-world events that haven't happened
yet. It should not be used as an input to a real pricing, investment, or
lending decision.

As with the other two case studies, no HAR data is used anywhere in this
analysis.
