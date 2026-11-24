# IBKR Connection Manager

Serviço partilhado pelos bots que falam com a IBKR (Forex + agentes TF/VB, Covered Calls, Earnings & Dividends).

- **Fase 1 (v0.1.0, activa):** registo único de client IDs (`config/registry.yaml`) com detecção de conflitos e
  verificação da configuração real de cada bot; monitor do **TWS live (7496)** e do **IB Gateway paper (4002)**
  (porta a cada 60 s, API `reqCurrentTime` a cada 5 min, CID 90, só leitura); alertas Telegram só quando o estado
  muda (em baixo / voltou), com silêncio na janela de manutenção diária da IBKR.
- **Fase 2 (planeada):** recuperação automática — se o TWS/IBG cair, arrancá-lo via **IBC** e confirmar. Ver
  `docs/FASE2_IBC.md`.
- Fora do âmbito: risco agregado (cada bot gere o seu) e encaminhamento de ordens (cada bot coloca as suas).

## Instalação (Windows, PowerShell)
```powershell
cd "<pasta>\ibkr-connection-manager"
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env     # e preencher os 3 valores Telegram (os mesmos do bot de forex)
.venv\Scripts\python scripts\run_monitor.py --check   # valida o registo
.venv\Scripts\python scripts\run_monitor.py --once    # uma verificação
powershell -ExecutionPolicy Bypass -File scripts\register_monitor_task.ps1   # arranque automático no logon
```

## Regras
- Um bot novo ou um client ID novo **entra primeiro no `registry.yaml`**; o monitor avisa no arranque se algum
  bot estiver configurado fora da sua faixa ou se dois bots partilharem um CID no mesmo endpoint.
- Credenciais (Telegram, e na Fase 2 as do IBC) nunca no código nem no Git — só em ficheiros locais ignorados.
