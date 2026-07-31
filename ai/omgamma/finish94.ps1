# Post-processing for the (9,4) campaign, run once the BFS lands.
#   export the compact certificate -> check it -> canary it -> full suite
Set-Location $PSScriptRoot
$log = "data\finish94.log"
"=== finish94 $(Get-Date -Format s) ===" | Out-File $log -Encoding utf8
python export_subcert.py 4 9 2>&1 | Tee-Object -Append $log
python checker_fast.py 9 4 `
  data\big_4_9\subcert_reps.txt.gz data\big_4_9\subcert_tree.txt.gz `
  data\big_4_9\subcert_gens.txt data\big_4_9\subcert_exhibits.txt 2>&1 |
  Tee-Object -Append $log
"checker exit=$LASTEXITCODE" | Tee-Object -Append $log
python canary_checker.py 9 4 `
  data\big_4_9\subcert_reps.txt.gz data\big_4_9\subcert_tree.txt.gz `
  data\big_4_9\subcert_gens.txt data\big_4_9\subcert_exhibits.txt --fast 2>&1 |
  Tee-Object -Append $log
"canary exit=$LASTEXITCODE" | Tee-Object -Append $log
python verify_omgamma.py 2>&1 | Tee-Object -Append $log
"verify exit=$LASTEXITCODE" | Tee-Object -Append $log
python final_summarize.py 2>&1 | Tee-Object -Append $log
