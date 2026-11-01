# Checklist de release VOC — preenchimento obrigatório quando houver artefato

| Campo | Evidência real / resultado |
| --- | --- |
| App e repositório | |
| Fonte autorizada (branch + commit + arquivo) | |
| Aprovação Android real da base | |
| SHA-256 do pacote-fonte/base | |
| applicationId / package | |
| versionCode / versionName base | |
| Certificado SHA-256 base | |
| Arquivos/trechos autorizados | |
| Arquivos/trechos realmente alterados | |
| Diff e testes | |
| Gradle APK / caminho / SHA-256 | |
| APK package / versão / DEX / resources | |
| APK assinatura/certificado | |
| Teste físico Android / quem confirmou | |
| Upload APK / URL direta / bytes remotos + hash | |
| Catálogo candidate / endpoint publicado | |
| Decisão de promoção para stable | |
| Maior versionCode já enviado ao Play | |
| AAB mesmo código final / versão / certificado | |
| Bundletool/estrutura do AAB / SHA-256 | |
| Play upload / release / status (somente com prova) | |
| Checkpoint de continuidade atualizado | |

## Estados honestos
- NÃO VERIFICADO: ainda não foi obtida evidência suficiente.
- ESTRUTURA OK: manifesto, recursos, DEX e assinatura tecnicamente inspecionados.
- BUILD OK: Gradle concluiu para a fonte registrada.
- TESTADO EM EMULADOR: emulador e cenário especificados.
- TESTADO NO ANDROID REAL: dispositivo e teste efetivamente registrados.
- APROVADO PELO USUÁRIO: confirmação explícita referente **ao mesmo APK exato**.

## Promoção e falha
- Candidate rejeitado: nunca usá-lo como nova base. Preservar código/artefato stable antes de qualquer limpeza.
- Stable confirmado: guardar fonte + commit, SHA-256, pacote e certificado, versão, changelog e evidência de funcionamento.
- O AAB é um passo posterior à validação do APK do **mesmo fonte final**; versão da Play deve ser selecionada antes da build de validação.
