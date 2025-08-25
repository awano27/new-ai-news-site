Param()
$ErrorActionPreference = 'Stop'

Write-Host '=== Daily AI News - Integrated Collect (X+RSS) ==='
Write-Host 'Only last 48h / Ensure >=20 items'

# Find python
$python = ''
try {
  & py -3 -V *> $null
  if ($LASTEXITCODE -eq 0) { $python = 'py -3' }
} catch {}
if (-not $python) {
  try {
    & python -V *> $null
    if ($LASTEXITCODE -eq 0) { $python = 'python' }
  } catch {}
}
if (-not $python) { throw 'Python 3 not found. Please install Python 3.' }

Write-Host 'STEP 1) Install Python deps (feedparser, requests)'
& cmd /c "$python -m pip install --upgrade pip"
& cmd /c "$python -m pip install feedparser requests"

Write-Host 'STEP 2) Run integrated build (scripts/integrated_build.py)'
& cmd /c "$python scripts\integrated_build.py"
if ($LASTEXITCODE -ne 0) { throw 'integrated_build.py failed' }

Write-Host 'STEP 3) Run acceptance tests (incl. freshness)'
& node scripts\tests\verify_acceptance.js
if ($LASTEXITCODE -ne 0) { throw 'verify_acceptance failed' }

Write-Host 'DONE. Use serve_docs.bat to preview locally.'
