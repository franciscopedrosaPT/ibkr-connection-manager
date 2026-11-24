# ARQUITETURA — IBKR Connection Manager

Versão: 0.3.0 (recuperação TWS live + IBG paper) (Fase 2 — recuperação IBG paper) (Fase 1 — registo + monitor)

```
config/registry.yaml      endpoints (tws_live 7496, ibg_paper 4002, tws_paper 7497) + bots e faixas de CID
src/icm/registry.py       load(), conflicts() [CID repetido no mesmo endpoint; 'any' colide com todos],
                          config_mismatches() [lê o CID real no .env / config.yaml de cada bot — nunca chaves de segredos]
src/icm/probe.py          tcp_ok() (porta da API), api_ok() (connect readonly CID 90 + reqCurrentTime + managedAccounts)
src/icm/notify.py         Telegram (TELEGRAM_BOT_TOKEN / CHAT_ID / GROUP_CHAT_ID do .env local)
src/icm/recovery.py       Recoverer.step(): arranque IBC / kill de IBG preso / limites / pausa (data/PAUSE_RECOVERY)
src/icm/monitor.py        ciclo: TCP a cada interval_s, API a cada api_every_n ciclos; DOWN após
                          down_after_failures falhas; alerta só em mudança de estado; quiet_windows_utc;
                          estado em data/state.json; hook on_down() (Fase 2)
scripts/run_monitor.py    --check | --once | loop; log em logs/monitor.log (versão no arranque)
scripts/run_monitor.cmd / register_monitor_task.ps1   Agendador de Tarefas (no logon, reinicia se terminar)
```

Client IDs reservados (ver registry.yaml): Forex dados 10, paper 43–46, live 47–50, master 0, TF/VB 51,
scripts 61–64; Earnings & Dividends 42; Covered Calls 70–71; monitor 90.

Princípios: só leitura (readonly=True, nunca envia ordens); não é ponto único de falha (os bots não dependem dele);
segredos só em ficheiros locais fora do Git.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.3.0 | 2026-11-24 | Recuperação automática do TWS LIVE via IBC: TWS offline 1050 (C:\Jts\1050), StartTWS.bat com config-live.ini (credenciais só lá, icacls só do utilizador), AutoRestartTime=05:15 AM (dentro da janela de manutenção). registry: tws_live.recover {StartTWS.bat, process_match ibctws (nunca o tws.exe antigo), stuck_min 20, wait_min 6, twofa}. Ao arrancar envia '🔐 APROVA o login no IBKR Mobile (2FA)'. Teste manual 24/11 ~14:50: login IBC + 2FA OK, 7496 UP às 14:52. |
| 0.2.1 | 2026-11-24 | Instância única do monitor (data/monitor.lock com PID); no teste de 24/11 ficaram monitores antigos (v0.1.x) a correr em paralelo → alertas em duplicado. |
| 0.2.0 | 2026-11-24 | Fase 2: recuperação automática do IB Gateway paper via IBC. recovery.Recoverer: enquanto o endpoint está em baixo (fora das janelas de manutenção e sem data/PAUSE_RECOVERY) arranca C:\IBC\StartGateway.bat; se o processo do IBG (cmdline com 'ibgateway', nunca o tws.exe) existe mas a porta está fechada há ≥10 min, termina-o e arranca de novo; 5 min entre tentativas; máx. 3/hora, depois avisa 'intervenção manual'. Telegram: 'a arrancar via IBC', 'recuperado automaticamente via IBC'. Tarefa agendada passa a Interactive (o IBG tem de abrir no ambiente de trabalho do utilizador) com pythonw. IBC: AcceptNonBrokerageAccountWarning=yes no config-paper.ini (o aviso do paper bloqueava a abertura da porta 4002); ficheiros do ZIP desbloqueados (Unblock-File). Dependência nova: psutil. |
| 0.1.3 | 2026-11-24 | tzdata nas dependências (erros 'No time zone found with key US/Eastern' ao ler ordens) |
| 0.1.2 | 2026-11-24 | Tarefa agendada com principal S4U (como a do TP cap do forex) e relançamento a cada 5 min se não estiver a correr |
| 0.1.1 | 2026-11-24 | Tarefa agendada via cmd.exe com aspas (caminho com espaços não arrancava) |
| 0.1.0 | 2026-11-24 | Fase 1: registo único de client IDs, verificação da configuração dos bots, monitor TWS live + IBG paper com Telegram |
