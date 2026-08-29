# VOC Manager — preparação da migração para GitLab

Base recuperada: VOC Manager 1.2.4 / versionCode 8.
Catálogo recuperado: 7 apps, atualizado em 2026-08-27T04:07:00Z.

## Estado preservado

- voc Manager 1.2.4 / vc 8 — APK — publicado
- voc TV 0.19.0 / vc 19 — APK — publicação pendente
- Damas 1.0.6 / vc 7 — APK — publicação pendente
- Jarvis 0.3.0 / vc 12 — APK — publicado
- Teclado Tradutor 1.15.0 / vc 15 — Google Play — publicado
- Simulador de LED 1.5 / vc 9 — Google Play — publicado
- Tela Sempre Ativa 1.0.15 / vc 16 — APK — publicação pendente

## Regra de segurança

Foram recuperados três ficheiros Java do VOC Manager 1.2.4: `CatalogApp.java`, `CatalogClient.java` e `MainActivity.java`. O `MainActivity.java` está preservado em `MainActivity.java.gz.b64`; o script de finalização reconstrói-o byte a byte antes de aplicar a troca de URL/texto.

Esses ficheiros representam o núcleo observado da 1.2.4, mas NÃO são, por si só, um projeto Android completo e não devem ser tratados como fonte compilável confirmada.

A migração final só deve gerar uma nova versão do Manager depois de recuperar/confirmar o projeto completo que produziu a 1.2.4. Não editar APK/DEX/smali para contornar a ausência da fonte.

## GitLab

Após criar/importar o projeto público no GitLab, execute:

`python migration/gitlab/finalize_gitlab_migration.py https://gitlab.com/SEU_NAMESPACE/voc-apps`

O script troca apenas referências que podem ser determinadas com segurança e gera `gitlab-finalization-report.json`. Ele não inventa APKs ausentes.

O pipeline `.gitlab-ci.yml` valida a estrutura do catálogo, Play URLs, hashes e assinaturas.
