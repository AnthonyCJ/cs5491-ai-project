#requires -Version 7.2
param(
 [Parameter(Mandatory)][string]$Runtime,
 [Parameter(Mandatory)][ValidateSet('svg','png','pdf','markdown')][string]$Task,
 [Parameter(Mandatory)][string]$Request,
 [Parameter(Mandatory)][string]$Output,
 [string]$Modules='', [string]$Browser='',
 [ValidateRange(1,300)][int]$LimitSeconds=60
)
$ErrorActionPreference='Stop'
$watch=[Diagnostics.Stopwatch]::StartNew()
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if((Get-Location).Path -ne $root){throw 'Use working-copy root'}
$destination=[IO.Path]::GetFullPath((Join-Path $root $Output))
if(-not $destination.StartsWith((Join-Path $root 'results')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or -not ([IO.Path]::GetFileName($destination)).StartsWith('local-') -or (Test-Path -LiteralPath $destination)){throw 'Use NEW results/local-* directory'}
$requestPath=[IO.Path]::GetFullPath((Join-Path $root $Request))
if(-not $requestPath.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Request outside root'}
[IO.Directory]::CreateDirectory($destination)|Out-Null
function Save([string]$Name,$Value){$p=Join-Path $destination $Name;if(Test-Path -LiteralPath $p){throw 'Receipt exists'};[IO.File]::WriteAllText($p,($Value|ConvertTo-Json -Depth 40)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))}
function SamePath([string]$A,[string]$B){[string]::Equals([IO.Path]::GetFullPath($A),[IO.Path]::GetFullPath($B),[StringComparison]::OrdinalIgnoreCase)}
$record=[ordered]@{schema_version=1;task=$Task;started_at=(Get-Date -Format o);limit_seconds=$LimitSeconds;status='failed';creation='not_requested';business_authorized=$false;errors=@();termination=@();processes=@()}
Save 'started.json' $record
$job=[IntPtr]::Zero;$child=$null;$assigned=$false;$threadClosed=$false;$held=@{};$exitCode=1;$tempRoot=Join-Path $destination 'process-temp'
function Observe {
 $account=[ReaderVisualNative]::Account($job)
 if($account.activeProcesses -eq 0){return $account}
 foreach($memberId in [ReaderVisualNative]::ProcessIds($job)){
  $key=[string]$memberId
  if($held.ContainsKey($key)){continue}
  $h=[ReaderVisualNative]::OpenProcess(0x101000,$false,$memberId)
  if($h -eq [IntPtr]::Zero){throw 'Cannot hold created process'}
  $row=[ordered]@{pid=$memberId;handle=$h;identity=$null;boundary=$null;command_line=$null;permitted=$false;first_seen_at=(Get-Date -Format o)}
  $held[$key]=$row
  $row.identity=[ReaderVisualNative]::Identity($h);$row.boundary=[ReaderVisualNative]::Boundary($h,$false);$row.command_line=[ReaderVisualNative]::CommandLine($h)
  $image=$row.identity.actual_image;$console=Join-Path ([Environment]::GetFolderPath('System')) 'conhost.exe'
  $known=(SamePath $image $runtimePath)
  if(SamePath $image $console){$known=($row.command_line -match '(?i)conhost\.exe"?\s+0x[0-9a-f]{1,16}(?:\s+-ForceV1)?\s*$')}
  if($Task -eq 'markdown' -and $Browser -and (SamePath $image $Browser)){$known=$true}
  $row.permitted=($known -and [ReaderVisualNative]::Member($job,$h) -and $row.boundary.permitted -and $row.boundary.user_sid -eq $record.launcher_boundary.user_sid)
  $row.image_sha256=(Get-FileHash -LiteralPath $image).Hash.ToLowerInvariant()
  if(-not $row.permitted){throw 'Visual process outside declared image/token/user boundary'}
 }
 return $account
}
try{
 Add-Type -Path (Join-Path $PSScriptRoot 'reader_visual_native.cs')
 $record.launcher_boundary=[ReaderVisualNative]::CurrentBoundary()
 if(-not $record.launcher_boundary.permitted){throw 'Visual launcher must be ordinary same-user non-AppContainer'}
 $runtimePath=(Get-Item -LiteralPath $Runtime).FullName
 [IO.Directory]::CreateDirectory($tempRoot)|Out-Null
 $environment=@{};foreach($entry in [Environment]::GetEnvironmentVariables().GetEnumerator()){$environment[$entry.Key]=[string]$entry.Value}
 foreach($key in @('TMPDIR','TEMP','TMP')){$environment[$key]=$tempRoot}
 $environment.Remove('PYTHONPATH');$environment.Remove('PYTHONHOME');$environment['PYTHONNOUSERSITE']='1';$environment['PYTHONDONTWRITEBYTECODE']='1';$environment['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD']='1'
 $block=(($environment.Keys|Sort-Object|ForEach-Object {$_+'='+$environment[$_]}) -join [char]0)+[char]0+[char]0
 $worker=if($Task -eq 'pdf'){'reader-visual-pdf.py'}else{'reader-visual.cjs'}
 $arguments=@($runtimePath);if($Task -eq 'pdf'){$arguments+=@('-B','-s')}
 $arguments+=@((Join-Path $PSScriptRoot $worker),'--task',$Task,'--root',$root,'--receipt',$destination,'--request',$Request)
 if($Modules){$arguments+=@('--modules',$Modules)};if($Browser){$arguments+=@('--browser',$Browser)}
 if(@($arguments|Where-Object {$_ -match '["\r\n]'}).Count){throw 'Unsupported path characters'}
 $command=($arguments|ForEach-Object {'"'+$_.TrimEnd('\')+'"'}) -join ' '
 $record.command=$arguments;$record.runtime_sha256=(Get-FileHash -LiteralPath $runtimePath).Hash.ToLowerInvariant();$record.request_sha256=(Get-FileHash -LiteralPath $requestPath).Hash.ToLowerInvariant()
 $record.source_sha256=@{};foreach($name in @('reader-visual.ps1','reader_visual_native.cs',$worker)){$record.source_sha256[$name]=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $name)).Hash.ToLowerInvariant()}
 Save 'launch-plan.json' @{command=$arguments;boundary=$record.launcher_boundary;source_sha256=$record.source_sha256;temp=$tempRoot;request_sha256=$record.request_sha256}
 $job=[ReaderVisualNative]::Job();if($watch.Elapsed.TotalSeconds -ge $LimitSeconds-5){throw 'Insufficient launch/cleanup time'}
 $record.creation='unknown';$child=[ReaderVisualNative]::Create($runtimePath,$command,$root,$block);$record.creation='created'
 $record.launch_identity=[ReaderVisualNative]::Identity($child.process);if(-not(SamePath $record.launch_identity.actual_image $runtimePath)){throw 'Suspended image mismatch'}
 [ReaderVisualNative]::Assign($job,$child.process);$assigned=$true;[ReaderVisualNative]::Resume($child.thread);$threadClosed=[ReaderVisualNative]::CloseHandle($child.thread)
 if(-not $threadClosed){throw 'Thread handle close failed'}
 $ready=Join-Path $destination 'ready.json'
 while(-not(Test-Path -LiteralPath $ready)){$null=Observe;if([ReaderVisualNative]::Exited($child.process)){throw 'Worker exited before ready'};if($watch.Elapsed.TotalSeconds -ge [Math]::Min(15,$LimitSeconds-5)){throw 'Ready deadline exceeded'};Start-Sleep -Milliseconds 25}
 $initial=Get-Content -LiteralPath $ready -Raw|ConvertFrom-Json
 if($initial.pid -ne $child.pid){throw 'Visual worker PID differs'}
 $null=Observe
 Save 'go.json' @{worker_pid=$initial.pid;boundary_verified=$true;permission='Import renderer and prepare browser only; no input rendering yet'}
 $renderReady=Join-Path $destination 'render-ready.json'
 while(-not(Test-Path -LiteralPath $renderReady)){$null=Observe;if([ReaderVisualNative]::Exited($child.process)){throw 'Renderer exited before readiness'};if($watch.Elapsed.TotalSeconds -ge $LimitSeconds-5){throw 'Renderer readiness deadline'};Start-Sleep -Milliseconds 25}
 $before=Observe
 if($before.totalProcesses -ne $held.Count){throw 'Incomplete creation set before render'}
 Save 'process-set-before-business.json' @{job=$before;processes=@($held.Values|ForEach-Object {@{pid=$_.pid;identity=$_.identity;boundary=$_.boundary;command_line=$_.command_line;image_sha256=$_.image_sha256;permitted=$_.permitted}})}
 $record.business_authorized=$true;Save 'render-go.json' @{worker_pid=$initial.pid;boundary_verified=$true;at=(Get-Date -Format o)}
 while(-not[ReaderVisualNative]::Exited($child.process)){$null=Observe;if($watch.Elapsed.TotalSeconds -ge $LimitSeconds-3){$record.timed_out=$true;throw 'Visual task deadline'};Start-Sleep -Milliseconds 25}
 $end=$watch.Elapsed.TotalSeconds+1
 do{$final=Observe;if($final.activeProcesses -eq 0){break};Start-Sleep -Milliseconds 25}while($watch.Elapsed.TotalSeconds -lt $end)
 $record.job_accounting=$final;$record.creation_set_complete=($final.totalProcesses -eq $held.Count);$record.all_job_exits_confirmed=($final.activeProcesses -eq 0)
 if(-not $record.creation_set_complete -or -not $record.all_job_exits_confirmed){throw 'Incomplete visual process creation/exit evidence'}
 $record.worker_exit_code=[ReaderVisualNative]::ExitCode($child.process)
 $result=Get-Content -LiteralPath (Join-Path $destination 'worker-result.json') -Raw|ConvertFrom-Json
 $record.temporary_cleanup_verified=(@(Get-ChildItem -LiteralPath $tempRoot -Force).Count -eq 0)
 if($record.worker_exit_code -ne 0 -or -not $result.gate_passed -or -not $record.temporary_cleanup_verified){throw 'Visual worker or cleanup failed'}
 $record.status='passed';$exitCode=0
}catch{$record.errors+=@{message=[string]$_;at=(Get-Date -Format o)};$cursor=$_.Exception;while($cursor){if($cursor.Data['creation_outcome']){$record.creation=$cursor.Data['creation_outcome']};$cursor=$cursor.InnerException}}
finally{
 try{
 if($child -and -not[ReaderVisualNative]::Exited($child.process)){if(-not(Test-Path -LiteralPath (Join-Path $destination 'stop.json'))){Save 'stop.json' @{reason='control failure'}};$err=if($assigned){[ReaderVisualNative]::StopJob($job,125)}else{[ReaderVisualNative]::StopProcess($child.process,125)};$record.termination+=@{api=$(if($assigned){'TerminateJobObject'}else{'TerminateProcess'});winerror=$err};$end=$watch.Elapsed.TotalSeconds+1;while(-not[ReaderVisualNative]::Exited($child.process) -and $watch.Elapsed.TotalSeconds -lt $end){Start-Sleep -Milliseconds 25}}
 $record.processes=@(foreach($row in $held.Values){$exited=[ReaderVisualNative]::Exited($row.handle);$entry=@{pid=$row.pid;identity=$row.identity;boundary=$row.boundary;command_line=$row.command_line;image_sha256=$row.image_sha256;permitted=$row.permitted;exit_confirmed=$exited;exit_code=[ReaderVisualNative]::ExitCode($row.handle);final_times=[ReaderVisualNative]::FinalTimes($row.handle);handle_closed=[ReaderVisualNative]::CloseHandle($row.handle)};if(-not $exited -or -not $entry.handle_closed){$record.status='failed';$exitCode=1};$entry})
 if($child){if(-not $threadClosed){$record.primary_thread_closed=[ReaderVisualNative]::CloseHandle($child.thread)}else{$record.primary_thread_closed=$true};$record.final_launch_exit_confirmed=[ReaderVisualNative]::Exited($child.process);$record.launch_handle_closed=[ReaderVisualNative]::CloseHandle($child.process)}
 if($job -ne [IntPtr]::Zero){$record.final_job_accounting=[ReaderVisualNative]::Account($job);$record.job_handle_closed=[ReaderVisualNative]::CloseHandle($job);$record.creation_set_complete=($record.final_job_accounting.totalProcesses -eq $held.Count);$record.all_job_exits_confirmed=($record.final_job_accounting.activeProcesses -eq 0)}
 }catch{$record.status='failed';$exitCode=1;$record.errors+=@{message="Final evidence error: $_"}}
 $record.wall_seconds=$watch.Elapsed.TotalSeconds;$record.ended_at=(Get-Date -Format o);Save 'receipt.json' $record
}
[pscustomobject]$record|Select-Object task,status,creation,business_authorized,creation_set_complete,all_job_exits_confirmed,temporary_cleanup_verified,wall_seconds,errors|ConvertTo-Json -Depth 5 -Compress
exit $exitCode
