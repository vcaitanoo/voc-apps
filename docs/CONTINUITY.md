# Continuidade — VOC Lab

Atualizado em 2026-10-19.

## Objetivo

Manter instruções versionadas para compreender o repositório VOC Apps, preservar stable/candidate e verificar a cadeia de distribuição do VOC Lab.

## Estado

- Repositório observado: https://github.com/vcaitanoo/voc-apps.
- A documentação inicial acrescenta instruções de raiz e referências operacionais. Nenhum app foi alterado, compilado, testado em dispositivo ou publicado por esta missão.
- lab/catalog.json é a referência atual para stable/candidate do VOC Lab. manifest.json é um catálogo separado do voc Manager.
- A fonte do app VOC Lab e o workflow de build têm informação divergente sobre o estado do próprio app. Reconcile essa evidência antes de uma nova build.
- A associação do endpoint principal de catálogo ao deployment ativo ainda precisa de confirmação.
- O acesso ao conteúdo e às políticas do armazenamento Supabase não foi confirmado.

## Próximos passos

1. Ao começar uma tarefa de app, leia AGENTS.md, docs/APP_INVENTORY.md, docs/VOC_LAB_WORKFLOW.md e lab/CONTINUAR_AQUI.md.
2. Confirme o repositório e o commit-fonte da versão stable.
3. Resolva as divergências de versão antes de compilar.
4. Verifique URL, APK, package, versão, SHA-256 e certificado antes de alterar o catálogo.
5. Teste instalação e comportamento em dispositivo antes de marcar uma versão como funcional.

As instruções de AGENTS.md são carregadas como instruções do projeto quando Codex trabalha no repositório. Os documentos de docs/ complementam essas instruções e precisam ser lidos explicitamente.


## VOC Lab — recuperacao de catalogo (2026-11-04)
- Falha relatada: Hora Jarvis 1.2.0-LAB nao aparecia no VOC Lab instalado, embora `lab/catalog.json` na branch main contenha `hora-jarvis` com candidato VC3 e APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`.
- Diagnostico: cliente Android da fonte consulta primeiro `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` e nao compara com GitHub se esse endpoint responder com catalogo antigo. Endpoint Vercel original sem projeto acessivel na conta conectada; espelho nao sincronizado.
- Correcao preparada: priorizar `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json` e manter Vercel como fallback em branch `fix/voc-lab-catalog-github-first-20261103`. Fonte-fix inicial `7a410c45e6f101d826bd33011e6bd5a90d1e3759`; candidata Android original (package `pt.vcaitano.voclab`, versionCode 4, versionName 1.0.3) NAO distribuida pois faltam os Secrets `VOC_LAB_KEYSTORE_B64`/senha; manter certificado esperado SHA-256 `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`, nao gerar chave substituta para o pacote oficial.
- Recuperacao temporaria: branch fonte `fix/voc-lab-catalog-github-first-20261103`, commit `99ed879a3d806c7bf2c2d23c21de5b39bfc8d2a6`, gerou app separadamente instalavel `pt.vcaitano.voclab.emergencia`, VC4/1.0.3, label `VOC Lab — Atualizado`, build Gradle debug + estrutura e assinatura validadas, APK SHA-256 `8a6c9428a0195075f8494b16cbfd89e4544c8f1d3dd89527e46523ffa9fa5fa0`.
- APK de recuperacao publico HTTPS: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/apks/voc-lab-emergencia/VOC-Lab-Atualizado-1.0.3-VC4.apk`; URL verificada pelo proprio workflow mediante download e comparacao byte-a-byte em `https://github.com/vcaitanoo/voc-apps/actions/runs/41743646813`.
- Estado: somente TESTE, nao aprovado em Android real, assinatura debug temporaria do runner sem identidade para futuras atualizacoes; nao e a stable do VOC Lab. Codigo original e stable nao alterados, `manifest.json` nao alterado, `lab/catalog.json` mantido.
- Proxima etapa: recuperar keystore original com backup privado valido e Secrets, compilar a correção sob pacote oficial com mesmo certificado, validar em Android e so depois distribuir o app oficial. Evitar substituir oficialmente a assinatura por debug.


## Hora — candidato separado para frases personalizadas (2026-11-04)
- Base oficial confirmada: `pt.vcaitano.horajarvis.lab` VC3/1.2.0-lab, APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`, certificado `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`. **Não alterada.**
- Novo candidato independente `Hora — Frases (Teste)`, package `pt.vcaitano.horajarvis.frases`, VC4/1.3.0-lab. Mostra e fala frases personalizadas por horário, mantém modo curto ou variado. APK: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Frases-1.3.0-VC4.apk`, SHA-256 `be199a3c81e302c171e80cae9786af6b010dd2810415001f2b02f85e58837e7c`, assinatura debug temporária `9a00499882708de3de94f3e66417240629866b221d94dd1ce9983f0926143af1`.
- GitHub e catálogo ativo Supabase `khinnoxpesnhtmmvrken/public.voc_lab_catalog_store` atualizados com entrada `hora-frases-teste`. Endpoint original do VOC Lab foi validado com 10 aplicativos e URL APK SHA correta no workflow `https://github.com/vcaitanoo/voc-apps/actions/runs/41830303395`.
- Código isolado: branch `feat/hora-frase-personalizada-v4-20261104`; commit de build `2a6f69d689d1089409e9020867d02373f2f9c592` e `lab/sources/hora-jarvis/CONTINUAR_AQUI.md` para auditoria completa.
- O teste instalado no Android ainda **não foi confirmado pelo utilizador**. Chave debug da variante experimental não preservada: não usar como assinatura futura nem promover a stable sem migração segura.

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
