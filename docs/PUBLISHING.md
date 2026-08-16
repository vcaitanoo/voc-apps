# Publicação dos apps no voc Manager

O `manifest.json` é o catálogo consumido pelo voc Manager. Os APKs publicados devem ficar em GitHub Releases ou noutro endereço HTTPS estável.

## Segurança

- Nunca colocar keystore, password, API key ou token neste repositório.
- O APK deve ser validado antes da publicação.
- Uma atualização só é válida se mantiver o `packageName` e a identidade de assinatura esperada.
- `versionCode` deve sempre aumentar.

## voc Manager

O workflow manual `.github/workflows/release-voc-manager.yml` cria a release assinada e atualiza automaticamente a entrada `voc-manager` no catálogo.

Secrets necessários no repositório:

- `VOC_MANAGER_KEYSTORE_B64`
- `VOC_MANAGER_KEYSTORE_PASSWORD`

A chave de assinatura deve permanecer guardada fora do GitHub público. O alias esperado pelo workflow é `voc-manager-release`.

## Adicionar um novo app

Adicionar uma entrada a `apps` em `manifest.json` com `status: "coming_soon"`. Depois de validar o APK final:

1. publicar o APK por HTTPS;
2. calcular o SHA-256 do APK;
3. obter o SHA-256 do certificado de assinatura;
4. preencher `versionCode`, `versionName`, `apkUrl`, `sha256` e `signatureSha256`;
5. mudar `status` para `published`.

O voc Manager passa a mostrar o novo app sem precisar de uma nova versão do Manager.

## Atualizar um app

Publicar o novo APK com `versionCode` maior, mantendo package e assinatura. Atualizar URL, versão, hash e changelog no catálogo. O Manager passa a mostrar `ATUALIZAÇÃO DISPONÍVEL` aos dispositivos com uma versão inferior.
