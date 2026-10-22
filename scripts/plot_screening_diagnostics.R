# Optional publication/export plots using base R only; no packages or model fits.
# Rscript scripts/plot_screening_diagnostics.R reports/diagnostics-2026-10-22
args <- commandArgs(trailingOnly = TRUE)
folder <- if (length(args)) args[1] else "output/screening-diagnostics"
d <- read.csv(file.path(folder, "scores.csv"), stringsAsFactors = FALSE)
elections <- unique(d$election)
labels <- c("2015", "Apr 2019", "Sep 2019", "2020", "2021", "2022")
models <- c("recency_7", "ridge_10", "forest_3_5", "xgb_2_50", "dynamic_01", "ensemble_1")
stages <- c("raw", "projected", "shrunk_projected", "integer")
colors <- c("#3067c5", "#8b51ad", "#b56a16", "#177c70")
stage_labels <- c("Full correction, unconstrained", "Full correction, sum 120",
                  "25% correction, sum 120", "25% correction, rounded")
png(file.path(folder, "history.png"), width = 1800, height = 1600, res = 150)
par(mfrow = c(3, 2), mar = c(4, 4.4, 2.2, 1), oma = c(2, 0, 5.5, 0), las = 1)
yr <- range(c(0, d$delta_from_matching_mean[d$method %in% models]))
yr <- yr + c(-1, 1)
for (model in models) {
  plot(NA, xlim = c(1, 6), ylim = yr, xaxt = "n", xlab = "Election (equal spacing)",
       ylab = "Error minus poll mean", main = model, bty = "l")
  axis(1, at = 1:6, labels = labels, cex.axis = 0.85)
  abline(h = axTicks(2), col = "#e1e6ec", lwd = 0.6)
  abline(h = 0, col = "#637186")
  for (i in seq_along(stages)) {
    rows <- d[d$method == model & d$stage == stages[i], ]
    values <- rows$delta_from_matching_mean[match(elections, rows$election)]
    lines(1:6, values, col = colors[i], lwd = 1.7, lty = if (i == 4) 2 else 1,
          type = "o", pch = c(1, 2, 5, 16)[i], cex = 0.7)
  }
}
mtext("Model differences before and after rounding", outer = TRUE, side = 3, line = 3.9, cex = 1.3, font = 2)
mtext("Below zero improves the mean. 2015-2020: history/OOF; 2021-2022: comparison. Missing fits are gaps.",
      outer = TRUE, side = 1, line = 0.5, cex = 0.78)
par(fig = c(0, 1, 0, 1), mar = c(0, 0, 0, 0), oma = c(0, 0, 0, 0), new = TRUE)
plot.new()
legend("top", inset = c(0, 0.045), legend = stage_labels, col = colors,
       lty = c(1, 1, 1, 2), pch = c(1, 2, 5, 16), ncol = 2, bty = "n", cex = 0.85)
invisible(dev.off())

comparison <- d[d$role == "comparison" & d$method != "rounded_mean_reference" & d$method != "empirical_l1_consensus", ]
models_all <- unique(comparison$method)
png(file.path(folder, "stages.png"), width = 2200, height = 1400, res = 150)
par(mfrow = c(2, 1), mar = c(7.5, 4.5, 2, 1), oma = c(0, 0, 4.5, 0), las = 1)
yr <- range(c(0, comparison$absolute_seat_error))
for (election in unique(comparison$election)) {
  rows <- comparison[comparison$election == election, ]
  plot(NA, xlim = c(1, length(models_all)), ylim = yr, xaxt = "n", xlab = "",
       ylab = "Total absolute seat error", main = sub(".*_", "", election), bty = "l")
  axis(1, at = seq_along(models_all), labels = FALSE)
  text(seq_along(models_all), par("usr")[3] - diff(par("usr")[3:4]) * 0.06,
       models_all, srt = 45, adj = 1, xpd = NA, cex = 0.75)
  abline(h = axTicks(2), col = "#e1e6ec", lwd = 0.6)
  for (i in 2:4) {
    selected <- rows[rows$stage == stages[i], ]
    values <- selected$absolute_seat_error[match(models_all, selected$method)]
    # Separate families; adjacent configurations are not a time trajectory.
    families <- sub("_.*", "", models_all)
    for (family in unique(families)) {
      idx <- which(families == family)
      lines(idx, values[idx], type = "o", col = colors[i], pch = c(1, 2, 5, 16)[i],
            lwd = 1.8, lty = if (i == 4) 2 else 1)
    }
  }
  reference <- d[d$election == election & d$method == "rounded_mean_reference", ]
  abline(h = reference$absolute_seat_error[reference$stage == "projected"], col = "#637186", lty = 3)
  abline(h = reference$absolute_seat_error[reference$stage == "integer"], col = "#637186", lty = 2)
}
mtext("Continuous estimates differ even when final allocations tie", outer = TRUE, side = 3, line = 2.8, cex = 1.25, font = 2)
mtext("Purple: full projected | Orange: 25% projected | Green: 25% rounded | Gray: mean references",
      outer = TRUE, side = 3, line = 1, cex = 0.85)
invisible(dev.off())
cat("Wrote history.png and stages.png; no models fitted.\n")
