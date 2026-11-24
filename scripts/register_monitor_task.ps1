# v0.2.0: regista o monitor no Agendador de Tarefas.
# Correr numa PowerShell NORMAL aberta na tua sessão do Windows (a mesma onde vês o TWS/IB Gateway),
# na raiz do projecto:  powershell -ExecutionPolicy Bypass -File scripts\register_monitor_task.ps1
# Remover:              powershell -ExecutionPolicy Bypass -File scripts\register_monitor_task.ps1 -Remove
#
# Interactive (não S4U): desde a Fase 2 o monitor arranca o IB Gateway via IBC e o IB Gateway tem de abrir
# no TEU ambiente de trabalho (S4U corre numa sessão invisível). Corre com pythonw (sem janela de consola).
# Arranca no logon e é relançado a cada 5 min se não estiver a correr (IgnoreNew → nunca duas instâncias).

param([switch]$Remove)

$root = Split-Path -Parent $PSScriptRoot
$name = "IBKR Connection Manager"
$user = "$env:USERDOMAIN\$env:USERNAME"
New-Item -ItemType Directory -Force -Path (Join-Path $root "logs") | Out-Null

if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $name -Confirm:$false
    Write-Host "Removida tarefa anterior: $name"
}
if ($Remove) { return }

$pyw = Join-Path $root ".venv\Scripts\pythonw.exe"
$script = Join-Path $root "scripts\run_monitor.py"
$action = New-ScheduledTaskAction -Execute $pyw -Argument "`"$script`"" -WorkingDirectory $root
$t1 = New-ScheduledTaskTrigger -AtLogOn -User $user
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 365)
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger @($t1, $t2) -Settings $settings -Principal $principal `
    -Description "Monitor + recuperacao (IBC) do TWS/IB Gateway. Projecto ibkr-connection-manager." | Out-Null
Start-ScheduledTask -TaskName $name
Start-Sleep -Seconds 8
Write-Host "Utilizador da tarefa: $user"
Get-ScheduledTask -TaskName $name | Select-Object TaskName, State
Get-ScheduledTaskInfo -TaskName $name | Select-Object LastRunTime, LastTaskResult
