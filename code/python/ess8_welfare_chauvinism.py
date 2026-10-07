"""
Welfare chauvinism and domicile: WLS regression on ESS Round 8 (2016)
=====================================================================

Author: Niccolò Pirola

Estimates two models of welfare chauvinism on the ESS Round 8 integrated file:

  - Model 1 (baseline): economic risk, ideology, education, age, gender
  - Domicile model:     Model 1 + dummies for the respondent's domicile

Both models use:
  - WLS with the ESS analysis weight `anweight`
  - country fixed effects
  - standard errors clustered by country (CR1, equivalent to R's
    sandwich::vcovCL(type = "HC1"))

It also computes standardised coefficients, beta_std = beta * SD(X) / SD(Y).

Usage
-----
    python ess8_welfare_chauvinism.py path/to/ESS8e02_3.csv

The data file is not included in the repository: download it for free from
https://ess.sikt.no (CSV, Stata .dta and SPSS .sav are all accepted).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

# ---------------------------------------------------------------------------
# 1. Settings
# ---------------------------------------------------------------------------

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "ESS8e02_3.csv"

RAW_VARS = [
    "cntry", "anweight", "imsclbn", "mnactic", "hinctnta",
    "lrscale", "eisced", "agea", "gndr", "domicil",
]

BASE_VARS = ["unemployed", "hinctnta", "lrscale", "eisced", "agea", "female"]
DOM_VARS = ["dom_suburbs", "dom_town", "dom_village", "dom_farm"]

LABELS = {
    "const": "Constant",
    "unemployed": "Unemployed (unemployed)",
    "hinctnta": "Household income decile (hinctnta)",
    "lrscale": "Left-right self-placement (lrscale)",
    "eisced": "Education, ES-ISCED (eisced)",
    "agea": "Age (agea)",
    "female": "Gender: female (female)",
    "dom_suburbs": "Suburbs of a big city (dom_suburbs)",
    "dom_town": "Town or small city (dom_town)",
    "dom_village": "Country village (dom_village)",
    "dom_farm": "Farm or home in countryside (dom_farm)",
}


# ---------------------------------------------------------------------------
# 2. Data loading and recoding
# ---------------------------------------------------------------------------

def load_ess(path: Path) -> pd.DataFrame:
    """Read the ESS file (csv, dta or sav), keeping only the needed columns."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, usecols=RAW_VARS, low_memory=False)
    elif suffix == ".dta":
        df = pd.read_stata(path, columns=RAW_VARS, convert_categoricals=False)
    elif suffix == ".sav":
        df = pd.read_spss(path, usecols=RAW_VARS, convert_categoricals=False)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    return df


def recode(df: pd.DataFrame) -> pd.DataFrame:
    """Recode ESS missing-value codes and build the model variables."""
    d = pd.DataFrame(index=df.index)
    d["cntry"] = df["cntry"]
    d["anweight"] = df["anweight"]

    # Dependent variable: "When should immigrants obtain rights to social
    # benefits/services?" 1 = immediately on arrival ... 5 = never.
    # Codes 7/8/9 (refusal, don't know, no answer) -> missing.
    d["y"] = df["imsclbn"].where(df["imsclbn"].between(1, 5))

    # Main activity in the last 7 days: 3 = unemployed, actively looking;
    # 4 = unemployed, not actively looking. Codes 66/77/88/99 -> missing.
    act = df["mnactic"].where(df["mnactic"].between(1, 9))
    d["unemployed"] = act.isin([3, 4]).astype(float).where(act.notna())

    # Household income decile (1-10); 77/88/99 -> missing
    d["hinctnta"] = df["hinctnta"].where(df["hinctnta"].between(1, 10))

    # Left-right self-placement (0-10); 77/88/99 -> missing
    d["lrscale"] = df["lrscale"].where(df["lrscale"].between(0, 10))

    # Education, ES-ISCED (1-7); 0/55/77/88/99 -> missing
    d["eisced"] = df["eisced"].where(df["eisced"].between(1, 7))

    # Age in years; 999 -> missing
    d["agea"] = df["agea"].where(df["agea"].between(14, 120))

    # Gender: 1 = male, 2 = female; 9 -> missing
    g = df["gndr"].where(df["gndr"].isin([1, 2]))
    d["female"] = (g == 2).astype(float).where(g.notna())

    # Domicile: 1 = big city (reference), 2 = suburbs, 3 = town or small
    # city, 4 = country village, 5 = farm or home in countryside
    dom = df["domicil"].where(df["domicil"].between(1, 5))
    for code, name in zip([2, 3, 4, 5], DOM_VARS):
        d[name] = (dom == code).astype(float).where(dom.notna())

    return d


# ---------------------------------------------------------------------------
# 3. Estimation
# ---------------------------------------------------------------------------

def fit_wls(d: pd.DataFrame, xvars: list[str]):
    """WLS with country fixed effects and country-clustered standard errors.

    Listwise deletion is applied on all variables of the model.
    """
    sample = d[["y", "anweight", "cntry"] + xvars].dropna()
    sample = sample[sample["anweight"] > 0]

    fe = pd.get_dummies(sample["cntry"], prefix="fe", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([sample[xvars], fe], axis=1))
    groups = pd.factorize(sample["cntry"])[0]

    model = sm.WLS(sample["y"], X, weights=sample["anweight"])
    # use_correction=True -> G/(G-1) * (N-1)/(N-K), same as vcovCL(type="HC1")
    res = model.fit(cov_type="cluster",
                    cov_kwds={"groups": groups, "use_correction": True},
                    use_t=True)
    return res, sample


def wald_test(res, names: list[str]):
    """Joint cluster-robust Wald F test that the listed coefficients are zero.

    Only the substantive covariates are tested, not the country dummies:
    with G clusters the cluster-robust covariance matrix has rank at most
    G - 1, so a joint test of more than G - 1 restrictions is not identified.
    """
    b = res.params[names].values
    V = res.cov_params().loc[names, names].values
    q = len(names)
    F = float(b @ np.linalg.solve(V, b)) / q
    df2 = res.df_resid
    p = stats.f.sf(F, q, df2)
    return F, q, df2, p


def weighted_sd(x: pd.Series, w: pd.Series) -> float:
    m = np.average(x, weights=w)
    return float(np.sqrt(np.average((x - m) ** 2, weights=w)))


def standardised_betas(res, sample: pd.DataFrame, xvars: list[str]) -> pd.Series:
    """beta_std = beta * SD(X) / SD(Y), weighted SDs on the estimation sample."""
    w = sample["anweight"]
    sd_y = weighted_sd(sample["y"], w)
    return pd.Series({v: res.params[v] * weighted_sd(sample[v], w) / sd_y
                      for v in xvars})


# ---------------------------------------------------------------------------
# 4. Output
# ---------------------------------------------------------------------------

def stars(p: float) -> str:
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."


def report(title: str, res, sample: pd.DataFrame, xvars: list[str]) -> pd.DataFrame:
    rows = ["const"] + xvars
    table = pd.DataFrame({
        "beta": res.params[rows],
        "se_cluster": res.bse[rows],
        "t": res.tvalues[rows],
    })
    # Two-sided p-values from a t distribution with the residual degrees of
    # freedom, as in R's lmtest::coeftest(). A more conservative alternative
    # with few clusters is t with G - 1 degrees of freedom.
    table["p"] = 2 * stats.t.sf(table["t"].abs(), res.df_resid)
    table["sig"] = table["p"].apply(stars)
    table.index = [LABELS[r] for r in rows]

    F, q, df2, p = wald_test(res, xvars)

    print(f"\n{title}  (N = {int(res.nobs):,})")
    print("-" * len(title))
    print(table.to_string(float_format=lambda v: f"{v:.4f}"))
    print(f"R2 = {res.rsquared:.4f}; adjusted R2 = {res.rsquared_adj:.4f}")
    print(f"Joint cluster-robust Wald test on the covariates: "
          f"F({q}, {int(df2)}) = {F:.2f}, p = {p:.4g}")
    print(f"Countries (clusters): {sample['cntry'].nunique()}; "
          f"country fixed effects included, not shown.")
    return table


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not path.exists():
        sys.exit(f"Data file not found: {path}\n"
                 "Download ESS Round 8 from https://ess.sikt.no and pass its path.")

    d = recode(load_ess(path))

    res1, s1 = fit_wls(d, BASE_VARS)
    report("Model 1 - baseline", res1, s1, BASE_VARS)

    xdom = BASE_VARS + DOM_VARS
    res2, s2 = fit_wls(d, xdom)
    report("Model with domicile", res2, s2, xdom)

    std = standardised_betas(res2, s2, xdom)
    print("\nStandardised coefficients (domicile model)")
    print(std[["lrscale", "eisced", "dom_farm", "dom_village", "dom_suburbs"]]
          .to_string(float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
