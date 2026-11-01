# COFRE VOC — GitHub como única plataforma

> Decisão do proprietário, 2026-11-01: **não utilizar Bitwarden, gestor de senhas externo ou outro serviço**. Central e fluxos de build ficam exclusivamente no GitHub. Este documento é **público e não contém segredos**.
>
> **ESTADO:** arquitetura documentada; o repositório privado [vcaitanoo/voc-cofre](https://github.com/vcaitanoo/voc-cofre) **foi confirmado como PRIVATE e recebeu estrutura documental em 2026-11-01**. Nenhuma credencial, keystore ou backup de assinatura foi transferido ou verificado.

## Regra permanente — registro automático de novas assinaturas (2026-11-01)
- A partir de agora, sempre que o trabalho autorizado criar **um app Android novo** ou **uma chave/certificado de assinatura novo expressamente autorizado**, executar **no mesmo fluxo**, sem esperar outro pedido, o inventário: app, packageName, versionCode, versionName, fingerprint SHA-256 do certificado público, SHA-256 do APK/AAB, repo/commit do código-fonte, nome dos Secrets e localização do backup. Atualizar `docs/CENTRAL_VOC.md` e o checkpoint do app, sem expor valores.
- **Nunca** gerar chave nova para atualizar aplicativo já instalado quando a assinatura original estiver disponível; preservar a identidade de assinatura. Alteração ou rotação de chave exige autorização específica e análise da compatibilidade com Google Play e dispositivos já instalados.
- Após um novo material de assinatura ter sido criado **com autorização**, configurar GitHub Actions Secrets adequados para assinatura automatizada **somente se houver acesso e permissão**, e preparar o backup da chave privada **criptografado antes de subir ao Git** no repositório privado `voc-cofre`, **somente após sua existência e acesso verificados**. Não armazenar keystore, senha ou token em texto puro em qualquer repositório, nem emitir valores em logs/relatórios/conversa. O proprietário mantém em segurança, fora do GitHub, a frase necessária para recuperar o backup cifrado.
- Testar o procedimento de recuperação do backup sem expor dados e registrar evidências não sensíveis. Se não for possível fazer backup seguro, não declarar a chave “salva”; explicar exatamente o que falta. Não criar nem descartar irrevogavelmente nova chave sem plano de recuperação.
- O proprietário **não precisa repetir essa instrução a cada tarefa**, desde que o agente esteja trabalhando no repositório com estas regras carregadas, ou dentro do Projeto ChatGPT que tenha as instruções aplicadas. Fora desses contextos, o carregamento automático **não é garantido**. GitHub Actions Secrets **não permitem consultar novamente o valor secreto**: não confundir segredo configurado com cópia recuperável.

## Arquitetura autorizada

1. **GitHub público:** `vcaitanoo/voc-apps` + [CENTRAL_VOC.md](CENTRAL_VOC.md) contêm documentação, links, repositórios, versões confirmadas, hashes, fingerprints públicos de certificados, nomes dos Secrets e localização lógica dos backups. Nunca valores secretos.
2. **GitHub privado (criado e confirmado como PRIVATE):** `vcaitanoo/voc-cofre` pode guardar inventário privado e **somente arquivos de backup já criptografados antes do commit** (por exemplo, keystore cifrado com criptografia autenticada e senha de descriptografia separada). A opção PRIVATE não transforma arquivos em texto puro em dados criptografados ponta a ponta.
3. **GitHub Actions Secrets:** armazenam credenciais de build e tokens para workflows autorizados e revisados nos repositórios onde os workflows são executados. Os valores são fornecidos apenas a workflows que os referenciem; não ficam visíveis posteriormente em uma página para copiar. Servem para assinar/publicar sem colar a senha numa conversa.
4. **Recuperação:** o proprietário precisa preservar um modo de recuperar a frase de descriptografia **fora do GitHub**, por exemplo uma cópia offline que ele controla e memoriza. Não colocar essa frase em arquivo, commit, issue, log, chat ou outro Secret que possa ser exposto junto do backup. Se perdê-la, pode ser impossível recuperar o keystore cifrado. Não há garantia absoluta de que apenas o proprietário ou um assistente técnico tenham acesso: GitHub, permissões de colaboradores, tokens e workflows são superfícies reais de acesso.

## Onde guardar cada informação

| Informação | Onde fica | Pode ser lida novamente no celular/PC? |
| --- | --- | --- |
| packageName, versionCode, versões aprovadas, URLs públicas, SHA-256, fingerprint do certificado | Central VOC no GitHub público | Sim |
| Lista de chaves, nome dos Secrets, política de backup, inventário privado sem valores sigilosos | GitHub privado `voc-cofre` | Sim, com acesso autorizado |
| Tokens de API, senhas de assinatura para execução automática | GitHub Actions Secrets no repositório do workflow | **Não**. Podem ser atualizados e usados por workflows, não recuperados em texto pela interface |
| Arquivo de assinatura Android `.jks` / `.keystore` | Backup **criptografado** num repositório privado e, se necessário, representação Base64 em Action Secret com limites de tamanho | Arquivo cifrado, sim; descriptografia somente com a frase fora do GitHub |
| Senha de recuperação / frase que abre o backup cifrado | Somente sob controle pessoal do proprietário, fora do GitHub | Depende do backup pessoal; **nunca registrar no GitHub** |

## Configuração pelo celular (GitHub, sem outro serviço)

1. Repositório criado e confirmado: [vcaitanoo/voc-cofre](https://github.com/vcaitanoo/voc-cofre) (**Private**). Não alterar para Public.
2. Restringir colaboradores, tokens, regras e workflows aos estritamente necessários. Habilitar autenticação de dois fatores na conta.
3. **Antes de enviar chaves privadas:** gerar cópia criptografada localmente, verificar a capacidade de descriptografar e manter a frase fora do GitHub. Um `.jks` não é um backup seguro só por estar num repositório Private.
4. Em cada repositório que precisa compilar: **Settings → Secrets and variables → Actions → New repository secret**. Colocar o token/senha na interface do GitHub, não na conversa e não em arquivos versionados.
5. Criar no índice `voc-cofre` apenas referências: qual app usa cada Secret, em qual repo ele existe, como repor o segredo e onde está o backup **cifrado**. Registar fingerprint SHA-256 da assinatura pública para verificação de identidade do APK.
6. Publicar APK candidato no VOC Lab seguindo a skill, sem expor segredos nos logs. Para Play Console, confirmar versão/certificado antes do AAB.

## Limitações de acesso do ChatGPT / Codex

- O assistente só pode ler/escrever um repositório privado quando a conexão do GitHub realmente autoriza. Não significa que pode abrir GitHub Actions Secrets ou ler o valor de uma senha.
- Um workflow legítimo pode usar um Secret para assinar um APK sem devolver a senha. Revisar as permissões do workflow; código malicioso ou colaboradores com escrita podem tentar exfiltrar segredos.
- Nenhuma IA deve afirmar que pode recuperar chaves, descriptografar backups ou fazer build assinado sem evidências e autorização.
- Não criar, publicar, descriptografar ou mover material sensível sem autorização explícita do proprietário.
- `voc-cofre` foi criado e seu acesso autorizado verificado; **nenhum segredo ou backup cifrado foi armazenado automaticamente**. **Não usar repositórios públicos**, incluindo `vcaitanoo/voc-apps`, para o backup do keystore nem criptografado sem análise específica do risco.
- Se um segredo for exposto num commit, apagar o arquivo não remove o histórico: revogar/rotacionar o segredo e avaliar impacto.

## Fonte oficial

- GitHub Docs: [Using secrets in GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).
- GitHub Docs: [Secrets reference](https://docs.github.com/en/actions/reference/security/secrets).
