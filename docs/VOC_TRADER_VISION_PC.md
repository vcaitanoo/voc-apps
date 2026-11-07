# VOC Trader Vision PC — Windows Beta 0.1.0 (2026-11-07)

## Estado real

- **Aplicação nova para Windows, não APK Android**. Solicitada como adaptação do VOC Trader Vision (Hezilex no Chrome) com motor técnico inspirado no projeto MT5.
- Código-fonte completo no mesmo repositório, branch `feature/voc-trader-vision-windows-adaptive-20261107`, pasta `trader-vision/windows/`.
- Commit-fonte integral da build Windows: `0def6ccfe19078abdfb1f90ebf43abdc83988724`.
- Backup original compactado no repositório: `trader-vision/windows/source.tar.xz.b64` (cópia exata de código + testes + docs), SHA-256 do arquivo .tar.xz `707ad38dc8b7cfd39cfc6a2a0f2a39b9479f4ac4e8a25f99bf5cf7170281aa83`.
- Windows GitHub Actions (runner Windows x64, Python 3.11, 10 testes): `https://github.com/vcaitanoo/voc-apps/actions/runs/42424660408` — **conclusão success**. Incluiu PyInstaller onedir, pacote ZIP, source commit e publicação.
- Release **pré-lançamento**, não stable: `https://github.com/vcaitanoo/voc-apps/releases/tag/voc-trader-vision-pc-v0.1.0-beta`.
- Download: `https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.0-beta/VOC-Trader-Vision-PC-0.1.0-beta.zip`
- ZIP asset tamanho 73.206.920 bytes, SHA-256 **`67001e91f944eb792fdf9a58e18c60de3827ade14b47c629008c88099479627f`** (GitHub Releases asset digest). **Executável Windows NÃO ASSINADO** e **não executado em computador físico** no assistente; CI/testes de lógica/empacotamento não garantem runtime correto nem eficácia de sinais.

## Funções implementadas (beta)

- Tkinter painel lateral, leitura da tela via mss, OCR opcional via Tesseract externo, calibração manual 10 regiões, detector de candles OpenCV, monitoramento e log. Ao iniciar sempre **desarmado**.
- Conta Demo, URL Hezilex, ativo, valor, expiração, saldo, cronômetro e botões devem ser reconhecidos na tela; Chrome/Edge/Brave precisa estar em primeiro plano; existe recaptura e revalidação imediatamente antes de clique DEMO com pyautogui. Se falhar qualquer verificação, **sem clique**. Não modifica stake/expiração do site.
- Motor de contexto H4/H1/M15/M5/M1 por candles fechados quando a fonte é **MT5 leitura apenas** ou arquivos CSV; classificação baseada em EMA9/21/50/200, ADX Wilder, ATR, RSI, Bollinger, estrutura, tick volume se presente; estratégias continuação, rompimento/reteste, varredura, extremos da lateralização, exaustão, expansão. Não representa probabilidade de acerto pela nota.
- Screen Hezilex só tem **um timeframe visual e OHLC de pixels**, não dados multi-timeframe reais. Não misturar preços MT5 com Hezilex. Se faltar histórico real, engine avisa; clique em modo M5 limitado precisa autorização explícita. Em screenshot normal de 32 candles não haverá gatilho porque exige 60 candles fechados (zoom/histórico/fornecedor pendente).
- Limite 1% estrito: **saldo €32,05 e mínimo €1 ⇒ bloqueado**, pois 1% são €0,32. Proteção não é burlada pela quantia mínima da corretora. Diário metas/perdas configuráveis; log de resultados por diferença de saldo com confirmação dupla e marcação de não confirmado.
- **MT5 não recebe ordens**: sem integração de execução com bot MT5 nem trailing original, que depende de fonte estável fornecida pelo dono. Hezilex tem expiração fixa sem SL/trailing de pips. Preservar a lógica do trailing original do MT5, não inventar adaptação.

## Próxima homologação

- Usuário precisa enviar **print completo do PC** com URL, Conta Demo, saldo, nome do ativo, gráfico, botões Comprar/Vender, valor, expiração e cronômetro, sem mostrar dados sensíveis.
- Calibrar o OCR e regiões na resolução real; conferir leitura e segurança do clique, janela da vela, início de operação, saldo, resultado e persistência.
- **Estado: BETA CANDIDATE, NÃO APROVADO em Windows físico.** Teste real necessário antes de promover a stable.

## Imutabilidade Android

- Android `pt.vcaitano.tradervision.gestaoteste` permanece como VC7 candidate no VOC Lab. `lab/catalog.json`, `manifest.json`, stable Android, assinaturas e `voc-cofre` não foram modificados por esse trabalho. Windows EXE não reutiliza nem modifica chave Android.
