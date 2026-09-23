#!/usr/bin/env python3
"""Aggregate ActionComm evaluator artifacts into paper-facing summaries."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

CHECKPOINTS = (0, 42, 100)
EXECUTION_SEEDS = (42, 43, 44, 45, 46)
DATASETS = ("kinshiphinton", "mquake_st_single", "mquake_st_multi", "metaqa")
LABELS = {
    "kinshiphinton": "KINSHIP",
    "mquake_st_single": "MQuAKE-ST Single",
    "mquake_st_multi": "MQuAKE-ST Multi",
    "metaqa": "MetaQA",
}
MODES = ("Greedy", "Top-2", "Top-4", "Unrestricted", "Beam")


def mode_name(row):
    if row["mode"] == "greedy":
        return "Greedy"
    if row["mode"] == "topk" and int(row["top_k"]) in (2, 4):
        return f"Top-{int(row['top_k'])}"
    if row["mode"] == "numpy_policy":
        return "Unrestricted"
    if row["mode"] == "deterministic_beam":
        return "Beam"
    return None


def load_runs(manifest):
    runs = []
    with Path(manifest).open(encoding="utf-8", newline="") as f:
        for entry in csv.DictReader(f, delimiter="\t"):
            out = Path(entry["output_dir"])
            rows = json.loads((out / "rate_sweep_summary.json").read_text(encoding="utf-8"))
            meta = json.loads((out / "rate_sweep_metadata.json").read_text(encoding="utf-8"))
            ckpt = int(entry["checkpoint_seed"])
            execution = int(entry["execution_seed"])
            rollouts = int(entry["rollouts"])
            assert int(meta["minerva_options"]["seed"]) == ckpt
            assert int(meta["rate_arguments"]["rate_seed"]) == execution
            assert int(meta["evaluation_overrides"]["effective_test_rollouts"]) == rollouts
            assert meta["dataset"] == entry["dataset"]
            cap = int(meta["evaluation_overrides"]["effective_max_num_actions"])
            for row in rows:
                mode = mode_name(row)
                if mode is not None:
                    runs.append({
                        "dataset": entry["dataset"],
                        "checkpoint_seed": ckpt,
                        "execution_seed": execution,
                        "rollouts": rollouts,
                        "cap": cap,
                        "mode": mode,
                        "row": row,
                    })
    return runs


def mean(xs):
    return statistics.fmean(xs)


def psd(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def require_checkpoints(records, context):
    got = sorted({r["checkpoint_seed"] for r in records})
    if got != list(CHECKPOINTS):
        raise ValueError(f"{context}: expected checkpoint seeds {CHECKPOINTS}, got {got}")


def aggregate_table2(runs, out):
    idx = {}
    for r in runs:
        key = (r["dataset"], r["checkpoint_seed"], r["rollouts"], r["mode"])
        if key in idx:
            raise ValueError(f"Duplicate Table 2 run: {key}")
        idx[key] = r

    rows = []
    for dataset in DATASETS:
        for mode in MODES:
            r100 = [idx[(dataset, s, 100, mode)] for s in CHECKPOINTS if (dataset, s, 100, mode) in idx]
            require_checkpoints(r100, f"{dataset} {mode} R=100")
            r1 = []
            if mode != "Beam":
                r1 = [idx[(dataset, s, 1, mode)] for s in CHECKPOINTS if (dataset, s, 1, mode) in idx]
                require_checkpoints(r1, f"{dataset} {mode} R=1")

            h100 = [float(r["row"]["hits_at_1"]) for r in r100]
            mrr = [float(r["row"]["mrr"]) for r in r100]
            payload = [float(r["row"]["mean_question_stochastic_action_payload_bits"]) for r in r100]
            h1 = [float(r["row"]["hits_at_1"]) for r in r1]
            rows.append({
                "dataset": LABELS[dataset],
                "mode": mode,
                "r1_hits1_mean": mean(h1) if h1 else None,
                "r1_hits1_population_sd": psd(h1) if h1 else None,
                "r100_hits1_mean": mean(h100),
                "r100_hits1_population_sd": psd(h100),
                "r100_mrr_mean": mean(mrr),
                "r100_mrr_population_sd": psd(mrr),
                "incremental_realization_bits_per_question": mean(payload),
            })

    write_csv(out / "table2.csv", rows)
    write_json(out / "table2.json", {"checkpoint_seeds": CHECKPOINTS, "execution_seed": 42, "rows": rows})


def aggregate_fig2(runs, out):
    runs = [r for r in runs if r["dataset"] == "metaqa" and r["rollouts"] == 100]
    require_checkpoints(runs, "Fig. 2")
    values = {}
    panel_b = []

    for ckpt in CHECKPOINTS:
        for mode in MODES:
            records = [r for r in runs if r["checkpoint_seed"] == ckpt and r["mode"] == mode]
            if mode == "Beam":
                records = [r for r in records if r["execution_seed"] == 42]
                if len(records) != 1:
                    raise ValueError(f"Expected one Beam run for checkpoint {ckpt}")
            else:
                got = sorted({r["execution_seed"] for r in records})
                if got != list(EXECUTION_SEEDS):
                    raise ValueError(f"{mode}, checkpoint {ckpt}: expected execution seeds {EXECUTION_SEEDS}, got {got}")
            mrr = mean([float(r["row"]["mrr"]) for r in records])
            payload = mean([float(r["row"]["mean_question_stochastic_action_payload_bits"]) for r in records])
            values[(ckpt, mode)] = (mrr, payload)
            panel_b.append({
                "checkpoint_seed": ckpt,
                "mode": mode,
                "candidate_ranking_mrr": mrr,
                "incremental_realization_bits_per_question": payload,
            })

    panel_a = []
    for mode in MODES:
        panel_a.append({
            "mode": mode,
            "candidate_ranking_mrr": mean([values[(s, mode)][0] for s in CHECKPOINTS]),
            "incremental_realization_bits_per_question": mean([values[(s, mode)][1] for s in CHECKPOINTS]),
        })

    recovery = []
    for ckpt in CHECKPOINTS:
        greedy = values[(ckpt, "Greedy")][0]
        unrestricted = values[(ckpt, "Unrestricted")][0]
        denom = unrestricted - greedy
        for mode in ("Top-2", "Top-4"):
            recovery.append({
                "checkpoint_seed": ckpt,
                "mode": mode,
                "recovery_percent": 100.0 * (values[(ckpt, mode)][0] - greedy) / denom,
            })
    for mode in ("Top-2", "Top-4"):
        xs = [r["recovery_percent"] for r in recovery if r["mode"] == mode]
        recovery.append({
            "checkpoint_seed": "aggregate",
            "mode": mode,
            "recovery_percent": mean(xs),
            "population_sd_percent": psd(xs),
        })

    write_csv(out / "fig2_panel_a.csv", panel_a)
    write_csv(out / "fig2_panel_b.csv", panel_b)
    write_csv(out / "fig2_recovery.csv", recovery)
    write_json(out / "fig2.json", {"panel_a": panel_a, "panel_b": panel_b, "recovery": recovery})


def aggregate_cap(runs, out):
    rows = []
    for dataset in ("mquake_st_single", "mquake_st_multi"):
        for cap in (200, 512):
            for mode in MODES:
                found = [
                    r for r in runs
                    if r["dataset"] == dataset
                    and r["checkpoint_seed"] == 42
                    and r["execution_seed"] == 42
                    and r["rollouts"] == 100
                    and r["cap"] == cap
                    and r["mode"] == mode
                ]
                if len(found) != 1:
                    raise ValueError(f"Expected one run for {dataset}, cap={cap}, mode={mode}; got {len(found)}")
                row = found[0]["row"]
                rows.append({
                    "dataset": LABELS[dataset],
                    "cap": cap,
                    "mode": mode,
                    "hits_at_1": float(row["hits_at_1"]),
                    "mrr": float(row["mrr"]),
                    "incremental_realization_bits_per_question": float(row["mean_question_stochastic_action_payload_bits"]),
                    "truncated_state_fraction": row.get("truncated_state_fraction"),
                })
    write_csv(out / "cap_sensitivity.csv", rows)
    write_json(out / "cap_sensitivity.json", {"checkpoint_seed": 42, "execution_seed": 42, "rows": rows})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=("table2", "fig2", "cap"))
    p.add_argument("--manifest", required=True)
    p.add_argument("--output-dir", required=True, type=Path)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    runs = load_runs(a.manifest)
    {"table2": aggregate_table2, "fig2": aggregate_fig2, "cap": aggregate_cap}[a.kind](runs, a.output_dir)


if __name__ == "__main__":
    main()
