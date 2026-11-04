# Hora — desenvolvimento isolado de frases personalizadas (04/11/2026)

## Base oficial aprovada — imutável
- Repositório: `vcaitanoo/voc-apps`; branch original da fonte aprovada: `ci/horajarvis-apk-v3`.
- APK estável preservado em `apks/hora-jarvis/stable/Hora-v1.2.0-VC3.apk`.
- packageName `pt.vcaitano.horajarvis.lab`; versionCode 3; versionName `1.2.0-lab`.
- APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`.
- Certificado SHA-256 `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`.
- O utilizador confirmou a versão estável em Android real. Ela NÃO foi alterada.
- A chave privada debug utilizada na assinatura da VC3 não foi preservada: NÃO assinar/pôr no VOC Lab uma atualização com certificado diferente.

## Candidata em desenvolvimento (não publicada)
- Branch isolada: `feat/hora-frase-personalizada-v4-20261104`.
- Cópia **intacta** dos arquivos-fonte reconstruídos da VC3 em `ci/horajarvis/review-v3/app/`. Reconstrução verificada com os hashes de fonte e patches do workflow histórico.
- Somente os arquivos alterados para a VC4 estão em `ci/horajarvis/v4-source/app/`. A fonte para compilar é a mesma VC3 restaurada com sobrescrita desses arquivos em cópia temporária.
- Package preservado `pt.vcaitano.horajarvis.lab`; versão de código 4; nome de versão `1.3.0-lab`.
- Arquivos de código modificados: `AppSettings.java`, `PhraseGenerator.java`, `MainActivity.java`, `AlertActivity.java`, `VoiceService.java`, `app/src/main/res/values/strings.xml`, `app/build.gradle`.
- Novidade: opção de texto personalizado geral ou por horário, usando `HH:MM | mensagem` e variável `{hora}`. Quando não há frase específica, preserva fala curta/variada. O texto gerado é compartilhado com voz, notificação e tela personalizada.
- Nome exibido no Android, cabeçalhos e notificação: `Hora`.
- Horários existentes, dias, frequência, vibração, alerta visual 70/30, publicidade somente fictícia, permissões e alarmes NÃO modificados.
- Workflow de compilação de diagnóstico: `.github/workflows/hora-v4-build.yml`. APK debug de runner é **somente artefato técnico**, não distribuível como atualização da VC3.
- Estado de publicação: `lab/catalog.json` **não modificado**, `manifest.json` **não modificado**, catálogo Supabase efetivo **não modificado**, stable VC3 preservada, candidate público nenhum.
- Próximo impedimento: recuperar a **mesma chave privada** do certificado VC3 ou autorizar explicitamente estratégia de migração/reinstalação com uma chave permanente e backup seguro. Compilar não valida execução real.
