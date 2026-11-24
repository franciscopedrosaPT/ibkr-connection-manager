# SPECS — IBKR Connection Manager

Versão: 0.1.2

## Objectivo
Um único sítio para (1) atribuir e verificar client IDs de todos os bots e (2) saber, e na Fase 2 corrigir,
quando o TWS live ou o IB Gateway paper deixam de responder.

## Requisitos Fase 1 (feito)
- R1 Registo YAML de endpoints e bots com faixas de CID; conflitos detectados no arranque e em `--check`.
- R2 Confirmação da configuração real de cada bot (forex .env, E&D .env, Covered Calls config.yaml).
- R3 Monitor: TCP 60 s; API a cada 5 ciclos (CID 90, readonly); DOWN após 2 falhas; alerta Telegram em mudança de
  estado; silêncio em janelas de manutenção (UTC 04:45–05:45 por defeito); endpoints não críticos só no log.
- R4 Arranque automático (Agendador, no logon) e reinício se o processo terminar.
- R5 Versão no log de arranque; segredos fora do Git.

## Requisitos Fase 2 (planeado)
- R6 Instalar IBC (gratuito, open-source) para TWS live e IB Gateway paper; credenciais só em config local do IBC.
- R7 on_down: arrancar o TWS/IBG via script do IBC, esperar pela API (timeout), confirmar no Telegram; máx. 3
  tentativas por hora; se o live pedir 2FA, avisar "aprova no IBKR Mobile" e esperar.
- R8 Não actuar dentro das janelas de manutenção nem se o utilizador fechou o TWS de propósito (ficheiro de pausa).

## Fora do âmbito
Risco agregado entre bots; encaminhamento de ordens.

## Histórico
| Versão | Data | Alteração |
|---|---|---|
| 0.1.2 | 2026-11-24 | Tarefa agendada com principal S4U (como a do TP cap do forex) e relançamento a cada 5 min se não estiver a correr |
| 0.1.1 | 2026-11-24 | Tarefa agendada via cmd.exe com aspas (caminho com espaços não arrancava) |
| 0.1.0 | 2026-11-24 | Fase 1 |
