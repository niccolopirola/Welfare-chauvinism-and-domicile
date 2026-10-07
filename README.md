# Welfare-chauvinism-and-domicile
WLS regression on European Social Survey Round 8 microdata (considering 23 countries) testing whether domicile predicts welfare chauvinism attitudes, with standardised coefficients compared against ideological self-placement.

An appendix of the empirical analysis carried out for my undergraduate thesis on *Populism and the Welfare State* (Università Cattolica del Sacro Cuore, Milan, 2026). The regression model of the determinants of **welfare chauvinism** is re-estimated with the respondent's **domicile** added. The theoretical framework behind this appendix is based on Christophe Guilluy's studies regarding centre-outskirts cleavages in France, trying to verify with empirical data and expand the analysis on 23 European Countries. 

**Author:** Niccolò Pirola

## At a glance

- **Data:** European Social Survey, Round 8 (2016), integrated file ESS8e02_3 (ed. 2.3), 23 countries.
- **Dependent variable:** the item "When should immigrants obtain rights to social benefits/services?", recoded from 1 (immediately on arrival) to 5 (never).
- **Estimation:** WLS with the `anweight` weight, country fixed effects and standard errors clustered by country.
- **New in this analysis:** dummy variables for domicile (ESS variable `domicil`; reference category: big city).

## Key results

| Variable | β | p |
|---|---|---|
| Left–right self-placement (`lrscale`) | 0.0622 | < 0.001 |
| Education (`eisced`) | -0.0495 | < 0.001 |
| Suburbs of a big city | 0.0813 | 0.010 |
| Country village | 0.1005 | 0.006 |
| Farm or home in the countryside | 0.1325 | < 0.001 |
| Unemployment, household income | — | n.s. |

N = 31,563; R² = 0.110.

Living outside city centres is associated with more chauvinist attitudes. Once the coefficients are standardised, however, ideological self-placement (β\* = 0.134) weighs about four times as much as living in the isolated countryside (β\* = 0.032). Objective economic conditions remain non-significant.

## Contents

| File | Description |
|---|---|
| [`analysis.md`](analysis.md) | Full text of the analysis, readable directly on GitHub |
| [`docs/analysis_domicile_original_IT.pdf`](docs/analysis_domicile_original_IT.pdf) | Original version in Italian (PDF) |

## Key chart

![Mean welfare chauvinism by domicile](Welfare-chauvinism-and-domicile/figures/chauvinism_by_domicile.png)

## Open question

How do exposure to immigrant communities (denser in urban suburbs) and geographic isolation (rural areas) interact in shaping chauvinist attitudes? The next step is to test this empirically.

## Data

The ESS microdata are not included in this repository. They can be downloaded free of charge, after registration, from the [ESS Data Portal](https://ess.sikt.no).

> European Social Survey ERIC (2023). *ESS8 – integrated file, edition 2.3* [Data set]. Sikt – Norwegian Agency for Shared Services in Education and Research.
