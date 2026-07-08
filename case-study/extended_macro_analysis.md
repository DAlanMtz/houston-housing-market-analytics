# Houston Housing Market: Extended Macro and Affordability Analysis

*This is a second, additive case study. It extends the original analysis in
`houston_housing_market_analysis.md` with six new public data sources and one
R-based statistical test, and does not change any of that document's
findings. Both case studies describe the same public, redistributable dataset
family; neither uses HAR data.*

## Question

The original case study found that Houston housing conditions moved through
recognizable cycles, but had little to explain what was driving those cycles
beyond the housing data itself. Several questions follow directly from that
gap: does an independent price index confirm the same price trends Redfin and
Zillow show, does Houston's energy-linked economy and local employment explain
market swings that the national mortgage rate alone doesn't, what does
affordability look like once it's measured against real income and rent
instead of only against the dataset's own price and rate history, how much of
the price trend is inflation rather than real appreciation, and does a formal
statistical test back up the informal correlation patterns found in the data?

This is descriptive and trend analysis for business intelligence and decision
support. It does not make causal claims; the Granger causality test described
below is a formal test of predictive information content, not of real-world
causation.

## Data

Six additional public sources were joined onto the existing monthly dataset,
producing `data/houston_housing_market_extended.csv`:

- **WTI crude oil price** (FRED `MCOILWTICO`), national, monthly. Houston's
  economy is unusually energy-linked, so this is included as demand-side
  macro context.
- **Houston MSA unemployment rate and nonfarm payroll** (FRED `HOUS448URN`,
  `HOUS448NA`), monthly, sourced from the Bureau of Labor Statistics.
- **Zillow Observed Rent Index (ZORI)**, Houston metro, monthly starting 2015.
- **FHFA All-Transactions House Price Index**, Houston metro, quarterly. A
  repeat-sales/appraisal-based index, methodologically independent of both
  Redfin's median and Zillow's ZHVI.
- **Harris County median household income** (FRED `MHITX48201A052NCEN`,
  Census-derived), annual.
- **CPI-U** (FRED `CPIAUCSL`), national, monthly, used to deflate nominal
  price and rent into constant dollars.

Full source, access, and license detail: `data/source_notes.md`. Column-level
detail: `data/data_dictionary_extended.md`.

## Cleaning

- The four monthly-native sources (oil, unemployment, payroll, rent) were
  merged directly onto the existing monthly grain.
- The FHFA index, published quarterly, was flat-filled to monthly: each month
  within a quarter repeats that quarter's value. This is a deliberate choice
  to avoid fabricating within-quarter movement FHFA doesn't publish.
- Harris County income, published annually, was forward-filled to monthly
  within each observed year only, with no extrapolation past the last
  published year (currently 2024).
- Seven new derived columns were computed: `price_to_income_ratio`,
  `price_to_annual_rent_ratio`, `absorption_rate_pct`, `new_to_closed_ratio`,
  `permit_single_family_share`, `real_median_price`, and
  `real_zori_rent_index`. None of these change or replace any v1 column; the
  original dataset is untouched.

## Analysis

The notebook (`notebooks/02_extended_macro_analysis.ipynb`) works through
three independent price signals, oil price against the market condition
score, employment against sales activity, income- and rent-based affordability
ratios, a lead-lag correlation scan, a seasonal decomposition, absorption
rate and permit mix, a three-event study, a k-means regime-clustering check
against the existing `market_condition_label`, real (inflation-adjusted)
price and rent, and a formal Granger causality test in R
(`methodology/r_analysis/granger_causality.R`). Selected results:

Redfin's median price, Zillow's ZHVI, and the FHFA HPI move together closely
over the full 2012-2026 period. That agreement across three independently
computed indices is good evidence the price trends in this project reflect
real market movement rather than one provider's particular methodology.

The 2015-2016 oil price collapse is clearly visible in the local market
condition score, which declines through the collapse and only partially
recovers by 2017. Houston's housing cycle and its energy sector appear to move
together closely across most of the full period shown, not just in this one
window.

Local employment correlates with sales activity more clearly than the
same-month mortgage rate did in the original case study. Once sales are
measured as year-over-year growth instead of a raw count, the correlation with
the mortgage rate strengthens substantially (around -0.45), but it holds
fairly flat across a six-month window in both directions rather than peaking
at a specific lag, pointing to a persistent regime-level association between
higher rates and slower sales growth rather than a short, discrete delay. The
oil-price correlation shows a similar broad pattern rather than a clean
short-horizon lead.

A seasonal decomposition (STL) separates a clear, repeating within-year sales
pattern from the underlying trend, confirming that short-term month-to-month
softening in sales is often seasonal rather than a market shift. The
decomposition's residual also flags a real, one-month anomaly: closed sales
fell 24.6% year-over-year in August 2017, recovering immediately the following
month. That timing lines up with Hurricane Harvey, illustrating how a
residual-based check can separate a genuine but temporary local shock from a
change in the underlying market trend.

Price-to-income and price-to-rent ratios add a real-world denominator the
original `affordability_pressure_index` didn't have, at the cost of coarser
update frequency (income is annual) and a narrower geography (Harris County
only) for the income figure.

A k-means clustering of the same inputs used in `market_condition_score`
agrees with the existing fixed-threshold `market_condition_label` in roughly
two-thirds of months, a reasonable validation of the simpler, more transparent
approach already documented in v1.

Roughly half of the nominal price increase in this dataset is inflation, not
real appreciation. Nominal median price rose 149.5% from January 2012 to May
2026; the CPI-adjusted real increase over the same period was 70.2%, meaning
inflation accounts for about 53% of the nominal figure. The real-price series
also tells a different recent story than the nominal one: it peaked around
2022 and has been declining since, while nominal price has stayed closer to
flat, since general inflation has partly offset a real decline.

A formal Granger causality test in R (`lmtest::grangertest`,
`tseries::adf.test`) sharpens the informal lead-lag correlation finding
above. None of the four series involved passed a stationarity test in their
original form, so the test was re-run on first-differenced, stationarity-
confirmed versions. After that correction, oil price and employment growth
both Granger-cause `sales_yoy_change` at every lag tested (3, 6, and 12
months, p < 0.001 in all cases), while the mortgage rate does not, at any
lag. This is stronger evidence than the correlation scan alone that oil and
local employment carry genuine predictive information about Houston sales
activity, while the rate's relationship looks more like a persistent
association than a specific lead-lag effect.

## Findings

Adding macro and affordability context strengthens, rather than overturns, the
original case study's conclusions. The price trends are corroborated by an
independent index, the market cycles line up with Houston's energy sector more
clearly than with the national mortgage rate alone, and a documented local
shock (Hurricane Harvey) is now separable from ordinary seasonal and trend
movement. Affordability, once measured against real income and rent, tells a
broadly consistent story with the original history-relative index, while
adding units a reader can interpret directly (years of income, multiples of
annual rent). Roughly half of the nominal price appreciation shown in the
original case study turns out to be inflation rather than a real increase,
and a formal statistical test confirms that oil price and local employment,
not the mortgage rate, carry the clearest predictive signal for sales
activity in this dataset.

## Limitations

Geography varies more here than in the original dataset. Oil is a national
price; unemployment and payroll are Houston MSA; income is Harris County only,
narrower than the metro used by every other source; rent and the FHFA index
are metro-level but not necessarily boundary-identical to Redfin's definition.

Source frequency is mixed. Only oil, employment, and rent are natively
monthly; the FHFA index (quarterly) and income (annual) are flat-filled, which
understates real within-quarter or within-year movement.

The lead-lag correlation scan is limited to a six-month window in each
direction and both series show their strongest correlation at the edge of that
window rather than an interior peak, meaning the true relationship, if it has
a specific lead time at all, may extend further than tested here.

No causal claims are made anywhere in this analysis. Every relationship shown
is correlational or descriptive.

Income and FHFA data both lag current months (income through 2024 only, FHFA
typically a quarter or more behind), so the most recent rows of the extended
dataset are incomplete for those two columns.

Real price and rent are deflated using national CPI-U, not a Houston-specific
cost-of-living index, since no public Houston-metro CPI series was identified
during this research pass.

Granger causality tests predictive information content in a time series
sense, not a real-world causal mechanism. A significant result does not
prove oil prices or employment are the true cause of sales movements, rule
out a shared third factor, or license a forecast beyond this dataset's own
window. Full stationarity discussion and caveats:
`methodology/r_analysis/README.md`.

As with the original case study, no HAR data of any kind is used here.
