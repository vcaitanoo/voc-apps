# Publicar APK no voc Manager

Este é o procedimento oficial para inserir ou atualizar um APK no voc Manager.

## Regra principal

Nunca publicar no catálogo um APK sem validar antes package, versionCode, versionName, SHA-256 do ficheiro e SHA-256 do certificado de assinatura.

Para apps já instaladas, a nova versão DEVE usar exatamente a mesma chave/certificado da versão instalada. Se a chave antiga tiver sido perdida, Android não permite atualização in-place: é necessária uma migração única por desinstalação/reinstalação. Depois da migração, todas as versões futuras devem usar uma chave permanente guardada.

## Fluxo

1. Usar a fonte correta/confirmada do app.
2. Incrementar `versionCode` e definir `versionName`.
3. Compilar o APK a partir da fonte.
4. Assinar com a chave permanente do app. **Nunca distribuir `assembleDebug` como versão gerida pelo Manager.**
5. Validar o APK:
   - packageName;
   - versionCode;
   - versionName;
   - SHA-256 do APK;
   - SHA-256 do certificado de assinatura.
6. Hospedar o APK em URL HTTPS estável e direta.
7. Atualizar `manifest.json` com esses valores exatos.
8. Se for importante o app continuar disponível quando o catálogo online falhar, atualizar também `manager/app/src/main/java/pt/vcaitano/vocmanager/CatalogClient.java` (`FALLBACK_CATALOG`).
9. Se o fallback do Manager foi alterado, incrementar a versão do próprio voc Manager, compilar e assinar com `voc-manager-release.jks`.
10. Testar no Manager: cartão aparece, estado é INSTALAR/ATUALIZAR/ABRIR conforme o caso e o download passa por SHA/package/version/signature.

## Estrutura de entrada no `manifest.json`

```json
{
  "id": "app-id",
  "name": "Nome",
  "packageName": "pt.vcaitano.exemplo",
  "category": "productivity",
  "description": "Descrição",
  "status": "published",
  "versionCode": 1,
  "versionName": "1.0.0",
  "minSdk": 26,
  "apkUrl": "https://.../app.apk",
  "sha256": "SHA256_DO_APK",
  "signatureSha256": "SHA256_DO_CERTIFICADO",
  "iconUrl": null,
  "changelog": "Alterações",
  "mandatory": false,
  "monetization": {
    "type": "free",
    "priceCents": 0,
    "currency": "EUR",
    "period": null,
    "trialDays": 0,
    "provider": "none"
  }
}
```

## Jarvis — regra permanente de assinatura

Package: `pt.vcaitano.jarvis`

A partir da migração de assinatura de 2026-08-26, o Jarvis deve usar sempre a chave permanente privada `jarvis-release.jks`, guardada fora do repositório público.

Alias: `jarvis-release`

Certificado SHA-256 esperado:

`f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2`

Nunca voltar a publicar Jarvis com a chave debug criada automaticamente por Gradle/Vercel. A chave privada e a password não devem ser commitadas no GitHub.

## voc Manager — assinatura

Package: `pt.vcaitano.vocmanager`

Certificado SHA-256 esperado:

`918b566590b49f691ec9880c95dd174a6c032b21f81dc66efcfac74d0de11aa8`

A chave privada do Manager também nunca deve ser commitada no repositório público.
