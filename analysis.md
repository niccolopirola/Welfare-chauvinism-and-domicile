# Analysis: The Role of the variable Domicile in Welfare Chauvinism

**Niccolò Pirola**

> **Abstract.** The same samples taken in consideration inside my thesis on welfare chauvinism (to read it, check out my LinkedIn page), are re-analysed with an additional level of analysis regarding the respondent's domicile. The regression results show that the centre-outskirts cleavage variable is significant, which in turn raises some considerations about the weight of several other variables in the model.

The regression was re-estimated on the same sample (ESS Round 8), using the same Model 1 and adding dummies derived from the `domicil` item provided by the survey service itself. The results are interesting and open up a new line of analysis. The non-significant variables remain those measuring objective economic conditions, as already shown in the earlier models. The real change is that the variable for living on a farm or in an isolated countryside home is highly significant.

## Model with domicile (N = 31,563)

| Variable | β | SE (cluster-robust) | t | p | Sig. |
|---|---|---|---|---|---|
| Constant | 3.0309 | 0.1273 | 23.816 | < 0.001 | *** |
| Unemployed (`unemployed`) | -0.0258 | 0.0717 | -0.360 | 0.719 | n.s. |
| Household income (`hinctnta`) | -0.0038 | 0.0038 | -0.990 | 0.322 | n.s. |
| Left–right self-placement (`lrscale`) | 0.0622 | 0.0134 | 4.652 | < 0.001 | *** |
| Education (`eisced`) | -0.0495 | 0.0081 | -6.083 | < 0.001 | *** |
| Age (`agea`) | 0.0031 | 0.0010 | 3.021 | 0.0025 | ** |
| Gender (`female`) | -0.0402 | 0.0167 | -2.411 | 0.0159 | * |
| Suburbs of a big city (`dom_suburbs`) | 0.0813 | 0.0316 | 2.574 | 0.0101 | * |
| Town or small city (`dom_town`) | 0.0555 | 0.0506 | 1.097 | 0.273 | n.s. |
| Country village (`dom_village`) | 0.1005 | 0.0368 | 2.731 | 0.0063 | ** |
| Farm or home in the countryside (`dom_farm`) | 0.1325 | 0.0342 | 3.878 | < 0.001 | *** |

Reference category: big city. Country fixed effects included but not reported.
R² = 0.1099; adjusted R² = 0.1089. Cluster-robust Wald F: F(32, 31530) = 119.00, p < 0.001.

The results led me to two questions:

- Which variable has the greater influence: ideological self-placement, or the objective condition of living in isolated rural areas?
- Assuming that support for ethnically conditional access to welfare is shaped, to some degree still to be determined, by the respondent's exposure to an immigrant community, how might living in contact with a different culture interact with living in an isolated place?

## First question: standardised coefficients

I was able to answer the first question, although it raised a methodological doubt. A quick look at the regression table shows that the coefficient on `dom_farm` (0.1325) is larger than the one on `lrscale` (0.0622). Comparing them this way is misleading, however, because the two variables are measured on different scales. Self-placement runs from 0 to 10, and its β is the change in the outcome for a one-step move along that scale. Living in the isolated countryside, by contrast, is a dummy variable that can be thought of as a Boolean taking the value 0 or 1. To answer the question properly, I standardised the coefficients to see how much each actually contributes to explaining *y*:

$$
\beta_j^{std} = \hat{\beta}_j \cdot \frac{SD(X_j)}{SD(Y)}
$$

Here $\hat{\beta}_j$ is the raw estimate taken directly from the table (0.0622), multiplied by the standard deviation of self-placement and divided by the standard deviation of *y*. The same procedure is then repeated for `dom_farm`.

| Variable | Standardised β |
|---|---|
| `lrscale` | 0.134 |
| `dom_farm` | 0.032 |

Ideological self-placement therefore turns out to be about four times as influential as domicile. This confirms that, among all the variables observed, self-placement is by far the most influential.

## Second question: exposure and isolation

I do not yet have an answer to the second question, and my hypothesis pulls in two directions. On the one hand, I would expect greater exposure to an immigrant population to foster a more exclusionary attitude. On the other, this does not square with the fact that voting in city centres tends to be more liberal and moderate (Kovalcsik & Nzimande, 2019). At the same time, exposure to ethnically different communities, especially in settings of urban and economic decline, does appear to increase exclusionary attitudes, through the cognitive mechanism that Scheiring et al. (2026) describe with regard to healthcare provision.

Since immigrant communities tend to settle in the suburbs of large cities, where jobs and members of the same communities are more plentiful, I suspect that chauvinist attitudes in isolated rural areas cannot be explained by the presence of, and coexistence with, ethnically different groups. I apply the same reasoning in the opposite direction: in cities, where immigrant communities are denser, living in a central, urbanised, well-served and generally wealthier area seems to have a stronger effect on the outcome I am studying.

This reasoning still needs empirical support, which is why I would like to take the analysis further with data in hand.

## References

- Kovalcsik, T., & Nzimande, N. P. (2019). Theories of the voting behaviour in the context of electoral and urban geography. *Belvedere Meridionale*, 31(4), 207–220.
- Scheiring, G., Jeannet, A.-M., & Stuckler, D. (2026). 'They Take Our Healthcare': Health and Attitudes towards Immigration in Europe. *Comparative Political Studies*, 59(3), 653–697.
