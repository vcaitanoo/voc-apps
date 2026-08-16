# voc apps

Repositório público de distribuição dos apps voc.

O código-fonte das aplicações permanece nos respetivos repositórios privados. Este repositório contém apenas o catálogo público usado pelo **voc Manager** e os APKs publicados através de GitHub Releases.

## Estrutura

- `manifest.json` — catálogo consumido pelo voc Manager.
- `schema/manifest.schema.json` — contrato do catálogo.
- `icons/` — ícones públicos dos apps, quando adicionados.
- GitHub Releases — APKs publicados para instalação e atualização.

## Regras de publicação

1. Nunca publicar chaves API, keystores, tokens ou código-fonte privado aqui.
2. Cada atualização deve manter o mesmo package e certificado de assinatura do app instalado.
3. `versionCode` deve aumentar a cada atualização.
4. O APK publicado deve ter SHA-256 registado no `manifest.json`.
5. O voc Manager deve validar package, versão, SHA-256 e assinatura antes de iniciar uma atualização.

## Estado inicial

O catálogo foi preparado para receber o **voc Manager** e os apps que serão adicionados progressivamente.
