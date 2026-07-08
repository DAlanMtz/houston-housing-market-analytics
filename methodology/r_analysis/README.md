# Formal causality testing (R)

Everything else in this project is Python. This one piece uses R because
`lmtest::grangertest` and `tseries::adf.test` are the standard, well-tested
tools for Granger causality and stationarity testing in applied econometrics,
with cleaner defaults than the closest Python equivalent
(`statsmodels.tsa.stattools.grangercausalitytests`). It's a small, self
contained piece, not a switch away from Python for the rest of the project.

## What this answers

The Python notebook's informal lagged-correlation scan
(`notebooks/02_extended_macro_analysis.ipynb`, section 6) found a fairly flat
correlation between the mortgage rate, oil price, and sales growth across a
six-month window, with no clear interior peak, which isn't conclusive on its
own. Granger causality asks a sharper, well-defined question instead: do past
values of X improve a forecast of `sales_yoy_change` beyond what
`sales_yoy_change`'s own past already provides, at a specific lag order.

## How to run

```bash
cd methodology/r_analysis
Rscript install_packages.R   # one-time setup
Rscript granger_causality.R
```

Reads `../../data/houston_housing_market_extended.csv` (the public repo's
extended dataset; no HAR data involved). Writes three result files into this
folder:

- `adf_stationarity_results.csv`: Augmented Dickey-Fuller test results for
  `sales_yoy_change`, `mortgage_rate_30yr`, `oil_price_yoy_change`, and
  `employment_yoy_change`, in their existing form.
- `granger_causality_results.csv`: Granger causality tests (lag orders 3, 6,
  and 12 months) for each of the three predictors against
  `sales_yoy_change`.
- `granger_causality_results_differenced.csv`: the same Granger tests
  re-run on first-differenced series, after none of the four series passed
  the ADF test in their original form.

## Results

None of the four series passed the Dickey-Fuller stationarity test in their
original form, including the two that are already year-over-year changes
(`oil_price_yoy_change`, `employment_yoy_change`). That's a real risk for
spurious regression, so the headline numbers below come from the
differenced, ADF-confirmed-stationary version. All four series pass ADF at
p < 0.01 after one difference.

| Predictor | Significant at any lag (differenced)? | p-value range (lags 3/6/12) |
|---|---|---|
| Mortgage rate (30yr) | No | 0.30 / 0.40 / 0.63 |
| Oil price (YoY change) | Yes, all three lags | < 0.0001 / < 0.0001 / 0.0001 |
| Employment (YoY change) | Yes, all three lags | < 0.0001 / < 0.0001 / < 0.0001 |

Oil price and local employment growth both Granger-cause Houston sales
growth at every lag tested, both before and after differencing. The
mortgage rate does not, at any lag, in either version. That sharpens what
the Python notebook's correlation scan couldn't resolve on its own: the
rate has a real but apparently non-predictive association with sales growth
(consistent with a persistent regime-level relationship rather than a
specific lead time), while oil and employment carry genuine, statistically
significant predictive information about sales growth in this dataset.

## What this does and does not mean

Granger causality is a statement about predictive information content in a
time series sense, not proof of a real-world causal mechanism. A significant
result here means past oil-price and employment changes help predict future
sales growth beyond what sales growth's own history predicts; it does not by
itself establish that oil prices or jobs numbers are the true driver, rule
out a shared third cause, or support a forecasting claim beyond this
dataset's own window. Treat these results the same way the rest of this
project treats correlation: directional evidence, not a causal claim.

## Baseline forecast (`forecast_baseline.R`)

A second, separate script in this folder produces a naive six-month-ahead
forecast of `closed_sales` and `median_price` using automatic exponential
smoothing (`forecast::ets`), with 80% and 95% prediction intervals.

This project is descriptive, not predictive, everywhere else. This script is
the one deliberate exception, and it exists to make that boundary concrete:
the forecast is a mechanical extrapolation of each series' own past pattern.
It has no access to the mortgage rate, oil price, employment, or any other
variable studied elsewhere in this project, and it is not a business
recommendation, a market call, or a claim about what will actually happen.
Treat it as a reference baseline, useful mainly for noticing when the real
market later diverges from what a naive model would have expected, not as
something to act on.

To reproduce: `Rscript forecast_baseline.R`. Writes
`forecast_baseline_results.csv` (point forecast and both intervals for each
of the 6 forecast months) and two PNG charts, copied into the shared
`figures/` folder as `23_r_closed_sales_baseline_forecast.png` and
`24_r_median_price_baseline_forecast.png`.
