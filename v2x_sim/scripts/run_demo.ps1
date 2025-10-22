param(
  [double]$Duration = 60,
  [double]$Dt = 0.1,
  [int]$EWCount = 6,
  [int]$NSCount = 6,
  [double]$SpawnGapEW = 2.5,
  [double]$SpawnGapNS = 2.2,
  [double]$VEW = 12.0,
  [double]$VNS = 11.0,
  [int]$Seed = 42,
  [double]$MinGreen = 8.0,
  [double]$MaxGreen = 25.0,
  [double]$Yellow = 3.0,
  [double]$AllRed = 1.0,
  [string]$Tag = ""
)

$python = "A:/ONE DRIVE/OneDrive - Apratim/Projects/automotive/.venv/Scripts/python.exe"

Write-Host "[1/3] Running unit tests..." -ForegroundColor Cyan
& $python -m unittest discover -s tests -p "test_*.py" -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }

Write-Host "[2/3] Running simulation..." -ForegroundColor Cyan
& $python .\main.py --duration $Duration --dt $Dt --ew-count $EWCount --ns-count $NSCount --spawn-gap-ew $SpawnGapEW --spawn-gap-ns $SpawnGapNS --v-ew $VEW --v-ns $VNS --seed $Seed --min-green $MinGreen --max-green $MaxGreen --yellow $Yellow --all-red $AllRed
if ($LASTEXITCODE -ne 0) { throw "Simulation run failed." }

Write-Host "[3/3] Generating artifacts..." -ForegroundColor Cyan
$tagArg = @()
if ($Tag -ne "") { $tagArg = @("--tag", $Tag) }
& $python .\scripts\generate_submission_artifacts.py --duration $Duration --dt $Dt --ew-count $EWCount --ns-count $NSCount --spawn-gap-ew $SpawnGapEW --spawn-gap-ns $SpawnGapNS --v-ew $VEW --v-ns $VNS --seed $Seed --min-green $MinGreen --max-green $MaxGreen --yellow $Yellow --all-red $AllRed @tagArg
if ($LASTEXITCODE -ne 0) { throw "Artifact generation failed." }

Write-Host "Demo complete." -ForegroundColor Green
