#!/bin/sh
# Post-processing for the (9,4) campaign, run once the BFS lands.
# Bash (not PowerShell): PS 5.1 mangles native-exe stderr and $LASTEXITCODE.
#
# IMPORTANT: exports to the subcertB_* prefix.  data/big_4_9/subcert_* is
# the certA-derived certificate already signed off by BOTH checkers and
# cited in OMGAMMA.md -- it must not be overwritten.  The result is two
# independent certificates of H = Gbar: one from certify.py's holonomy on
# the level-9 checkpoint, one from the completed sweep's own generators.
set -x
cd "$(dirname "$0")" || exit 1
log=data/finish94.log
{
  date
  python final_summarize.py
  python export_subcert.py 4 9 data/big_4_9/subcertB
  python checker_fast.py 9 4 \
      data/big_4_9/subcertB_reps.txt.gz data/big_4_9/subcertB_tree.txt.gz \
      data/big_4_9/subcertB_gens.txt data/big_4_9/subcertB_exhibits.txt
  echo "checker_fast rc=$?"
  python canary_checker.py 9 4 \
      data/big_4_9/subcertB_reps.txt.gz data/big_4_9/subcertB_tree.txt.gz \
      data/big_4_9/subcertB_gens.txt data/big_4_9/subcertB_exhibits.txt \
      --fast
  echo "canary rc=$?"
  python verify_omgamma.py
  echo "verify rc=$?"
  python stabstats.py 4 9
} 2>&1 | tee "$log"
