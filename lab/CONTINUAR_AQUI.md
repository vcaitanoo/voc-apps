# VOC Lab — CONTINUAR AQUI

## Objetivo
VOC Lab é o canal privado de desenvolvimento. O VOC Manager oficial não deve ser alterado para testes.

## App
- Nome: VOC Lab
- Package: `pt.vcaitano.voclab`
- Fonte: `lab/`
- Catálogo: `lab/catalog.json`
- APK do próprio Lab: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/VOC-Lab-v1.0.0.apk`

## Build inicial do VOC Lab — 1.0.0
- versionCode: `1`
- versionName: `1.0.0`
- minSdk: `28`
- targetSdk: `36`
- compileSdk: `36`
- Gradle: build concluído com `BUILD SUCCESSFUL`
- APK SHA-256: `af691404cf1057a8149f837348bf8f24d6e89eb935f3a946d1f554d9a004cf1a`
- Certificado SHA-256: `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`
- Certificado DN: `CN=VOC Lab, OU=Android, O=vcaitano, L=Lousada, ST=Porto, C=PT`
- Assinatura verificada no APK: APK Signature Scheme v3.
- Estrutura confirmada: `AndroidManifest.xml`, `classes.dex`, `resources.arsc`, atividade principal `pt.vcaitano.voclab.MainActivity`.
- Permissões confirmadas: INTERNET, REQUEST_INSTALL_PACKAGES e QUERY_ALL_PACKAGES.
- Estado: compilação e estrutura verificadas. **Ainda não considerar execução em Android confirmada até o utilizador instalar, abrir e testar no telemóvel.**
- Chave privada: usar sempre a mesma chave do pacote privado `VOC_LAB_CHAVE_PRIVADA_BACKUP.zip`; nunca gerar outra chave para atualização.

## Regra de continuidade
Cada app possui no máximo:
1. uma versão `stable` confirmada pelo utilizador;
2. uma versão `candidate` em teste.

Uma build apenas compilada nunca vira `stable`.

## Publicar um candidato
1. Partir da última fonte confirmada do app.
2. Registar packageName, versionCode, versionName, SHA-256 da fonte/base, certificado de assinatura e ficheiros modificados.
3. Fazer somente as alterações pedidas.
4. Gerar APK pelo Gradle a partir da fonte.
5. Validar packageName, versionCode, versionName, SHA-256 do APK e SHA-256 do certificado.
6. Hospedar o APK numa URL HTTPS direta e permanente, preferencialmente neste repositório em `lab/apks/<app-id>/candidate/`.
7. Editar APENAS o campo `candidate` do app em `lab/catalog.json`.
8. Não substituir `stable` até o utilizador testar e confirmar que funciona.

Formato do candidato:
```json
"candidate": {
  "versionCode": 40,
  "versionName": "2.9",
  "apkUrl": "https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/apks/app-id/candidate/app.apk",
  "sha256": "SHA256_DO_APK",
  "signatureSha256": "SHA256_DO_CERTIFICADO",
  "notes": "Alteração exata desta build"
}
```

## Quando o utilizador disser que ficou perfeito / aprovado
1. Copiar os dados de `candidate` para `stable`.
2. Mover/copiar o APK aprovado para `lab/apks/<app-id>/stable/` e atualizar a URL.
3. Definir `candidate` como `null`.
4. Atualizar o checkpoint do projeto e guardar a fonte confirmada.
5. Manter no máximo a stable atual + uma stable anterior de segurança na área de fonte; candidatos rejeitados devem ser eliminados.

## Quando o candidato falhar
1. NÃO alterar `stable`.
2. Remover o APK candidato rejeitado.
3. Definir `candidate` como `null`.
4. Voltar obrigatoriamente à fonte marcada como estável.

## Regra para qualquer IA
A IA deve ler este ficheiro e `lab/catalog.json` antes de publicar qualquer APK. Nunca inferir a base a partir do nome de APK, conversa antiga, pasta temporária ou build não confirmada.

## Teste no telemóvel
Abrir VOC Lab > ATUALIZAR LISTA > escolher o app > INSTALAR/ATUALIZAR PARA CANDIDATO.
O Lab valida SHA-256, packageName, versionCode e assinatura antes de pedir a instalação ao Android.

## Separação obrigatória
- `VOC Lab`: desenvolvimento e testes privados.
- `VOC Manager`: distribuição oficial/futura dos apps aprovados.
