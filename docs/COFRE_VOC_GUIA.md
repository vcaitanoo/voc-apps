# COFRE VOC — política de recuperação de credenciais

> Este guia é público e **não contém segredos**. `vcaitanoo/voc-apps` é um repositório público. Nunca inserir aqui chaves, tokens, senhas, `.jks`, `.keystore`, `service-account.json`, `.env`, códigos de recuperação, credenciais privadas ou certificados com chave privada.

## Dois lugares diferentes

1. **Central no GitHub:** códigos-fonte, instruções, catálogos, versões aprovadas, hashes, fingerprints de certificado, arquivos de configuração não secretos, nomes dos segredos e referências de onde foram guardados. Consultar [CENTRAL_VOC.md](CENTRAL_VOC.md).
2. **Cofre de segredos:** gestor de senhas com criptografia ponta a ponta para valores recuperáveis no celular e PC (por exemplo, um gestor de senhas reputado com notas seguras), protegido por senha mestra forte e autenticação de dois fatores; backup seguro separado. Não confundir um repositório privado com um cofre criptográfico.

## Onde colocar cada dado

| Dado | Local seguro recomendado | No GitHub público |
| --- | --- | --- |
| Repo/branch/commit, tarefas, URLs públicas, hash SHA-256, fingerprint **público** do certificado | Documentação versionada | Sim |
| Android packageName, versionCode, versionName, App ID AdMob (identificador público) | Documentação versionada | Em geral, sim |
| Senha de keystore, senha do alias, tokens pessoais, Supabase service_role, senhas de contas | Gestor de senhas/secret manager | **Nunca** |
| Arquivo de assinatura Android `.jks`/`.keystore` (chave privada) | Backup **criptografado** separado, com recuperação testada e proteção de acesso | **Nunca em claro**, nem em repo privado |
| Tokens/credenciais de compilação GitHub Actions | Repository → Settings → Secrets and variables → Actions | Guardar só o **nome** do Secret |
| Credenciais do runtime Vercel/Supabase | Variáveis de ambiente/secret store das plataformas | Apenas a referência, nunca o valor |
| Credenciais que você precisa consultar no telefone/PC | Gestor de senhas / notas seguras | Não colocar o valor |

### GitHub Actions Secrets não são o cofre de consulta

GitHub Actions Secrets servem para **usar** um segredo em workflows sem guardá-lo no código. O GitHub não disponibiliza o valor como uma nota legível para você consultar depois. Guarde a cópia recuperável em cofre próprio e armazene apenas o nome do Secret no índice.

### Como criar o acesso no celular e PC

1. Instalar/abrir um gestor de senhas confiável em ambos os aparelhos e habilitar autenticação de dois fatores.
2. Organizar entradas por app (VOC Lab, GPS 3D, Jarvis, Ache Aqui etc.) com nomes identificáveis; colocar senhas, tokens e instruções de recuperação em notas seguras. Não enviar a senha mestra em conversa.
3. Guardar keystores como **backup criptografado em armazenamento privado adequado**, em pelo menos duas cópias controladas, com a chave/senha de decriptação em local separado e seguro. Confirmar a capacidade de recuperação antes de depender desses backups.
4. No GitHub, documentar somente o nome do segredo e **qual sistema o contém**, não valores. Em `CENTRAL_VOC.md`, links e pontos de continuidade podem ser públicos.
5. Conectar apps/contas a ferramentas de automação apenas com permissões mínimas necessárias. Revogar/rotacionar segredos expostos.

### Repositório privado (opcional)

Um repositório `voc-cofre` privado no GitHub pode organizar **documentação privada não ultrassensível e backups já criptografados**. Não guardar segredos em texto puro nem assumir que a flag “private” elimina os riscos do histórico Git, acesso indevido ou compartilhamento acidental. Criação de outro repositório deve ser feita pelo proprietário via conta GitHub quando necessário.

## Regra para ChatGPT e Codex

- Nunca solicitar senha mestra, keystore privado, token ou chave sigilosa apenas para registrar na documentação pública.
- Antes de criar/alterar docs, verificar que arquivos e diffs não contêm segredo. Nunca usar `git add .` cegamente.
- Não imprimir valores secretos em respostas, logs, issues, PRs, catálogos nem commits.
- Caso o usuário forneça material sigiloso para uma operação legítima, tratar como dado sensível, aplicar somente no destino seguro autorizado e não retransmitir em arquivos públicos. Preferir controles nativos de secret management.
- Se qualquer credencial for exposta num repositório, primeiro **revogar/rotacionar**; simplesmente apagar um arquivo não elimina o histórico Git.
