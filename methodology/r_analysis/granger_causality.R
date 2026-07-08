# Granger causality tests: does the mortgage rate, oil price, or local
# employment growth have predictive power for Houston sales growth beyond
# what sales growth's own history already provides?
#
# This formalizes the informal lagged-correlation scan in
# notebooks/02_extended_macro_analysis.ipynb (section 6). That scan found a
# fairly flat correlation across a 6-month window with no clear interior
# peak, which is not conclusive on its own. A Granger test asks a sharper,
# well-defined question: do past values of X improve a forecast of Y beyond
# past values of Y alone, at a specific, chosen lag order.
#
# R is used here (lmtest::grangertest, tseries::adf.test) because these are
# the standard, well-tested implementations for this specific class of test
# in applied econometrics, with cleaner default output than the closest
# Python equivalent (statsmodels.tsa.stattools.grangercausalitytests).
#
# Run from this directory: Rscript granger_causality.R
# Requires: lmtest, tseries (see install_packages.R)

suppressPackageStartupMessages({
  library(lmtest)
  library(tseries)
})

df <- read.csv("../../data/houston_housing_market_extended.csv")
df$month <- as.Date(df$month)
df <- df[order(df$month), ]

start_year <- as.numeric(format(min(df$month), "%Y"))
start_month <- as.numeric(format(min(df$month), "%m"))

to_ts <- function(colname) {
  ts(df[[colname]], start = c(start_year, start_month), frequency = 12)
}

sales_yoy <- to_ts("sales_yoy_change")
rate <- to_ts("mortgage_rate_30yr")
oil_yoy <- to_ts("oil_price_yoy_change")
employment_yoy <- to_ts("employment_yoy_change")

# ---------------------------------------------------------------------------
# 1. Stationarity check (Augmented Dickey-Fuller). Granger causality assumes
# stationary inputs; a series with a strong trend or unit root can produce a
# spurious "significant" result. sales_yoy_change, oil_price_yoy_change, and
# employment_yoy_change are already year-over-year changes (pre-detrended by
# construction). mortgage_rate_30yr is a level, not a change, and is tested
# as-is since that is the same form used in the Python lagged-correlation
# scan; results for that series should be read with more caution.
# ---------------------------------------------------------------------------
adf_results <- data.frame(
  series = c("sales_yoy_change", "mortgage_rate_30yr", "oil_price_yoy_change", "employment_yoy_change"),
  adf_p_value = c(
    adf.test(na.omit(sales_yoy))$p.value,
    adf.test(na.omit(rate))$p.value,
    adf.test(na.omit(oil_yoy))$p.value,
    adf.test(na.omit(employment_yoy))$p.value
  )
)
adf_results$likely_stationary_at_5pct <- adf_results$adf_p_value < 0.05

cat("=== Augmented Dickey-Fuller stationarity tests ===\n")
print(adf_results, row.names = FALSE)
cat("\n(Null hypothesis: series has a unit root / is non-stationary.",
    "A p-value below 0.05 rejects that null.)\n\n")

# ---------------------------------------------------------------------------
# 2. Granger causality tests at three lag orders (3, 6, 12 months), testing
# whether each candidate predictor Granger-causes sales_yoy_change.
# ---------------------------------------------------------------------------
run_granger <- function(predictor_name, predictor_ts, target_ts, target_name, lags = c(3, 6, 12)) {
  merged <- na.omit(ts.union(target_ts, predictor_ts))
  rows <- list()
  for (lag in lags) {
    # grangertest(y ~ x) tests whether x Granger-causes y; we want predictor -> target
    test <- tryCatch(
      grangertest(merged[, "target_ts"] ~ merged[, "predictor_ts"], order = lag, data = merged),
      error = function(e) NULL
    )
    if (!is.null(test)) {
      rows[[length(rows) + 1]] <- data.frame(
        predictor = predictor_name,
        target = target_name,
        lag_months = lag,
        f_statistic = round(test$F[2], 3),
        p_value = round(test$`Pr(>F)`[2], 4)
      )
    }
  }
  do.call(rbind, rows)
}

results <- rbind(
  run_granger("mortgage_rate_30yr", rate, sales_yoy, "sales_yoy_change"),
  run_granger("oil_price_yoy_change", oil_yoy, sales_yoy, "sales_yoy_change"),
  run_granger("employment_yoy_change", employment_yoy, sales_yoy, "sales_yoy_change")
)
results$significant_at_5pct <- results$p_value < 0.05

cat("=== Granger causality tests (predictor -> sales_yoy_change) ===\n")
print(results, row.names = FALSE)

write.csv(results, "granger_causality_results.csv", row.names = FALSE)
write.csv(adf_results, "adf_stationarity_results.csv", row.names = FALSE)

cat("\nWrote granger_causality_results.csv and adf_stationarity_results.csv\n")

# ---------------------------------------------------------------------------
# 3. Robustness check: none of the four series above passed the ADF test in
# levels (or, for the YoY columns, in their existing form), which raises a
# spurious-regression risk for the results above. First-differencing each
# series resolves that (all four pass ADF at p < 0.01 after one difference).
# Re-running the same Granger tests on the differenced series checks whether
# the oil and employment findings survive a stricter stationarity standard.
# ---------------------------------------------------------------------------
sales_yoy_d <- diff(sales_yoy)
rate_d <- diff(rate)
oil_yoy_d <- diff(oil_yoy)
employment_yoy_d <- diff(employment_yoy)

diff_adf <- data.frame(
  series = c("sales_yoy_change", "mortgage_rate_30yr", "oil_price_yoy_change", "employment_yoy_change"),
  adf_p_value_after_diff = c(
    adf.test(na.omit(sales_yoy_d))$p.value,
    adf.test(na.omit(rate_d))$p.value,
    adf.test(na.omit(oil_yoy_d))$p.value,
    adf.test(na.omit(employment_yoy_d))$p.value
  )
)
cat("\n=== ADF on first-differenced series (robustness check) ===\n")
print(diff_adf, row.names = FALSE)

results_diff <- rbind(
  run_granger("mortgage_rate_30yr (first diff)", rate_d, sales_yoy_d, "sales_yoy_change (first diff)"),
  run_granger("oil_price_yoy_change (first diff)", oil_yoy_d, sales_yoy_d, "sales_yoy_change (first diff)"),
  run_granger("employment_yoy_change (first diff)", employment_yoy_d, sales_yoy_d, "sales_yoy_change (first diff)")
)
results_diff$significant_at_5pct <- results_diff$p_value < 0.05

cat("\n=== Granger causality tests on first-differenced series (robustness check) ===\n")
print(results_diff, row.names = FALSE)

write.csv(results_diff, "granger_causality_results_differenced.csv", row.names = FALSE)
cat("\nWrote granger_causality_results_differenced.csv\n")
