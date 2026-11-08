# VOC Trader Vision PC 0.1.5 Beta — Layout real Hezilex desktop (1366×768)

Correção feita sobre **0.1.4**, sem criar outro programa e sem mexer nas estratégias, gestão, modo DEMO, fontes MT5/CSV, trailing, contas ou lógica de fechamento de operação.

**Sua tela de 1366×768 mostra BNB, 5 min, saldo €33,08, valor de entrada €5,00 e cerca de 35 velas visíveis.** Essa captura não autoriza operação automática: o símbolo configurado é EURUSD, o gráfico tem menos de 60 velas fechadas e €5 excedem 1% de €33,08 (€0,3308).

1. Abra a Hezilex no Chrome, na conta DEMO, sem mudar zoom do navegador nem posição dos componentes.
2. No VOC Trader PC abra **CALIBRAR TELA → MODELO PC 1366×768**. O modelo só é oferecido se a resolução for idêntica **e** os botões verde/vermelho estiverem nas posições esperadas.
3. O programa desenha dez retângulos sobre a captura. **Verifique cada área antes de confirmar.** A correspondência de cores NÃO garante texto, saldo ou preço corretos. Se algo não coincidir, responda NÃO e calibre manualmente.
4. Na configuração **Ativo**, escreva o ativo efetivamente aberto (ex.: BNB). O programa não muda automaticamente o ativo para evitar operar outro mercado.
5. Recolha o zoom do gráfico para mostrar pelo menos **61 candles, incluindo a vela aberta** (o motor exige 60 fechados). Clique OBSERVAR.
6. O painel flutuante mostrará **AJUSTE** com os motivos exatos enquanto faltar histórico, OCR, houver símbolo divergente ou valor acima de 1%.
7. Para 1% de risco com €33,08, o orçamento máximo por entrada é cerca de €0,33. Se a corretora exigir ao menos €1, as entradas permanecem bloqueadas; não aumentar o risco sem uma decisão expressa.

**Como calibrar o contador:** escolha os números pequenos **04:48** no rótulo VERDE de preço, à direita das velas. O relógio **04:47** no topo do bloco Expiração é outro elemento e não deve ser usado para detectar a abertura da vela.

**Painel invisível em print do Windows:** a versão 0.1.4 tenta impedir que o painel apareça em screenshots para não contaminar a leitura do gráfico. Por isso, a captura enviada pelo usuário pode não mostrá-lo embora esteja visível na tela física. Use o botão PAINEL na janela do robô para reabrir se o tiver ocultado; mantenha OBSERVAR ativo.

Esta versão **não ignora limitações de dados**, não usa informações futuras e não tenta enviar uma ordem em conta REAL. Se não houver condições de mercado e saldo adequados, a decisão correta é AGUARDAR/BLOQUEADO. Só operações conciliadas aparecem como WIN/LOSS. O Windows continua precisando de Tesseract OCR para analisar textos.

Portátil Windows: https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.5-beta/VOC-Trader-Vision-PC-0.1.5-beta.zip

---

# VOC Trader Vision PC 0.1.4 Beta — Painel flutuante para Hezilex

Nova versão portátil Windows: mesmo app/fonte da 0.1.3; sem duplicar o programa.

- Ao clicar **OBSERVAR**, aparece o **PAINEL** flutuante sempre no topo, movível pela barra superior. A janela principal tem **◉ PAINEL** para reabri-lo.
- Mostra leitura DEMO/OCR, ativo, timeframe, velas detectadas, estratégia, direção, nota técnica, cronômetro, saldo/entrada/expiração lidos, motivo de espera ou bloqueio, último gesto e WIN/LOSS confirmados.
- **■ PARAR BOT** desarma os cliques e interrompe a observação; **—** recolhe, **×** apenas esconde o painel, sem parar o bot.
- O relatório de acompanhamento é salvo em `%APPDATA%\\VOCTraderVisionPC\\monitoramento_pc.csv`, com dados reais observados, ao menos uma linha por minuto. Clique em **RELATÓRIO** para abrir.
- Para não confundir o painel com velas, o programa tenta a exclusão de captura do Windows; se indisponível, oculta temporariamente o painel durante cada screenshot. O reconhecimento continua impedindo cliques inseguros.
- A execução começa **com os cliques DESARMADOS**; nenhuma estratégia, gestão, consentimento DEMO ou limite de 1% foi alterado. Um gesto não é prova de ordem aceita: só operações conciliadas contam como WIN/LOSS.
- Para acompanhar durante a noite mantenha o PC ligado, sem bloquear a sessão; mantenha a Hezilex aberta no Chrome com a conta DEMO, sem cobrir gráfico/campos. Se a sessão bloquear ou a tela dormir, o bot não pode ler corretamente.
- Python já está incluído no ZIP; Tesseract OCR é necessário para ler texto da Hezilex e liberar tentativas DEMO. O Windows pode alertar por falta de assinatura de código.
- **Build automatizado não substitui teste real no seu computador.**

Download do portátil atualizado: https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.4-beta/VOC-Trader-Vision-PC-0.1.4-beta.zip

---

# VOC Trader Vision PC 0.1.3-beta — CALIBRAR TELA sempre visível

Correção solicitada após teste no Windows 11 1366x768: o botão CALIBRAR TELA
estava escondido abaixo de SALVAR CONFIGURAÇÃO, porque a coluna lateral tinha
mais campos que a altura da janela e não possuía rolagem.

Agora, CALIBRAR TELA e OBSERVAR/PARAR ficam fixos no alto da coluna CONTROLES;
os restantes campos podem ser percorridos pela barra de rolagem vertical.
Nenhuma alteração nas estratégias, motor de análise, gestão, permissões,
ativação do modo DEMO ou sistema de cliques.

ZIP portátil (Python embutido):
https://github.com/vcaitanoo/voc-apps/releases/download/voc-trader-vision-pc-v0.1.3-beta/VOC-Trader-Vision-PC-0.1.3-beta.zip

O usuário deve extrair tudo e executar VOC-Trader-Vision-PC.exe; não executar
START_WINDOWS.bat da fonte. O Tesseract OCR continua sendo necessário para
validar textos e habilitar toques na conta DEMO.

---

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
