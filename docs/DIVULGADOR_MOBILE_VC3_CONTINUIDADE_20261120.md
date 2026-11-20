# Divulgador Android — candidato VC3 / 0.1.2

Atualizado em 2026-11-20. Estado: **APK DEBUG compilado, candidato release NÃO publicado**.

## Base de origem
- App Android anterior: `vcaitanoo/voc-lab/lab/sources/divulgador/android`, referência GitHub `c37ee7198121fbd93ea97ee9fdc1a2f2f5c58a9b`.
- APK candidato anterior: Divulgador-0.1.1-vc2.apk.
- APK SHA-256 candidato VC2: `98f2ece033463c437404cdd9268ca625c2d26a17a2c21cf18ed0cd541e7d9bbe`.
- Package: `pt.vcaitano.divulgador`; versionCode anterior 2, versionName 0.1.1; **sem stable aprovada**.
- Certificado de assinatura anterior SHA-256: `918b566590b49f691ec9880c95dd174a6c032b21f81dc66efcfac74d0de11aa8`.
- Base anterior não foi confirmada pelo usuário como estável; sua candidate anterior permanece íntegra.

## Modificações da VC3
- `lab/sources/divulgador/android/app/build.gradle.kts`: VC3 / 0.1.2.
- `lab/sources/divulgador/android/app/src/main/AndroidManifest.xml`: registra GeneratorActivity e SendActivity e fecha cleartext HTTP (API já HTTPS).
- `lab/sources/divulgador/android/app/src/main/java/pt/vcaitano/divulgador/MainActivity.kt`: acrescenta 2 botões e preparar e-mail por campanha, preservando os demais controles.
- `.../GeneratorActivity.java`: port da app gerador CSV com 22 formatos locais PT e duplicatas tratadas.
- `.../SendActivity.java`: editor de campanha, importação CSV que exige consentimento explícito, composição via cliente email, confirmação manual e bloqueio de destinatários.
- `.github/workflows/build-divulgador-mobile-vc3.yml`: pipeline de compilação e release com verificação de assinatura (falha fechada se chave faltar).
- `Api.kt` foi copiado identicamente da base, sem alterações funcionais.

## Validação observada
- GitHub Actions job ID `136591009499`, run `44823763957`: `:app:assembleDebug` PASSOU.
- Verificação da estrutura ZIP e manifesto Debug: PASSOU; package `pt.vcaitano.divulgador`, VC3, 0.1.2.
- Assinatura release: **BLOQUEADA** porque o GitHub Actions `VOC_MANAGER_KEYSTORE_B64` está vazio/indisponível (job encerrou após debug).
- `assembleRelease`, certificado original e implantação no Lab: **NÃO EXECUTADOS**.
- Execução Android real: **NÃO TESTADA**.
- O backend Supabase existente informa DRY_RUN=true, emailConfigured=false e realSendReady=false; botão Enviar abre app de e-mail para confirmação pelo usuário, não é disparo automático.

## Continuidade obrigatória
- Repor em GitHub Actions, para o repositório vcaitanoo/voc-apps, os secrets `VOC_MANAGER_KEYSTORE_B64` e `VOC_MANAGER_KEYSTORE_PASSWORD` com a chave release ORIGINAL (alias `voc-manager-release`).
- Rerun do workflow a partir da branch feature; validar certificado igual ao SHA-256 da VC2. **Não gerar nova chave** para atualizar `pt.vcaitano.divulgador`.
- Somente após release válida atualizar a candidate `divulgador` no catálogo GitHub e no catálogo live Supabase `voc_lab_catalog_store`, mantendo stable intocada. O catálogo do VOC Lab primário é servido por Supabase, não basta alterar o GitHub.
- O APK Debug é assinado com chave efêmera e **não pode atualizar** o APK VC2 original.
