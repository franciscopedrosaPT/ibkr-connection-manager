@echo off
rem ibkr-connection-manager: monitor (usado pelo Agendador de Tarefas)
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" scripts\run_monitor.py
