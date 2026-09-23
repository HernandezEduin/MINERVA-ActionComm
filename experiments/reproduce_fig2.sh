#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
manifest="experiment_logs/fig2_manifest.tsv"
out="experiment_logs/fig2"
mkdir -p experiment_logs
rm -f "$manifest"
for checkpoint_seed in 0 42 100; do
  for execution_seed in 42 43 44 45 46; do
    include_beam=false
    [[ "$execution_seed" == "42" ]] && include_beam=true
    bash scripts/run_paper_eval.sh fig2 configs/metaqa.yaml "$checkpoint_seed" "$execution_seed" 100 "$include_beam" "$manifest"
  done
done
python scripts/aggregate_paper_results.py fig2 --manifest "$manifest" --output-dir "$out"
echo "Fig. 2 summaries written to $out"
