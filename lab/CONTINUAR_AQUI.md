# VOC Lab — CONTINUAR AQUI

## Objetivo
VOC Lab é o canal privado de desenvolvimento. O VOC Manager oficial não deve ser alterado para testes.

## App
- Nome: VOC Lab
- Package: `pt.vcaitano.voclab`
- Fonte: `lab/`
- Catálogo oficial: `lab/catalog.json`
- APK candidato atual do próprio Lab: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/VOC-Lab-v1.0.1.apk`
- Catálogo primário no app 1.0.1: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json`
- Fallback de catálogo: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json`

## Estado do VOC Lab

### 1.0.0 — REJEITADA EM RUNTIME
- versionCode: `1`
- versionName: `1.0.0`
- APK SHA-256: `af691404cf1057a8149f837348bf8f24d6e89eb935f3a946d1f554d9a004cf1a`
- Certificado SHA-256: `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`
- Compilação/estrutura: OK.
- Resultado no telemóvel informado pelo utilizador: **falha ao atualizar a lista**.
- Causa tratada: dependência de um único endpoint `raw.githubusercontent.com` para carregar o catálogo.
- Regra: NÃO promover 1.0.0 a estável e não voltar a usá-la como versão final.

### 1.0.1 — CANDIDATA ATUAL
- versionCode: `2`
- versionName: `1.0.1`
- minSdk: `28`
- targetSdk: `36`
- compileSdk: `36`
- Gradle: `BUILD SUCCESSFUL`
- APK: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/VOC-Lab-v1.0.1.apk`
- APK SHA-256: `d2720ed431478383e5604e084e8a57c1e693d27e8075bc1aefe9e02284725003`
- Certificado SHA-256: `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`
- Certificado DN: `CN=VOC Lab, OU=Android, O=vcaitano, L=Lousada, ST=Porto, C=PT`
- Assinatura verificada: APK Signature Scheme v3.
- Mesma assinatura da 1.0.0: SIM.
- Fonte/arquivo de build desta candidata SHA-256: `bda659206f2601c936988a1b045cbe82e30cba365dabe2bb2af6b13da2fb9ba8`
- Ficheiros alterados em relação à 1.0.0:
  1. `lab/app/build.gradle.kts` — apenas versionCode/versionName para 2 / 1.0.1.
  2. `lab/app/src/main/java/pt/vcaitano/voclab/MainActivity.java` — catálogo redundante, leitura via Vercel com fallback GitHub e erro indicando o host que falhou.
- Catálogo Vercel validado por HTTP 200 e `application/json`.
- APK validado por HTTP 200 e `application/vnd.android.package-archive`.
- Estado: compilação, estrutura, package, versão, SHA e assinatura verificados. **Execução real ainda depende de teste do utilizador.**
- Regra: somente promover 1.0.1 a STABLE se o utilizador confirmar que a lista carrega no telemóvel.

## Chave do VOC Lab
- Usar sempre a mesma chave do pacote privado `VOC_LAB_CHAVE_PRIVADA_BACKUP.zip`.
- Nunca gerar outra chave para uma atualização do package `pt.vcaitano.voclab`.
- Nunca publicar a chave ou palavras-passe em repositório público.

## Regra de continuidade
Cada app possui no máximo:
1. uma versão `stable` confirmada pelo utilizador;
2. uma versão `candidate` em teste.

Uma build apenas compilada nunca vira `stable`.

## Publicar um candidato
1. Partir da última fonte confirmada do app.
2. Registar packageName, versionCode, versionName, SHA-256 da fonte/base, certificado de assinatura e ficheiros modificados.
3. Fazer somente as alterações pedidas.
4. Gerar APK pelo Gradle a partir da fonte.
5. Validar packageName, versionCode, versionName, SHA-256 do APK e SHA-256 do certificado.
6. Hospedar o APK numa URL HTTPS direta.
7. Editar APENAS o campo `candidate` do app em `lab/catalog.json`.
8. Sincronizar também o catálogo servido pelo VOC Lab no Vercel quando esse endpoint for usado como primário.
9. Não substituir `stable` até o utilizador testar e confirmar que funciona.

Formato do candidato:
```json
"candidate": {
  "versionCode": 40,
  "versionName": "2.9",
  "apkUrl": "URL_HTTPS_DIRETA_DO_APK",
  "sha256": "SHA256_DO_APK",
  "signatureSha256": "SHA256_DO_CERTIFICADO",
  "notes": "Alteração exata desta build"
}
```

## Tela Sempre Ativa — regra específica atual
- `stable` deve permanecer V25 / versionName `1.0.20` / versionCode `25` até confirmação explícita do utilizador de uma candidata mais nova.
- Uma V29 em geração noutra conversa deve entrar somente como `candidate` depois que o APK real estiver disponível e forem verificados package, versionCode, versionName, SHA-256 e certificado.
- Não usar V28, ficheiros antigos ou APK inferido pelo nome como substituto da V29.

## Quando o utilizador disser que ficou perfeito / aprovado
1. Copiar os dados de `candidate` para `stable`.
2. Mover/copiar o APK aprovado para a área estável e atualizar a URL.
3. Definir `candidate` como `null`.
4. Atualizar o checkpoint do projeto e guardar a fonte confirmada.
5. Manter no máximo a stable atual + uma stable anterior de segurança na área de fonte; candidatos rejeitados devem ser eliminados.

## Quando o candidato falhar
1. NÃO alterar `stable`.
2. Remover o APK candidato rejeitado.
3. Definir `candidate` como `null`.
4. Voltar obrigatoriamente à fonte marcada como estável.

## Regra para qualquer IA
A IA deve ler este ficheiro e `lab/catalog.json` antes de publicar qualquer APK. Nunca inferir a base a partir do nome de APK, conversa antiga, pasta temporária ou build não confirmada.

## Teste no telemóvel
Abrir VOC Lab > ATUALIZAR LISTA > escolher o app > INSTALAR/ATUALIZAR PARA CANDIDATO.
O Lab valida SHA-256, packageName, versionCode e assinatura antes de pedir a instalação ao Android.

## Separação obrigatória
- `VOC Lab`: desenvolvimento e testes privados.
- `VOC Manager`: distribuição oficial/futura dos apps aprovados.


## VOC Lab — recuperacao de catalogo (2026-11-04)
- Falha relatada: Hora Jarvis 1.2.0-LAB nao aparecia no VOC Lab instalado, embora `lab/catalog.json` na branch main contenha `hora-jarvis` com candidato VC3 e APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`.
- Diagnostico: cliente Android da fonte consulta primeiro `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` e nao compara com GitHub se esse endpoint responder com catalogo antigo. Endpoint Vercel original sem projeto acessivel na conta conectada; espelho nao sincronizado.
- Correcao preparada: priorizar `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json` e manter Vercel como fallback em branch `fix/voc-lab-catalog-github-first-20261103`. Fonte-fix inicial `7a410c45e6f101d826bd33011e6bd5a90d1e3759`; candidata Android original (package `pt.vcaitano.voclab`, versionCode 4, versionName 1.0.3) NAO distribuida pois faltam os Secrets `VOC_LAB_KEYSTORE_B64`/senha; manter certificado esperado SHA-256 `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`, nao gerar chave substituta para o pacote oficial.
- Recuperacao temporaria: branch fonte `fix/voc-lab-catalog-github-first-20261103`, commit `99ed879a3d806c7bf2c2d23c21de5b39bfc8d2a6`, gerou app separadamente instalavel `pt.vcaitano.voclab.emergencia`, VC4/1.0.3, label `VOC Lab — Atualizado`, build Gradle debug + estrutura e assinatura validadas, APK SHA-256 `8a6c9428a0195075f8494b16cbfd89e4544c8f1d3dd89527e46523ffa9fa5fa0`.
- APK de recuperacao publico HTTPS: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/apks/voc-lab-emergencia/VOC-Lab-Atualizado-1.0.3-VC4.apk`; URL verificada pelo proprio workflow mediante download e comparacao byte-a-byte em `https://github.com/vcaitanoo/voc-apps/actions/runs/41743646813`.
- Estado: somente TESTE, nao aprovado em Android real, assinatura debug temporaria do runner sem identidade para futuras atualizacoes; nao e a stable do VOC Lab. Codigo original e stable nao alterados, `manifest.json` nao alterado, `lab/catalog.json` mantido.
- Proxima etapa: recuperar keystore original com backup privado valido e Secrets, compilar a correção sob pacote oficial com mesmo certificado, validar em Android e so depois distribuir o app oficial. Evitar substituir oficialmente a assinatura por debug.

## Hora Jarvis — confirmado no catálogo do VOC Lab ORIGINAL (2026-11-04)
- Pedido: Hora Jarvis 1.2.0 no VOC Lab Android original, junto dos outros apps, sem instalar um segundo Lab.
- Causa confirmada no GitHub Actions (workflow read-only `41745953937`): `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` HTTP 200 com 8 apps, sem `hora-jarvis`, atualizado em 2026-11-01; `lab/catalog.json` GitHub possuía Hora Jarvis, mas o app Android aceita o primeiro catálogo válido e não chega ao fallback.
- Caminho real do endpoint: alias `temporary-snappy-redwood-yqm3s0d.vercel.app` pertence ao projeto Vercel `prj_EU0b8etzUUFAMiLg18Ll7EU7uXN4` (atual nome `ache-aqui-politica-privacidade`), deploy `dpl_9VXHTWu99R32KqtXXe7wyPS34L4Y`; `vercel.json` reescreve `/catalog.json` para Supabase Edge Function `https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/voc-lab-catalog`.
- A função `voc-lab-catalog` lê exclusivamente `public.voc_lab_catalog_store`, linha `id=main`, campo JSONB `body`; por isso o GitHub estava correto mas não aparecia no Lab original.
- CORREÇÃO EFETIVA: SQL condicional no projeto Supabase `khinnoxpesnhtmmvrken`, acrescentou APENAS a entrada `hora-jarvis` retirada de `lab/catalog.json` ao JSONB da linha `main`, preservando as 8 entradas existentes e seus estados. `updatedAt` ficou `2026-11-04T00:22:14Z`.
- Verificação final independente (GitHub Actions read-only `41746339571`, executado depois da alteração): endpoint Vercel ORIGINAL HTTP 200, `app_count=9`, `has_hora_jarvis=True`; ids: `tela-sempre-ativa,voc-manager,voc-tv,damas,jarvis,simulador-jetpack,divulgador,gps-3d,hora-jarvis`. APK do Hora Jarvis HTTP 200, 38139 bytes, SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e` (igual ao candidato do catálogo).
- Nenhum APK de app, assinatura, versão stable, `manifest.json`, código Android VOC Lab, Vercel/privacidade Ache Aqui ou outros 8 apps foi modificado nesta correção. App normal instalado deve buscar o catálogo atualizado tocando em ATUALIZAR LISTA.
- O novo Hora Jarvis `1.2.0-lab` `versionCode 3` é CANDIDATO, não confirmado como funcional em Android real. A versão `1.1.0-teste` confirmada permanece base estável do Hora Jarvis fora do LAB.
- Evitar usar a branch experimental `fix/voc-lab-catalog-github-first-20261103` como base ou implantar VOC Lab de recuperação. A correção real foi no backend que já atende o VOC Lab original.

## VOC Trader Vision — VC3 permanente publicada após migração autorizada (2026-11-04)

- Autorização do proprietário: **uma única reinstalação** para substituir o certificado debug da VC2 por uma identidade de assinatura permanente; **não criar outro app**. A única entrada de catálogo permanece `voc-trader-vision-gestao-teste`, nome **VOC Trader Vision**, package **`pt.vcaitano.tradervision.gestaoteste`**.
- APK nova candidata VC3 / `0.3.0-demo` publicado na URL `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.3.0-demo-VC3.apk`; SHA-256 **`18d0c7f5ae76595bf2fe248c6a664807cf735b75991e0ac1969e101056a21f88`**.
- Certificado público SHA-256 **`e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`** (ESSA é a identidade fixa para todas as próximas atualizações). Assinatura nova da VC3 é DIFERENTE da V2 `3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`; para instalar VC3, desinstalar VC2 UMA VEZ (perda possível de configurações locais); depois nunca mais alterar a assinatura.
- Código de release: `vcaitanoo/voc-apps`, branch `release/voc-trader-vision-vc3-permanent-key-20261104`, commit **`4425d13b64cf67c2b7c74afb215edbb627a2cb5d`** (Gradle signed release). Workflow `41925752844`: **sucesso**, testes RiskManager, EntryTiming, PanelPosition; Gradle, manifesto, package, DEX/resources, assinatura, APK SHA/URL verificados. Endpoint primário do VOC Lab `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` validado no workflow **`41926433279`**: uma única entrada VC3. `lab/catalog.json` no GitHub: 8 apps, 1 Trader; Supabase ativo `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store/main`: 10 apps, 1 Trader. Outras aplicações, stable e `manifest.json` preservados.
- Chave privada Android **não** guardada em claro; PKCS#12 + passwords cifrados com RSA-OAEP-SHA256 + AES-256-GCM no GitHub privado `vcaitanoo/voc-cofre/projetos/voc-trader-vision/keystore-vc3-permanent.encrypted.json`; chave RSA privada de recuperação cifrada com senha PBKDF2 no mesmo diretório `recovery-private-encrypted.pem`; foi entregue um **kit de recuperação privado** com código de recuperação só ao proprietário (não no Git). Correspondência ciphertext conferida; rotina `trader-vision/scripts/recover_signer.py` e referência `trader-vision/security/CONTINUIDADE_ASSINATURA.md` na branch release. Para futura release, **RECUPERAR e REUTILIZAR a MESMA keystore**, nunca gerar outra. O workflow de migração original foi bloqueado contra regeneração após o sucesso.
- **Estado: CANDIDATE; NÃO STABLE.** APK ainda **não foi aberto/testado em Android real** pelo usuário. Sem confirmação, nunca promover a stable. O score 0/100 quando não há sinal continua normal; score 92/100 é heurística de confluência, não 92% de probabilidade. Clique de ordem segue condicionado à acessibilidade/conta DEMO/campos e não foi comprovado no telefone.

## VOC Trader Vision — VC4 publicada no mesmo app, OCR DEMO e permissões (2026-11-04)

- **Problema observado em Android na VC3:** screenshot mostrava VENDER 96/100 e "Intervalo entre tentativas: 255s restantes", mas TENTATIVAS=0. No código o cooldown era iniciado ANTES da validação de conta/campos/gesto. Também a Hezilex desenha parte da interface em canvas e não oferece todos os textos via Accessibility, impedindo confirmações necessárias.
- **Correção VC4:** `pt.vcaitano.tradervision.gestaoteste` **idêntico**, `versionCode=4`, `versionName=0.4.0-demo`. Aguardar sinal estável, executar OCR local ML Kit do screenshot para conferir rótulo Conta Demo na região ativa, valor e expiração abaixo dos botões, e só então despachar gesto via AccessibilityService em Chrome. **Falha de OCR/gesto não inicia cooldown longo:** exibe razão `SEM ENTRADA` e tenta novamente após 10s. Cooldown `max(timeframe, expiração)` começa APENAS quando Android confirma a conclusão do gesto; contador de tentativas é contador de **gestos**, não garantia de ordem aceita pela corretora. Conta real continua estritamente bloqueada.
- **Pedidos adicionais do dono:** ao abrir, pedir automaticamente permissões faltantes em sequência (notificações, sobreposição, acessibilidade e consentimento de captura de ecrã); Android exige ação manual do usuário nas próprias telas e consentimento para cada sessão MediaProjection. Botão `GUARDAR CONFIGURAÇÃO` movido para BAIXO dos controles de ativação e abertura Hezilex. Painel arrastável e todas as estratégias/gestão anteriores preservados.
- Arquivos Android modificados: `trader-vision/app/src/main/java/pt/vcaitano/tradervision/MainActivity.java`, `VisionService.java`, `TapService.java`, novo `VisualTradeVerifier.java`, `app/build.gradle.kts` (+ ML Kit bundled local OCR), teste `trader-vision/tests/VisualTradeVerifierTest.java`. Nenhum package novo. Fontes exatas do build validado branch `fix/voc-trader-vision-vc4-real-entry-20261104`, commit `697df843ad6818a889e7a5e543656ade8bffc875` (testes + Gradle debug/release unsigned).
- **Assinatura reutilizada sem gerar nova chave:** certificado imutável VC3 SHA-256 `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`. O kit privado de recuperação fornecido pelo proprietário foi usado **localmente/offline** para desencriptar a PKCS#12 de `voc-cofre`. Com `apksigner` v2 e `--alignment-preserved true`, foi criado o APK VC4 assinado, sem transmitir a chave privada a workflows ou repositórios. Um bloco de assinatura digital **público** foi publicado na branch (não contém senha nem chave privada), permitindo reconstruir exatamente o mesmo APK a partir do unsigned imutável; GitHub Actions `41931994531` reconstruiu, verificou package/resources/DEX, assinatura, SHA, publicou e verificou HTTPS byte a byte.
- **APK VC4:** `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.4.0-demo-VC4.apk`; SHA-256 **`a567f412d23ee308251d752b3e04f2cd21371f9fe4679792a130e234194d441b`**, certificado igual VC3 `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`. Atualiza **por cima** da VC3 já instalada, sem reinstalação nem criação de app separado.
- Catálogo GitHub `lab/catalog.json` e o ativo Supabase `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store/main` atualizados, preservados todas as demais apps/estáveis e **exatamente uma entrada** VOC Trader Vision (`voc-trader-vision-gestao-teste`). Validação independente endpoint original no CI **`41932337199`**: sucesso, 1 Trader, versionCode4 e assinatura/hash iguais, URL APK SHA válida.
- **Validação:** 4 suites JDK `RiskManagerTest`, `EntryTimingTest`, `PanelPositionTest`, `VisualTradeVerifierTest`, Gradle compile, APK manifesto/package vc4, recursos e DEX, assinatura e hash remoto. **Execução Android real da VC4 ainda NÃO VERIFICADA** (a VC3 foi vista aberta mas não executou ordem). Não promover VC4 a stable até o dono confirmar comportamento em Android; não afirmar que trade é aceito ou que 96/100 é 96% de chance de acerto.
- **Continuidade futura:** só atualizar a fonte confirmada pelo usuário, package id fixo, assinatura VC3 fixa, versionCode sempre crescente, usar voc-cofre para recuperação; publicar candidatos APENAS no registro existente VOC Lab, nunca outros apps nem APK com nova chave.

## VOC Trader Vision — pendências relatadas em teste real da VC4 (2026-11-05; NÃO IMPLEMENTAR AINDA)

O proprietário **pediu expressamente apenas registrar observações e continuar testando**. Não modificar APK, código-fonte, assinatura, stable/candidate ou catálogo por causa desta nota. A VC4 permanece candidata, sem confirmação de aprovação como base estável.

1. **Resultados não computados:** o painel mostrou `TENTATIVAS 2 • WIN 0 • LOSS 0`; o usuário relatou que **as duas operações foram WIN**. Atual implementação conta gestos Android completados e possui botões de marcação manual, mas não reconcilia automaticamente o resultado real/histórico da Hezilex. Próxima atualização: identificar operação efetivamente aceita (não apenas gesto) e resultado final pelo histórico ou por comprovação visual, evitando contabilizar duas vezes. Não inventar resultados.
2. **Momento da entrada:** usuário observou toques **no meio das velas de 5 minutos**. Próxima atualização: avaliar sincronização de fecho/abertura conforme período real do gráfico e expiração da corretora; manter confirmação da estratégia e não supor que o relógio Android equivale ao relógio da Hezilex.
3. **Detecção visual de velas deficiente — nova captura `41098.jpg`:** robô mostra `Velas visíveis: 16`, `Zoom/histórico insuficiente: requer 22 velas identificáveis`, `MERCADO: SEM DADOS`, `AGUARDAR 0/100`, embora o gráfico apresente visualmente **dezenas** de candles vermelhos e verdes, vários estreitos. A falha é compatível com subcontagem pelo segmentador, e não prova zoom insuficiente. Inspecionado `VisionEngine.java`: region of interest começa em `h * .38`; colunas exigem pelo menos 3 pixels coloridos; agrupamento de corridas tolera lacunas de até 4 px, rejeita `votes < 18` e `last-st < 3`. **Hipóteses a validar com testes de imagem**, não diagnóstico definitivo: velas estreitas/doji desconsideradas, candles vizinhos fundidos, sobreposição de traço de preço e texto, cores/zoom e área de recorte incompleta. Para a próxima revisão, criar testes com capturas reais, comparar contagem e posições (incluindo pavios, corpos finos/doji, espaçamento e cores), reduzir falsos positivos e mostrar distinção entre "não detectado" e "histórico insuficiente". Não diminuir cegamente o limiar para forçar operações.
4. Continuar com **um único** app/package `pt.vcaitano.tradervision.gestaoteste`, certificado permanente SHA-256 `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`; próxima alteração só após autorização posterior. Nada foi compilado ou publicado em decorrência destas anotações.

## VOC Trader Vision — VC5 DEMO publicada (2026-11-05): velas, sincronização e resultados

- **Pedido autorizado:** corrigir os três problemas anotados na VC4: (1) subcontagem de velas visíveis (16 vs dezenas no screenshot), (2) entradas no meio das velas, (3) WIN/LOSS não contabilizados. Nenhum outro aplicativo foi modificado e nenhuma nova identidade Android foi criada.
- **Base candidata observada em Android:** VC4 `0.4.0-demo`, package `pt.vcaitano.tradervision.gestaoteste`, APK SHA-256 `a567f412d23ee308251d752b3e04f2cd21371f9fe4679792a130e234194d441b`, assinatura permanente SHA-256 `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`, source build `697df843ad6818a889e7a5e543656ade8bffc875`. A VC4 era **CANDIDATE**, não confirmação de base estável final.
- **Novo candidato único:** VC5 `0.5.0-demo` / `versionCode=5`, **mesmo** package `pt.vcaitano.tradervision.gestaoteste`, **mesmo** certificado permanente `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`; não desinstalar VC4 para instalar VC5.
- **Detector melhorado:** `VisionEngine.java` corta menos a área superior, separa candlesticks adjacentes sem tolerância de 4px que fundia velas e depois as descartava por largura; remove linhas de preço horizontais e exclui as coordenadas da sobreposição móvel. No screenshot real `41098.jpg` uma verificação local exploratória do segmentador encontrou cerca de **48** barras em vez de 16; contagem no Android/Hezilex após VC5 ainda requer teste. Fixture sintética `VisionEngineTest.java` cobre velas estreitas, linha de preço e sobreposição.
- **Momento da entrada:** `CandleClock.java` e OCR `VisualTradeVerifier.candleRemainingSeconds` leem os segundos restantes mostrados junto ao preço no gráfico Hezilex. Toques automáticos DEMO só são elegíveis nos **primeiros 15 segundos da vela** do período escolhido; não usam o relógio civil do Android. Se o cronômetro não for reconhecido, bloqueia a entrada, informa o motivo e tenta nova leitura sem inventar horário. Mantém estabilidade do sinal e gestão/limites já existentes.
- **Resultados:** `OutcomeLedger.java` e `VisionService.java` registram, depois de um gesto DEMO, o saldo inicial OCR e um resultado pendente. Depois da expiração, duas leituras posteriores do saldo compatíveis com o lucro ou perda daquela única operação podem contabilizar `WIN`/`LOSS` automaticamente. Se não houver prova suficiente em até 3 minutos após expiração, contabiliza `NÃO CONFIRMADO` (não finge vitória nem derrota); resultado se baseia em diferença de saldo visível, **não em um recibo oficial da corretora**. Só permite uma operação pendente de cada vez; mantenha outros trades fora dessa conta para não contaminar saldo. As duas vitórias relatadas na VC4 NÃO são importadas retroativamente e podem ser marcadas manualmente.
- **Arquivos Android alterados/adicionados apenas no projeto trader-vision:** `VisionEngine.java`, `VisionService.java`, `VisualTradeVerifier.java`, `MainActivity.java`, `CandleClock.java` (novo), `OutcomeLedger.java` (novo), `app/build.gradle.kts`; novos testes `VisionEngineTest.java`, `CandleClockTest.java`, `OutcomeLedgerTest.java`, alteração `VisualTradeVerifierTest.java`. Não modificar lógica de risco, estratégias, acessibilidade, consentimento, layout principal, package, AdMob ou assinatura.
- **Fonte do APK compilado:** `vcaitanoo/voc-apps` branch `fix/voc-trader-vision-vc5-candles-timing-results-20261105`, commit-fonte `e7158b86b4d21d05378c7fc6261875421f73307f`. CI `41940351683` sucesso: 7 suites de testes Java e Gradle `assembleDebug` + `assembleRelease` unsigned, manifesto, DEX, resources. APK unsigned SHA `0c1719188d11fd0de105adbf63b7cd4aabd7fc7ebc75d0008c5a032895557780`.
- **Assinatura:** a **mesma keystore PKCS12 permanente VC3** foi recuperada localmente do backup cifrado no `vcaitanoo/voc-cofre`, verificada contra o certificado fixo, usada para assinar offline o APK do exato unsigned build; nenhuma chave nova foi criada. Foi publicado somente o bloco público de assinatura (não a chave/segredo) em `trader-vision/signing/vc5-public-signing-block.json.gz.b64`. CI `41940975678` sucesso: recompôs APK byte-a-byte, verificou assinatura, package, versionCode, DEX/resources, publicou e verificou download HTTPS idêntico.
- **Artefato:** `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.5.0-demo-VC5.apk`, APK SHA-256 **`6612e077545e4ae901b78d5e2b2dd75bef60763a3a116fa1d12679e73c310670`**, certificado `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`. GitHub `lab/catalog.json`, Supabase ativo `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store/main` e endpoint público `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` atualizados/verificados; CI endpoint `41941165864` sucesso, **uma só entrada VOC Trader Vision**.
- **Importante:** compilação, testes de lógica, hash, assinatura, URL e catálogo validados; **execução da VC5, detecção real de WIN/LOSS e toque real no Android ainda NÃO testados**, portanto VC5 segue `candidate` e NÃO pode promover-se a stable sem aprovação explícita do usuário.

## VOC Trader Vision — VC6 corrigiu 0 velas quando painel encobria Vender (2026-11-05)

- **Relato real:** na candidata VC5, captura `41100.jpg` mostrava candlesticks visíveis, mas painel flutuante arrastado para a região de **Vender**, com `Velas visíveis: 0`, `Tela: NÃO CALIBRADA`, `Não achei simultaneamente Comprar e Vender`. Defeito comprovado na `VisionEngine.analyze`: retornava imediatamente ao falhar a calibração dos dois botões, antes de executar qualquer detecção de velas.
- **Base reconstruída:** a fonte da VC6 foi recriada a partir da fonte da **VC4 observada fazendo duas tentativas no Android**, branch anterior `fix/voc-trader-vision-vc4-real-entry-20261104`, commit base `d1b18ebe8e7dc95cbedc71af76831bc79a29a32f` (código Android da VC4). Foram reaplicados os recursos pedidos na VC5 (detector, momento da vela, apuração DEMO) junto à correção, sem usar APK, bytecode ou artefatos defeituosos como base.
- **Correção VC6:** o reconhecimento de candlesticks deixou de depender da detecção dos botões. Detecta a faixa horizontal larga de Comprar para calibrar a geometria, mede o CENTRO vertical da faixa para posicionar o toque dentro do botão e faz o chart analyzer continuar mesmo se Comprar/Vender não puderem ser calibrados. `out.buttons=false` **bloqueia todos os toques** quando controles estão cobertos e o painel explica que deve ser movido. A máscara das regiões ocultadas pela sobreposição é atualizada quando o próprio texto do painel muda de altura. Sem desligar proteções contra conta REAL ou alterar gestão/estratégias.
- **Validação da captura:** ensaio local de segmentação sobre `41100.jpg` detectou aproximadamente **34 velas** apesar do painel encobrindo a região de Vender (não é teste de câmera Android). `VisionEngineTest` ganhou regressões sintéticas para painel sobre Vender e ambos os controles, sem apagar a detecção de velas, além da checagem das coordenadas verticais do toque.
- **Identidade invariável:** único package `pt.vcaitano.tradervision.gestaoteste`, versão candidata **0.6.0-demo** / `versionCode 6`, sem outro app no catálogo; certificado permanente original SHA-256 `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`. Chave da assinatura recuperada do kit original cifrado no `vcaitanoo/voc-cofre`, assinatura feita offline, material em claro não foi publicado e **nenhuma nova chave** foi criada.
- **Fonte compilada:** branch `fix/voc-trader-vision-vc6-from-tested-vc4-20261105`, commit `2cdf33e988134a5d27f7d4bc2a10d97a8c9433d2`. Comparação com fonte VC4 autorizada: `VisionEngine.java`, `VisionService.java`, `VisualTradeVerifier.java`, `MainActivity.java`, `CandleClock.java` (novo), `OutcomeLedger.java` (novo), `app/build.gradle.kts`, e testes `VisionEngineTest.java`, `VisualTradeVerifierTest.java`, `CandleClockTest.java`, `OutcomeLedgerTest.java`; foi criado workflow de validação VC6. O motor de estratégias em `VisionEngine.evaluate` permanece intacto, bem como gerenciamento de risco e serviços de acessibilidade.
- **Build/QA:** GitHub Actions `41944388874` (CI 7 suites Java, Gradle debug + unsigned release, package/versões, recursos/DEX), unsigned APK SHA-256 `6a8597f310a0d57a0dce08caa7c252af9138cdee7939ad934824903398c9ba01`. O build unsigned do checkpoint reconstituído é byte a byte idêntico à versão validada no commit `03634126145fcbdcf7a9095bda5afe11b52cd2a6`. Assinatura offline e bloco público `trader-vision/signing/vc6-public-signing-block.json.gz.b64`; workflow `41944945374` confirmou assinatura, manifesto/DEX/resources, SHA-256 e download remoto byte a byte.
- **APK candidato:** `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.6.0-demo-VC6.apk`, SHA-256 **`3bf00b2b277292aec724d5597f8eee476b4e9eb4764a0641382a778f6052a125`**, certificado SHA-256 inalterado. GitHub `lab/catalog.json` com **8 apps / 1 Trader** e Supabase ativo `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store/main` com **10 apps / 1 Trader**, ambos candidatos VC6. Workflow `41945133997` verificou endpoint primário efetivo `temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` (somente uma entrada Trader, VC6 e URL/hash da APK válidos).
- **Estado:** **CANDIDATE**, stable não modificada, `manifest.json` oficial intacto. NÃO foi testada a execução, análise em tempo real, gestos ou apuração de resultado da VC6 em Android físico/emulador; compilação e validação estrutural **não** provam que abre. Após usuário instalar por cima da VC5 e confirmar funcionamento, reavaliar promoção e checkpoint estável. **Se o painel cobrir os botões, mover o painel antes de permitir cliques, ainda que candlesticks apareçam.**

## VOC Trader Vision VC7 — confirmação oscilante 2/3, contagem antiga de 90 s e painel piscando (2026-11-05)

- **Relato real sobre a VC6:** nota ultrapassa 78 mas oscila; confirmação de 3 capturas nunca passa de 2; painel pisca e mostra repetidamente "faltam 90 segundos" sem entrada. A VC6 é CANDIDATE COM DEFEITO, jamais promovê-la a base estável.
- **Diagnóstico de código:** `VisionService.evaluateSignal` construía a chave de estabilidade como `direção|nome da estratégia` e reiniciava imediatamente a contagem em qualquer leitura sem sinal; mudança de estratégia, mesmo preservando VENDER/COMPRAR, reiniciava 2/3. Quando `CandleClock.check` não autorizava, `reportGesture(clock.reason)` fixava o texto do contador por **30 segundos**, o que parecia um cronômetro parado; loop de OCR aproximadamente a cada segundo e `text.setText` a cada captura causavam redesenhos/flicker.
- **Fonte-base escolhida:** último código observado executando operações no Android foi VC4 (duas entradas; usuário relatou ambas WIN), branch `fix/voc-trader-vision-vc4-real-entry-20261104`, commit base `d1b18ebe8e7dc95cbedc71af76831bc79a29a32f`; VC5 e VC6 são tentativas não aprovadas e NÃO viraram base. Branch VC7 `fix/voc-trader-vision-vc7-signal-clock-20261105` derivada da fonte VC4 com funcionalidades já solicitadas reaplicadas seletivamente.
- **Correções realizadas:** novo `SignalConfirmation.java` com votos de direção COMPRAR/VENDER em janela deslizante de cinco capturas, só permite avançar com pelo menos **3 concordantes** e no máximo **1 voto oposto**, exigindo sinal/score válido NA captura atual; nome de estratégia não reinicia progresso. `EntryTiming` continua com meta de 3 confirmações e cooldown original; não se relaxa a gestão nem permite conta real. `VisionService` limita OCR do cronômetro a aproximadamente 1/3 segundos, registra motivo de espera de vela sem `reportGesture` com validade fixa de 30 segundos, limita redesenho normal do painel a 2,2 s e entrega erros/gestos imediatamente. Entrada continua condicionada ao início de nova vela confirmado pelo cronômetro da própria Hezilex; **90 s para virar a vela são uma espera legítima**, não autorização para entrar no meio.
- **Arquivos modificados desde fonte VC4:** `trader-vision/app/src/main/java/pt/vcaitano/tradervision/VisionService.java`, `VisionEngine.java`, `VisualTradeVerifier.java`, `MainActivity.java`, `app/build.gradle.kts`; adicionados `SignalConfirmation.java`, `CandleClock.java`, `OutcomeLedger.java`, testes `SignalConfirmationTest.java`, `VisionEngineTest.java`, `VisualTradeVerifierTest.java`, `CandleClockTest.java`, `OutcomeLedgerTest.java` e workflow de validação. `TapService`, RiskManager, package, permissões, assinatura e gestão existentes NÃO foram alterados.
- **Fonte EXATA compilada:** commit `f441b67689f6aed06681a0e6b660648f236b60ad` na branch VC7. CI GitHub Actions `41949231141` passou testes unitários Java (incluindo novo caso 3-de-5), Gradle assembleDebug + assembleRelease unsigned, manifesto/package/versionCode/recursos/DEX. APK unsigned SHA-256 `d1e432f9f39bca663322512fb9239612a7262e8bb0107c2d49b2d2b3ecda0c9e`.
- **Identidade Android inalterada:** `pt.vcaitano.tradervision.gestaoteste`, versionCode **7**, versionName `0.7.0-demo`. Certificado SHA-256 permanente e imutável **`e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`**, mesma keystore VC3–VC6 recuperada do backup cifrado no `vcaitanoo/voc-cofre`. Nenhuma nova chave/identidade foi criada. Assinatura Android APK Signature Scheme v2 verificada (v1/v3 não utilizados). Material privado recuperado e usado localmente; somente bloco de assinatura público `trader-vision/signing/vc7-public-signing-block.json.gz.b64` foi inserido no GitHub para reconstrução remota, sem senhas.
- **APK candidato:** `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.7.0-demo-VC7.apk`. APK SHA-256 **`a6210df7b93e3658de4314618fa1791e5eeeee757d4b0e06d48e13d8c7279ba3`**. Workflow publicação `41949924033`: sucesso no hash idêntico ao APK assinado, assinatura/package/versionCode/DEX/resources e download HTTPS byte a byte. Workflow catálogo primário VOC Lab `41950104706`: sucesso. `lab/catalog.json` contém 8 apps, 1 Trader VC7; Supabase ativo `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store/main` contém 10 apps, 1 Trader VC7; outras entradas preservadas.
- **Estado CANDIDATE, NÃO STABLE.** Nenhuma execução real Android da VC7, aceitação de ordens nem resultado de trades foi testado (só testes unitários e validação estrutural). Até aprovação explícita do usuário, não substituir a base confirmada por essa candidata. Para teste: no VOC Lab → ATUALIZAR LISTA → VOC Trader Vision → ATUALIZAR CANDIDATO; não desinstalar VC6 pois package/certificado são iguais.
