# CENTRAL VOC — índice permanente dos projetos

> Atualizado: 2026-11-01. Este documento é **público**. Não inserir credenciais, tokens, senhas, keystores, chaves privadas nem valores de Secrets.
>
> Objetivo: acesso pelo celular/PC, ChatGPT, Codex e outros agentes com permissão, sem depender de uma conversa específica.

## Acesso e links principais

| Finalidade | Endereço ou arquivo canônico |
| --- | --- |
| Hub e distribuição | https://github.com/vcaitanoo/voc-apps |
| Instruções do Codex | [AGENTS.md](../AGENTS.md) |
| Skill de desenvolvimento | [VOC Lab Master](../.agents/skills/voc-lab-master/SKILL.md) |
| Instruções do Projeto ChatGPT | [VOC Lab ChatGPT](VOC_LAB_CHATGPT_PROJECT_INSTRUCTIONS.md) |
| Estado do VOC Lab | [CONTINUAR_AQUI.md](../lab/CONTINUAR_AQUI.md) |
| Catálogo de candidatos e estáveis | [lab/catalog.json](../lab/catalog.json) |
| Catálogo oficial do VOC Manager | [manifest.json](../manifest.json) |
| Fluxo de atualização | [VOC_LAB_WORKFLOW.md](VOC_LAB_WORKFLOW.md) |
| Registro geral de continuidade | [CONTINUITY.md](CONTINUITY.md) |
| Inventário de apps | [APP_INVENTORY.md](APP_INVENTORY.md) |
| Guia de segredos/credenciais | [COFRE_VOC_GUIA.md](COFRE_VOC_GUIA.md) |
| Repositório privado do Cofre VOC (acesso autenticado) | [vcaitanoo/voc-cofre](https://github.com/vcaitanoo/voc-cofre) |

**Separação essencial:** `lab/catalog.json` destina-se ao VOC Lab, com `stable` e `candidate`; `manifest.json` pertence ao VOC Manager oficial. Publicar candidato no Lab não promove stable automaticamente.

## Projetos e código-fonte

| Projeto | Fonte / identificação a conferir |
| --- | --- |
| GPS 3D | https://github.com/vcaitanoo/gps-3d |
| VOC Lab (app Android) | [lab/](../lab/) |
| VOC Manager | [manager/](../manager/) |
| Jarvis | Verificar a fonte canônica e o checkpoint atual; artefatos históricos em `lab/sources/jarvis/`; não assumir que uma tentativa recente é aprovada |
| Damas | Consultar inventário e catálogo, confirmar repo da fonte e versão aprovada |
| Tela Sempre Ativa | Consultar inventário, catálogo e checkpoint da fonte confirmada |
| VOC TV | Consultar inventário, catálogo e repo de origem |
| Ache Aqui e outros projetos | Repositório próprio a confirmar; **não adicionar ao catálogo** por suposição |

## O que conservar de cada aplicativo

Manter um checkpoint por app, em documentação **sem segredos** e com evidências verificáveis:
1. Nome, repo/branch/commit da fonte e packageName.
2. Última **versão efetivamente aprovada pelo usuário**, com data/ambiente do teste; não inferir aprovação por Gradle ou catálogo.
3. versionCode, versionName, SHA-256 do APK/base, SHA-256 do certificado de assinatura e localização da cópia aprovada.
4. Identificação da candidata atual, o que mudou, quais testes foram realmente executados e quais ficaram pendentes.
5. Backlog de bugs, comportamentos a preservar, decisões do usuário, alertas de regressão e próximo passo.
6. Histórico de Play Console (maior versionCode já enviado) **apenas após verificação**.
7. Nomes/referências de Secrets e localização do cofre (sem os valores), com responsável pelo acesso e rotina de recuperação.

### Modelo copiável de checkpoint

```md
# CHECKPOINT — <app>
Atualizado: AAAA-MM-DD
Repo / branch / commit-fonte: NÃO VERIFICADO
Fonte da última versão aprovada: NÃO VERIFICADO
Aprovação do usuário e teste real: NÃO VERIFICADO
Package name: NÃO VERIFICADO
Stable: versionCode / versionName / SHA-256 APK: NÃO VERIFICADO
Certificado SHA-256: NÃO VERIFICADO
Candidate: versão / URL / SHA-256 / status: NÃO VERIFICADO
O que já funciona e deve ser preservado:
O que foi solicitado:
Arquivos alterados:
Build: NÃO VERIFICADO
Teste em dispositivo Android real: NÃO VERIFICADO
Último versionCode usado na Play: NÃO VERIFICADO
Local de credenciais (somente referência, não valor):
Ponto exato para continuar:
```

## Regra de trabalho entre celular, PC e IAs

- Usar este índice como **porta de entrada**. Ler instruções e checkpoint específico antes de editar apps.
- Sempre que algo de valor duradouro for confirmado (versão estável, SHA, assinatura, arquitetura, bug resolvido, setup, decisão, link oficial), atualizar a documentação apropriada no GitHub, sem divulgar segredos.
- Não tratar uma tentativa recente como base estável. Preservar a fonte da última versão aprovada e só promover candidato após confirmação real em Android.
- Após solicitação de alteração Android, o canal de entrega padrão é publicar o APK candidato **no VOC Lab**, nunca apenas entregar APK avulso, respeitando os requisitos técnicos.
- **Arquitetura exclusiva GitHub escolhida pelo proprietário:** documentação no repositório público; backups de chaves privadas somente criptografados antes de commit no repositório privado confirmado `vcaitanoo/voc-cofre` (estrutura preparada, backups não verificados); credenciais operacionais em GitHub Actions Secrets, sem acesso posterior ao valor. Nunca guardar valores confidenciais em texto puro em repos, arquivos, issues ou logs. Consultar [COFRE_VOC_GUIA.md](COFRE_VOC_GUIA.md).


## GPS 3D Auto — APK experimental isolado (03/11/2026)

- Estado: **teste técnico independente, NÃO é stable, não aprovado em carro Android Auto**.
- Repositório-fonte: [vcaitanoo/gps-3d](https://github.com/vcaitanoo/gps-3d); branch `feat/android-auto-test`, commit `e74c549f063c5ede23b7191c77089d1298ce88cf`; base GitHub `5f620b121335103d75d7a2c5097a44d99dd7e6e1`.
- Pacote **separado**: `pt.vcaitano.gps3d.auto`; `versionCode=1`, `versionName=0.1.0-auto-test`; app original `pt.vcaitano.gps3d` intocado.
- APK debug (9.496.946 bytes): https://github.com/vcaitanoo/gps-3d/releases/download/gps-3d-auto-test-v1-20261103/GPS-3D-Auto-0.1.0-vc1-debug.apk
- SHA-256 do APK: `c917572529ad48a9442c8a52a6ec5f2e71f7f291ebec706e40c214fda88c3ff2`.
- Certificado público debug SHA-256: `5a710c8048911525c477b13ed6055539d9a1cce9a38390f83004308b6f956af1`. **Chave privada temporária criada pelo runner do GitHub; sem backup verificável e sem GitHub Secret persistente.** Builds futuras não devem tentar atualizar este pacote com certificado diferente; instalar novamente depois de desinstalar, ou configurar uma chave persistente autorizada com backup criptografado no cofre.
- CI GitHub Actions: https://github.com/vcaitanoo/gps-3d/actions/runs/41727952664 — **SUCCESS**. Gradle `assembleDebug`, `aapt` package/version/CarAppService/NAVIGATION/ACCESS_SURFACE, DEX, `apksigner verify` e checksum SHA-256 confirmados.
- Integração: Android for Cars App Library 1.7.0, `NavigationTemplate`, `SurfaceCallback`, `VirtualDisplay` + `WebViewAssetLoader` apontando ao bundle GPS 3D; renderização 3D no carro, GPS, desempenho e navegação sincronizada **NÃO VERIFICADOS**.
- Distribuição Android Auto: instalação direta do APK no telefone pode não habilitar app de navegação na central. Para testar em veículo real, usar distribuição confiável da Google Play (Internal App Sharing / track interno), conforme política Android for Cars; **não afirmar que APK sideload é suficiente**.
- Fonte oficial GPS 3D e catálogos `lab/catalog.json` e `manifest.json` preservados. Nenhum AAB para Play criado. Último versionCode já submetido à Play para **este pacote novo**: NÃO VERIFICADO. Este APK nunca foi testado num Android físico nesta execução.


### GPS 3D Auto v0.2.0 / VC2 — teste isolado, 03/11/2026
- Pacote independente: `pt.vcaitano.gps3d.auto` (não substitui `pt.vcaitano.gps3d`).
- Fonte web do GPS 3D no `main` do repositório específico deriva do commit `87b1c92da2a3dbe4a6cc0d72760674fcc1cd68fc` da edição oficial. A comparação até `5f620b121335103d75d7a2c5097a44d99dd7e6e1` mostrou somente alterações de documentação e CI, sem alterar HTML, navegação ou modelos originais.
- Branch isolada de desenvolvimento `feat/android-auto-test`, commit V2 `ceb79c906794dc4705a9051f4cc9d38251be2352`. Implementação exclusivamente em arquivos novos sob `android-auto-test/` e workflows novos, preservando fontes principais, estável e candidato do VOC Lab.
- Diagnóstico da v0.1: a WebView Android Auto abria `/assets/public/index.html` mas o `WebViewAssetLoader` servia o Vite `/assets/index-*.js` a partir do caminho errado, impedindo inicializar o bridge do GPS e parte das camadas 3D. V2 corrige a tradução do caminho, habilita geolocalização na WebView, solicita permissão de localização no telefone e acrescenta sincronização **experimental** de rota entre a interface do telefone e o mapa na central.
- Apk v0.2.0 / versionCode 2 / 9.501.460 bytes; SHA256 `b2ec829557d27d1ed038870410df41f38e188cd4413e4430f40f7dbd622cbbc5`.
- Certificado debug v0.2.0 SHA-256 `bebb568460f41453f677475ca834c25833684003fab3ff0648f666a42e08e650`; diferente da v0.1 (depuração com keystore efêmero). **Desinstalar somente a v0.1 GPS 3D Auto antes de instalar a v0.2; não desinstalar a oficial.** Keystore não recuperável no fluxo debug do runner. Para futuras atualizações regulares, usar assinatura persistente com backup seguro devidamente autorizado.
- GitHub Actions `41734075387`: Gradle `assembleDebug` PASS; `aapt` manifest/package/versão/permissões/service, DEX, `apksigner verify`, recursos Vite/PMTiles/edifícios/igrejas/mercados/postos/scripts de sincronização e SHA-256 do APK PASS. Nenhuma execução Android real ou Android Auto comprovada; renderização/mapas, captação GPS no carro e sincronização efetiva ainda exigem testes físicos.
- Release privada: https://github.com/vcaitanoo/gps-3d/releases/tag/gps-3d-auto-test-v2-20261103
- **Download via Google Drive autenticado**, ZIP contendo exatamente o APK verificado e um arquivo `.sha256`: https://drive.google.com/file/d/1bV2P6V-DRX4k3icszyc7jFhwoHSZzFx-/view?usp=drivesdk . O APK extraído teve SHA-256 idêntico ao da compilação/release.
- Endereço alternativo no ChatGPT Library: `/VOC_LAB_Testes/GPS-3D-Auto-0.2.0-vc2-debug.apk`.
- Android Auto: teste em veículo pode requerer distribuição por trilha interna/compartilhamento interno da Play; APK instalado manualmente não garante exibição da categoria NAVIGATION na central. **Não publicar AAB**, promover stable ou alterar catálogo oficial sem validação e autorização. 

## Hora — aplicativo de avisos falados, BASE ESTÁVEL (2026-11-04)
- Nome de exibição aprovado: **Hora**. O usuário confirmou a versão 1.2.0 LAB instalada via VOC Lab como versão oficial funcional em Android.
- APK imutável: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`, sha256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`, size 38139 bytes, certificate sha256 `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`.
- Package `pt.vcaitano.horajarvis.lab`, versionCode 3, versionName `1.2.0-lab`; `lab/catalog.json` e catálogo Supabase ativo devem exibir nome `Hora`, stable VC3 e candidate nulo.
- Checkpoint completo: `lab/sources/hora-jarvis/CONTINUAR_AQUI.md`.
- Chave de assinatura debug da versão aprovada sem backup; **não gerar APK de atualização com assinatura diferente**. O nome do ícone Android não muda com atualização do catálogo.


## Hora — candidato separado para frases personalizadas (2026-11-04)
- Base oficial confirmada: `pt.vcaitano.horajarvis.lab` VC3/1.2.0-lab, APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`, certificado `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`. **Não alterada.**
- Novo candidato independente `Hora — Frases (Teste)`, package `pt.vcaitano.horajarvis.frases`, VC4/1.3.0-lab. Mostra e fala frases personalizadas por horário, mantém modo curto ou variado. APK: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Frases-1.3.0-VC4.apk`, SHA-256 `be199a3c81e302c171e80cae9786af6b010dd2810415001f2b02f85e58837e7c`, assinatura debug temporária `9a00499882708de3de94f3e66417240629866b221d94dd1ce9983f0926143af1`.
- GitHub e catálogo ativo Supabase `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store` atualizados com entrada `hora-frases-teste`. Endpoint original do VOC Lab foi validado com 10 aplicativos e URL APK SHA correta no workflow `https://github.com/vcaitanoo/voc-apps/actions/runs/41830303395`.
- Código isolado: branch `feat/hora-frase-personalizada-v4-20261104`; commit de build `2a6f69d689d1089409e9020867d02373f2f9c592` e `lab/sources/hora-jarvis/CONTINUAR_AQUI.md` para auditoria completa.
- O teste instalado no Android ainda **não foi confirmado pelo utilizador**. Chave debug da variante experimental não preservada: não usar como assinatura futura nem promover a stable sem migração segura.

## Hora — 04/11/2026: VC5 corrigida publicada, apenas 1 registro VOC Lab

- App visível no VOC Lab: **Hora** (id `hora`), candidato `1.3.1-lab` VC5, package `pt.vcaitano.horajarvis.frases5`; APK `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Frases-1.3.1-VC5.apk`; SHA-256 `4b5e68212e7ea9cdf8ecfb907701c71aab8f690bfe4ef24a92493f2760f28073`; certificado SHA-256 `8254f8b635c828029cff88f88555f5b63d307512e57755863e4e29cad864d35c`. Chave DEBUG temporária **não recuperável confirmada**. Código-fonte `fix/hora-voz-sem-repetir-v5-20261104`.
- Mudança: evita repetir hora curta quando frase livre já contém hora; respeita `{hora}` e fallback para frase sem horário. 10 testes JDK passaram; build Gradle, estrutura APK, assinaturas e distribuição HTTPS verificadas. **Sem teste físico de execução VC5**.
- Na interface VOC Lab foram removidos apenas os registros antigos `hora-jarvis` e `hora-frases-teste` a pedido explícito; mantidos seus binários e base estável. O pacote oficial aprovado da VC3 `pt.vcaitano.horajarvis.lab`, SHA APK `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`, cert `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`, fica intocável em `apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`. VC4 de teste também arquivada.
- Publicação e verificação: `https://github.com/vcaitanoo/voc-apps/actions/runs/41832564966` e `https://github.com/vcaitanoo/voc-apps/actions/runs/41832966609`. Catálogo ativo Supabase `khinnoxpesnhtmmvrken` 9 apps, fallback GitHub 7 apps; em ambos somente 1 Hora VC5. Instalação separada; remover/desativar apps Hora antigos no aparelho para evitar alarmes simultâneos. Detalhes em `lab/sources/hora-jarvis/CONTINUAR_AQUI.md`.

## VOC Trader Vision — linha única no VOC Lab (2026-11-04)

- Decisão explícita do proprietário: **não criar novas apps/pacotes por atualização**. Retirar o VOC Trader Vision V1 da listagem e continuar **somente a V2 já existente**. Nenhum APK novo foi gerado nesta limpeza de catálogo.
- **Único app visível:** `VOC Trader Vision`, ID de catálogo `voc-trader-vision-gestao-teste` (ID técnico existente preservado, não equivale a novo app), package/applicationId **`pt.vcaitano.tradervision.gestaoteste`**, versionCode **2**, versionName **`0.2.0-demo`**; status **candidate, sem stable homologada**.
- APK V2 já publicado e preservado: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-Gestao-0.2.0-demo-VC2.apk`; SHA-256 **`d7c23b9fbaa4d3f48fd264b66bec5ef060966e676bfc9f3d3fc5ae26706f1d3c`**; certificado SHA-256 **`3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`** (debug temporário).
- **Fonte de continuidade:** branch `feat/voc-trader-vision-v2-gestao-20261104` do repositório `vcaitanoo/voc-apps`, commit de build **`70e766ca26103246fee0cb0556dc651f61f12fd7`**; arquivos Android sob `trader-vision/`; workflow V2 `.github/workflows/build-voc-trader-vision-v2-gestao.yml`. Houve testes de gestão matemática e CI Gradle/assinatura/manifesto/DEX/URL, mas **execução da V2 em Android real ainda não confirmada pelo usuário**.
- V1 apenas ARQUIVADA fora da listagem: package `pt.vcaitano.tradervision`, VC1/0.1.0-demo, SHA APK `51b125105128f3442fd05ee8fe1ddf864a2f166c9aa2a1d6c850ee155188cf9a`, certificado `da17fe1c3ac49d1fcd4c2cc6067f3fad0b1acdcee143129dcc2f1e6a76371f35`. Preservar o APK/fonte históricos para rastreabilidade, mas **não voltar a publicar V1 nem criar V3 com package diferente**.
- Alteração só em catálogo: GitHub `lab/catalog.json` commit `719d3ce5f5b349297c9d8ed97579ba7d455d5d77` (8 apps, 1 Trader Vision). Catálogo ativo Supabase `khinnoxpesnhtmmvrken`, `public.voc_lab_catalog_store` id `main`: 10 apps, 1 Trader Vision. Preservadas as entradas alheias, `manifest.json` e todas as estáveis.
- **Bloqueio de atualização in-place:** a chave privada do certificado debug V2 NÃO foi preservada/recuperada. Não é possível assinar APK seguinte para instalar **por cima** da V2 sem recuperar exatamente a chave original; compilar com debug temporário novamente causará incompatibilidade de assinatura. Antes da próxima entrega, resolver o mecanismo de assinatura permanente sem criar outro pacote/app; se recuperar a chave V2 for impossível, será necessária uma **migração/reinstalação única** no MESMO package com keystore persistente e backup cifrado autorizado. Não declarar atualização instalável por cima se a identidade de assinatura não coincidir. Nunca sobrescrever a V2 instalada sem validação.
- No aparelho, remover V1 antiga é ação manual do usuário (limpeza de catálogo não desinstala um app Android instalado). Não dar a entender que o telefone foi desinstalado remotamente.

## VOC Trader Vision — correção do gatilho de entrada VC3 (2026-11-04)

- Motivo reportado em Android: sinal VENDER nota 92/100, mas painel aguardava início da vela de 5min. A nota é heurística visual, não percentual de acerto; análise de imagem não comprova os OHLC nem fechamento da vela na Hezilex.
- Diagnóstico reproduzido no código V2: o executor só habilitava tentativa entre o **3º e o 12º segundo após minuto divisível por timeframe**, calculado pelo relógio local do Android. A condição era independente do score e frequentemente perdia um sinal já confirmado.
- Correção VC3 no MESMO package `pt.vcaitano.tradervision.gestaoteste`, `versionCode=3`, `versionName=0.3.0-demo`, sem criar novo app: branch `fix/voc-trader-vision-v3-criterio-entrada-20261104`, commit `f5130f0b69168a5fc8ae88f510ad377e987a4e54`.
- Novo gatilho DEMO: score acima do limiar mais **3 capturas consecutivas com mesma estratégia e direção**; executa sem janela arbitrária de 10 segundos, mantém limite de tentativas com intervalo `max(timeframe, expiração)`, mantém conta demo validada por acessibilidade, valor e expiração conferidos, stop diário e demais proteções. Mostra recusa do gesto durante 30 segundos. Score 92/100 NÃO garante trade: sem rótulo acessível da conta demo ou campos, o executor recusa.
- Testes automatizados: GitHub Actions run `41919303114` **sucesso** (RiskManagerTest, EntryTimingTest, Gradle build, package/manifest, DEX/resources e apksigner). Teste Android real da VC3 **NÃO REALIZADO**.
- **NÃO PUBLICAR a VC3 ainda:** o build de validação usou debug signer SHA-256 `81ded275e0c3b51d8745b10dd4ef2b0261de500ffa8d6b29b8e188af277356c1` diferente do certificado V2 instalado SHA-256 `3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`. A chave privada V2 não foi recuperada no voc-cofre (somente modelos/documentos). Android recusará atualizar in-place com assinatura diferente. Não alterar stable/candidate do Lab e não inventar APK instalável por cima. Para publicar atualização real, recuperar a chave V2 ou fazer migração de assinatura única explicitamente autorizada, preservando o MESMO package.
- Catálogo VOC Lab e versão V2 mantidos; não criar uma variante separada ou substituir a base V2 por compilação que não passou no aparelho.

## VOC Trader Vision — painel arrastável (2026-11-04)

- Pedido: mover o painel flutuante sobre a Hezilex com o dedo para não cobrir o gráfico e os comandos.
- Fonte mantida no MESMO package `pt.vcaitano.tradervision.gestaoteste`, versionCode 3 / versionName `0.3.0-demo`, branch `fix/voc-trader-vision-v3-criterio-entrada-20261104`, commit de funcionalidade `c241daf6c2ff559934a03af8855a48dd3d431485` e commit de CI `5aa098279372b55979907fb2b2d3c379cdac04d4`.
- Apenas interface de sobreposição: adicionada faixa "↕ ARRASTE PARA MOVER"; movimento também ao tocar no texto do painel; botão PARAR ROBÔ preservado, fora da zona de arraste. Posição relativa guardada em SharedPreferences; limites impedem sair do ecrã. Funcionalidade encapsulada em `PanelPosition.java`, `PanelPositionTest.java`; `VisionService.java` modificado; documentação e CI de teste atualizados. Estratégias, gestão da banca, permissão, package e executor da Hezilex não foram alterados.
- Evidência CI: GitHub Actions `41921664458` **sucesso**, incluindo RiskManagerTest, EntryTimingTest, PanelPositionTest, Gradle assembleDebug, manifesto/package/version, DEX, resources e apksigner. SHA-256 do APK de teste `380d3fa8d51e1f684b5e96bdae58f0916c7d0c3ba342e84bc114407c5c6905d5`; certificado debug do runner `290113ca92eedb2358fdc2e292d6d4cf23cd048c6dfdac6172e56893ec2ff6e4` **NÃO COMPATÍVEL** com a V2 instalada de certificado `3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`. Nenhum emulador ou Android real testado nesta revisão.
- **SEM PUBLICAÇÃO**: V2 permanece candidata no catálogo; não criar outro package/app, não substituir stable, não publicar APK de assinatura incompatível. A chave privada da V2 continua não localizada no cofre, portanto atualização por cima não é instalável até recuperar a chave ou autorizar plano de migração de certificado preservando o mesmo package.

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
