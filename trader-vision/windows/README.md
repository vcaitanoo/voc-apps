# VOC Trader Vision PC — Portable 0.1.2 beta (Windows x64)

**Correção da execução silenciosa (VC0.1.2):** marcar ARMAR CLIQUES agora ativa o sinal real do executor e inicia a observação automaticamente após confirmação; mostra no painel se faltam velas, se o OCR/Tesseract está indisponível, se a Hezilex não é DEMO ou se o risco impede €1. Preserva limites de 1% e calibração obrigatória. Isso NÃO garante a aceitação de qualquer ordem ou a existência de oportunidades de mercado.

**Baixe o EXE portátil, não o código-fonte:**
https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.2-beta/VOC-Trader-Vision-PC-0.1.2-beta.zip

# VOC Trader Vision PC — Portable 0.1.1 beta (Windows x64)

**IMPORTANTE: não é necessário instalar Python.** Baixe a versão executável correta no GitHub Releases:

https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.1-beta/VOC-Trader-Vision-PC-0.1.1-beta.zip

1. Extraia o ZIP inteiro numa pasta (não abra o executável de dentro do arquivo ZIP).
2. Execute **VOC-Trader-Vision-PC.exe**, na RAIZ da pasta extraída.
3. Mantenha a pasta **_internal** junto ao .exe. Não mova apenas o executável.
4. O programa inicia com cliques DESATIVADOS, aguardando sua calibração da Conta Demo.

**NÃO use** `START_WINDOWS.bat` ou `run.py` para iniciar a versão portátil. Esses dois arquivos são exclusivos do **pacote de código-fonte**, destinado a desenvolvedores, e exigem Python instalado. A janela `No suitable Python runtime found` significa que foi aberto `START_WINDOWS.bat` da fonte, **não o executável portátil**.

A V0.1.1 mantém o motor, a gestão e o painel da V0.1.0. A única correção é o empacotamento: instalador Python independente, executável em primeiro nível e teste de inicialização do pacote sem Python no PATH.

**Tesseract OCR é outra dependência**: para reconhecer os campos e autorizar cliques na conta DEMO, ele ainda precisa estar instalado/configurado; sem Tesseract, o modo de análise não deve enviar ordens.

---

# VOC Trader Vision PC — Beta 0.1.0 (Windows 11)

**Primeiro candidato de Windows, separado do app Android existente.** Este pacote não substitui a VC7 no VOC Lab, não altera qualquer app Android e não usa a keystore Android. O objetivo é testar o monitoramento e a calibração na Hezilex **DEMO** e analisar dados reais multi-timeframe do MT5 sem enviar ordens.

## Instalação

**Versão executável (se disponibilizada no GitHub Releases):** baixar `VOC-Trader-Vision-PC-0.1.0-beta.zip`, extrair toda a pasta, executar `VOC-Trader-Vision-PC.exe`. O executável é **não assinado** (o Windows SmartScreen pode pedir confirmação); não foi testado em Windows físico ainda.

**Versão pelo código-fonte:** instalar Python 3.11 x64, abrir o PowerShell na pasta, executar:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Para OCR das telas instale o **Tesseract OCR** para Windows (ou indique o caminho de `tesseract.exe` no painel). O Tesseract não acompanha o zip por ser um componente externo. É obrigatório para verificar `Conta Demo`, o domínio, o saldo, o valor, a expiração e o relógio da vela antes de qualquer clique. Sem OCR funcional, **NÃO HÁ CLIQUES**.

## Modo Hezilex — SCREEN

1. Abra `https://app.hezilex.com/traderoom` no Chrome/Edge/Brave no computador e entre em **Conta Demo**.
2. Deixe visíveis o gráfico, o ativo, os botões Comprar/Vender, o saldo, o valor e expiração. Não use zoom do navegador, mude apenas o zoom **do gráfico** se necessário.
3. No VOC Trader Vision PC selecione `SCREEN`, o ativo (ex. `AUDCAD`) e o timeframe visual (ex. `M5`); pressione **CALIBRAR ELEMENTOS NA TELA**. Selecione dez retângulos por arrasto: gráfico, conta demo, saldo, URL, nome do ativo, valor, expiração, cronômetro, comprar, vender.
4. Clique em **SALVAR CONFIGURAÇÃO** e **OBSERVAR**. Deixe `ARMAR CLIQUES` desmarcado inicialmente. Confira na aba Log que a OCR leu todos os campos e na aba Contexto que as velas são reconhecidas.
5. Só para **teste DEMO**, se escolher aceitar contexto limitado, poderá marcar a caixa e armar cliques. Mesmo armado, o sistema bloqueia automaticamente se faltarem velas (60 fechadas), não houver sinal confirmado, conta demo não for comprovada, URL/domínio não for comprovado, ativo não corresponder, valor/expiração divergirem, botões estiverem ocultos, vela não estiver nos primeiros 15 segundos ou risco exceder 1%.

**Limitação explícita:** um único print do gráfico NÃO contém H4/H1/M15/M5/M1 de modo confiável. O modo SCREEN usa apenas o timeframe visual com preços relativos de pixels, não OHLC verdadeiro. Para análise multi-timeframe real use MT5 ou pasta de CSV. **Nunca misture os preços relativos da tela Hezilex com dados MT5 para gerar um clique Hezilex.** O modo MT5 é somente leitura, pois a Hezilex pode ter preços/ativos OTC diferentes. Esta beta ainda **não é uma implementação comprovada de execução automatizada** — depende de calibração de seu layout real.

## Modo MT5 — dados, não execução

- MT5 instalado e aberto no mesmo PC, Python MetaTrader5 disponível. Na versão pelo código, execute `py -3.11 -m pip install MetaTrader5`. O executável de CI inclui o pacote quando a instalação no Windows funciona.
- Escolha `MT5`, escreva o símbolo exato do seu broker e clique OBSERVAR. A análise lê velas fechadas H4/H1/M15/M5/M1, classifica regime, escolhe setups e aguarda confirmação. **Nunca abre operações no MT5.**
- Gestão / trailing original: para ordens MT5, precisamos reutilizar o `.mq5` do bot MT5 estável e o trailing original. Não foi substituído por um novo algoritmo. Na Hezilex, expiração fixa não oferece trailing SL por pip, portanto não foi falsamente implementado.

## CSV / Análise offline

- Numa pasta, arquivos `EURUSD_H4.csv`, `EURUSD_H1.csv`, `EURUSD_M15.csv`, `EURUSD_M5.csv`, `EURUSD_M1.csv`, ou somente os timeframes disponíveis.
- Colunas: `timestamp,open,high,low,close,tick_volume`; `timestamp` UNIX em segundos ou data ISO 8601. Série crescente, só candles fechados.
- Escolha CSV → IMPORTAR PASTA CSV → OBSERVAR.
- Comparação histórica das operações liquidadas é informativa apenas com **pelo menos 30 operações realmente observadas** no mesmo setup e regime; uma nota 90/100 não significa 90% de acerto.

## Gestão de risco

- Máximo **1%** de saldo por entrada, sem arredondamento para cima além do limite.
- Se o mínimo Hezilex for €1, o saldo precisará ser **no mínimo €100** para autorizar €1 a 1%. Exemplo: com €32,05, 1% = €0,32 — o sistema bloqueia, pois €1 equivale a 3,12% do saldo.
- Meta diária (padrão 2%), limite de perdas e máximo de entradas configuráveis. Nenhuma garantia de lucro.
- Histórico de operações salvo em `%APPDATA%\VOCTraderVisionPC\demo_journal.jsonl`; configurações em `%APPDATA%\VOCTraderVisionPC\settings.json`. Resultado deduzido de duas leituras do saldo após expiração e classificado como **não confirmado** quando ambíguo; não é recibo de operação. Histórico da Hezilex permanece fonte primária.

## Projeto, continuidade e limites

- Motores: `voc_trader_pc/engine.py`, `indicators.py`, `screen.py`, `risk.py`, `tracker.py`, `journal.py`.
- Testes: `python -m pytest -q` (sem Windows/Hezilex real, testes apenas de lógica e estrutura).
- Versão candidata PC: **0.1.0-beta**, sem promoção a estável até homologação em Windows real.
- Não modifica `lab/catalog.json`, `manifest.json` nem VC7 Android.

### Para calibrar seu PC

**Envie um print COMPLETO da Hezilex no Windows, com o navegador e barra de endereço, gráfico, ativo selecionado, Conta Demo, saldo, valor, expiração e os botões Comprar/Vender visíveis.** Assim poderemos ajustar os reconhecedores e adicionar testes de regressão da geometria real do seu monitor. Não inclua credenciais, dados pessoais ou chaves no print.
