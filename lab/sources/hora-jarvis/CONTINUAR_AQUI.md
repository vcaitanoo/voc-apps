# Hora Jarvis — continuidade (2026-11-03)

## BASE CONFIRMADA PELO UTILIZADOR (NÃO SUBSTITUIR)
- Fonte: HoraJarvis-Fonte-v1.1.0-TESTE.zip
- SHA-256 fonte: `f3da73c22e6ab3efcd7689635da5fe1ee84209de146a2eab3503366a75435a5a`
- APK: HoraJarvis-v1.1.0-TESTE.apk
- SHA-256 APK: `f9048df617e7f8cdfa1ca21237b05c94ab432dc70e7be13d14bce55ba06e988c`
- Application ID instalado: `pt.vcaitano.horajarvis.teste`
- versionCode: `2`, versionName: `1.1.0-teste`
- Certificado SHA-256: `15972ae9618f1d1afa5c0519786dd3c0ac9d32d4df2ab34410a9874835d0fc9d`
- O utilizador confirmou que FUNCIONA no Android real; no entanto, o aviso personalizado foi substituído pela notificação de destaque da Samsung.
- **A chave debug dessa compilação não foi preservada**, logo um novo build assinado com outra chave não consegue atualizar esse pacote in-place.

## CANDIDATO 1.2.0 LAB (NÃO É ESTÁVEL)
- Source: reconstituir no GitHub em `vcaitanoo/voc-apps`, branch `ci/horajarvis-apk-v3`, patch v3 sobre fontes v1.1.0
- Patch V3 SHA-256: `d0c9b1104f1ee01f830c3c9a243f130c285b77477dba1eceee68f54f609ff826`
- APK URL: https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/candidate/HoraJarvis-v1.2.0-LAB-VC3.apk
- package: `pt.vcaitano.horajarvis.lab`
- versionCode: `3`
- versionName: `1.2.0-lab`
- SHA-256: `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`
- Certificado SHA-256: `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`
- Assinatura debug temporária da execução GitHub Actions; **chave privada não preservada**, logo não garantir atualização in-place para futuras candidatas LAB.
- Modificados: `app/build.gradle`, `AppSettings.java`, `PhraseGenerator.java`, `AlarmReceiver.java`, `VoiceService.java`, `MainActivity.java`, `AlertActivity.java`.
- Intactos: `TimeScheduler.java`, `CustomTimes.java`, `SystemEventReceiver.java`, `AndroidManifest.xml` e recursos.
- Novidades: fala curta apenas com hora, fala variada existente, mesma frase na notificação, toque na notificação abre AlertActivity personalizada, visualização manual 70% espaço de publicidade **fictícia** e 30% aviso completo (scroll), sem anúncios reais e sem rede.
- O Android pode manter heads-up Samsung em segundo plano; full-screen na tela bloqueada depende de permissão/sistema. Não declarar substituição automática garantida.
- GitHub Actions sucesso: https://github.com/vcaitanoo/voc-apps/actions/runs/41741150964
- Compilação/estrutura/signature: verificadas. Execução em Android real: ainda não testada.
- Registro no VOC Lab: `lab/catalog.json`, entrada `hora-jarvis` como `candidate` apenas, `stable` LAB ainda não existe.

## Segurança e monetização
- Publicidade exibida é apenas um exemplo local. O app não contém AdMob nem rastreio.
- A Google Play proíbe monetizar tela bloqueada e anúncios sobre outros aplicativos. Não colocar SDK real de anúncios nessa tela.
- Antes de futuras atualizações/publicação, criar chave permanente no cofre privado `vcaitanoo/voc-cofre` e assinar uma linhagem separada ou planear migração sem invalidar uma versão aprovada.
- Nunca promover a candidata 1.2.0 a stable sem confirmação explícita do utilizador de teste real.

## BASE ESTÁVEL OFICIAL — HORA 1.2.0, CONFIRMADA (04/11/2026)
- **Confirmação explícita do utilizador**: "Funcionou. E ja esta no voc lab. Essa agora é o oficial. E o nome passa a ser somente hora". A versão LAB instalada é aprovada como versão oficial funcional.
- Nome público aprovado: **Hora** (não "Hora Jarvis — LAB").
- Package imutável instalado: `pt.vcaitano.horajarvis.lab`; versionCode **3**; versionName real do APK **1.2.0-lab**; não editar metadados internos do APK aprovado.
- Base estável binária **exatamente igual** à candidata confirmada: objeto Git `08a37e175c8e2f4459834af1db764f0a5061c756`, copiado como referência, sem reconstruir, no caminho permanente `apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`.
- URL oficial no VOC Lab: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`.
- SHA-256 do APK aprovado: `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e` (38139 bytes).
- Certificado público SHA-256: `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`; **chave privada temporária não preservada**, situação de assinatura NÃO RESOLVIDA. Uma próxima APK com assinatura diferente NÃO atualizará esta instalação. Antes de qualquer build de atualização, recuperar chave original ou planear migração explicitamente, sem sobrescrever base.
- Fonte correspondente: reconstrução v1.2.0 em branch `ci/horajarvis-apk-v3`, patch v3 SHA-256 `d0c9b1104f1ee01f830c3c9a243f130c285b77477dba1eceee68f54f609ff826`, derivada da base v1.1.0 aprovada. Conservar fontes e os patches históricos; não usar commits experimentais.
- Catálogo GitHub `lab/catalog.json`: `name=Hora`, `stable=VC3`, `candidate=null`. Catálogo Supabase real servido no endpoint original deve receber **a mesma atualização SOMENTE no registro Hora**, preservando 8 outros apps.
- **IMPORTANTE NOME**: o texto no VOC Lab muda imediatamente para `Hora`; o label embutido no APK Android aprovado permanece o anterior até uma recompilação assinada com a chave idêntica. Não alegar que o ícone Android foi renomeado sem APK validado/instalado.
- **Publicação na Google Play**: NÃO realizada. "Oficial" neste checkpoint significa a base stable no VOC Lab com aprovação em dispositivo, não publicação na Play Store.


## TESTE APARTADO — HORA FRASES 1.3.0 VC4 (2026-11-04)

- Solicitação: renomear para Hora e permitir fala personalizada por horário ou frase geral, preservando o modo de fala curto, as combinações variadas, notificações, anúncios fictícios e programações.
- Implementado em fonte isolada (sem modificar o código da base aprovada): branch `feat/hora-frase-personalizada-v4-20261104`, arquivos parciais em `ci/horajarvis/v4-source/app/`, reconstruindo a fonte oficial VC3 a partir dos patches de hash conferido. Commit compilado: `2a6f69d689d1089409e9020867d02373f2f9c592`.
- Arquivos V4 alterados na fonte: `app/build.gradle`, `AppSettings.java`, `PhraseGenerator.java`, `MainActivity.java`, `AlertActivity.java`, `VoiceService.java` e `res/values/strings.xml`. Ajuste adicional do applicationIdSuffix de `.lab` para `.frases` no build experimental, para instalar ao lado do original.
- O app da instalação oficial `pt.vcaitano.horajarvis.lab`, VC3 e certificado `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b` permanecem intactos. Sua assinatura privada original continua indisponível, portanto nenhuma atualização in-place foi tentada.
- APK experimental distinto: package `pt.vcaitano.horajarvis.frases`, versionCode `4`, versionName `1.3.0-lab`, nome Android **Hora**, SDK min 26, target 36.
- URL HTTPS validada: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Frases-1.3.0-VC4.apk`.
- APK: 39791 bytes, SHA-256 `be199a3c81e302c171e80cae9786af6b010dd2810415001f2b02f85e58837e7c`, certificado debug temporário SHA-256 `9a00499882708de3de94f3e66417240629866b221d94dd1ce9983f0926143af1`. **Este certificado não é uma chave recuperável para próximas atualizações**, não promover a stable nem assumir continuidade de assinatura.
- GitHub Actions build/publicação: `https://github.com/vcaitanoo/voc-apps/actions/runs/41829756744`, sucesso com Gradle, verificação de package, DEX, manifesto, resources, assinatura e hash.
- Catálogo GitHub `lab/catalog.json`: acrescida somente entrada `hora-frases-teste` com `candidate=VC4` e `stable=VC0` sem APK; a entrada `hora-jarvis` stable VC3 permanece igual; `manifest.json` não alterado.
- Catálogo **real** do VOC Lab original: `public.voc_lab_catalog_store` em Supabase `khinnoxpesnhtmmvrken`, registro `id=main`, atualizado apenas por *append* protegido contra duplicação da nova entrada, passando de 9 para 10 aplicativos; 9 anteriores preservados. Endpoint primário `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json`.
- Verificação externa HTTPS do catálogo ativo e APK (download, SHA, ZIP e entradas): `https://github.com/vcaitanoo/voc-apps/actions/runs/41830303395`, sucesso: `CATALOGO_ATIVO_OK 10 APPS`, `HORA_STABLE_VC3_INTACTO`, `HORA_FRASES_TESTE_VC4_PRESENTE`, `APK_SHA256_VERIFICADO`.
- **Execução Android real não testada**, aguardar confirmação do utilizador. Esta variante de teste NÃO substitui o Hora original; nome idêntico no lançador pode mostrar dois ícones "Hora" até que se faça futura migração segura e assinada.
- Regra de continuidade: qualquer atualização do Hora oficial usa somente a base stable VC3 até que exista migração explicitamente aprovada; não usar este APK experimental nem sua assinatura debug efémera como base de uma futura atualização oficial.

## HORA VC5 — CORREÇÃO DE HORA DUPLICADA / UM ÚNICO ITEM VOC LAB (04/11/2026)

- O utilizador testou VC4 no Android e confirmou que o aplicativo avisa, mas relatou bug na fala: a hora curta antecedia uma mensagem que já dizia a própria hora. A VC4 **não foi homologada**, porque continha esse defeito.
- A correção VC5 foi feita exclusivamente sobre a fonte VC3 reconstruída (base aprovada) com as funcionalidades VC4 reaplicadas, sem usar o APK defeituoso para engenharia. Branch: `fix/hora-voz-sem-repetir-v5-20261104`, receita: `.github/workflows/hora-v5-build-publish.yml`. Mudanças de lógica: `ci/horajarvis/v4-source/app/src/main/java/pt/vcaitano/horajarvis/PhraseGenerator.java` chama `CustomSpeech.format`, novo `CustomSpeech.java` detecta hora atual escrita como `12h40`, `12:40`, `12 horas e 40 minutos`, `são 12 e 40`, `são 12h`, `17h` e substitui `{hora}`. Sem horário, continua anunciando hora curta antes da frase. `app/build.gradle`: VC5 / 1.3.1-lab. Nenhuma outra função existente modificada. Testes Java de regressão em `ci/horajarvis/tests/CustomSpeechRegression.java` (10 cenários, sucesso).
- App independente, necessário pela assinatura temporária perdida da VC4: package `pt.vcaitano.horajarvis.frases5`, label `Hora`, versionCode 5, versionName `1.3.1-lab`.
- APK HTTPS publicado e verificado: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Frases-1.3.1-VC5.apk`, 40527 bytes, SHA-256 `4b5e68212e7ea9cdf8ecfb907701c71aab8f690bfe4ef24a92493f2760f28073`, certificado SHA-256 `8254f8b635c828029cff88f88555f5b63d307512e57755863e4e29cad864d35c`. Chave privada DEBUG temporária NÃO preservada: novas builds de atualização com a mesma package podem falhar, não assumir assinatura recuperável.
- Build e publicação: `https://github.com/vcaitanoo/voc-apps/actions/runs/41832564966`, SUCCESS (Gradle, testes de regressão, manifesto, DEX, resources, aapt, apksigner, hash HTTPS).
- A pedido explícito do utilizador, catálogo VOC Lab mostra apenas um item `Hora` (id `hora`), candidato VC5 com stable placeholder VC0 não aprovada. As entradas `hora-jarvis` e `hora-frases-teste` foram retiradas SOMENTE dos catálogos (GitHub `lab/catalog.json` e Supabase `khinnoxpesnhtmmvrken`, tabela `public.voc_lab_catalog_store`, id `main`). Não apagar APKs históricos nem a fonte original! A base aprovada VC3 foi removida da lista a pedido do utilizador, MAS continua **BASE ESTÁVEL PRESERVADA** no GitHub: pacote `pt.vcaitano.horajarvis.lab`, versionCode 3, SHA `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`, assinatura `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`; APK `apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`. VC4 segue arquivada em `apks/hora-jarvis/teste/Hora-Frases-1.3.0-VC4.apk`, SHA `be199a3c81e302c171e80cae9786af6b010dd2810415001f2b02f85e58837e7c`.
- Verificação externa pelo runner (HTTP) tanto do catálogo primário do VOC Lab (9 apps) quanto fallback GitHub (7 apps), ambos com **apenas Hora VC5**, além do APK e SHA correto: `https://github.com/vcaitanoo/voc-apps/actions/runs/41832966609`, SUCCESS.
- Android real da VC5: **NÃO TESTADO AINDA**. A pedido do usuário, orientar `VOC Lab → ATUALIZAR LISTA → Hora → INSTALAR CANDIDATO`. A remoção dos apps antigos da lista **NÃO** desinstala seus pacotes do dispositivo; o utilizador precisa desativar ou desinstalar os Hora anteriores para evitar alarmes duplos.
- NÃO promover VC5 a stable antes de confirmação explícita em Android. Para atualizar o mesmo package no futuro será necessário recuperar a chave DEBUG da VC5 (não preservada) ou planejar migração; nunca simular assinatura.


## HORA VC6 — CORREÇÃO DE NOTIFICAÇÕES, CANDIDATO, NÃO APROVADO (05/11/2026)
- Relato usuário em 2026-11-05: "essa ultima versao nao esta notificando. arrume", referente à VC5 (última candidata do VOC Lab naquele momento). A VC5 NÃO foi aprovada como estável. A base realmente aprovada e preservada continua VC3 `pt.vcaitano.horajarvis.lab`, APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`; não modificar nem usar candidatos defeituosos como base estável.
- Diagnóstico pelo código: as variantes de teste VC4/VC5 têm package distintos e não herdam `SharedPreferences` nem as permissões de notificações e alarmes do pacote anterior; `enabled` começa como `false`. A VC5 solicitava `POST_NOTIFICATIONS` apenas após tocar em SALVAR CONFIGURAÇÃO e não tinha teste específico de entrega de notificações. No Android 13+, a permissão da nova instalação costuma iniciar negada; no Android 14+, alarmes exatos também requerem autorização específica. Essas são **causas plausíveis identificadas no código**, não um diagnóstico ADB confirmado em hardware.
- Alteração mínima aplicada na fonte experimental derivada da VC3 por restauração e patch SHA-256 verificados, preservando a personalização VC4 e correção de fala VC5. Branch `fix/hora-notificacoes-vc6-20261105`, commit compilado `3596bf9ff404d9e2b2a130965ad4e0caa15732ff`. `MainActivity.java` modificado para: (1) solicitar permissões de notificações e alarmes exatos automaticamente na primeira abertura (sem loops após negação); (2) verificar `NotificationManager.areNotificationsEnabled()`; (3) reprogramar após resultado da permissão; (4) informar claramente quando avisos estão desligados/bloqueados; (5) adicionar botão "TESTAR NOTIFICAÇÃO AGORA" para disparar notificação real local e verificar telefone/relógio; (6) ligar botão de permissões ao fluxo completo. `app/build.gradle` passou a `versionCode=6`, `versionName=1.3.2-lab`; script de build configura somente a variante `applicationIdSuffix='.frases6'` para evitar conflito da assinatura antiga indisponível. **Não modificados**: `AlarmReceiver.java`, `TimeScheduler.java`, `VoiceService.java`, `CustomTimes.java`, `SystemEventReceiver.java`, `AndroidManifest.xml`, lógica de frases, layouts anteriores fora do botão de teste, anúncio fictício.
- APK resultante: `pt.vcaitano.horajarvis.frases6`, VC6 1.3.2-lab, nome Android `Hora`. URL `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/hora-jarvis/teste/Hora-Notificacoes-1.3.2-VC6.apk`. SHA-256 `f6e03c18d74e7adf89aca02476124891e2a4e65c9534bd52edc5f372281e83a5`; certificado de debug SHA-256 `c69713c0051fe396c70343a291d8f34fbd1df72a68ae5970de2bb5c77604ffdd`. Chave debug **temporária NÃO preservada**; NÃO tentar atualizar esta package com outra assinatura. Solução definitiva de assinatura estável requer chave própria criptografada e recuperável conforme política do `vcaitanoo/voc-cofre`, sem substituir a assinatura da versão VC3/VC5.
- GitHub Actions build `https://github.com/vcaitanoo/voc-apps/actions/runs/42081398047`: SUCESSO, restauração de fontes VC3 com hashes, sobreposição de mudanças de funcionalidades, 10 testes Java da fala, Gradle Android, verificação de manifesto/package/version, resources/DEX, assinatura `apksigner`, SHA e download HTTPS idêntico. GitHub commit catálogo candidato `39384c50f8768cb1a1402024fbc517ad1c579f48`, apenas entrada `id=hora`, stable placeholder do catálogo mantido, outras 7 entradas do GitHub intactas. Backend Supabase `khinnoxpesnhtmmvrken` `public.voc_lab_catalog_store` `id=main`: apenas `hora.packageName` e `hora.candidate` atualizados; outros 9 aplicativos, stable e nomes preservados. Endpoint efetivo `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` e GitHub raw verificados com VC6, APK HTTP 200/hashes: `https://github.com/vcaitanoo/voc-apps/actions/runs/42081923612` SUCCESS.
- **EXECUÇÃO REAL NO ANDROID / NOTIFICAÇÃO COM APP FECHADO / VIBRAÇÃO NO RELÓGIO: PENDENTE**, não afirmar corrigido por compilação. Pedir ao utilizador: VOC Lab original → ATUALIZAR LISTA → Hora → INSTALAR CANDIDATO; no Hora novo, aceitar notificações e Alarmes e lembretes, ativar avisos, configurar e SALVAR, usar TESTAR NOTIFICAÇÃO AGORA e esperar um horário programado com a tela bloqueada. Manter VC3 intacta até confirmação; como pacote VC6 distinto, preferir desativar as versões anteriores durante teste para evitar alarmes repetidos.
- NÃO promover VC6 a stable nem retomar a partir dela em futuras alterações enquanto não houver aprovação explícita no Samsung.
