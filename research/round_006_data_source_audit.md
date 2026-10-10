# Round 006 Data Source Audit — Real Scientific Data Feasibility

**Date:** 2026-10-10  
**Status:** DOCUMENTATION ONLY — no bulk download, no execution

---

## 1. CHEMISTRY: Delaney ESOL (PRIMARY)

| Item | Status | Evidence |
|------|--------|----------|
| **URL** | https://github.com/deepchem/deepchem/blob/master/deepchem/molnet/load_function/delaney_datasets.py | VERIFIED_DOC |
| **Dataset** | Delaney ESOL, 1,128 molecules | VERIFIED_DOC |
| **Labels** | Experimental log aqueous solubility (measured) | VERIFIED_DOC |
| **Format** | SMILES + measured value | VERIFIED_DOC |
| **Split** | Scaffold split (default in DeepChem) | VERIFIED_DOC |
| **Software license** | MIT (DeepChem code) | VERIFIED_DOC |
| **Data license** | Original Delaney paper terms | UNCERTAIN |
| **Size** | ~1,128 rows, small CSV | VERIFIED_DOC |
| **Runtime** | Python + RDKit + sklearn | VERIFIED_DOC |
| **CPU cost** | Low (1128 molecules, standard descriptors) | VERIFIED_DOC |

**Key findings:**
- Genuine experimentally measured solubility values (not simulated)
- Scaffold split provides molecularly disjoint holdout
- Well-established baselines (RDKit + Ridge/RF)
- **Risk:** 1,128 samples may be underpowered for multi-round benchmark
- **Risk:** Labels may be memorized by pretrained LLMs

**Verification status:** `VERIFIED_OFFICIAL_DOC` (API and loader documented; runtime not tested this round)

---

## 2. SPATIAL: NOAA GHCN-Daily (PRIMARY SECOND DOMAIN)

| Item | Status | Evidence |
|------|--------|----------|
| **URL** | https://www.ncei.noaa.gov/pub/data/ghcn/daily/ | VERIFIED_DOC |
| **Dataset** | GHCN-Daily station observations | VERIFIED_DOC |
| **Labels** | Real measured temperature/precipitation | VERIFIED_DOC |
| **Format** | Station/year/variable records with QC flags | VERIFIED_DOC |
| **License** | NOAA public data (US Government) | VERIFIED_DOC |
| **Size** | Full archive: multi-GB (DO NOT download) | VERIFIED_DOC |
| **Bounded subset** | Small region + year feasible | UNCERTAIN |
| **Runtime** | Python + pandas + scipy | VERIFIED_DOC |

**Key findings:**
- Real weather station measurements (not simulated)
- QC flags (M, Q, S) for data quality filtering
- Spatial blocking feasible (station clusters)
- **Risk:** Temporal autocorrelation makes spatial task easy
- **Risk:** Need to verify enough stations per region for holdout

**Verification status:** `VERIFIED_OFFICIAL_DOC` (NOAA catalog confirmed; bounded subset not yet selected)

---

## 3. BIO: Bioconductor airway/pasilla (CONDITIONAL)

| Item | Status | Evidence |
|------|--------|----------|
| **URL** | https://bioconductor.org/packages/release/data/experiment/html/airway.html | VERIFIED_DOC |
| **Dataset** | RNA-seq counts (4 cell lines, drug vs control) | VERIFIED_DOC |
| **Labels** | Gene expression counts (measured) | VERIFIED_DOC |
| **Ground truth** | NO exhaustive true DE gene list | **BLOCKED** |
| **License** | Bioconductor experiment data | VERIFIED_DOC |
| **Runtime** | R + Bioconductor + DESeq2 | VERIFIED_DOC |

**CRITICAL LIMITATION:**
- airway/pasilla do NOT provide objective true DE gene labels
- DESeq2 output is a statistical estimate, NOT ground truth
- Cannot compute genuine FDP/power
- **Status: BLOCKED** for outcome-grounded gate

**Possible weaker outcome:** Replicate stability, held-out sample likelihood

---

## Summary

| Domain | Dataset | Labels | Independent scorer | Status |
|--------|---------|--------|-------------------|--------|
| Chemistry | Delaney ESOL | Measured solubility | RMSE/MAE on scaffold holdout | **VERIFIED_DOC** |
| Spatial | NOAA GHCN | Measured weather | RMSE/MAE on blocked holdout | **VERIFIED_DOC** |
| Bio | airway/pasilla | Count data | No true DE truth | **BLOCKED** |

**Recommendation:** Start with Chemistry + Spatial as two mechanistically distinct real-data workflows. Bio requires independent gold standard before inclusion.
