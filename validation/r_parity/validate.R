# validation/r_parity/validate.R
# Run metafor on the SAME BCG dataset used by Python tests.
# Reads yi/vi from data/built_in/bcg_vaccine.json so data matches exactly.
# Usage: Rscript validation/r_parity/validate.R  (from project root)
library(metafor)
library(jsonlite)

# Read the BCG data from the project's JSON file (same as Python uses)
data_path <- "data/built_in/bcg_vaccine.json"
if (!file.exists(data_path)) {
  stop("Cannot find ", data_path, " — run from project root")
}
studies <- fromJSON(data_path)
yi <- studies$yi
vi <- studies$vi

# Print yi and vi for data verification
cat("=== BCG yi/vi from JSON ===\n")
for (i in 1:length(yi)) {
  cat(sprintf("study %d: yi=%.10f  vi=%.10f\n", i, yi[i], vi[i]))
}
cat(sprintf("k=%d\n", length(yi)))
cat("===========================\n\n")

methods <- c("FE", "DL", "REML", "PM", "SJ", "ML")
results <- data.frame()

for (m in methods) {
  fit <- rma(yi=yi, vi=vi, method=m)
  results <- rbind(results, data.frame(
    method=m,
    theta=as.numeric(fit$beta),
    se=fit$se,
    tau2=fit$tau2,
    I2=fit$I2,
    p=fit$pval
  ))
}

# Write results CSV
# Find script directory from command-line args (works with Rscript)
args <- commandArgs(trailingOnly = FALSE)
script_arg <- args[grep("--file=", args)]
if (length(script_arg) > 0) {
  out_dir <- dirname(sub("--file=", "", script_arg))
} else {
  # Fallback: assume running from project root
  out_dir <- "validation/r_parity"
}
write.csv(results, file.path(out_dir, "bcg_r_results.csv"), row.names=FALSE)

cat("=== Estimator results ===\n")
print(results)
cat("=========================\n\n")

# Trim-and-fill
tf <- trimfill(rma(yi=yi, vi=vi, method="DL"))
cat(sprintf("tf_k0=%d\n", tf$k0))
cat(sprintf("tf_theta=%.10f\n", as.numeric(tf$beta)))
cat(sprintf("tf_se=%.10f\n", tf$se))

# Egger test
reg <- regtest(rma(yi=yi, vi=vi, method="FE"), model="lm")
cat(sprintf("egger_p=%.10f\n", reg$pval))

cat("\nR validation complete\n")
