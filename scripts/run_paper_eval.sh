#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 7 ]]; then
  echo "Usage: $0 <experiment> <config> <checkpoint_seed> <execution_seed> <R> <include_beam:true|false> <manifest> [extra rate args...]" >&2
  exit 2
fi

experiment="$1"
config="$2"
checkpoint_seed="$3"
execution_seed="$4"
rollouts="$5"
include_beam="$6"
manifest="$7"
shift 7

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ "$config" != /* ]]; then
  config="$repo_root/$config"
fi
if [[ ! -f "$config" ]]; then
  echo "Config not found: $config" >&2
  exit 2
fi

if [[ "$manifest" != /* ]]; then
  manifest="$repo_root/$manifest"
fi
mkdir -p "$(dirname "$manifest")"

case "$include_beam" in
  true|false) ;;
  *) echo "include_beam must be true or false" >&2; exit 2 ;;
esac

tmp_config="$(mktemp "${TMPDIR:-/tmp}/actioncomm_config.XXXXXX.yaml")"
trap 'rm -f "$tmp_config"' EXIT

python - "$config" "$tmp_config" "$checkpoint_seed" <<'PY'
from pathlib import Path
import re, sys
source, target, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
text = Path(source).read_text(encoding="utf-8")
updated, count = re.subn(r"(?m)^seed:\s*[^#\n]+(?:\s*#.*)?$", f"seed: {seed}", text, count=1)
if count != 1:
    raise SystemExit(f"Expected exactly one top-level seed field in {source}, found {count}.")
Path(target).write_text(updated, encoding="utf-8")
PY

base_output_dir="$(python - "$tmp_config" <<'PY'
from pathlib import Path
import re, sys
text = Path(sys.argv[1]).read_text(encoding="utf-8")
m = re.search(r'(?m)^base_output_dir:\s*["\x27]?([^"\x27\n]+)', text)
if m is None:
    raise SystemExit("Could not read base_output_dir from config.")
print(m.group(1).strip())
PY
)"

case "$(basename "$config")" in
  kinshiphinton.yaml) dataset="kinshiphinton" ;;
  metaqa.yaml) dataset="metaqa" ;;
  mquake_st_single.yaml) dataset="mquake_st_single" ;;
  mquake_st_multi.yaml) dataset="mquake_st_multi" ;;
  *) echo "Unknown paper config: $config" >&2; exit 2 ;;
esac

tag="${experiment}_${dataset}_ckpt${checkpoint_seed}_exec${execution_seed}_r${rollouts}_$(date +%Y%m%d_%H%M%S)_${RANDOM}"

rate_args=(
  --rate_test_rollouts "$rollouts"
  --rate_top_k 2 4
  --rate_include_numpy_policy true
  --rate_include_unrestricted false
  --rate_seed "$execution_seed"
)

if [[ "$include_beam" == "true" ]]; then
  rate_args+=(--rate_include_deterministic_beam true --rate_beam_width 100)
else
  rate_args+=(--rate_include_deterministic_beam false)
fi

conda_env="${ACTIONCOMM_ENV-minerva_tf2}"
if [[ -n "$conda_env" ]]; then
  if ! command -v conda >/dev/null 2>&1; then
    echo "Conda was not found. Set ACTIONCOMM_ENV=\"\" to use the current environment." >&2
    exit 2
  fi
  conda run -n "$conda_env" bash run_rate_sweep.sh "$tmp_config" "${rate_args[@]}" "$@" --timestamp "$tag"
else
  bash run_rate_sweep.sh "$tmp_config" "${rate_args[@]}" "$@" --timestamp "$tag"
fi

output_dir="$repo_root/${base_output_dir%/}/$tag/rate_sweep"
if [[ ! -f "$output_dir/rate_sweep_summary.json" || ! -f "$output_dir/rate_sweep_metadata.json" ]]; then
  echo "Expected evaluator artifacts were not found at $output_dir" >&2
  exit 1
fi

if [[ ! -s "$manifest" ]]; then
  printf 'experiment\tdataset\tcheckpoint_seed\texecution_seed\trollouts\toutput_dir\n' > "$manifest"
fi
printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$experiment" "$dataset" "$checkpoint_seed" "$execution_seed" "$rollouts" "$output_dir" >> "$manifest"

echo "Recorded: $output_dir"
