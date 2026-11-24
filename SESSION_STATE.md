# SESSION_STATE — IBKR Connection Manager

Última actualização: 2026-11-24
Versão: 0.1.2 (Fase 1 — registo + monitor)

**Origem (24/11/2026):** decisão do Francisco — um serviço para os bots que falam com a IBKR (Forex + TF/VB,
Covered Calls, Earnings & Dividends): gerir client IDs e, quando o TWS/IBG cair, voltar a levantá-lo. Sem risco
agregado (cada bot gere o seu; forex/TF/VB já coordenados no projecto forex). Hoje o TWS e o IBG são arrancados à
mão; IBC ainda não instalado.

**Estado:** Fase 1 implementada e testada no sandbox (pytest 4/4; `--check` sem conflitos e com a configuração real
dos 3 projectos a bater certo; `--once` sem TWS → DOWN). Falta: instalar no PC (venv, .env Telegram, tarefa).

**v0.1.1:** instalado no PC; --once OK (TWS live e IBG paper UP). A tarefa agendada não arrancava (caminho com espaços) → corrigido.

**v0.1.2:** a tarefa 0.1.1 nunca correu (LastTaskResult 267011) → principal S4U + gatilho de 5 em 5 min com IgnoreNew.

**Próximo:** Fase 2 — instalar IBC (ver docs/FASE2_IBC.md), testar primeiro no IB Gateway paper (sem 2FA), depois TWS live.

**Regras:** só leitura; nunca escrever credenciais em código, logs ou Git; actualizar ARQUITETURA, SPECS,
SESSION_STATE e VERSION em cada alteração; comandos PowerShell para git.
