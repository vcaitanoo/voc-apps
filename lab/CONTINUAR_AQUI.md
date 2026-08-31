# VOC Lab — CONTINUAR AQUI

## Objetivo
VOC Lab é o canal privado de desenvolvimento. O VOC Manager oficial não deve ser alterado para testes.

## App
- Nome: VOC Lab
- Package: `pt.vcaitano.voclab`
- Fonte: `lab/`
- Catálogo: `lab/catalog.json`
- APK do próprio Lab: `lab/apk/`

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
