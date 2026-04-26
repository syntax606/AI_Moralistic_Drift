# CLAUDE.md

## Project Overview

This project studies **normative drift in language models under agentic commitment in multi-turn dialogue**.

The system:

1. Generates structured moral scenarios
2. Runs multi-turn conversations with LLMs
3. Parses structured responses
4. Computes drift and trajectory metrics
5. Runs statistical models
6. Produces figures for analysis

The experiment is **sensitive to prompt structure and execution order**. Do not modify components casually.

---

## Core Design Principles

- Prompts are **strictly controlled** (see `prompt_schema.py`)
- First response in each trajectory is the **anchor**
- Drift is always measured relative to this anchor
- Two key conditions:
  - `history` (multi-turn conversation)
  - `no_history` (independent evaluation)
- Two trajectory orders:
  - `forward`: R → C1 → C2 → C3 → C4
  - `reverse`: C4 → C3 → C2 → C1 → R

---

## Directory Structure

```
project/
├── src/                 # all core code
├── data/                # scripts + generated outputs
├── results/             # metrics, models, figures
├── tests/               # prompt snapshot tests
├── environment/         # dependencies
```

---

## Execution Pipeline (IMPORTANT)

Always run steps in this exact order:

```bash
python -m src.make_scripts
python -m src.generate
python -m src.sanity_check
python -m src.parse_outputs
python -m src.metrics
python -m src.stats_stance
python -m src.stats_drift
python -m src.plots
```

Do NOT skip steps unless explicitly debugging.

---

## Key Files and Responsibilities

**src/config.py**
Defines:
- models
- trajectories
- experimental parameters

**src/prompt_schema.py**
Defines ALL prompts.
⚠️ Changing this affects the entire experiment.

**src/generate.py**
Runs model inference and logs outputs.

**src/parse_outputs.py**
Extracts:
- stance
- score
- confidence
- explanation

**src/metrics.py**
Computes:
- shift
- deviation
- step_delta
- NDI
- trajectory consistency
- rule_shift (reverse only)
- reliability metrics

**src/stats_stance.py**
Ordinal regression on stance scores, including C×order interaction for H3.

**src/stats_drift.py**
Regression models testing hypotheses H1–H5.

**src/plots.py**
Generates all figures.

---

## Critical Constraints

### 1. Prompt Stability

DO NOT change prompt formatting without updating:
- `tests/test_prompt_snapshots.py`

Prompt changes invalidate experiments.

---

### 2. Structured Output Format

Models must output:
```
STANCE:
SCORE:
CONFIDENCE:
EXPLANATION:
```
Parsing depends on this format.

---

### 3. Conversation Integrity

- `history` mode must preserve full conversation
- `no_history` must NOT include prior turns

Do not mix these behaviors.

---

### 4. Anchor Definition

Anchor = first stance in each trajectory.
All drift metrics depend on this.

---

### 5. Reproducibility

Every run logs:
- model ID
- prompt hash
- generation parameters

Do not remove logging fields.

---

## Expected Outputs

After full run:

**Data**
```
data/generations.jsonl
data/parsed.csv
```

**Metrics**
```
results/turn_metrics.csv
results/conversation_metrics.csv
results/reliability.csv
results/analysis_dataset.csv
```

**Statistical models**
```
results/stance_ordered_logit.txt
results/drift_deviation_model.txt
results/drift_signed_model.txt
results/path_dependence_model.txt
results/rule_revision_model.txt
results/history_effect_model.txt
results/ndi_model.txt
```

**Figures**
```
results/figures/fig1_mean_shift_by_C.png
results/figures/fig2_mean_deviation_by_C.png
results/figures/fig3_path_dependence.png
results/figures/fig4_history_effect.png
results/figures/fig5_rule_shift_hist.png
results/figures/fig6_ndi_by_order.png
results/figures/fig7_trajectory_examples.png
```

---

## Testing

Run:
```bash
pytest
```

Key test:
- `test_prompt_snapshots.py` ensures prompt stability

If this test fails, DO NOT proceed with experiments.

---

## Common Failure Modes

**Parsing failures**
- Models may not follow format
- Check `parse_ok` column

**Model incompatibility**
- Some models lack chat templates
- `models_chat.py` handles fallback

**GPU / memory issues**
- Try smaller models or disable 4-bit loading

**Token truncation**
- Check `hit_max_tokens` flag

---

## Guidelines for Modifying Code

Only modify code if necessary.

Safe to modify:
- `make_scripts.py` (add scenarios)
- `plots.py` (new visualizations)
- `stats_*.py` (additional models)

Modify with caution:
- `metrics.py`
- `generate.py`

Do NOT modify without updating tests:
- `prompt_schema.py`

---

## Experiment Logic Summary

This project tests:

1. Whether commitment increases deviation from moral rules (H1)
2. Whether drift is directional (H2)
3. Whether trajectories depend on order (H3)
4. Whether rules are revised post-commitment (H4)
5. Whether dialogue amplifies drift (H5)

---

## When Running in Claude Code

- Always follow execution order
- Do not rewrite large files unless asked
- Prefer minimal, targeted changes
- Preserve all logging and outputs
- Never silently change experimental assumptions

---

## Final Note

This is a research experiment, not just an application.
Small implementation changes can:
- invalidate results
- introduce confounds
- break reproducibility

Proceed carefully.
