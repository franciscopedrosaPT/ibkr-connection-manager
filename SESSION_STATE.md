# SESSION_STATE — IBKR Connection Manager

Última actualização: 2026-11-24
Versão: 0.2.1 (Fase 2 — recuperação IBG paper) (Fase 1 — registo + monitor)

**Origem (24/11/2026):** decisão do Francisco — um serviço para os bots que falam com a IBKR (Forex + TF/VB,
Covered Calls, Earnings & Dividends): gerir client IDs e, quando o TWS/IBG cair, voltar a levantá-lo. Sem risco
agregado (cada bot gere o seu; forex/TF/VB já coordenados no projecto forex). Hoje o TWS e o IBG são arrancados à
mão; IBC ainda não instalado.

**Estado:** Fase 1 implementada e testada no sandbox (pytest 4/4; `--check` sem conflitos e com a configuração real
dos 3 projectos a bater certo; `--once` sem TWS → DOWN). Falta: instalar no PC (venv, .env Telegram, tarefa).

**v0.1.1:** instalado no PC; --once OK (TWS live e IBG paper UP). A tarefa agendada não arrancava (caminho com espaços) → corrigido.

**v0.1.2:** a tarefa 0.1.1 nunca correu (LastTaskResult 267011) → principal S4U + gatilho de 5 em 5 min com IgnoreNew.

**GitHub:** https://github.com/franciscopedrosaPT/ibkr-connection-manager (público), commit inicial 2ab4664 (v0.1.2). Monitor a correr pela tarefa 'IBKR Connection Manager' desde 24/11 11:41.

**Fase 2 em curso (24/11):** IBC 3.24.2 instalado em C:\IBC; StartGateway.bat com IB Gateway 1051, paper, CONFIG=Documents\IBC\config-paper.ini (credenciais só lá). 1.º arranque 13:34 → a sessão IBC tomou o lugar do IBG aberto à mão (Error 1100 no antigo às 13:36). TWS live está instalado na versão auto-actualizável → para IBC é preciso o TWS offline. Muitos crashes Java (hs_err_pid*.log em C:\Jts, >70 desde agosto).

**24/11 ~13:50:** o IBG 1051 lançado pelo IBC fez login (DUP883691) mas NÃO abriu a porta 4002 (netstat sem LISTENING) apesar de Socket port=4002 nas definições; abriu depois de Apply/alterar a porta. Antes de activar a recuperação automática do paper: repetir um arranque pelo IBC e confirmar se a 4002 abre sozinha (ver OverrideTwsApiPort=4002 no config-paper.ini); se não, on_down terá de alertar 'porta não abriu'.

**v0.2.0 (24/11):** Fase 2: recuperação automática do IB Gateway paper via IBC. recovery.Recoverer: enquanto o endpoint está em baixo (fora das janelas de manutenção e sem data/PAUSE_RECOVERY) arranca C:\IBC\StartGateway.bat; se o processo do IBG (cmdline com 'ibgateway', nunca o tws.exe) existe mas a porta está fechada há ≥10 min, termina-o e arranca de novo; 5 min entre tentativas; máx. 3/hora, depois avisa 'intervenção manual'. Telegram: 'a arrancar via IBC', 'recuperado automaticamente via IBC'. Tarefa agendada passa a Interactive (o IBG tem de abrir no ambiente de trabalho do utilizador) com pythonw. IBC: AcceptNonBrokerageAccountWarning=yes no config-paper.ini (o aviso do paper bloqueava a abertura da porta 4002); ficheiros do ZIP desbloqueados (Unblock-File). Dependência nova: psutil. Teste manual: arranque pelo IBC abriu a 4002 sozinho.

**Teste 24/11 14:23:** IBG paper fechado → 14:23 '🔧 a arrancar via IBC' → 14:24:46 UP ('recuperado automaticamente via IBC') — recuperação automática do paper CONFIRMADA. v0.2.1: Instância única do monitor (data/monitor.lock com PID); no teste de 24/11 ficaram monitores antigos (v0.1.x) a correr em paralelo → alertas em duplicado.

**Próximo:** Fase 2 — instalar IBC (ver docs/FASE2_IBC.md), testar primeiro no IB Gateway paper (sem 2FA), depois TWS live.

**Regras:** só leitura; nunca escrever credenciais em código, logs ou Git; actualizar ARQUITETURA, SPECS,
SESSION_STATE e VERSION em cada alteração; comandos PowerShell para git.
