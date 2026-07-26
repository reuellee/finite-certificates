#!/usr/bin/env bash
set -euxo pipefail
cd ~/repl_bundle
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.12.13
uv venv --python 3.12.13 ~/venv312
source ~/venv312/bin/activate
uv pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0 pandas
python -c "import sys,numpy,scipy,sklearn,pandas;print(sys.version);print('numpy',numpy.__version__,'scipy',scipy.__version__,'sklearn',sklearn.__version__,'pandas',pandas.__version__)"
python analysis/check_coherence_transfer_gradients.py
time python experiments/coherence_transfer_semireal.py \
  --architectures l1,topk \
  --seeds 0,1,2,3,4,5,6,7,8,9,10,11 \
  --betas 0,0.025,0.0625,0.25,0.5 \
  --widths 68 \
  --outdir results/coherence_transfer_semireal_reproduction \
  --save-weights
python analysis/analyze_coherence_transfer_semireal.py results/coherence_transfer_semireal_reproduction
sha256sum results/coherence_transfer_semireal_reproduction/run_metrics.csv
echo REPLICATION_DONE
