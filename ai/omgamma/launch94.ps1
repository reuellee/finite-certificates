# Launch / relaunch the (9,4) BFS campaign detached with logging.
#   .\launch94.ps1              -> resume from the last checkpoint
#   .\launch94.ps1 -Workers 4   -> fewer workers (memory pressure)
#   .\launch94.ps1 -Scratch     -> from scratch (DESTROYS level_001+)
param([int]$Workers = 6, [switch]$Scratch)
Set-Location $PSScriptRoot
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$log = "data\run94_$stamp.log"
$err = "data\run94_$stamp.err"
if ($Scratch) {
  $argl = @("runbig.py", "4", "9", "$Workers", "4000")
} else {
  $argl = @("runbig.py", "4", "9", "$Workers", "--resume")
}
Start-Process -FilePath "python" -ArgumentList $argl `
  -RedirectStandardOutput $log -RedirectStandardError $err `
  -WindowStyle Hidden
Write-Output "launched: python $($argl -join ' ')"
Write-Output "log: $log"
