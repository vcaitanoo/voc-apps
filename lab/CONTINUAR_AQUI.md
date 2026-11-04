# VOC Lab — CONTINUAR AQUI

## Objetivo
VOC Lab é o canal privado de desenvolvimento. O VOC Manager oficial não deve ser alterado para testes.

## App
- Nome: VOC Lab
- Package: `pt.vcaitano.voclab`
- Fonte: `lab/`
- Catálogo oficial: `lab/catalog.json`
- APK candidato atual do próprio Lab: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/VOC-Lab-v1.0.1.apk`
- Catálogo primário no app 1.0.1: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json`
- Fallback de catálogo: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json`

## Estado do VOC Lab

### 1.0.0 — REJEITADA EM RUNTIME
- versionCode: `1`
- versionName: `1.0.0`
- APK SHA-256: `af691404cf1057a8149f837348bf8f24d6e89eb935f3a946d1f554d9a004cf1a`
- Certificado SHA-256: `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`
- Compilação/estrutura: OK.
- Resultado no telemóvel informado pelo utilizador: **falha ao atualizar a lista**.
- Causa tratada: dependência de um único endpoint `raw.githubusercontent.com` para carregar o catálogo.
- Regra: NÃO promover 1.0.0 a estável e não voltar a usá-la como versão final.

### 1.0.1 — CANDIDATA ATUAL
- versionCode: `2`
- versionName: `1.0.1`
- minSdk: `28`
- targetSdk: `36`
- compileSdk: `36`
- Gradle: `BUILD SUCCESSFUL`
- APK: `https://temporary-snappy-redwood-yqm3s0d.vercel.app/VOC-Lab-v1.0.1.apk`
- APK SHA-256: `d2720ed431478383e5604e084e8a57c1e693d27e8075bc1aefe9e02284725003`
- Certificado SHA-256: `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`
- Certificado DN: `CN=VOC Lab, OU=Android, O=vcaitano, L=Lousada, ST=Porto, C=PT`
- Assinatura verificada: APK Signature Scheme v3.
- Mesma assinatura da 1.0.0: SIM.
- Fonte/arquivo de build desta candidata SHA-256: `bda659206f2601c936988a1b045cbe82e30cba365dabe2bb2af6b13da2fb9ba8`
- Ficheiros alterados em relação à 1.0.0:
  1. `lab/app/build.gradle.kts` — apenas versionCode/versionName para 2 / 1.0.1.
  2. `lab/app/src/main/java/pt/vcaitano/voclab/MainActivity.java` — catálogo redundante, leitura via Vercel com fallback GitHub e erro indicando o host que falhou.
- Catálogo Vercel validado por HTTP 200 e `application/json`.
- APK validado por HTTP 200 e `application/vnd.android.package-archive`.
- Estado: compilação, estrutura, package, versão, SHA e assinatura verificados. **Execução real ainda depende de teste do utilizador.**
- Regra: somente promover 1.0.1 a STABLE se o utilizador confirmar que a lista carrega no telemóvel.

## Chave do VOC Lab
- Usar sempre a mesma chave do pacote privado `VOC_LAB_CHAVE_PRIVADA_BACKUP.zip`.
- Nunca gerar outra chave para uma atualização do package `pt.vcaitano.voclab`.
- Nunca publicar a chave ou palavras-passe em repositório público.

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
6. Hospedar o APK numa URL HTTPS direta.
7. Editar APENAS o campo `candidate` do app em `lab/catalog.json`.
8. Sincronizar também o catálogo servido pelo VOC Lab no Vercel quando esse endpoint for usado como primário.
9. Não substituir `stable` até o utilizador testar e confirmar que funciona.

Formato do candidato:
```json
"candidate": {
  "versionCode": 40,
  "versionName": "2.9",
  "apkUrl": "URL_HTTPS_DIRETA_DO_APK",
  "sha256": "SHA256_DO_APK",
  "signatureSha256": "SHA256_DO_CERTIFICADO",
  "notes": "Alteração exata desta build"
}
```

## Tela Sempre Ativa — regra específica atual
- `stable` deve permanecer V25 / versionName `1.0.20` / versionCode `25` até confirmação explícita do utilizador de uma candidata mais nova.
- Uma V29 em geração noutra conversa deve entrar somente como `candidate` depois que o APK real estiver disponível e forem verificados package, versionCode, versionName, SHA-256 e certificado.
- Não usar V28, ficheiros antigos ou APK inferido pelo nome como substituto da V29.

## Quando o utilizador disser que ficou perfeito / aprovado
1. Copiar os dados de `candidate` para `stable`.
2. Mover/copiar o APK aprovado para a área estável e atualizar a URL.
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


## VOC Lab — recuperacao de catalogo (2026-11-04)
- Falha relatada: Hora Jarvis 1.2.0-LAB nao aparecia no VOC Lab instalado, embora `lab/catalog.json` na branch main contenha `hora-jarvis` com candidato VC3 e APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`.
- Diagnostico: cliente Android da fonte consulta primeiro `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` e nao compara com GitHub se esse endpoint responder com catalogo antigo. Endpoint Vercel original sem projeto acessivel na conta conectada; espelho nao sincronizado.
- Correcao preparada: priorizar `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json` e manter Vercel como fallback em branch `fix/voc-lab-catalog-github-first-20261103`. Fonte-fix inicial `7a410c45e6f101d826bd33011e6bd5a90d1e3759`; candidata Android original (package `pt.vcaitano.voclab`, versionCode 4, versionName 1.0.3) NAO distribuida pois faltam os Secrets `VOC_LAB_KEYSTORE_B64`/senha; manter certificado esperado SHA-256 `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`, nao gerar chave substituta para o pacote oficial.
- Recuperacao temporaria: branch fonte `fix/voc-lab-catalog-github-first-20261103`, commit `99ed879a3d806c7bf2c2d23c21de5b39bfc8d2a6`, gerou app separadamente instalavel `pt.vcaitano.voclab.emergencia`, VC4/1.0.3, label `VOC Lab — Atualizado`, build Gradle debug + estrutura e assinatura validadas, APK SHA-256 `8a6c9428a0195075f8494b16cbfd89e4544c8f1d3dd89527e46523ffa9fa5fa0`.
- APK de recuperacao publico HTTPS: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/apks/voc-lab-emergencia/VOC-Lab-Atualizado-1.0.3-VC4.apk`; URL verificada pelo proprio workflow mediante download e comparacao byte-a-byte em `https://github.com/vcaitanoo/voc-apps/actions/runs/41743646813`.
- Estado: somente TESTE, nao aprovado em Android real, assinatura debug temporaria do runner sem identidade para futuras atualizacoes; nao e a stable do VOC Lab. Codigo original e stable nao alterados, `manifest.json` nao alterado, `lab/catalog.json` mantido.
- Proxima etapa: recuperar keystore original com backup privado valido e Secrets, compilar a correção sob pacote oficial com mesmo certificado, validar em Android e so depois distribuir o app oficial. Evitar substituir oficialmente a assinatura por debug.

## Hora Jarvis — confirmado no catálogo do VOC Lab ORIGINAL (2026-11-04)
- Pedido: Hora Jarvis 1.2.0 no VOC Lab Android original, junto dos outros apps, sem instalar um segundo Lab.
- Causa confirmada no GitHub Actions (workflow read-only `41745953937`): `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` HTTP 200 com 8 apps, sem `hora-jarvis`, atualizado em 2026-11-01; `lab/catalog.json` GitHub possuía Hora Jarvis, mas o app Android aceita o primeiro catálogo válido e não chega ao fallback.
- Caminho real do endpoint: alias `temporary-snappy-redwood-yqm3s0d.vercel.app` pertence ao projeto Vercel `prj_EU0b8etzUUFAMiLg18Ll7EU7uXN4` (atual nome `ache-aqui-politica-privacidade`), deploy `dpl_9VXHTWu99R32KqtXXe7wyPS34L4Y`; `vercel.json` reescreve `/catalog.json` para Supabase Edge Function `https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/voc-lab-catalog`.
- A função `voc-lab-catalog` lê exclusivamente `public.voc_lab_catalog_store`, linha `id=main`, campo JSONB `body`; por isso o GitHub estava correto mas não aparecia no Lab original.
- CORREÇÃO EFETIVA: SQL condicional no projeto Supabase `khinnoxpesnhtmmvrken`, acrescentou APENAS a entrada `hora-jarvis` retirada de `lab/catalog.json` ao JSONB da linha `main`, preservando as 8 entradas existentes e seus estados. `updatedAt` ficou `2026-11-04T00:22:14Z`.
- Verificação final independente (GitHub Actions read-only `41746339571`, executado depois da alteração): endpoint Vercel ORIGINAL HTTP 200, `app_count=9`, `has_hora_jarvis=True`; ids: `tela-sempre-ativa,voc-manager,voc-tv,damas,jarvis,simulador-jetpack,divulgador,gps-3d,hora-jarvis`. APK do Hora Jarvis HTTP 200, 38139 bytes, SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e` (igual ao candidato do catálogo).
- Nenhum APK de app, assinatura, versão stable, `manifest.json`, código Android VOC Lab, Vercel/privacidade Ache Aqui ou outros 8 apps foi modificado nesta correção. App normal instalado deve buscar o catálogo atualizado tocando em ATUALIZAR LISTA.
- O novo Hora Jarvis `1.2.0-lab` `versionCode 3` é CANDIDATO, não confirmado como funcional em Android real. A versão `1.1.0-teste` confirmada permanece base estável do Hora Jarvis fora do LAB.
- Evitar usar a branch experimental `fix/voc-lab-catalog-github-first-20261103` como base ou implantar VOC Lab de recuperação. A correção real foi no backend que já atende o VOC Lab original.
