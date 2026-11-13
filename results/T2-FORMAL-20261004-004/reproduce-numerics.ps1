param([Parameter(Mandatory=$true)][string]$OutputDirectory)
# Numerical reproduction only; no claim of private Windows controller validation.
$ErrorActionPreference='Stop'
$repo=(Get-Item -LiteralPath $PSScriptRoot).Parent.Parent.FullName
$python=Join-Path $repo '.venv-s2/Scripts/python.exe'
if(-not(Test-Path -LiteralPath $python)){throw 'The documented pinned project environment must already be available'}
$destination=if([IO.Path]::IsPathRooted($OutputDirectory)){[IO.Path]::GetFullPath($OutputDirectory)}else{[IO.Path]::GetFullPath((Join-Path $repo $OutputDirectory))}
if(-not $destination.StartsWith($repo+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Choose a new output directory inside this repository'}
if(Test-Path -LiteralPath $destination){throw 'Refusing to overwrite an existing reproduction directory'}
$conditions=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'conditions.json') -Raw|ConvertFrom-Json
$null=New-Item -ItemType Directory -Path $destination
Push-Location -LiteralPath $repo
try{
 foreach($condition in $conditions){
  $output=Join-Path $destination $condition.case_id
  $check=Join-Path $destination ($condition.case_id+'-check.json')
  & $python -B -u (Join-Path $repo 'run_optimizer.py') run --config (Join-Path $repo $condition.config) --output $output
  if($LASTEXITCODE -ne 0){throw ('Optimizer failed: '+$condition.case_id)}
  & $python -B -u (Join-Path $repo 'experiments/t2_formal_check.py') --output $output --check-output $check
  if($LASTEXITCODE -ne 0){throw ('Saved-result check failed: '+$condition.case_id)}
 }
}finally{Pop-Location}
