#requires -Version 7.2
param(
 [Parameter(Mandatory)][string]$Python,
 [Parameter(Mandatory)][ValidateSet('preflight','saved-score','missing-input','tampered-result','timeout-fixture','formal','s3','formal-figures','s3-saved-figures','s3-fresh-figures','proposal','milestone')][string]$Task,
 [Parameter(Mandatory)][string]$Output,
 [string]$InputRun='', [string]$FontDir='C:/Windows/Fonts',
 [ValidateRange(1,1200)][int]$LimitSeconds=60
)
$ErrorActionPreference='Stop'
$watch=[Diagnostics.Stopwatch]::StartNew()
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if((Get-Location).Path -ne $repo){throw 'Run from the repository root'}
$destination=[IO.Path]::GetFullPath((Join-Path $repo $Output))
if(-not $destination.StartsWith((Join-Path $repo 'results')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or -not ([IO.Path]::GetFileName($destination)).StartsWith('local-')){throw 'Output must be a new results/local-* directory'}
if(Test-Path -LiteralPath $destination){throw 'Refusing an existing output directory'}
[IO.Directory]::CreateDirectory($destination)|Out-Null
function Save([string]$Name,$Value){
 $path=Join-Path $destination $Name
 if(Test-Path -LiteralPath $path){throw "Receipt already exists: $Name"}
 [IO.File]::WriteAllText($path+'.pending',($Value|ConvertTo-Json -Depth 30)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
 [IO.File]::Move($path+'.pending',$path)
}
function SamePath([string]$A,[string]$B){[string]::Equals([IO.Path]::GetFullPath($A),[IO.Path]::GetFullPath($B),[StringComparison]::OrdinalIgnoreCase)}
$record=[ordered]@{schema_version=1;task=$Task;started_at=(Get-Date -Format o);limit_seconds=$LimitSeconds;creation='not_requested';launch_identity_verified=$false;worker_identity_verified=$false;worker_image_verified=$false;business_authorized=$false;worker_exit_confirmed=$false;all_job_exits_confirmed=$false;status='failed';errors=@();termination=@();expected_negative=($Task -in @('missing-input','tampered-result','timeout-fixture'))}
Save 'started.json' $record
$job=[IntPtr]::Zero;$child=$null;$workerHandle=[IntPtr]::Zero;$assigned=$false;$threadClosed=$false;$exitCode=1;$additional=@()
try{
 Add-Type -Path (Join-Path $PSScriptRoot 'reader_native.cs')
 $record.launcher_boundary=[ReaderNative]::CurrentBoundary()
 if(-not $record.launcher_boundary.permitted){throw 'Reader launch requires an ordinary non-elevated, non-AppContainer token'}
 $pythonPath=(Get-Item -LiteralPath $Python).FullName
 $basePython=$pythonPath
 $venvConfig=Join-Path ([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($pythonPath))) 'pyvenv.cfg'
 if(Test-Path -LiteralPath $venvConfig){
  $line=Get-Content -LiteralPath $venvConfig|Where-Object {$_ -match '^home = '}
  if(@($line).Count -ne 1){throw 'Ambiguous virtual environment home'}
  $basePython=[IO.Path]::GetFullPath((Join-Path $line.Substring(7) 'python.exe'))
  if(-not(Test-Path -LiteralPath $basePython -PathType Leaf)){throw 'Missing base interpreter'}
 }
 $tempRoot=Join-Path $destination 'process-temp'
 [IO.Directory]::CreateDirectory($tempRoot)|Out-Null
 $environment=@{}
 foreach($entry in [Environment]::GetEnvironmentVariables().GetEnumerator()){$environment[$entry.Key]=[string]$entry.Value}
 $environment.Remove('PYTHONPATH');$environment.Remove('PYTHONHOME')
 foreach($key in @('TMPDIR','TEMP','TMP')){$environment[$key]=$tempRoot}
 $environment['PYTHONNOUSERSITE']='1';$environment['PYTHONDONTWRITEBYTECODE']='1'
 $environment['MPLCONFIGDIR']=Join-Path $tempRoot 'initial-mpl'
 $block=(($environment.Keys|Sort-Object|ForEach-Object {$_+'='+$environment[$_]}) -join [char]0)+[char]0+[char]0
 $arguments=@($pythonPath,'-B','-s',(Join-Path $PSScriptRoot 'reader_worker.py'),'--task',$Task,'--receipt',$destination,'--root',$repo,'--font-dir',$FontDir)
 if($InputRun){$arguments+=@('--input-run',$InputRun)}
 if(@($arguments|Where-Object {$_ -match '["\r\n]'}).Count){throw 'Quotes/newlines are not supported in these paths'}
 $command=($arguments|ForEach-Object {'"'+$_.TrimEnd('\')+'"'}) -join ' '
 $record.command=$arguments;$record.python_sha256=(Get-FileHash -LiteralPath $pythonPath).Hash.ToLowerInvariant()
 $record.base_python_sha256=(Get-FileHash -LiteralPath $basePython).Hash.ToLowerInvariant()
 $record.source_sha256=@{}
 foreach($name in @('reader-run.ps1','reader_native.cs','reader_worker.py')){$record.source_sha256[$name]=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $name)).Hash.ToLowerInvariant()}
 Save 'launch-plan.json' @{command=$arguments;temporary_root=$tempRoot;environment=@{TMPDIR=$tempRoot;TEMP=$tempRoot;TMP=$tempRoot};boundary=$record.launcher_boundary;source_sha256=$record.source_sha256}
 $job=[ReaderNative]::Job()
 if($watch.Elapsed.TotalSeconds -ge $LimitSeconds-5){throw 'Insufficient time for launch and bounded cleanup'}
 $record.creation='unknown'
 $child=[ReaderNative]::Create($pythonPath,$command,$repo,$block)
 $record.creation='created';$record.launch_pid=$child.pid
 $record.launch_identity=[ReaderNative]::Identity($child.process)
 if(-not(SamePath $record.launch_identity.actual_image $pythonPath)){throw 'Actual suspended launch image differs'}
 $record.launch_identity_verified=$true
 [ReaderNative]::Assign($job,$child.process);$assigned=$true
 [ReaderNative]::Resume($child.thread)
 $threadClosed=[ReaderNative]::CloseHandle($child.thread)
 if(-not $threadClosed){throw 'Primary thread handle close failed'}
 $readyPath=Join-Path $destination 'ready.json'
 while(-not(Test-Path -LiteralPath $readyPath)){
  if([ReaderNative]::Exited($child.process)){throw 'Python exited before its startup receipt'}
  if($watch.Elapsed.TotalSeconds -gt [Math]::Min(15,$LimitSeconds)){throw 'Startup receipt deadline exceeded'}
  Start-Sleep -Milliseconds 25
 }
 $ready=Get-Content -LiteralPath $readyPath -Raw|ConvertFrom-Json
 $workerHandle=[ReaderNative]::OpenProcess(0x101000,$false,[uint32]$ready.pid)
 if($workerHandle -eq [IntPtr]::Zero){throw 'Unable to hold the waiting worker process'}
 $record.worker_pid=$ready.pid;$record.worker_identity=[ReaderNative]::Identity($workerHandle)
 if(-not [ReaderNative]::Member($job,$workerHandle)){throw 'Worker is not a member of the held job'}
 if($record.worker_identity.creation_ticks -lt $record.launch_identity.creation_ticks){throw 'Worker predates its launcher'}
 $record.worker_identity_verified=$true
 if(-not(SamePath $record.worker_identity.actual_image $basePython)){throw 'Actual waiting worker image differs from its base interpreter'}
 $record.worker_image_verified=$true
 $record.worker_boundary=[ReaderNative]::Boundary($workerHandle,$false)
 if(-not $record.worker_boundary.permitted -or $record.worker_boundary.user_sid -ne $record.launcher_boundary.user_sid){throw 'Worker token is outside the approved boundary'}
 # Capture the complete live set while Python is still waiting, before business.
 # A Windows console host is OS infrastructure, never a shell/query allowance.
 $ids=[ReaderNative]::ProcessIds($job)
 $record.job_before_business=[ReaderNative]::Account($job)
 $record.pids_before_business=$ids
 foreach($memberId in $ids){
  if($memberId -eq $child.pid -or $memberId -eq $ready.pid){continue}
  $h=[ReaderNative]::OpenProcess(0x101000,$false,$memberId)
  if($h -eq [IntPtr]::Zero){throw 'Cannot hold an additional job member'}
  $row=[ordered]@{pid=$memberId;handle=$h;identity=$null;boundary=$null;command_line=$null;permitted=$false}
  $additional+=,$row
  $row.identity=[ReaderNative]::Identity($h);$row.boundary=[ReaderNative]::Boundary($h,$false);$row.command_line=[ReaderNative]::CommandLine($h)
  $consoleHost=Join-Path ([Environment]::GetFolderPath('System')) 'conhost.exe'
  $row.permitted=([ReaderNative]::Member($job,$h) -and (SamePath $row.identity.actual_image $consoleHost) -and $row.boundary.permitted -and $row.boundary.user_sid -eq $record.launcher_boundary.user_sid -and $row.command_line -match '(?i)conhost\.exe"?\s+0x[0-9a-f]{1,16}(?:\s+-ForceV1)?\s*$')
  if(-not $row.permitted -or $additional.Count -gt 1){throw 'Unrecognized additional job member; business remains stopped'}
  $row.image_sha256=(Get-FileHash -LiteralPath $consoleHost).Hash.ToLowerInvariant()
 }
 $expectedProcesses=if($ready.pid -eq $child.pid){1}else{2}
 $expectedProcesses+=$additional.Count
 Save 'process-set-before-business.json' @{job=$record.job_before_business;pids=$ids;additional=@($additional|ForEach-Object {@{pid=$_.pid;identity=$_.identity;boundary=$_.boundary;command_line=$_.command_line;permitted=$_.permitted}});expected_count=$expectedProcesses}
 if($ids.Count -ne $expectedProcesses -or $record.job_before_business.totalProcesses -ne $expectedProcesses){throw 'Creation set is incomplete before business'}
 $record.business_authorized=$true
 Save 'go.json' @{worker_pid=$ready.pid;actual_image=$record.worker_identity.actual_image;boundary_verified=$true;observed_at=(Get-Date -Format o)}
 $timedOut=$false
 # The timeout fixture reaches an actual deadline; it is not a fabricated receipt.
 $businessDeadline=if($Task -eq 'timeout-fixture'){$watch.Elapsed.TotalSeconds+1.0}else{[double]$LimitSeconds-3.0}
 while(-not [ReaderNative]::Exited($child.process)){
  if($watch.Elapsed.TotalSeconds -ge $businessDeadline){$timedOut=$true;Save 'stop.json' @{reason='deadline';at=(Get-Date -Format o)};break}
  Start-Sleep -Milliseconds 25
 }
 if($timedOut){
  $end=$watch.Elapsed.TotalSeconds+1.0
  while(-not [ReaderNative]::Exited($child.process) -and $watch.Elapsed.TotalSeconds -lt $end){Start-Sleep -Milliseconds 25}
  if(-not [ReaderNative]::Exited($child.process)){$native=[ReaderNative]::StopJob($job,124);$record.termination+=@{api='TerminateJobObject';winerror=$native;at=(Get-Date -Format o)}}
 }
 $end=$watch.Elapsed.TotalSeconds+1.0
 do{$account=[ReaderNative]::Account($job);if($account.activeProcesses -eq 0){break};Start-Sleep -Milliseconds 25}while($watch.Elapsed.TotalSeconds -lt $end)
 $record.job_accounting=$account
 $record.worker_exit_confirmed=[ReaderNative]::Exited($workerHandle)
 $record.launch_exit_confirmed=[ReaderNative]::Exited($child.process)
 $record.all_job_exits_confirmed=($account.activeProcesses -eq 0)
 $record.creation_set_complete=($account.totalProcesses -eq $expectedProcesses)
 $record.additional_processes=@(foreach($row in $additional){@{pid=$row.pid;identity=$row.identity;boundary=$row.boundary;command_line=$row.command_line;image_sha256=$row.image_sha256;exit_confirmed=[ReaderNative]::Exited($row.handle);exit_code=[ReaderNative]::ExitCode($row.handle);final_times=[ReaderNative]::FinalTimes($row.handle)}})
 if(@($record.additional_processes|Where-Object {-not $_.exit_confirmed -or $_.final_times.creation_ticks -ne $_.identity.creation_ticks}).Count){throw 'Additional process exit/identity unconfirmed'}
 if(-not $record.worker_exit_confirmed -or -not $record.launch_exit_confirmed -or -not $record.all_job_exits_confirmed -or -not $record.creation_set_complete){throw 'Process creation/exit evidence is incomplete'}
 $record.worker_exit_code=[ReaderNative]::ExitCode($workerHandle)
 $record.launch_exit_code=[ReaderNative]::ExitCode($child.process)
 $record.worker_final=[ReaderNative]::FinalTimes($workerHandle)
 if($record.worker_final.creation_ticks -ne $record.worker_identity.creation_ticks){throw 'Held worker identity changed'}
 $worker=Get-Content -LiteralPath (Join-Path $destination 'worker-result.json') -Raw|ConvertFrom-Json
 $record.business_status=$worker.status;$record.timed_out=$timedOut
 if($Task -eq 'timeout-fixture'){
  if(-not $timedOut -or $worker.status -ne 'stopped' -or $record.worker_exit_code -ne 124){throw 'Timeout fixture did not save its real failure receipt'}
 }else{
  if($timedOut -or $record.worker_exit_code -ne 0 -or -not $worker.gate_passed){throw 'Worker business gate did not pass'}
 }
 $record.temporary_cleanup_verified=(@(Get-ChildItem -LiteralPath $tempRoot -Force).Count -eq 0)
 if(-not $record.temporary_cleanup_verified){throw 'Temporary/cache cleanup did not finish normally'}
 $record.status='passed';$exitCode=0
}catch{
 $cursor=$_.Exception;$native=$null
 while($cursor){if($cursor -is [ComponentModel.Win32Exception]){$native=$cursor.NativeErrorCode};if($cursor.Data['creation_outcome']){$record.creation=$cursor.Data['creation_outcome']};$cursor=$cursor.InnerException}
 $record.errors+=@{message=[string]$_;native_error=$native;at=(Get-Date -Format o)}
}finally{
 try{
 if($child){
  if(-not [ReaderNative]::Exited($child.process)){
   if(-not(Test-Path -LiteralPath (Join-Path $destination 'stop.json'))){Save 'stop.json' @{reason='launcher_failure';at=(Get-Date -Format o)}}
   $err=if($assigned){[ReaderNative]::StopJob($job,125)}else{[ReaderNative]::StopProcess($child.process,125)}
   $record.termination+=@{api=$(if($assigned){'TerminateJobObject'}else{'TerminateProcess'});winerror=$err;same_handle_exit_immediate=[ReaderNative]::Exited($child.process)}
   $end=$watch.Elapsed.TotalSeconds+1.0
   while(-not [ReaderNative]::Exited($child.process) -and $watch.Elapsed.TotalSeconds -lt $end){Start-Sleep -Milliseconds 25}
  }
  $record.final_launch_exit_confirmed=[ReaderNative]::Exited($child.process)
  if(-not $threadClosed){$record.primary_thread_closed=[ReaderNative]::CloseHandle($child.thread)}else{$record.primary_thread_closed=$true}
  $record.launch_handle_closed=[ReaderNative]::CloseHandle($child.process)
 }
 if($workerHandle -ne [IntPtr]::Zero){$record.worker_handle_closed=[ReaderNative]::CloseHandle($workerHandle)}
 $record.additional_cleanup=@(foreach($row in $additional){@{pid=$row.pid;exit_confirmed=[ReaderNative]::Exited($row.handle);handle_closed=[ReaderNative]::CloseHandle($row.handle);identity=$row.identity;command_line=$row.command_line;permitted=$row.permitted}})
 if(@($record.additional_cleanup|Where-Object {-not $_.exit_confirmed -or -not $_.handle_closed}).Count){$record.status='failed';$exitCode=1}
 if($job -ne [IntPtr]::Zero){$record.final_job_accounting=[ReaderNative]::Account($job);$record.job_handle_closed=[ReaderNative]::CloseHandle($job)}
 foreach($key in @('primary_thread_closed','launch_handle_closed','worker_handle_closed','job_handle_closed')){
  if($record.Contains($key) -and -not $record[$key]){$record.status='failed';$exitCode=1;$record.errors+=@{message="Handle cleanup failed: $key"}}
 }
 }catch{$record.status='failed';$exitCode=1;$record.errors+=@{message="Final cleanup evidence error: $_"}}
 $record.wall_seconds=$watch.Elapsed.TotalSeconds;$record.ended_at=(Get-Date -Format o)
 Save 'receipt.json' $record
}
Write-Output ($record|ConvertTo-Json -Depth 4 -Compress)
exit $exitCode
