#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || $1 != /* ]]; then
  echo "usage: $0 ABSOLUTE_INSTALL_PREFIX" >&2
  exit 2
fi

install_prefix=$1
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/9dvl-exact-cas-smoke.XXXXXX")
trap 'case "$work_dir" in /tmp/9dvl-exact-cas-smoke.*) rm -rf -- "$work_dir" ;; esac' EXIT

export PATH="$install_prefix/bin:/usr/bin:/bin"
export LD_LIBRARY_PATH="$install_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

Singular -q "$script_dir/smoke/singular_smoke.sing" | grep -Fx 'SINGULAR_SMOKE_OK'

msolve -p 128 -f "$script_dir/smoke/msolve_smoke.ms" -o "$work_dir/msolve.out"
grep -Fq '[0, [1,' "$work_dir/msolve.out"
grep -Fq '[[[' "$work_dir/msolve.out"
echo MSOLVE_SMOKE_OK

cp "$script_dir/smoke/normaliz_smoke.in" "$work_dir/normaliz_smoke.in"
(cd "$work_dir" && normaliz -f normaliz_smoke >/dev/null)
grep -Fq '2 Hilbert basis elements' "$work_dir/normaliz_smoke.out"
echo NORMALIZ_SMOKE_OK

cp "$script_dir/smoke/graver_smoke.mat" "$work_dir/graver_smoke.mat"
(cd "$work_dir" && graver graver_smoke >/dev/null)
test -s "$work_dir/graver_smoke.gra"
echo FOURTI2_SMOKE_OK

python - <<'PY'
from flint import fmpq_mat

m = fmpq_mat([[1, 2, 3], [2, 4, 7], [0, 1, 1]])
assert m.rank() == 3
assert m.det() == -1
print("PYTHON_FLINT_SMOKE_OK")
PY

echo EXACT_CAS_SMOKE_OK

