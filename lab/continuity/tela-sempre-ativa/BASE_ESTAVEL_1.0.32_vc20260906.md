# Tela Sempre Ativa — BASE ESTÁVEL CONFIRMADA: 1.0.32

**Confirmação do utilizador:** 2026-11-03. Instalou o APK de teste no Samsung; abriu, apresentou um anúncio logo após a instalação e apresentou o segundo anúncio cinco minutos depois.

**Limites da confirmação:** demonstra abertura e dois anúncios nesta instalação. Não valida todas as funções nem a distribuição AAB pela Google Play.

## Identidade
- Package: `pt.vcaitano.telasempreativa`
- versionName: `1.0.32`
- versionCode: `20260906` (o próximo AAB requer um código estritamente superior se este for submetido)
- Alias assinatura APK de teste: `telaativa`
- Certificado de assinatura SHA-256: `f3e732553e25bb86bc5ca7c2aa5a0a6f9f9e798d9def964338a744f399b01d3a`
- **Não armazenar chaves privadas/senhas neste registo.**

## SHA-256 exatos
- Fonte ZIP: `4fb030d5851fbb02be4648fdb92399ff389aa32971e6b7bd3054cf94d22d4f64`
- APK testado: `e9c5785f74eb206810d8a7006495d937bac50f74c7ae3bdb6e3fd8af50f912f9`
- AAB do mesmo código-fonte (CANDIDATO): `250ae9d558d7b8c012f2bc789ad21d205835000860bc775ab859d63c901daf4c`

## Proveniência
- Branch compilação: `build/tsa-v37-ads-vc20260906-20261103`
- Workflow commit: `958e3f30c0bda74fa2be4ee19edb72bde0816f20`
- GitHub Actions run: https://github.com/vcaitanoo/voc-apps/actions/runs/41721716089
- Patch exclusivamente de anúncios: `lab/patches/tsa-v37-ad-fix.patch` na branch.
- Fonte completa, APK, AAB e metadados reunidos no pacote local `TelaSempreAtiva_BASE_ESTAVEL_1.0.32_CONTINUIDADE.zip`.

## Diferenças relativamente à 1.0.31
- `app/build.gradle` — nova versão
- `app/src/main/java/pt/vcaitano/telasempreativa/MainActivity.java` — abrir diagnóstico com pressão longa em Pré-visualizar
- `app/src/main/java/pt/vcaitano/telasempreativa/AdConsent.java` — renovar UMP na sessão AOD
- `app/src/main/java/pt/vcaitano/telasempreativa/AodAdController.java` — fallback banner/nativo e diagnóstico

## Regra de continuidade
**Nunca substituir esta base confirmada por qualquer versão posterior não confirmada pelo utilizador.** Antes de nova alteração recuperar fonte ZIP com SHA acima, aplicar apenas diferenças explicitamente autorizadas, compilar APK com Gradle e comparar estruturas. Não afirmar testes em Android salvo confirmação em dispositivo real. Apenas preparar/publicar o AAB a partir da mesma fonte após confirmar a instalação de teste.
