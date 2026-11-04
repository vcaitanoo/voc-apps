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
