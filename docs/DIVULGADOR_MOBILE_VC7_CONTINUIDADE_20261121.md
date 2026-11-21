# Divulgador Mobile VC7 (0.1.6) — envio automático com várias contas Gmail

## Base e controles de não regressão

- Base do código: `vcaitanoo/voc-apps` em `main`, SHA de entrada `54485292936cee13e87a14c3fd0419675b2626d5`.
- App a alterar: `pt.vcaitano.divulgadormobile` (pacote original VC6, **não** `pt.vcaitano.divulgador`).
- VC6 candidato previamente distribuído: `versionCode 6`, `versionName 0.1.5`, APK SHA256 `c7e426939fd6526b634db315c87b4a63d6636fab0f0692afbc1f2af5f23e1ca3`.
- Certificado VC6 SHA256 obrigatório: `b159a98ffef27e280b29af85de8ec1a3ddf60898acc58d8d7d1fb1e1b1391006`.
- Keystore **PKCS12** já recuperado e certificado verificado; nunca criar nova chave. Chaves e senhas não devem ser commitadas.
- VC6 não foi declarada base estável pelo usuário; portanto VC7 é candidata até a execução em Android ser aprovada.

## Experiência nova

O usuário cadastra um ou vários remetentes Gmail; as senhas de app Google (não senha principal) ficam criptografadas com AES-GCM/AndroidKeyStore. No editor já existente:
- importar CSV com `Email` obrigatório e `Consentimento` validado;
- gerar CSV sintético sem autorização de envio por padrão;
- configurar produto/link/assunto/corpo/fotos (persistir fotos em lote imutável);
- clicar em **PREPARAR FILA** e **INICIAR ENVIO AUTOMÁTICO**;
- a fila processa sem exigir confirmação de cada mensagem e pode ser **PAUSADA**;
- usar **GERENCIAR CONTAS GMAIL** para adicionar/remover/testar várias contas;
- exibir pendentes, enviados, falhas, incertos e bloqueados.

## Implementação

- `GmailAccounts.java`: armazenamento criptografado e validado de contas Gmail.
- `GmailAccountsActivity.java`: controles de cadastro, ativação, teste de conexão e remoção de contas.
- `AutoMailQueue.java`: SQLite local persistente, deduplicação global, opt-in, blacklist, status de envio incerto, foto congelada por campanha, limite por remetente/dia.
- `SmtpMailSender.java`: Gmail SMTP (SSL 465), conteúdo personalizado e fotos como MIME anexos, pausa em rejeições/quota, sem bypass de limites.
- `AutoMailWorker.java`: WorkManager com requisito de internet, ciclos automáticos de até 8 mensagens a intervalos de no mínimo 30 s; agendamento periódico de 15 min. O Android pode atrasar ciclos por Doze ou limitações de bateria.
- `SendActivity.java`: botões de preparar, iniciar, pausar, configurações Gmail, estatísticas; mantém envio manual como alternativa.
- `MainActivity.kt`: acesso direto à configuração das contas.
- `AndroidManifest.xml`: `ACCESS_NETWORK_STATE` e atividade.
- `app/build.gradle.kts`: `versionCode 7` / `versionName 0.1.6`, dependências Android WorkManager e JavaMail.

## Segurança e limitações

- Somente destinatários com autorização afirmativa e que **não** sejam sintéticos entram na fila.
- Nunca inventar consentimento para os e-mails do gerador.
- Limite configurável de 1–100 envios/dia/conta, com limite mínimo de 30 segundos entre mensagens.
- Erro de quota, bloqueio ou autenticação do Gmail **pausa a campanha inteira** — não pula para outra conta para contornar a restrição.
- SMTP pode falhar após aceite parcial. Operações interrompidas são classificadas como `uncertain` (não reenviar automaticamente).
- WorkManager não garante horário exato quando Android limita o segundo plano.
- O envio será real somente após o proprietário configurar e testar suas próprias contas e iniciar campanha autorizada.
- Não introduzir Gmail OAuth, Google Cloud credentials ou servidor autenticado sem consentimento/configuração adequada; senhas de app podem estar indisponíveis conforme regras da conta.
- O `divulgador-api` Supabase anterior permanece `DRY_RUN` e seu endpoint público não será usado para guardar credenciais nem disparar emails.
- Não afirmar `testado no Android` sem emulador ou dispositivo.
- Não publicar APK debug/unsigned nem candidato com assinatura diferente da VC6.
- O pipeline GitHub ainda necessita dos segredos de assinatura para distribuição automática; não incluir em Git.
