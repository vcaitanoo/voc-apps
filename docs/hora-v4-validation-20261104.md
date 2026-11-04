# Hora 1.3.0 (VC4) — resultado de validação e impedimento de distribuição

Data: 2026-11-04.

## Construção verificada
- Repositório: vcaitanoo/voc-apps.
- Branch isolada: feat/hora-frase-personalizada-v4-20261104.
- Commit compilado: 007e2fcd3b505f446ad55539bf821c2f7b390802.
- GitHub Actions: https://github.com/vcaitanoo/voc-apps/actions/runs/41828427653
- Gradle 8.13 + SDK 36: **BUILD SUCCESSFUL**, 34 tarefas executadas.
- APK de diagnóstico: package `pt.vcaitano.horajarvis.lab`, versionCode 4, versionName `1.3.0-lab`, rótulo Android `Hora`, minSdk 26, targetSdk 36.
- Manifesto, recursos, classes.dex, ZIP e assinatura estrutural: verificações concluídas com sucesso.
- APK debug do runner: SHA-256 `24eac6ab50a708bf3661a61b63570d49959f0210e51fb1a0f5f429deae3daa41`; certificado SHA-256 `0068ddd5003fd1d2df6c40171f0aaaae36b9f478da74494a3d6dd6bdb161c4b2`.
- Certificado da versão *estável aprovada*: `13b7cccb5897d962c532cc11e39a0d0b95900ee5659e64b9feceb9e541d3a94b`.
- **As assinaturas NÃO são iguais**. Este APK de diagnóstico **não instala como atualização** sobre a versão estável. Não publicar no VOC Lab nem declarar teste Android real.
- A chave de assinatura da stable VC3 não foi guardada no workflow original: não gerar chave substituta e não tocar na instalação do utilizador sem autorização de migração.

## Escopo implementado
- Guardar switch e texto de frases personalizadas em SharedPreferences.
- Uma frase geral para todos os horários ou linhas `HH:MM | frase` individuais (por exemplo 11:00 e 17:00).
- Marcador `{hora}` substituído pela hora atual; sem marcador, o app anuncia a hora antes da mensagem.
- Quando não existe frase para determinado horário, usa a fala curta/variada já existente.
- Preview de voz e da tela do aviso mostram o texto personalizado mesmo antes de salvar.
- Nome do app e títulos de notificação/aviso renomeados para `Hora`; anúncio fictício e restante comportamento preservados.
- Arquivos afetados, e somente eles: `app/build.gradle`, `AppSettings.java`, `PhraseGenerator.java`, `MainActivity.java`, `AlertActivity.java`, `VoiceService.java`, `res/values/strings.xml`.
- Base VC3, manifesto Android, TimeScheduler, AlarmReceiver, permissões, anúncios fictícios, stable no `lab/catalog.json`, endpoint Supabase efetivo e `manifest.json`: **inalterados**.

## Pendente
- Recuperação da mesma chave privada da assinatura VC3, ou autorização específica para migração/reinstalação com assinatura nova e persistente.
- Publicação de candidato no VOC Lab apenas após compatibilidade de assinatura e hash confirmados.
- Teste real de execução e TTS em Android.
