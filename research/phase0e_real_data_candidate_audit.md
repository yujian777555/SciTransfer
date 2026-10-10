# Phase 0-E — Real-Data Scientific Workflow Feasibility (Planner proposal)

**Date:** 2026-10-10
**Status:** DOCUMENTED PUBLIC CANDIDATES ONLY. Not downloaded, installed, executed, scored or independently license-cleared on Executor's machine.
**User decision:** Approve investigation of a narrower real scientific-analysis-task approach after the Phase0D D1 simulation NO-GO. Preserves `planner/PROJECT_CHARTER.md`.
**Boundary:** This replaces *outcome measurement approach*, NOT the central research hypothesis. No paid model, agent training, Phase1, or transfer claims authorized here.

## 1. Why not repair the custom simulator again

Past D1 `ALLOCATE_REPLICATE` only incremented a counter, without creating actual observations; evaluator and candidate were in one Python process; fixed-step rules were mislabeled evidence-responsive. Another in-house simulator is a high-risk engineering distraction. We need at least one already-existing executable scientific workflow with **actual measurements and locked reference labels**, checked by a separate trusted scorer. A task should expose a real choice of preprocessing, validation, statistical model or measurement selection, with observable DEV feedback and a final held-out result.

**Important:** Existing recorded real data do not magically create new lab measurements. An allowed action may reveal a *pre-collected* train/DEV subset from a fixed pool with a declared cost. Call this `retrospective information acquisition`, never “running new wet-lab replicates.” When observations are static, distinguish stepwise *analytical* decisions (split, QC, fit, validate, revise) from physical experiments.

## 2. Candidate A — CHEMISTRY: Delaney ESOL / DeepChem (PRIMARY)

**Primary implementation/data provenance:** https://github.com/deepchem/deepchem/blob/master/deepchem/molnet/load_function/delaney_datasets.py
**Reference API:** https://deepchem.readthedocs.io/en/latest/api_reference/moleculenet.html
**Reported contents:** Delaney ESOL has **1,128** molecules, SMILES and experimentally measured log aqueous solubility. DeepChem's `load_delaney` defaults to `splitter='scaffold'`; raw data location and transformer behavior in the loader must be separately verified/pinned.

**Potential trusted score:** RMSE/MAE of final predictions for molecularly disjoint, predeclared **scaffold-held-out** compounds; no proxy/external LLM judge. Additional: molecular/scaffold overlap/leak detection, train-time budget, model complexity, uncertainty calibration if relevant. Holdout and labels owned by evaluator only. Baselines: RDKit descriptors + Ridge/RandomForest, standard scaffold splitter, library default pipeline, generic checklist and no-strategy under identical budgets.

**Scientific decisions actually possible:** structure standardization, leakage/QC checks, descriptor selection, regularization, train/DEV validation protocol, model choice and when to distrust a random split; return real dev errors and final prediction artifact. Claim **retrospective solubility modelling**, not experiment design or discovery of new compounds.

**Risks and gates:** 1,128 observations may be underpowered for a large multi-round strategy benchmark; scaffold split may be challenging and labels may already be memorized by LLMs; compare molecular scaffolds and source identifiers, dataset rights and original Delaney redistribution terms before collecting or committing CSVs; base package environments may be heavy. Check raw CSV bytes/version and license independently; DeepChem software license ≠ automatically the dataset's data license. Select only small lawful files and avoid hardcoding favorable splits.

## 3. Candidate B — SPATIAL SCIENCE: NOAA GHCN-Daily (PRIMARY SECOND DOMAIN)

**Primary data source:** https://www.ncei.noaa.gov/pub/data/ghcn/daily/
**NOAA documentation/catalog:** https://catalog.data.gov/dataset/global-historical-climatology-network-daily-ghcn-daily-version-3
**Format/metadata:** station observations, station inventory and historical daily climate variables; missing data/measurement, quality and source flags. Dataset changes over time, so freeze a specific date/version, station list, bounded region/time window and SHA256.

**Potential trusted score:** spatially **blocked** held-out station/region temperature predictions RMSE/MAE, coverage/calibration for probabilistic estimates; compare to simple train-set mean, nearest station, inverse-distance weighting and a reproducible geostatistical baseline. Test labels are real withheld observations (not objective physical truth); replicate missing/quality filtering.

**Scientific decisions actually possible:** quality-flag filtering, temporal aggregation, spatial validation vs random split, leakage check, selection of interpolation baseline, diagnostic/residual inspection and revised prediction. No new weather stations created: only analyses on existing measurements.

**Risks and gates:** NOAA archive overall is several gigabytes: **DO NOT download the full archive**. Select a small bounded historical year and geography; verify enough stations with overlapping dates, coordinate/ID validity, minimum spatial separation and withheld station design. Beware temporal autocorrelation, nearby stations making spatial tasks trivial, and data updates/rights/attribution. Verify NOAA source terms and third-party contributing records. Distinguish scientific spatial validation from ordinary random train/test split.

## 4. Candidate C — BIOINFORMATICS: Bioconductor airway / pasilla + DESeq2 (CONDITIONAL THIRD DOMAIN)

**DESeq2 official:** https://bioconductor.org/packages/release/bioc/html/DESeq2.html
**DESeq2 tutorial:** https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html
**airway dataset:** https://bioconductor.org/packages/release/data/experiment/html/airway.html
**pasilla dataset:** https://bioconductor.org/packages/release/data/experiment/html/pasilla.html

`airway` contains RNA-seq read counts from four airway cell lines under dexamethasone vs untreated conditions; `pasilla` contains selected Drosophila gene/exon count data. DESeq2 is a mature NB-GLM-based differential-expression method, with QC, design formulas, dispersion estimation, outlier handling and statistical corrections.

**CRITICAL GROUND-TRUTH LIMITATION:** airway/pasilla genuine expression counts DO NOT provide an exhaustive list of objectively known true DE genes. One cannot compute empirical true gene-level FDP/power by comparing to DESeq2 output; that output is a statistical estimate, NOT an external truth oracle. A package concordance or replicate-stability measure is a *proxy* and must be labeled as such. Third-domain scientific claim stays **BLOCKED** until a verifiable independent gold/validated-spike-in truth or a separately defensible outcome measure is selected, licensed, and independently scored. Do not declare actual experimental sample acquisition from reusing this fixed dataset.

**Viable weaker outcome examples:** reproducible held-out sample log-likelihood, prospective replicate-stability of a frozen analysis method or external replication experiments (if available). These are not substitutes for true FDR/power and should not be pooled as equivalent without justification.

## 5. Two-domain-first decision and external validity

Start by checking **A chemistry + B spatial** as two *mechanistically distinct, real-label regression/validation workflows*; not yet claim general cross-disciplinary scientific discovery. Require a genuinely shared *process* strategy (e.g. “inspect leakage and shift before selecting validation procedure,” “validate before trusting best-DEV result,” “reconsider a model after a diagnostic mismatch”), which can map to domain-specific action schemas and has nontrivial downstream consequences. This shared methodological skill is NOT inherently novel, and published memory/agent work already covers general validation routines.

For a **cross-domain** claim, prove source-only extraction, a frozen strategy, target holdout and matched A/B/placebo on at least 2 disparate task populations. Two workflows are a feasibility pilot, not robust across-science generalization; a third genuinely distinct externally scoreable domain is needed before ambitious cross-science statements.

## 6. Hard evidence and licensing checklist

For each dataset/tool, Executor must record:
- official URL, dataset paper/DOI, file path/API name, version/date, intended snapshot hash, citation, and distinct **software vs data license/rights**;
- actual reachable URL evidence (bounded HEAD/metadata only; no big download now); local runtime stack and rough CPU/disk requirements, whether R/Bioconductor needed;
- labels/holdout, train/DEV/test split freeze, duplicate/station/scaffold leakage analysis plan, scorer formula and **independent implementation**; no test labels visible to candidate;
- exact permissible scientific actions with a real artifact/outcome and feasible baseline under same resource budget;
- confidence for each entry: VERIFIED_OFFICIAL_DOC, VERIFIED_RUNTIME (not authorized this round), UNCERTAIN, BLOCKED.

## 7. Initial readiness verdict

**CONDITIONAL DESIGN GO ONLY**: A and B appear to have genuine labels and known independent scoring metrics; no local fetch or execution has been verified and data rights/contamination concerns remain. C remains **CONDITIONAL** due missing exhaustive DE truth. If A or B cannot support a safe fixed heldout and meaningful action-responsive workflow, reject and return to user rather than quietly build another simulator or switch tasks post hoc.
