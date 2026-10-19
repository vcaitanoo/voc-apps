# Fluxo operacional do VOC Lab

Snapshot público do repositório vcaitanoo/voc-apps, investigado em 2026-10-19.

## Componentes

- App Android VOC Lab: projeto em lab/, package pt.vcaitano.voclab.
- Catálogo de desenvolvimento: lab/catalog.json, com campos stable e candidate.
- Fonte da interface web/PWA: docs/voc-lab/.
- voc Manager: projeto Android em manager/; usa o catálogo oficial manifest.json.
- Os catálogos manifest.json e lab/catalog.json são separados e não se atualizam entre si.

## Fluxo de atualização

Fonte e branch do app
→ compilação
→ validação de package, versão, SHA-256 e assinatura
→ upload do APK HTTPS
→ atualização da entrada stable/candidate em lab/catalog.json
→ leitura pelo VOC Lab
→ comparação com a versão instalada
→ validação do APK e solicitação de instalação ao Android
→ teste real e aprovação do usuário antes da promoção a stable.

O catálogo não guarda o sourceCommit de cada APK. Registe a origem da build junto dos resultados.

## Leitura e instalação

lab/app/src/main/java/pt/vcaitano/voclab/MainActivity.java implementa o fluxo nativo. A aplicação tenta o endpoint de catálogo principal configurado no código e usa o raw GitHub como fallback. Exibe stable e candidate; se houver candidate, seleciona-o como alvo. Lê o versionCode instalado e oferece instalar, atualizar ou abrir. Antes de chamar PackageInstaller, verifica SHA-256, packageName, versionCode e certificado do APK.

A aplicação atualiza o catálogo no arranque e através da ação ATUALIZAR LISTA. Não foi encontrado um mecanismo de notificação push no código consultado.

docs/voc-lab/index.html exibe links diretos de APK e consulta o catálogo raw do GitHub. O fluxo web entrega o arquivo ao navegador e não executa as verificações de integridade feitas pelo app Android.

## Build e publicação observados

.github/workflows/build-voc-lab.yml:

- Runner ubuntu-latest.
- Temurin Java 17, Android platform 36, Build Tools 36.0.0 e Gradle 8.13.
- Build release em lab/app/build/outputs/apk/release/app-release.apk.
- Usa material de assinatura provisionado por secrets do GitHub Actions.
- Valida metadados e certificado, calcula SHA-256, prepara um APK e release.json em lab/ e tenta registrar a saída na branch main.
- O build workflow e o documento lab/CONTINUAR_AQUI.md divergem sobre o estado do próprio app VOC Lab. Reconcilie código, APK, catálogo e teste antes de escolher a base para uma nova build.

.github/workflows/validate-catalog.yml valida manifest.json e schema/manifest.schema.json. O filtro desse workflow não inclui lab/catalog.json. Valide manualmente o JSON do catálogo do Lab e os invariantes de cada release antes da publicação.

Os apps podem usar workflows próprios. Confirme o runner, a assinatura e o tipo de APK no repositório da app antes de compilar.

## Hospedagem

Os campos apkUrl atuais apontam para provedores HTTPS distintos, incluindo GitHub, Vercel e Supabase Storage. O arquivo vercel.json indica que o diretório de saída é lab/. A associação do deployment ativo e as permissões de Storage não foram confirmadas nesta investigação. Uma URL no catálogo não confirma que o APK está acessível.

A fonte PWA está em docs/voc-lab; o método e domínio usados para publicá-la ainda precisam de confirmação.

## Procedimento

1. Leia AGENTS.md, docs/CONTINUITY.md, docs/APP_INVENTORY.md, lab/CONTINUAR_AQUI.md e o catálogo atual.
2. Confirme a origem e o estado da versão stable. Preserve a working tree e a branch que encontrar.
3. Faça apenas a alteração solicitada e mantenha a versão em candidate.
4. Compile e execute os testes disponíveis. Registe cada nível de validação separadamente.
5. Valide package, versionCode, versionName, SHA-256 do APK e SHA-256 do certificado.
6. Publique em URL direta HTTPS; confirme a resposta e que o catálogo aponta para o mesmo artefato.
7. Teste a instalação e o comportamento no dispositivo quando disponível.
8. Promova candidate a stable somente após aprovação explícita do usuário.
9. Atualize docs/CONTINUITY.md com as evidências e pendências.

O histórico da Google Play Console não foi consultado. Antes de gerar uma versão para Play, confirme o último versionCode usado no projeto e no canal correto.
