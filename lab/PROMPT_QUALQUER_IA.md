# VOC LAB — PROMPT UNIVERSAL PARA QUALQUER IA

Se recebeu acesso a este repositório para continuar um dos apps, comece SEMPRE assim:

> Leia `lab/CONTINUAR_AQUI.md` e `lab/catalog.json` antes de fazer qualquer alteração. O campo `stable` é a última versão aprovada e não pode ser substituído por uma build apenas compilada. Pode existir no máximo um `candidate`. Nunca use uma branch `tmp`, APK antigo, nome semelhante ou tentativa falhada como base. Trabalhe somente a partir da fonte estável confirmada do projeto. Depois de gerar um APK candidato, valide packageName, versionCode, versionName, SHA-256 e certificado de assinatura, publique o APK no VOC Lab e atualize somente `candidate`. Espere confirmação do utilizador antes de promover para `stable`.

## OPERAÇÃO: PUBLICAR CANDIDATO

Quando o utilizador pedir uma alteração e quiser testar no telemóvel:

1. Identificar a fonte/base que o checkpoint do projeto marca como estável.
2. Registar ANTES da alteração:
   - packageName;
   - versionCode/versionName da base;
   - SHA-256 da base/fonte;
   - SHA-256 do certificado de assinatura;
   - ficheiros que serão modificados.
3. Alterar somente o que foi pedido.
4. Compilar APK a partir do código-fonte com Gradle.
5. Validar estruturalmente o APK. Não afirmar que abre/funciona sem teste real em Android.
6. O novo `versionCode` deve ser maior que o da versão instalada/estável quando a atualização in-place exigir isso.
7. Copiar o APK para:
   `lab/apks/<app-id>/candidate/<nome-do-apk>.apk`
8. Calcular SHA-256 do APK.
9. Atualizar SOMENTE `candidate` do app em `lab/catalog.json` com:
   - versionCode;
   - versionName;
   - URL RAW HTTPS do APK;
   - SHA-256 do APK;
   - SHA-256 do certificado;
   - notes com a alteração exata.
10. Commitar/pushar APK + `lab/catalog.json`.
11. Informar ao utilizador: abrir VOC Lab > ATUALIZAR LISTA > instalar candidato.

## OPERAÇÃO: APROVAR

Executar somente depois de o utilizador confirmar explicitamente que o APK testado funciona/perfeito:

1. Confirmar que o `candidate` atual é exatamente o APK que o utilizador testou.
2. Copiar/mover esse APK para:
   `lab/apks/<app-id>/stable/<nome-do-apk>.apk`
3. Atualizar a URL para o caminho `stable`.
4. Copiar todos os metadados do candidato aprovado para `stable`.
5. Definir `candidate: null`.
6. Atualizar o checkpoint/fonte do projeto para marcar essa fonte como NOVA BASE ESTÁVEL.
7. Guardar SHA-256, versão, certificado e lista das funções/alterações confirmadas.
8. Manter apenas a stable atual e uma stable anterior de segurança na área de continuidade.
9. Não apagar a versão anterior até a promoção estar completamente registada.

## OPERAÇÃO: DESCARTAR

Quando o utilizador disser que o candidato falhou:

1. NÃO alterar `stable`.
2. Eliminar do Lab somente o APK de `candidate` rejeitado.
3. Definir `candidate: null`.
4. Eliminar fontes/builds temporários dessa tentativa depois de confirmar que a fonte estável continua preservada.
5. A próxima tentativa deve começar novamente da fonte marcada como estável, nunca da tentativa rejeitada.

## REGRA ABSOLUTA

`stable` = confirmado pelo utilizador.

`candidate` = ainda em teste.

Compilar não significa funcionar.

A conversa de uma IA não é a fonte da verdade. O checkpoint do projeto + `lab/catalog.json` são a fonte da verdade.

## VOC MANAGER OFICIAL

Não publicar candidatos nem builds de teste no VOC Manager oficial. O VOC Manager fica reservado para distribuição futura dos apps aprovados.
