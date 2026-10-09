# SciAgentGYM Feasibility Assessment — Round 003

**Date:** 2026-10-09  
**Author:** MiMo (Executor)  
**Plan:** `planner/plan_003.md` Track B  
**Timebox:** 2 hours  
**Budget:** $0 paid API

---

## 1. Repository metadata

| Item | Value |
|------|-------|
| URL | https://github.com/CMarsRover/SciAgentGYM |
| License | Not specified in GitHub API (check LICENSE file) |
| Clone status | **BLOCKED** — GitHub network unreachable (connection reset) |
| Static analysis | README + evaluator.py + env.py fetched via raw.githubusercontent.com |

---

## 2. Architecture (from source)

### Core components:
- `gym/env.py`: `MinimalSciEnv` with `reset()` / `step(ToolCall)` interface
- `gym/core/evaluator.py`: `extract_boxed_answer()`, `is_answer_correct()`, `calculate_answer_score()`
- `gym/core/tool_loader.py`: Dynamic tool loading from task metadata
- `gym/tool.py`: `EnvironmentTool` base class, `GenericFunctionTool`
- `gym/toolbox.py`: `Toolbox.register` decorator

### Key design:
- **Typed tools**: Each tool has `name`, `description`, `arguments` (JSON schema), `use()` method
- **Isolated instances**: Each task runs in its own environment with `case_id` and `domain`
- **Multi-step**: `ToolCall` → `step()` → `Observation` → next `ToolCall`
- **Structured traces**: All executions recorded

---

## 3. Tool distribution (from README)

| Discipline | Tools | Python files |
|------------|-------|-------------|
| Physics | Optics, Mechanics, EM, Thermo, etc. | 96+ |
| Chemistry | Analytical, Physical, Computational, Organic, Environmental | 28+ |
| Materials Science | Crystallography, Spectroscopy, XRD | 24+ |
| Life Science | Structural Biology, Mass Spectrometry | 19+ |
| Astronomy | — | 6+ |

**Total:** 1,780+ scientific tools

---

## 4. Evaluation pipeline (from evaluator.py)

### `extract_boxed_answer(response)`:
- Extracts `\boxed{}` content from model response
- Supports nested braces
- Pure function, no API needed

### `is_answer_correct(question, model_answer, gold_answer, id)`:
- **Uses LLM judge** (JUDGE_MODEL, typically gpt-4.1)
- Requires API access
- **NOT usable offline**

### `calculate_answer_score(model_answer, gold_answer, tolerance=0.05)`:
- **Pure function** — numerical/string comparison with tolerance
- Supports dict/list/leaf comparison
- Secondary LLM verification on mismatch (optional)
- **CAN work offline** if secondary verification is disabled

### Dataset fields (from README):
```
question, answer, metadata.subject, metadata.topic,
metadata.solution_steps, metadata.tool_expected,
metadata.golden_answer, usage_tool_protocol
```

**Hidden fields** (need isolation): `answer`, `golden_answer`, `solution_steps`, `tool_expected`

---

## 5. Feasibility assessment

### ✅ Strengths:
1. **Real multi-step tool-use**: `ToolCall` → `step()` → `Observation` loop
2. **Typed tools**: JSON schema for arguments, automatic validation
3. **Multiple disciplines**: Physics, Chemistry, Materials, Life Science, Astronomy
4. **Pure scoring function**: `calculate_answer_score()` works offline
5. **Isolated instances**: Each task has its own environment
6. **Structured traces**: All executions recorded

### ⚠️ Concerns:
1. **LLM judge required** for `is_answer_correct()` — needs API access
2. **GitHub network blocked** — cannot clone for full installation test
3. **Hidden answers in dataset** — `answer`, `golden_answer`, `solution_steps` need isolation
4. **Complex dependencies** — conda env with many scientific packages

### ❌ Blockers:
1. **Cannot clone repository** — network connectivity issues
2. **Cannot verify installation** — no local checkout
3. **Cannot run smoke test** — no executable environment

---

## 6. Comparison with DiscoveryWorld and ScienceAgentBench

| Criterion | SciAgentGYM | DiscoveryWorld | ScienceAgentBench |
|-----------|-------------|----------------|-------------------|
| Multi-step tools | ✅ 1780+ typed tools | ✅ 17 actions | ❌ single-shot |
| Scoring | LLM judge + pure function | Game engine | Official evaluators |
| Disciplines | 5 (Physics, Chem, Materials, Life, Astronomy) | 8+ themes | 4 (Bio, Chem, GIS, Psych) |
| Offline scoring | ⚠️ partial (pure function only) | ✅ | ✅ |
| Hidden answer isolation | ⚠️ needs work | ⚠️ needs work | ⚠️ needs work |
| Installation | ⚠️ complex (conda) | ✅ pip | ⚠️ Docker |
| Reproducibility | ✅ seeds, traces | ✅ seeds | ⚠️ agent stochastic |

---

## 7. Verdict: **CONDITIONAL**

### Rationale:
- SciAgentGYM has the **right architecture** for multi-step scientific tool-use
- **1780+ typed tools** across 5 disciplines is impressive
- **Pure scoring function** can work offline
- **BUT**: Cannot verify installation due to network issues
- **BUT**: LLM judge required for full evaluation

### Conditions for GO:
1. Successfully clone and install in authorized workspace
2. Run at least one 2-step tool sequence offline
3. Demonstrate hidden answer isolation
4. Verify `calculate_answer_score()` works without LLM

### If BLOCKED:
- Network issues prevent cloning
- Installation too complex for 2h timebox
- Fall back to DiscoveryWorld with improved prompting

---

## 8. Evidence limitations

- **Static analysis only** — README + 2 source files fetched
- **No installation test** — network blocked
- **No runtime verification** — cannot execute tools
- **License not verified** — check LICENSE file after clone

---

## 9. Recommendation

**CONDITIONAL GO for SciAgentGYM** as a candidate for future strategy-transfer experiments, pending:
1. Network access to clone repository
2. Successful installation in authorized workspace
3. Offline smoke test with 2+ sequential tool calls
4. Hidden answer isolation implementation

**Alternative if blocked:** Improve DiscoveryWorld prompting (better LLM strategy, more steps) or propose methodological redesign to Planner.
