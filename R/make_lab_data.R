# ─────────────────────────────────────────────────────────────────────────────
# make_lab_data.R  —  seeded lab-data generator for ENGR-3027
#
# Run ONCE per term:   Rscript R/make_lab_data.R
#
# Emits (into ./lab_data/, which is gitignored — stage these on FOL, do NOT
# commit them; the repo convention is that all lab data lives on FOL):
#
#   vsm_station_data.csv     — Lab 4  (Lean VSM) station table
#   precitech_shift_log.csv  — Lab 13 (TPM/OEE) one-week shift log
#
# Prints answer keys for marking (these are NOT written to the student book):
#
#   Lab 4  — takt time, bottleneck station, process cycle efficiency
#   Lab 6  — caliper reference values, indicative %GRR / ndc, seeded Cpk
#   Lab 13 — expected weekly OEE, dominant Big Loss, AI4I 2020 Pareto order
#   Lab 14 — expected simulated cycle-time range vs takt
#
# Everything is set.seed()-ed so the answer keys stay valid across terms.
# Base R only — no package dependencies.
# ─────────────────────────────────────────────────────────────────────────────

out_dir <- "lab_data"
if (!dir.exists(out_dir)) dir.create(out_dir)

rule <- function(title) cat("\n", strrep("─", 74), "\n", title, "\n",
                            strrep("─", 74), "\n", sep = "")

# Précitech demand basis (shared by Labs 4 and 14)
shift_seconds     <- 8 * 3600          # one 8-hour shift
break_seconds     <- 2 * 20 * 60       # two 20-minute breaks
available_seconds <- shift_seconds - break_seconds
daily_demand      <- 250               # kits/day
takt_seconds      <- available_seconds / daily_demand

# ─────────────────────────────────────────────────────────────────────────────
# Lab 4 — Lean VSM station table
# ─────────────────────────────────────────────────────────────────────────────
set.seed(3027)

vsm <- data.frame(
  station        = c("CNC turn", "Deburr", "Wash", "Inspect", "Kitting cell"),
  cycle_time_s   = c(120, 74, 40, 58, 96),      # per-unit cycle time
  changeover_min = c(45, 10, 5, 8, 12),         # setup / changeover
  uptime_pct     = c(82, 95, 98, 99, 93),       # equipment uptime
  wip_units      = c(180, 240, 90, 150, 260),   # inventory downstream of station
  batch_size     = c(60, 60, 30, 30, 20),
  value_added    = c(TRUE, FALSE, FALSE, FALSE, TRUE),
  stringsAsFactors = FALSE
)

write.csv(vsm, file.path(out_dir, "vsm_station_data.csv"), row.names = FALSE)

va_time_s     <- sum(vsm$cycle_time_s[vsm$value_added])
total_cycle_s <- sum(vsm$cycle_time_s)
total_wip     <- sum(vsm$wip_units)
# Little's law: wait time = WIP / throughput; throughput = demand / available time
wip_wait_s    <- total_wip * takt_seconds
lead_time_s   <- total_cycle_s + wip_wait_s
pce           <- va_time_s / lead_time_s
bottleneck    <- vsm$station[which.max(vsm$cycle_time_s)]

rule("LAB 4 — Lean VSM answer key")
cat(sprintf("Available time / shift : %.0f s  (%.2f h)\n",
            available_seconds, available_seconds / 3600))
cat(sprintf("Takt time             : %.1f s/kit  (demand %d kits/day)\n",
            takt_seconds, daily_demand))
cat(sprintf("Bottleneck station    : %s  (C/T %.0f s > takt %.1f s)\n",
            bottleneck, max(vsm$cycle_time_s), takt_seconds))
cat(sprintf("Value-added time       : %.0f s\n", va_time_s))
cat(sprintf("Production lead time   : %.0f s  (%.1f h)\n",
            lead_time_s, lead_time_s / 3600))
cat(sprintf("Process cycle efficiency (VA / lead time): %.2f %%\n", 100 * pce))
cat("Stations below takt (spare capacity): ",
    paste(vsm$station[vsm$cycle_time_s < takt_seconds], collapse = ", "), "\n")
cat("Wrote ", file.path(out_dir, "vsm_station_data.csv"), "\n", sep = "")

# ─────────────────────────────────────────────────────────────────────────────
# Lab 6 — Virtual caliper reference values + indicative Gauge R&R + seeded Cpk
#
# The caliper and the SPC data are generated INSIDE the webR cells in
# 30-Labs.qmd; this block reproduces that seeding so the instructor has the
# ground truth for marking. It also simulates one plausible measurement run so
# %GRR and ndc can be quoted to an order of magnitude — actual student numbers
# depend on their reading error.
# ─────────────────────────────────────────────────────────────────────────────
set.seed(3027)
caliper_ref  <- round(sort(runif(10, 24.90, 25.10)), 3)
caliper_bias <- 0.03 + 0.05 * (caliper_ref - 25.00)

rule("LAB 6 — Virtual caliper answer key")
cat("Part | certified reference (mm) | gauge bias at that size (mm)\n")
for (i in 1:10)
  cat(sprintf("%4d | %24.3f | %+.4f\n", i, caliper_ref[i], caliper_bias[i]))
cat(sprintf("\nMean gauge bias across the 10 parts: %+.4f mm (expect ~ +0.030)\n",
            mean(caliper_bias)))

# --- simulate one measurement run (3 operators, 3 trials, resolution 0.05) ---
set.seed(606)
op_offset <- rnorm(3, 0, 0.008)          # reproducibility between operators
sd_repeat <- 0.010                       # within-operator reading noise
quant     <- function(v) round(v / 0.05) * 0.05

sim_op <- function(o) {
  m <- matrix(NA_real_, 10, 3)
  for (p in 1:10) for (t in 1:3)
    m[p, t] <- quant(caliper_ref[p] + caliper_bias[p] + op_offset[o] +
                       rnorm(1, 0, sd_repeat))
  m
}
ops <- list(A = sim_op(1), B = sim_op(2), C = sim_op(3))

trials <- 3; operators <- 3; parts <- 10
K1 <- 0.5908; K2 <- 0.5231; K3 <- 0.3146          # AIAG constants (3,3,10)

part_op_range <- sapply(ops, function(M) apply(M, 1, function(x) max(x) - min(x)))
Rbar <- mean(part_op_range); EV <- Rbar * K1
op_means <- sapply(ops, mean); Xdiff <- max(op_means) - min(op_means)
AV  <- sqrt(max(0, (Xdiff * K2)^2 - (EV^2 / (parts * trials))))
GRR <- sqrt(EV^2 + AV^2)
part_means <- rowMeans(sapply(ops, function(M) rowMeans(M)))
PV  <- (max(part_means) - min(part_means)) * K3
TV  <- sqrt(GRR^2 + PV^2)
pGRR <- 100 * GRR / TV
ndc  <- floor(1.41 * PV / GRR)

cat(sprintf("\nIndicative study (simulated reading error):\n"))
cat(sprintf("  EV = %.4f  AV = %.4f  GRR = %.4f  PV = %.4f  TV = %.4f mm\n",
            EV, AV, GRR, PV, TV))
cat(sprintf("  %%GRR = %.1f %%   ndc = %d\n", pGRR, ndc))
cat("  Interpretation: 0.05 mm resolution against a +/-0.05 mm tolerance is a\n")
cat("  marginal gauge. This simulated run uses modest reading error; expect\n")
cat("  student %GRR roughly 20-35 % (marginal band) with ndc ~ 4-6. Sloppier\n")
cat("  reading pushes %GRR past 30 % and ndc below 5 — that is the Task 6 lesson.\n")

# --- seeded SPC dataset (mirrors the `spc` webR cell) ---
set.seed(250)
n_sub <- 25; n <- 5
USL <- 25.050; LSL <- 24.950
mu_series <- rep(25.002, n_sub)
mu_series[12:16] <- mu_series[12:16] + 0.030
x    <- t(sapply(mu_series, function(m) rnorm(n, m, 0.011)))
xbar <- rowMeans(x); Rg <- apply(x, 1, function(v) max(v) - min(v))
xbarbar <- mean(xbar); Rbar_spc <- mean(Rg)
d2 <- 2.326; A2 <- 0.577
sigma_hat <- Rbar_spc / d2
UCL_x <- xbarbar + A2 * Rbar_spc; LCL_x <- xbarbar - A2 * Rbar_spc
Cp  <- (USL - LSL) / (6 * sigma_hat)
Cpk <- min(USL - xbarbar, xbarbar - LSL) / (3 * sigma_hat)
ooc <- which(xbar > UCL_x | xbar < LCL_x)

cat(sprintf("\nSeeded X-bar/R + Cpk dataset (same for every group):\n"))
cat(sprintf("  X-bar-bar = %.4f  R-bar = %.4f  sigma_hat = %.4f mm\n",
            xbarbar, Rbar_spc, sigma_hat))
cat(sprintf("  X-bar limits = [%.4f, %.4f]\n", LCL_x, UCL_x))
cat(sprintf("  Cp = %.2f   Cpk = %.2f   (Tier-1 target Cpk >= 1.33)\n", Cp, Cpk))
cat(sprintf("  Beyond-3-sigma subgroups: %s  (special-cause shift seeded at 12-16)\n",
            paste(ooc, collapse = " ")))

# ─────────────────────────────────────────────────────────────────────────────
# Lab 13 — Précitech shift log + OEE answer key
# ─────────────────────────────────────────────────────────────────────────────
set.seed(1213)

days <- sprintf("2025-09-%02d", 8:12)             # Mon–Fri
planned_min       <- rep(440, 5)                  # 8 h shift minus 40 min breaks
breakdown_min     <- c(35, 18, 62, 22, 40)        # unplanned stops (Big Loss 1)
setup_min         <- c(28, 20, 24, 30, 22)        # setup & adjustment (Big Loss 2)
small_stop_min    <- c(12, 15, 10, 18, 14)        # idling & minor stops (Big Loss 3)
ideal_cycle_s     <- rep(96, 5)                   # ideal seconds per kit
scrap_count       <- c(6, 4, 9, 5, 7)             # production rejects (Big Loss 6)
startup_scrap     <- c(3, 2, 3, 2, 3)             # startup rejects (Big Loss 5)

run_min     <- planned_min - breakdown_min - setup_min - small_stop_min
# reduced-speed loss (Big Loss 4): actual pace is a little slower than ideal
speed_factor <- c(0.94, 0.97, 0.90, 0.96, 0.93)
total_count <- round(run_min * 60 / ideal_cycle_s * speed_factor)
good_count  <- total_count - scrap_count - startup_scrap

shift_log <- data.frame(
  date                    = days,
  planned_production_min   = planned_min,
  breakdown_min            = breakdown_min,
  setup_adjustment_min     = setup_min,
  small_stops_min          = small_stop_min,
  ideal_cycle_time_s       = ideal_cycle_s,
  total_count              = total_count,
  scrap_count              = scrap_count,
  startup_reject_count     = startup_scrap,
  good_count               = good_count,
  stringsAsFactors = FALSE
)
write.csv(shift_log, file.path(out_dir, "precitech_shift_log.csv"), row.names = FALSE)

availability <- sum(run_min) / sum(planned_min)
performance  <- sum(ideal_cycle_s * total_count) / (sum(run_min) * 60)
quality      <- sum(good_count) / sum(total_count)
oee          <- availability * performance * quality

big_loss <- c(
  "Breakdowns"          = sum(breakdown_min),
  "Setup & adjustment"  = sum(setup_min),
  "Small stops"         = sum(small_stop_min),
  "Reduced speed (min-equiv)" = sum(run_min) * (1 - performance),
  "Startup rejects"     = sum(startup_scrap) * ideal_cycle_s[1] / 60,
  "Production rejects"   = sum(scrap_count) * ideal_cycle_s[1] / 60
)

rule("LAB 13 — TPM/OEE answer key")
cat(sprintf("Availability : %.1f %%\n", 100 * availability))
cat(sprintf("Performance  : %.1f %%\n", 100 * performance))
cat(sprintf("Quality      : %.1f %%\n", 100 * quality))
cat(sprintf("OEE (weekly) : %.1f %%\n", 100 * oee))
cat("\nSix Big Losses, ranked by lost minutes (equiv.):\n")
bl <- sort(big_loss, decreasing = TRUE)
for (nm in names(bl)) cat(sprintf("  %-28s %6.1f min\n", nm, bl[nm]))
cat(sprintf("\nDominant Big Loss: %s\n", names(bl)[1]))
cat("\nAI4I 2020 failure-mode Pareto (known dataset counts, ~339 failures):\n")
cat("  HDF (heat dissipation) ~ OSF (overstrain) ~ PWF (power)  >  TWF (tool wear)  >  RNF (random)\n")
cat("  RNF is injected noise — exclude it from corrective action.\n")
cat("  Failure rate ~ 3.4 %  =>  accuracy is a useless metric; use precision/recall.\n")
cat("Wrote ", file.path(out_dir, "precitech_shift_log.csv"), "\n", sep = "")

# ─────────────────────────────────────────────────────────────────────────────
# Lab 14 — RoboDK work cell: expected cycle time vs takt
# ─────────────────────────────────────────────────────────────────────────────
rule("LAB 14 — RoboDK work cell answer key")
cat(sprintf("Takt time (from Lab 4): %.1f s/kit\n", takt_seconds))
cat("Expected simulated single-part cycle time, mid-size 6-axis arm:\n")
cat("  first working program : ~ 12-22 s   (default joint speeds, generous approaches)\n")
cat("  after optimisation    : ~ 7-14 s    (reordered targets, faster joints, short approaches)\n")
cat(sprintf("One robot meets takt comfortably (cycle << %.0f s); the teaching point\n",
            takt_seconds))
cat("is the optimisation method and the guarding-distance calculation, not a\n")
cat("capacity shortfall.\n")

rule("DONE")
cat("Stage the two CSVs from ./lab_data/ on FOL. Do not commit them.\n")
