# Round 003-R1 Runtime Report — SciAgentGYM

**Date:** 2026-10-09  
**Pin:** `e9dbbea4369d67694e38bf8be67bedbcaf9e9300`  
**License:** Apache-2.0

---

## 1. Source acquisition

| Item | Value |
|------|-------|
| Clone | `git clone --filter=blob:none --no-checkout` + checkout |
| SHA verified | `e9dbbea4369d67694e38bf8be67bedbcaf9e9300` ✅ |
| Location | `../SciAgentGYM-src` (outside SciTransfer tree) |

## 2. Core modules

| Module | Status |
|--------|--------|
| `gym.env.MinimalSciEnv` | ✅ Import OK |
| `gym.tool.EnvironmentTool` | ✅ Import OK |
| `gym.toolbox.Toolbox` | ✅ Import OK |
| `gym.entities.Observation` | ✅ Import OK |
| `gym.core.evaluator` | ✅ Import OK |

## 3. Two sequential scientific tool calls (R3R1-02)

### Tool Call 1: `calculate_thin_film_interference`
- **Input:** `n1=1.0, n2=1.5, d=300.0`
- **Output:** `enhanced_wavelength_nm=1800.0, weakened_wavelength_nm=900.0`
- **Evidence:** Real physics computation

### Tool Call 2: `compute_photon_energy` (evidence-dependent)
- **Input:** `wavelength_nm=1800.0` (from Call 1 output)
- **Output:** `energy_ev=0.6888, energy_j=1.1036e-19`
- **Evidence dependency:** Call 2 input derived from Call 1 output ✅

## 4. Second discipline (R3R1-03)

| Discipline | Status |
|------------|--------|
| Physics | ✅ 9 tool modules (optics, mechanics, EM, thermo, etc.) |
| Chemistry | ✅ 5 tool modules (analytical, physical, computational, organic, environmental) |
| Materials Science | Available |
| Life Science | Available |
| Astronomy | Available |

**Chemistry tool test:** `compute_molecular_weight("H2O")` → `18.015` ✅

## 5. Scorer integrity (R3R1-05)

| Path | Judge-free? | Finding |
|------|-------------|---------|
| Perfect match | ✅ Yes | `calculate_answer_score` returns 100% without judge |
| Mismatch | ❌ No | Calls `secondary_verification_with_llm` → **JUDGE_REQUIRED** |
| `is_answer_correct` | ❌ No | Always uses LLM judge |
| `extract_boxed_answer` | ✅ Yes | Pure regex function |

**Label:** `JUDGE_REQUIRED` for mismatch paths. `OFFLINE_SCORER_NOT_EQUIVALENT` for full evaluation.

## 6. Hidden answer isolation (R3R1-04)

| Test | Result |
|------|--------|
| Hidden fields identified | `answer`, `golden_answer`, `solution_steps`, `tool_expected` |
| Canary in candidate view | **PASS** (no leak) |
| Canary in hidden data | PASS (present as expected) |

---

## Verdict

**CONDITIONAL GO** for SciAgentGYM as a measurement environment:

✅ Real multi-step scientific tool execution  
✅ Evidence-dependent sequential calls  
✅ Multiple disciplines (Physics, Chemistry, Materials, Life, Astronomy)  
✅ `extract_boxed_answer` and perfect-match scoring work offline  

⚠️ **JUDGE_REQUIRED** for mismatch scoring (not fully offline)  
⚠️ Hidden answer isolation needs runtime enforcement (canary tests pass)
