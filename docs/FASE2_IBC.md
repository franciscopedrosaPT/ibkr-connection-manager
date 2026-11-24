# Fase 2 — recuperação automática com IBC (planeado)

IBC (github.com/IbcAlpha/IBC) arranca o TWS ou o IB Gateway e faz o login sozinho. A password fica no `config.ini`
do IBC, no teu PC, escrita por ti — nunca neste repositório.

Passos (quando avançarmos):
1. Descarregar a versão Windows do IBC e descompactar em `C:\IBC` (e criar `C:\IBC\paper` e `C:\IBC\live`).
2. Copiar `config.ini` para cada pasta; preencher tu `IbLoginId`/`IbPassword` (paper no ficheiro paper, live no live),
   `TradingMode=paper|live`, `AcceptIncomingConnectionAction=accept`, `ExistingSessionDetectedAction=primary`.
3. Ajustar `StartGateway.bat` (paper) e `StartTWS.bat` (live): versão instalada, pasta do TWS/IBG, caminho do config.
4. Testar à mão: fechar o IB Gateway paper e correr `StartGateway.bat` → deve voltar sozinho.
5. Só então: `on_down` passa a chamar esses .bat (paper primeiro; live depois, com aviso de 2FA no Telegram).
No TWS live: activar Configure → Lock and Exit → **Auto restart** (mantém a sessão a semana inteira sem novo login).
