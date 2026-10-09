# Round 001-R3 Preflight Report

**Date:** 2026-10-09 (UTC+8)
**Executor:** MiMo
**Plan:** `planner/plan_001_r3.md`
**Platform:** Windows 10/11 (win32)
**Python:** 3.10.1 (system)

## 1. ZIP & Artifact Integrity

| Item | Value |
|------|-------|
| ZIP size | 1,769,478,786 bytes (exact match) |
| ZIP SHA256 | `46E715D3B2196D459D2DFF52AA487F506A95EC44B44262E82208D086EA879610` |
| Upstream commit | `c26e151ed601ba109dc4d35e057ff8e73fec469d` |
| Verified parquet SHA256 | `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147` |

## 2. Official Scorer Semantics (confirmed by reading source)

### Task 85 — `biopsykit_saliva_eval.py`
- **File SHA256:** `31920bb30c6926d2598c00ae8a1bd6d80158ed2afe3ed96ca8bb982f8858ceef`
- **Metric:** JSON key-set equality, then per-key value comparison
  - Float: `math.isclose(gold, pred, rel_tol=1e-9)` (relative tolerance)
  - String: exact equality
- **Gold SHA256:** `23ee04300efec5e1b3a6c1821be0caa7e959f31b187742486caf2c2961a78eac`

### Task 16 — `antibioticsai_filter_eval.py`
- **File SHA256:** `216935482b08427dc5c713f4c4b0a83f46eb637846c7f847cfab44cf270bf873`
- **Metric:** Set intersection coverage: `overlap = len(pred∩gold) / len(gold)`, score=1 if `overlap==1.0`
- **Key fact:** Extra lines in pred are **allowed**. This is NOT exact text equality.
- **Gold SHA256:** `bad3cea5b4017bf0b6b082c32ba5d4c71c1cd9429c91d531902e60ca217a7ca4`

### Task 21 — `eval_deforestation.py`
- **File SHA256:** `c1b2ca7c15c1f2b4ba3520e9d89e35a5656a1c98e63cfac58f63221b46f49819`
- **Metric:** `metric = abs(pred_val - gold_val) / gold_val`, score=1 if `metric <= 0.05` (5% tolerance)
- **Key fact:** Numerical formatting differences within 5% are **accepted**. NOT exact text equality.
- **Gold SHA256:** `d4bcb2ac0c76bfcdb8795c178ba12924f92778a1016c823e03784da870d3ca1b`

## 3. R2 Scoring Divergence (erratum)

The R2 `scripts/r2_evaluate_all.py` claimed "All eval() functions are UNMODIFIED" but actually used **reimplemented** scoring:

| Task | R2 Implementation | Official Semantics | Impact |
|------|-------------------|-------------------|--------|
| 85 | Hand-written `score_85()` | `math.isclose(rel_tol=1e-9)` | Logic similar but not direct import |
| 16 | `gold_text == pred_text` (exact string) | Set coverage `overlap==1.0` (extra rows OK) | **May cause false 0** |
| 21 | `gold_text == pred_text` (exact string) | MAE ratio ≤ 5% tolerance | **May cause false 0** |

## 4. Environment

| Component | Status |
|-----------|--------|
| Docker Desktop | Installed (29.3.1), currently Stopped |
| Docker build network | Blocked (apt-get/pip mirrors unreachable) |
| OPENAI_API_KEY | DashScope value (non-OpenAI), passes non-empty preflight |
| Local Python | 3.10.1 with pandas, rdkit, geopandas, shapely installed |

## 5. Resource Budget (R3)

- Zero API regeneration calls
- Local CPU scoring only
- Timeout per program: 300s (raised from R2's 120s for GIS tasks, same for both arms)
- Expected wall time: ~30 minutes for 6 programs + tests

## 6. Frozen Program Hashes (from `results/round_001_r1_program_hashes.json`)

| Run | SHA256 (full) |
|-----|---------------|
| sab_verified_85__NO_STRATEGY__seed0 | `58c7bc1f4ae66bfd...` (see catalog) |
| sab_verified_85__FIXED_STRATEGY__seed0 | `b6e31cb05291e70c...` |
| sab_verified_16__NO_STRATEGY__seed0 | `df1a03d317d1d7c4...` |
| sab_verified_16__FIXED_STRATEGY__seed0 | `86acf1e1567ebe70...` |
| sab_verified_21__NO_STRATEGY__seed0 | `f140501cf8e078ec...` |
| sab_verified_21__FIXED_STRATEGY__seed0 | `0ed0ee5def739864...` |
