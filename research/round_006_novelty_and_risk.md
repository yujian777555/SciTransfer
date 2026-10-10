# Round 006 Novelty and Risk Analysis

**Date:** 2026-10-10  
**Status:** Independent review

---

## 1. Related work collision matrix

| Work | Year | Overlap | Gap / Non-overlap | Status |
|------|------|---------|-------------------|--------|
| **SciAgentGym/SciForge** | ICML 2026 | Cross-domain science tool transfer | Controlled process-strategy interventions, not tool-use | VERIFIED |
| **Memory Transfer Learning** | arXiv 2026 | Abstraction levels, negative transfer | Outcome-grounded paired RMSE, not memory similarity | VERIFIED |
| **MCMA** | ACL 2026 | Hierarchical memory abstraction | Selective abstention with risk-coverage | VERIFIED |
| **Co-Scientist** | Nature 2026 | Hypothesis generation | Process strategy transfer (not hypothesis) | VERIFIED |
| **Robin** | Nature 2026 | Bio hypothesis + experiments | Not isolated causal strategy transfer | VERIFIED |
| **AI Scientist** | Nature 2026 | Automated research lifecycle | Not selective cross-domain strategy | VERIFIED |
| **Metacognitive Steering** | arXiv 2025 | Scientific judgment control | Paired outcome identification | UNVERIFIED |
| **PrimeScientist** | — | — | Not checked | UNVERIFIED |
| **COGTRL** | — | — | Not checked | UNVERIFIED |
| **EvoScientist** | — | — | Not checked | UNVERIFIED |
| **MARS** | — | — | Not checked | UNVERIFIED |

---

## 2. Narrow contribution claims

**C1:** Causally identified cross-domain process-strategy transfer with paired held-out RMSE on real measured labels.

**C2:** Outcome-calibrated selective abstention with risk-coverage curves.

**C3:** Mechanism sensitivity analysis (why strategies help/harm).

---

## 3. Honest assessment

**Is "cross-domain process strategy" just CV hygiene?**

**Partially YES:**
- "Compare grouped vs random split" is standard ML practice
- "Check leakage before trusting results" is textbook advice

**But the RESEARCH contribution would be:**
1. Formalizing this as a transferable *process strategy* (not just advice)
2. Measuring causal effect with paired interventions
3. Quantifying when transfer helps vs hurts
4. Selective abstention based on predicted utility

**Verdict:** The *methodological insight* is not novel. The *causal measurement framework* could be, if executed rigorously.

---

## 4. CCF-B level plausibility

**CONDITIONAL:**
- Plausible if: rigorous paired design + real data + negative transfer results + strong baselines
- NOT plausible if: just applying standard CV to two datasets

**Key question:** Is there a genuine scientific insight beyond "use grouped CV"?

**Answer:** Probably NOT, unless the strategy captures something deeper about *when* to use which validation procedure based on observable diagnostics.

---

## 5. GO / NO-GO

**CONDITIONAL GO for micro-smoke:**
- ESOL + NOAA are genuine real-label datasets
- Independent scorer (RMSE on holdout) is well-defined
- BUT: novelty is narrow; need strong baselines and honest framing

**NO-GO if:**
- Strategy reduces to standard CV advice without added value
- Only 2 domains with no clear mechanism difference
- Labels contaminated by pretraining
