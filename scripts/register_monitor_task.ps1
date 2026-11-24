# v0.1.2: regista o monitor no Agendador de Tarefas (mesmo padrão da tarefa do TP cap do forex, que funciona).
# Correr na raiz do projecto:  powershell -ExecutionPolicy Bypass -File scripts\register_monitor_task.ps1
# Remover:                     powershell -ExecutionPolicy Bypass -File scripts\register_monitor_task.ps1 -Remove
#
# Arranca no logon E é relançada a cada 5 min se não estiver a correr (MultipleInstances IgnoreNew → nunca
# duas instâncias). Log em logs\monitor.log.

param([switch]$Remove)

$root = Split-Path -Parent $PSScriptRoot
$name = "IBKR Connection Manager"
New-Item -ItemType Directory -Force -Path (Join-Path $root "logs") | Out-Null

if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
    Write-Host "Removida tarefa anterior: $name"
}
if ($Remove) { return }

$script = Join-Path $root "scripts\run_monitor.cmd"
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"`"$script`"`"" -WorkingDirectory $root
$t1 = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 365)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger @($t1, $t2) -Settings $settings -Principal $principal `
    -Description "Monitor TWS live / IB Gateway paper (so leitura). Projecto ibkr-connection-manager." | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 8
Get-ScheduledTask -TaskName $name | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName $name | Select-Object LastRunTime, LastTaskResult
