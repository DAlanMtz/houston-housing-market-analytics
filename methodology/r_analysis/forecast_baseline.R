# Baseline forecast: a naive, mechanical extrapolation of closed_sales and
# median_price six months forward, using R's forecast package (ets, automatic
# exponential smoothing model selection).
#
# This project is explicitly descriptive, not predictive, everywhere else.
# This script is the one deliberate exception, and it exists to make that
# boundary concrete rather than abstract: a forecast here is a mechanical
# projection of past patterns, not a business recommendation, a market call,
# or a claim about what will actually happen. It has no access to anything
# outside its own two input series, no macro context, no knowledge of the
# oil, employment, or rate variables studied elsewhere in this project.
#
# R is used here because the forecast package's ets() and auto.arima() give
# a standard, well-documented automatic model selection and clean prediction
# intervals, matching this project's other use of R for time-series-specific
# tooling (see granger_causality.R).
#
# Run from this directory: Rscript forecast_baseline.R
# Requires: forecast (see install_packages.R)

suppressPackageStartupMessages({
  library(forecast)
})

df <- read.csv("../../data/houston_housing_market.csv")
df$month <- as.Date(df$month)
df <- df[order(df$month), ]

start_year <- as.numeric(format(min(df$month), "%Y"))
start_month <- as.numeric(format(min(df$month), "%m"))

sales_ts <- ts(df$closed_sales, start = c(start_year, start_month), frequency = 12)
price_ts <- ts(df$median_price, start = c(start_year, start_month), frequency = 12)

horizon <- 6

# Small base-R helper for month arithmetic, to avoid a lubridate dependency.
add_months <- function(date, n) {
  seq(date, by = paste(n, "months"), length.out = 2)[2]
}

fit_and_forecast <- function(series_ts, series_name) {
  fit <- ets(series_ts)
  fc <- forecast(fit, h = horizon)

  png(paste0(series_name, "_forecast.png"), width = 1100, height = 550, res = 120)
  plot(fc, main = paste0(series_name, ": ", horizon, "-Month Baseline Forecast (ETS, ", fit$method, ")"),
       ylab = series_name, xlab = "Year", flty = 2)
  dev.off()

  fc_dates <- seq(add_months(max(df$month), 1), by = "month", length.out = horizon)
  data.frame(
    month = format(fc_dates, "%Y-%m-%d"),
    series = series_name,
    point_forecast = round(as.numeric(fc$mean), 1),
    lo_80 = round(as.numeric(fc$lower[, 1]), 1),
    hi_80 = round(as.numeric(fc$upper[, 1]), 1),
    lo_95 = round(as.numeric(fc$lower[, 2]), 1),
    hi_95 = round(as.numeric(fc$upper[, 2]), 1),
    model = fit$method
  )
}

sales_forecast <- fit_and_forecast(sales_ts, "closed_sales")
price_forecast <- fit_and_forecast(price_ts, "median_price")

results <- rbind(sales_forecast, price_forecast)
cat("=== Baseline ETS forecast, 6 months ahead ===\n")
print(results, row.names = FALSE)

write.csv(results, "forecast_baseline_results.csv", row.names = FALSE)
cat("\nWrote forecast_baseline_results.csv, closed_sales_forecast.png, median_price_forecast.png\n")
cat("\nReminder: this is a mechanical extrapolation of two series' own history,\n",
    "with no macro context. Not a prediction to act on.\n")
