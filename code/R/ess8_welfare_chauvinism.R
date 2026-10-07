# =============================================================================
# Welfare chauvinism and domicile: WLS regression on ESS Round 8 (2016)
# =============================================================================
#
# Author: Niccolò Pirola
#
# Estimates two models of welfare chauvinism on the ESS Round 8 integrated file:
#   - Model 1 (baseline): economic risk, ideology, education, age, gender
#   - Domicile model:     Model 1 + dummies for the respondent's domicile
#
# Both models use WLS with the ESS analysis weight `anweight`, country fixed
# effects and standard errors clustered by country (sandwich::vcovCL, HC1).
# Standardised coefficients are computed as beta * SD(X) / SD(Y).
#
# Usage (from RStudio or the terminal):
#   Rscript ess8_welfare_chauvinism.R path/to/ESS8e02_3.csv
#
# The data file is not included in the repository: download it for free from
# https://ess.sikt.no (CSV, Stata .dta and SPSS .sav are all accepted).
# =============================================================================

# install.packages(c("sandwich", "lmtest"))         # once
# install.packages("haven")                         # only for .dta / .sav files
suppressPackageStartupMessages({
  library(sandwich)
  library(lmtest)
})

# -----------------------------------------------------------------------------
# 1. Settings
# -----------------------------------------------------------------------------

args <- commandArgs(trailingOnly = TRUE)
data_path <- if (length(args) > 0) args[1] else file.path("data", "ESS8e02_3.csv")

raw_vars  <- c("cntry", "anweight", "imsclbn", "mnactic", "hinctnta",
               "lrscale", "eisced", "agea", "gndr", "domicil")
base_vars <- c("unemployed", "hinctnta", "lrscale", "eisced", "agea", "female")
dom_vars  <- c("dom_suburbs", "dom_town", "dom_village", "dom_farm")

# -----------------------------------------------------------------------------
# 2. Data loading and recoding
# -----------------------------------------------------------------------------

load_ess <- function(path) {
  if (!file.exists(path)) {
    stop("Data file not found: ", path,
         "\nDownload ESS Round 8 from https://ess.sikt.no and pass its path.")
  }
  ext <- tolower(tools::file_ext(path))
  df <- switch(ext,
    csv = read.csv(path, stringsAsFactors = FALSE),
    dta = haven::zap_labels(haven::read_dta(path)),
    sav = haven::zap_labels(haven::read_sav(path)),
    stop("Unsupported file type: ", ext)
  )
  as.data.frame(df)[, raw_vars]
}

# Keep a value only if it lies in the valid range, otherwise NA
valid <- function(x, lo, hi) ifelse(x >= lo & x <= hi, x, NA)

recode_ess <- function(df) {
  d <- data.frame(cntry = df$cntry, anweight = df$anweight)

  # Dependent variable: "When should immigrants obtain rights to social
  # benefits/services?" 1 = immediately on arrival ... 5 = never.
  d$y <- valid(df$imsclbn, 1, 5)

  # Main activity: 3 / 4 = unemployed (looking / not looking for a job)
  act <- valid(df$mnactic, 1, 9)
  d$unemployed <- ifelse(is.na(act), NA, as.numeric(act %in% c(3, 4)))

  d$hinctnta <- valid(df$hinctnta, 1, 10)   # household income decile
  d$lrscale  <- valid(df$lrscale, 0, 10)    # left-right self-placement
  d$eisced   <- valid(df$eisced, 1, 7)      # education, ES-ISCED
  d$agea     <- valid(df$agea, 14, 120)     # age in years

  g <- ifelse(df$gndr %in% c(1, 2), df$gndr, NA)
  d$female <- ifelse(is.na(g), NA, as.numeric(g == 2))

  # Domicile: 1 = big city (reference), 2 = suburbs, 3 = town or small city,
  # 4 = country village, 5 = farm or home in countryside
  dom <- valid(df$domicil, 1, 5)
  for (i in seq_along(dom_vars)) {
    d[[dom_vars[i]]] <- ifelse(is.na(dom), NA, as.numeric(dom == i + 1))
  }
  d
}

# -----------------------------------------------------------------------------
# 3. Estimation
# -----------------------------------------------------------------------------

fit_wls <- function(d, xvars) {
  sample <- na.omit(d[, c("y", "anweight", "cntry", xvars)])
  sample <- sample[sample$anweight > 0, ]
  f <- reformulate(c(xvars, "factor(cntry)"), response = "y")
  fit <- lm(f, data = sample, weights = anweight)
  vc  <- vcovCL(fit, cluster = ~cntry, type = "HC1")
  list(fit = fit, vcov = vc, sample = sample, xvars = xvars)
}

# Joint cluster-robust Wald F test on the substantive covariates only.
# With G clusters the cluster-robust covariance matrix has rank at most
# G - 1, so the country dummies are not included in the joint test.
wald_test <- function(m) {
  b <- coef(m$fit)[m$xvars]
  V <- m$vcov[m$xvars, m$xvars]
  q <- length(b)
  F <- as.numeric(t(b) %*% solve(V, b)) / q
  df2 <- df.residual(m$fit)
  c(F = F, df1 = q, df2 = df2, p = pf(F, q, df2, lower.tail = FALSE))
}

wsd <- function(x, w) {
  m <- weighted.mean(x, w)
  sqrt(weighted.mean((x - m)^2, w))
}

# beta_std = beta * SD(X) / SD(Y), weighted SDs on the estimation sample
standardised_betas <- function(m) {
  s <- m$sample
  sd_y <- wsd(s$y, s$anweight)
  sapply(m$xvars, function(v) coef(m$fit)[[v]] * wsd(s[[v]], s$anweight) / sd_y)
}

# -----------------------------------------------------------------------------
# 4. Output
# -----------------------------------------------------------------------------

stars <- function(p) ifelse(p < 0.001, "***", ifelse(p < 0.01, "**",
                     ifelse(p < 0.05, "*", "n.s.")))

report <- function(title, m) {
  ct <- coeftest(m$fit, vcov. = m$vcov)
  rows <- c("(Intercept)", m$xvars)
  tab <- data.frame(beta = ct[rows, 1], se_cluster = ct[rows, 2],
                    t = ct[rows, 3], p = ct[rows, 4])
  tab$sig <- stars(tab$p)
  w  <- wald_test(m)
  sm <- summary(m$fit)

  cat("\n", title, "  (N = ", format(nobs(m$fit), big.mark = ","), ")\n", sep = "")
  print(format(tab, digits = 4, nsmall = 4), quote = FALSE)
  cat(sprintf("R2 = %.4f; adjusted R2 = %.4f\n", sm$r.squared, sm$adj.r.squared))
  cat(sprintf("Joint cluster-robust Wald test on the covariates: F(%d, %d) = %.2f, p = %.4g\n",
              w["df1"], w["df2"], w["F"], w["p"]))
  cat("Countries (clusters):", length(unique(m$sample$cntry)),
      "- country fixed effects included, not shown.\n")
  invisible(tab)
}

# -----------------------------------------------------------------------------
# 5. Run
# -----------------------------------------------------------------------------

d <- recode_ess(load_ess(data_path))

m1 <- fit_wls(d, base_vars)
report("Model 1 - baseline", m1)

m2 <- fit_wls(d, c(base_vars, dom_vars))
report("Model with domicile", m2)

cat("\nStandardised coefficients (domicile model)\n")
print(round(standardised_betas(m2)[c("lrscale", "eisced", "dom_farm",
                                     "dom_village", "dom_suburbs")], 3))
