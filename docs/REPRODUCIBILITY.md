# Reproducing the paper

This document maps the experiments in **Action Communication in Shared-Policy Multi-Hop Graph Navigation** to the public code in this repository.

Datasets and pretrained checkpoints are distributed through [THESEUS](https://github.com/HalcyonSolutions/THESEUS).

## Seed terminology

The manuscript uses two distinct sources of variation.

**Checkpoint seed** identifies an independently trained MINERVA checkpoint. The main cross-checkpoint results use checkpoint seeds **0, 42, and 100**.

**Execution seed** controls stochastic action sampling during evaluation. Table 2 uses execution seed **42**. The MetaQA experiment used for Fig. 2 averages execution seeds **42, 43, 44, 45, and 46** within each checkpoint.

The helper `scripts/run_paper_eval.sh` creates a temporary copy of the selected YAML config with the requested checkpoint seed. This is necessary because the checkpoint path is interpolated from the YAML `seed` field.

## Table 1

Table 1 reports dataset and evaluation settings.

The fixed settings come from `configs/*.yaml`. Decoder-dependent Greedy truncation is emitted by the same R=100 evaluations used for Table 2.

## Table 2

Run:

```bash
bash experiments/reproduce_table2.sh
```

Protocol:

- datasets: KINSHIP, MetaQA, MQuAKE-ST Single, MQuAKE-ST Multi
- checkpoint seeds: 0, 42, 100
- execution seed: 42
- R=1: Greedy, Top-2, Top-4, unrestricted NumPy sampling
- R=100: Greedy, Top-2, Top-4, unrestricted NumPy sampling, deterministic Beam-100
- statistics: mean and population standard deviation across the three checkpoint seeds
- realization payload: `mean_question_stochastic_action_payload_bits`

Generated paper-level files:

```text
experiment_logs/table2_manifest.tsv
experiment_logs/table2/table2.csv
experiment_logs/table2/table2.json
```

## Figure 2

Run:

```bash
bash experiments/reproduce_fig2.sh
```

Protocol:

- dataset: MetaQA
- R=100
- checkpoint seeds: 0, 42, 100
- stochastic execution seeds: 42-46
- stochastic modes: Greedy, Top-2, Top-4, unrestricted NumPy sampling
- deterministic mode: Beam-100

For stochastic modes, execution seeds are averaged within each checkpoint first. Panel (a) then averages the three checkpoint-level values. Panel (b) reports checkpoint-level MRR directly.

Beam is evaluated once per checkpoint because it is deterministic under the fixed shared state and tie-breaking assumptions.

Generated paper-level files:

```text
experiment_logs/fig2_manifest.tsv
experiment_logs/fig2/fig2_panel_a.csv
experiment_logs/fig2/fig2_panel_b.csv
experiment_logs/fig2/fig2_recovery.csv
experiment_logs/fig2/fig2.json
```

## MQuAKE-ST action-cap sensitivity

Run:

```bash
bash experiments/reproduce_cap_sensitivity.sh
```

Protocol:

- datasets: MQuAKE-ST Single and Multi
- checkpoint seed: 42
- execution seed: 42
- R=100
- standard cap: 200
- sensitivity cap: 512
- modes: Greedy, Top-2, Top-4, unrestricted NumPy sampling, Beam-100

The cap of 512 is an evaluation-only sensitivity condition. It does not retrain the checkpoint.

## Environment

The paper wrappers default to `minerva_tf2`.

Use another Conda environment with:

```bash
ACTIONCOMM_ENV=my_environment bash experiments/reproduce_table2.sh
```

Use the currently active environment without `conda run` with:

```bash
ACTIONCOMM_ENV="" bash experiments/reproduce_table2.sh
```

## Raw artifacts

Every evaluator run records the effective rollout count, effective action cap, checkpoint path and identity, checkpoint seed, execution seed, repository revisions, candidate-ranking metrics, and communication metrics.

The paper-level aggregator validates each manifest entry against this metadata before computing the reported summaries.
