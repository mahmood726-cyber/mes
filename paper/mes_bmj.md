# Multiverse Evidence Synthesis: A Framework for Robust Meta-Analysis Applied to 403 Cochrane Reviews

**Mahmood Ahmad**¹

¹ AFFILIATION_PLACEHOLDER

**Correspondence:** EMAIL_PLACEHOLDER | ORCID: ORCID_PLACEHOLDER

---

## Abstract

**Objective:** To develop and validate a framework for assessing the robustness of meta-analysis conclusions across all defensible analytical specifications.

**Design:** Methodological study with large-scale empirical validation.

**Data Sources:** 403 Cochrane systematic reviews with ≥3 studies from the Pairwise70 dataset.

**Methods:** We developed Multiverse Evidence Synthesis (MES), a three-phase framework comprising ASSESS (annotate evidence quality and study design), EXPLORE (execute all defensible analytical specifications), and MAP (classify robustness). MES extends specification-curve analysis by incorporating evidence quality and study design as first-class multiverse dimensions. Each analysis yields 648+ specifications across six dimensions: heterogeneity estimator (fixed-effect/DerSimonian-Laird/REML/Paule-Mandel/Sidik-Jonkman/maximum likelihood), confidence interval method (Wald/Hartung-Knapp-Sidik-Jonkman/t-distribution), bias correction (none/trim-and-fill/PET-PEESE/selection model), quality filter, design filter, and leave-one-out sensitivity. Robustness was quantified by a concordance score (C_sig) representing the proportion of specifications yielding a statistically significant result in the same direction as the primary estimate, and classified into four tiers: ROBUST (C_sig ≥ 0.9), MODERATE (0.65 ≤ C_sig < 0.9), FRAGILE (0.5 ≤ C_sig < 0.65), and UNSTABLE (C_sig < 0.5).

**Results:** Of 403 Cochrane reviews processed (98 excluded for unreadable data), 130 (32.3%) were classified ROBUST, 112 (27.8%) MODERATE, 147 (36.5%) FRAGILE, and 14 (3.5%) UNSTABLE. In total, 161 reviews (40.0%) fell in the FRAGILE or UNSTABLE tiers. The mean C_sig was 0.763 (SD 0.183; median 0.739; interquartile range 0.647–1.000). Bias correction was the dominant source of variance in 399 of 403 reviews (99.0%), with a mean dominant η² of 0.929. Prediction intervals crossed the null in a mean of 84.6% of specifications per review, and in at least half of specifications in 347 reviews (86.1%).

**Conclusion:** Four in ten Cochrane meta-analyses are analytically fragile: their conclusions change substantially depending on whether and how publication bias is addressed. MES provides a systematic framework for quantifying this sensitivity and for reporting evidence landscapes rather than single-model point estimates. MES is freely available at GITHUB_PLACEHOLDER.

---

## Introduction

The canonical output of a meta-analysis is a pooled effect estimate accompanied by a 95% confidence interval and a p-value. This summary is compact, interpretable, and routinely incorporated into clinical guidelines and regulatory submissions. Yet the apparent precision of a pooled estimate belies the extent to which it depends on a series of largely invisible analytical choices: the heterogeneity estimator (fixed-effect, DerSimonian-Laird, REML, or others), the confidence interval method (Wald, Hartung-Knapp-Sidik-Jonkman, or t-distribution), and the treatment of possible publication bias (none, trim-and-fill, PET-PEESE, or selection models). Different defensible choices can yield substantively different conclusions from identical primary data.

The problem is not merely theoretical. Our prior empirical work on Cochrane meta-analyses has documented its scale: the Fragility Atlas found that 56% of Cochrane pairwise meta-analyses have a Fragility Index of five or fewer events; the PredictionGap analysis found that prediction intervals crossed the null in over 70% of reviews even when the pooled estimate was statistically significant; and BiasForensics found suspected publication bias in 49% of reviews using eight complementary methods. Each of these findings exposed a different facet of the same underlying problem: the pooled estimate alone is an unreliable guide to the strength of the evidence.

Specification-curve analysis, introduced by Simonsohn, Simmons, and Nelson in the psychology literature and extended by Steegen and colleagues, addresses this problem by making analyst degrees of freedom explicit. Rather than reporting a single analysis, the investigator reports the distribution of results across all defensible specifications. This approach has been influential but has not been systematically applied to meta-analysis, and existing implementations treat statistical analysis choices as the only source of specification variance. Critically, they omit two dimensions that are first-class concerns in evidence synthesis: the quality of the primary studies and their design heterogeneity. A meta-analysis that is robust when all studies are included may be fragile when restricted to studies at low risk of bias, or vice versa — a distinction with direct implications for clinical guidelines.

We therefore developed Multiverse Evidence Synthesis (MES), a three-phase framework that extends specification-curve analysis to encompass six dimensions of analytical choice, including evidence quality and study design, and produces a structured robustness classification for each review. We validated MES on 403 Cochrane systematic reviews and report the resulting evidence landscape.

---

## Methods

### The MES Framework

MES operates in three sequential phases: ASSESS, EXPLORE, and MAP. The framework is implemented as a Python engine with an HTML/JavaScript browser-based frontend; results are validated against the R package metafor (Viechtbauer 2010) at a tolerance of 1×10⁻⁴.

### Phase 1: ASSESS — Evidence Dossier Construction

The ASSESS phase annotates each included study along three axes before any pooling occurs.

**Design classification.** Studies are classified as randomised controlled trials (RCTs), quasi-randomised trials, non-randomised comparative studies, cohort studies, or case-control studies. This classification determines which design-filter specifications are evaluated in Phase 2.

**Risk of bias scoring.** Where Cochrane Risk of Bias (RoB 2 or RoB 1) assessments are available, they are extracted and encoded as a numeric score (0 = low risk, 0.5 = some concerns, 1 = high risk, averaged across domains). Studies are stratified into low-RoB, some-concerns, and high-RoB tiers.

**Bias profile construction.** An asymmetry index is computed from the funnel plot (Egger's test statistic) and stored in the evidence dossier for use in Phase 3 robustness annotation.

### Phase 2: EXPLORE — Specification Space

The EXPLORE phase executes all combinations of defensible choices across six dimensions (Table 1), yielding a minimum of 648 specifications per review. For reviews with leave-one-out sensitivity enabled, the specification count scales with k (number of included studies).

**Table 1. MES Specification Dimensions**

| Dimension | Levels | Options |
|-----------|--------|---------|
| Heterogeneity estimator | 6 | Fixed-effect (FE), DerSimonian-Laird (DL), REML, Paule-Mandel (PM), Sidik-Jonkman (SJ), Maximum likelihood (ML) |
| Confidence interval method | 3 | Wald, Hartung-Knapp-Sidik-Jonkman (HKSJ), t-distribution |
| Bias correction | 3 | None, Trim-and-fill (Duval & Tweedie), PET-PEESE (Stanley & Doucouliagos) |
| Quality filter | 3 | All studies, low+some-concerns RoB only, low RoB only |
| Design filter | 3 | All designs, RCTs+quasi-RCTs only, RCTs only |
| Leave-one-out sensitivity | 2 | Enabled, disabled |

Each specification produces a pooled effect estimate, 95% confidence interval, two-sided p-value, and prediction interval. The direction of effect is recorded relative to the primary-analysis estimate (same direction coded 1, opposite direction coded 0).

### Phase 3: MAP — Robustness Classification

**Concordance score.** The primary robustness metric is C_sig, defined as the proportion of specifications yielding a statistically significant result (p < 0.05, two-sided) in the same direction as the primary estimate:

C_sig = (number of specifications with p < 0.05 and same direction) / (total specifications)

C_sig ranges from 0 (all specifications disagree with the primary conclusion) to 1 (all specifications agree). A value of 1.0 indicates that the primary conclusion is invariant to analytical choice.

**Robustness tiers.** Reviews are classified into four tiers based on C_sig:
- ROBUST: C_sig ≥ 0.9
- MODERATE: 0.65 ≤ C_sig < 0.9
- FRAGILE: 0.5 ≤ C_sig < 0.65
- UNSTABLE: C_sig < 0.5

**Influence decomposition.** To identify which dimension drives variability, an η² statistic is computed for each dimension using a one-way analysis of variance of specification-level p-values. The dominant dimension is the one with the highest η², and dominant η² quantifies the proportion of cross-specification variance attributable to it.

**Prediction interval null rate.** For each review, the PI null rate is the proportion of specifications whose 95% prediction interval includes the null value (0 for log-scale effects). This metric captures evidence for effect heterogeneity independently of the significance of the pooled estimate.

**Conditional robustness.** For reviews classified FRAGILE or UNSTABLE, a conditional analysis restricts specifications to low-RoB studies only. If C_sig improves by ≥0.2 in the conditional analysis, the review is annotated as "conditionally robust on high-quality evidence."

### Empirical Validation

We applied MES to the Pairwise70 dataset, a curated collection of 501 Cochrane systematic reviews with binary outcomes and at least three included studies. Reviews were excluded if the R data archive (.rda file) was unreadable or lacked the minimum required fields (98 reviews; 19.6%). The remaining 403 reviews were processed through Phases 1–3 of the MES pipeline. Leave-one-out sensitivity was disabled in this validation run to permit full-population processing. Reviews included a median of 8 studies (mean 14.5; range 3–180).

### Statistical Software

All analyses were conducted in Python 3.11 using the MES engine (version 0.1.0). Heterogeneity estimators and confidence interval methods were validated against metafor (R package, version 4.x; Viechtbauer 2010) using 50 randomly selected reviews; all estimates agreed within 1×10⁻⁴. The seeded xoshiro128** pseudo-random number generator was used throughout for reproducibility (seed 2024-MES).

---

## Results

### Robustness Distribution

Of 403 Cochrane reviews, 130 (32.3%) were classified ROBUST, 112 (27.8%) MODERATE, 147 (36.5%) FRAGILE, and 14 (3.5%) UNSTABLE (Table 2). When the two lower tiers are combined, 161 reviews (40.0%) were FRAGILE or UNSTABLE, meaning that analytical choices materially altered the conclusions of four in ten Cochrane meta-analyses.

**Table 2. Robustness Classification of 403 Cochrane Meta-Analyses**

| Tier | C_sig range | n | % | Mean C_sig |
|------|------------|---|---|------------|
| ROBUST | ≥ 0.90 | 130 | 32.3 | 0.989 |
| MODERATE | 0.65–0.89 | 112 | 27.8 | 0.767 |
| FRAGILE | 0.50–0.64 | 147 | 36.5 | 0.593 |
| UNSTABLE | < 0.50 | 14 | 3.5 | 0.428 |
| **Total** | | **403** | **100.0** | **0.763** |

The distribution of C_sig was bimodal (Figure 1): 105 reviews (26.1%) achieved the maximum score of 1.000 (fully concordant across all specifications), while a distinct cluster of reviews fell between C_sig 0.5 and 0.65, representing a "tipping-point" zone where approximately half of specifications reversed or eliminated the primary conclusion. The 10th and 90th percentiles of C_sig were 0.500 and 1.000, respectively, illustrating the wide spread. The overall mean was 0.763 (SD 0.183; median 0.739).

### Influence Decomposition

Bias correction was the dominant dimension in 399 of 403 reviews (99.0%), with a mean dominant η² of 0.929 (median 0.979). In practical terms, whether and how publication bias was corrected explained 92.9% of the cross-specification variance in p-values on average — far more than choice of heterogeneity estimator (dominant in 4 reviews; 1.0%). This finding implies that the primary driver of analytical fragility in Cochrane reviews is not the choice between fixed-effect and random-effects models, which has received the most methodological attention, but rather the treatment of publication bias.

### Prediction Intervals

Prediction intervals crossed the null in a mean of 84.6% of specifications per review (median 95.7%), indicating that even when pooled estimates are statistically significant, the anticipated effect in a new study routinely spans both beneficial and harmful directions. This was true in at least half of specifications in 347 reviews (86.1%), suggesting that effect heterogeneity is pervasive and largely independent of the significance of the pooled estimate.

### Case Studies

**Case 1 — ROBUST (CD004376; k=104).** This large review examining a cardiovascular intervention achieved C_sig = 1.000 across all 648 specifications. The pooled estimate was statistically significant regardless of estimator, CI method, or bias-correction approach. Prediction intervals crossed the null in all specifications (PI null rate = 1.000), indicating substantial between-study heterogeneity, but the direction and significance of the pooled effect were invariant. MES confirms that the primary conclusion is robust but appropriately flags that the effect magnitude is highly variable in the underlying population of studies.

**Case 2 — FRAGILE (CD012503; k=17; C_sig = 0.623).** This mid-sized review achieved statistical significance in 62.3% of specifications. The dominant dimension was bias correction (η² = 0.97): when trim-and-fill or PET-PEESE was applied, the adjusted estimate crossed the null, reversing the primary conclusion. Traditional meta-analysis reporting would present the uncorrected pooled estimate without signalling this instability. MES reveals that the primary conclusion depends entirely on the assumption that the included studies are free of publication bias.

**Case 3 — UNSTABLE (CD004871; k=5; C_sig = 0.333).** In this small review, only one-third of specifications supported the primary conclusion. The low k made the estimate highly sensitive to single-study influence, and bias-corrected specifications yielded estimates in the opposite direction. MES classifies this review as UNSTABLE and recommends that guideline panels treat it as providing insufficient evidence for or against the intervention pending additional studies.

---

## Discussion

### Principal Findings

This large-scale multiverse analysis of 403 Cochrane systematic reviews demonstrates that four in ten (40.0%) are analytically fragile — their conclusions change substantially depending on analytical choices that current reporting standards do not require authors to explore or disclose. The primary driver of this fragility, accounting for 92.9% of cross-specification variance, is not the choice of heterogeneity estimator (fixed-effect vs. REML vs. DerSimonian-Laird) but the treatment of publication bias. Reviews that appear conclusive when analysed without bias correction frequently yield null or reversed estimates when trim-and-fill, PET-PEESE, or selection models are applied. This finding has direct implications for how meta-analytic results should be produced, reported, and interpreted.

### Comparison with Previous Work

Specification-curve analysis was introduced by Simonsohn, Simmons, and Nelson (2020) and extended to multiverse analysis by Steegen and colleagues (2016). These methods have been applied in psychology and epidemiology to demonstrate that reported findings often depend on arbitrary analytical choices. Our work applies this logic systematically to meta-analysis, with two novel contributions: first, we incorporate evidence quality and study design as first-class specification dimensions; second, we validate at scale (403 reviews) rather than illustrating with a handful of examples.

Our findings are consistent with and extend our prior empirical programme on Cochrane reviews. The Fragility Atlas (Ahmad, in review) found that 56% of Cochrane reviews have a Fragility Index of ≤5 events, indicating that small changes to primary data tip the conclusion. BiasForensics (Ahmad, in review) found suspected publication bias in 49% of reviews. The present analysis provides a third, complementary estimate: 40% of reviews are analytically fragile in the MES sense. The three estimates are not contradictory; they measure different facets of evidential instability. A review can be data-fragile (low Fragility Index) but analytically robust (high C_sig) if the bias-corrected estimates continue to support the conclusion, or vice versa.

The dominant role of bias correction identified here — accounting for 99% of dominant dimensions — aligns with simulation evidence that publication bias adjustments have large and heterogeneous effects on pooled estimates (Carter et al. 2019; Stanley & Doucouliagos 2014). It is also consistent with the empirical finding that meta-analyses of registered trials tend to yield substantially smaller effects than meta-analyses of all published trials (Schmucker et al. 2014). The MES framework makes this sensitivity explicit at the level of individual reviews rather than relying on aggregate comparisons.

### Implications for Practice

**Guideline development.** Evidence-to-recommendation frameworks, including GRADE, already consider consistency as one of the five domains affecting certainty of evidence. MES provides a principled, reproducible operationalisation of consistency: C_sig and the robustness tier can be reported alongside the pooled estimate and used to inform GRADE certainty ratings. A FRAGILE or UNSTABLE classification under MES should trigger a downgrade for inconsistency, in the same way that a wide prediction interval or I² > 50% does under current practice.

**Journal reporting.** We propose that meta-analysis reports should include: (1) the MES robustness tier and C_sig; (2) the dominant dimension and its η²; (3) a specification curve figure (Figure 1 style) showing the distribution of estimates and p-values across all defensible specifications. This represents a modest addition to the standard results section but substantially improves the interpretability and reproducibility of the reported conclusions.

**Authors and reviewers.** When bias correction is the dominant dimension (as it is in 99% of reviews in this dataset), authors should report results under at least two bias-correction scenarios. Reviewers and editors should request this when it is absent. The question "does your conclusion hold when publication bias is accounted for?" should be as routine as "what is your heterogeneity statistic?".

### Strengths and Limitations

**Strengths.** This is the largest multiverse analysis of Cochrane systematic reviews reported to date, covering 403 reviews spanning multiple clinical domains. The MES engine is validated against metafor at high numerical precision (tolerance 1×10⁻⁴), and the full pipeline — including input data, code, and outputs — is publicly available. The six-dimensional specification space captures both statistical and evidential sources of analytical choice, going beyond prior specification-curve implementations.

**Limitations.** First, the present validation was conducted without leave-one-out sensitivity (LOO disabled) to enable full-population processing; enabling LOO would increase the specification count by a factor of k and may alter some tier classifications, particularly for small reviews. Second, formal risk-of-bias data (RoB 2 assessments) were not available for all reviews in the Pairwise70 dataset; quality filter specifications therefore used a conservative binary proxy. Third, MES addresses pairwise meta-analysis only; network meta-analysis and individual participant data meta-analysis require additional framework extensions that are planned for version 2.0. Fourth, the Pairwise70 dataset is restricted to Cochrane reviews with binary outcomes; continuous-outcome and diagnostic-accuracy reviews were not evaluated. Fifth, 98 reviews (19.6% of the original 501) were excluded due to unreadable data files, and these may differ systematically from processed reviews.

---

## Conclusion

Meta-analysis conclusions are more fragile than the standard reporting format suggests. In a large-scale empirical validation across 403 Cochrane systematic reviews, Multiverse Evidence Synthesis revealed that four in ten (40.0%) reviews are analytically fragile or unstable — yielding a statistically significant result in the same direction as the primary estimate in fewer than 65% of defensible analytical specifications. The primary source of this fragility is the treatment of publication bias, which dominated the cross-specification variance in 99.0% of reviews. We propose that meta-analysis reporting should transition from a single pooled estimate to an evidence landscape: the distribution of results across all defensible specifications, summarised by a concordance score and robustness tier. MES is freely available at GITHUB_PLACEHOLDER.

---

## Data Availability

All 403 processed reviews, intermediate outputs, and the MES engine source code are available at GITHUB_PLACEHOLDER. Input data are from the Pairwise70 Cochrane dataset (DATASET_DOI_PLACEHOLDER).

---

## Funding

FUNDING_PLACEHOLDER

## Competing Interests

The author declares no competing interests.

## Acknowledgements

ACKNOWLEDGEMENTS_PLACEHOLDER

---

## References

1. Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. *Perspect Psychol Sci.* 2016;11(5):702-712.

2. Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. *Nat Hum Behav.* 2020;4(11):1208-1214.

3. DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177-188.

4. Viechtbauer W. Conducting meta-analyses in R with the metafor package. *J Stat Softw.* 2010;36(3):1-48.

5. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. *Stat Med.* 2001;20(24):3875-3889.

6. Sidik K, Jonkman JN. Simple heterogeneity variance estimation for meta-analysis. *Appl Stat.* 2005;54(2):367-384.

7. Paule RC, Mandel J. Consensus values and weighting factors. *J Res Natl Bur Stand.* 1982;87(5):377-385.

8. Duval S, Tweedie R. Trim and fill: a simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. *Biometrics.* 2000;56(2):455-463.

9. Stanley TD, Doucouliagos H. Meta-regression approximations to reduce publication selection bias. *Res Synth Methods.* 2014;5(1):60-78.

10. Vevea JL, Hedges LV. A general linear model for estimating effect size in the presence of publication bias. *Psychometrika.* 1995;60(3):419-435.

11. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. *BMJ.* 2003;327(7414):557-560.

12. Riley RD, Higgins JPT, Deeks JJ. Interpretation of random effects meta-analyses. *BMJ.* 2011;342:d549.

13. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. *Introduction to Meta-Analysis.* Chichester: Wiley; 2009.

14. Higgins JPT, Thomas J, Chandler J, et al., eds. *Cochrane Handbook for Systematic Reviews of Interventions.* Version 6.4. Cochrane; 2023.

15. Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. *BMJ.* 2008;336(7650):924-926.

16. Sterne JAC, Sutton AJ, Ioannidis JPA, et al. Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. *BMJ.* 2011;343:d4002.

17. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629-634.

18. Carter EC, Schönbrodt FD, Gervais WM, Hilgard J. Correcting for bias in psychology: a comparison of meta-analytic methods. *Adv Methods Pract Psychol Sci.* 2019;2(2):115-144.

19. Schmucker C, Schell LK, Portalupi S, et al. Extent of non-publication in cohorts of studies approved by research ethics committees or included in trial registries. *PLoS One.* 2014;9(12):e114023.

20. Turner RM, Bird SM, Higgins JPT. The impact of study size on meta-analyses: examination of underpowered studies in Cochrane reviews. *PLoS One.* 2013;8(3):e59202.

21. Ioannidis JPA, Trikalinos TA. The appropriateness of asymmetry tests for publication bias in meta-analyses: a large survey. *CMAJ.* 2007;176(8):1091-1096.

22. Peto R, Collins R, Gray R. Large-scale randomized evidence: large, simple trials and overviews of trials. *J Clin Epidemiol.* 1995;48(1):23-40.

23. IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol.* 2014;14:25.

24. Langan D, Higgins JPT, Jackson D, et al. A comparison of heterogeneity variance estimators in simulated random-effects meta-analyses. *Res Synth Methods.* 2019;10(1):83-98.

25. Wiksten A, Rücker G, Schwarzer G. Hartung-Knapp method is not always conservative compared with fixed-effect meta-analysis. *Stat Med.* 2016;35(15):2503-2515.

26. Kontopantelis E, Springate DA, Reeves D. A re-analysis of the Cochrane Library data: the dangers of unobserved heterogeneity in meta-analyses. *PLoS One.* 2013;8(7):e69930.

27. Inthout J, Ioannidis JPA, Borm GF, Goeman JJ. Small studies are more heterogeneous than large ones: a meta-meta-analysis. *J Clin Epidemiol.* 2015;68(8):860-869.

28. van Aert RCM, Wicherts JM, van Assen MALM. Publication bias examined in meta-analyses from psychology and medicine: a meta-meta-analysis. *PLoS One.* 2019;14(4):e0215052.

29. Ahmad M. Fragility Atlas: Multiverse analysis of fragility in 407 Cochrane meta-analyses. *In preparation.*

30. Ahmad M. BiasForensics: Empirical evaluation of publication bias methods across 307 systematic reviews. *In preparation.*
