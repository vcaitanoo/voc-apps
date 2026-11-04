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
