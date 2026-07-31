# Launch the (9,4) BFS campaign detached with logging.
Set-Location $PSScriptRoot
Start-Process -FilePath "python" -ArgumentList "runbig.py","4","9","8","4000" `
  -RedirectStandardOutput "data\run94.log" -RedirectStandardError "data\run94.err" `
  -WindowStyle Hidden
Write-Output "launched runbig 4 9 with 8 workers; log: data\run94.log"
