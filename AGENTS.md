# Instruções persistentes — VOC Apps e VOC Lab

Estas regras aplicam-se a trabalhos no repositório vcaitanoo/voc-apps e aos aplicativos apresentados no catálogo do VOC Lab.

## Antes de alterar um app

1. Leia este arquivo, docs/CONTINUITY.md, docs/APP_INVENTORY.md, docs/VOC_LAB_WORKFLOW.md, lab/CONTINUAR_AQUI.md e lab/catalog.json.
2. Consulte também README.md, docs/PUBLISHING.md e docs/PUBLICAR_APK_NO_VOC_MANAGER.md quando o trabalho tocar no VOC Manager ou na distribuição oficial.
3. Confirme o repositório, branch, commit, packageName, versionCode, versionName, certificado e artefato da base usada. O commit atual da branch do app não prova que o APK estável foi compilado daquele commit.
4. Trabalhe num app por vez e na branch real desse app. Preserve alterações existentes na working tree.
5. Trate a versão stable do catálogo como registro de distribuição. Registre como confirmação funcional apenas quando existir aprovação explícita do usuário ou teste real documentado.

## Integridade e publicação

- Mantenha packageName, assinatura e identidade de instalação existentes.
- Nunca altere stable antes da confirmação do usuário. Desenvolva em candidate e preserve a stable registrada.
- Compile a partir da fonte correta. Não edite APK, DEX, smali ou bytecode quando houver fonte disponível.
- Antes de publicar, valide package, versões, SHA-256 do APK e SHA-256 do certificado. Registre a origem exata do build.
- Separe commit de código, build, artefato, catálogo, publicação e instalação real. Um commit ou uma compilação não confirma que o app funciona nem que a atualização aparece no VOC Lab.
- Não publique chaves, senhas, tokens, keystores, conteúdo de signing material ou ficheiros de ambiente.
- Não altere apps não pedidos, não faça reset destrutivo, force push ou limpeza indiscriminada.

## Catálogos separados

- lab/catalog.json é o catálogo de stable/candidate consumido pelo VOC Lab.
- manifest.json é o catálogo consumido pelo voc Manager.
- Atualizar um catálogo não atualiza automaticamente o outro.
- Confirme a URL e a resposta publicada antes de declarar uma publicação disponível.

## Continuidade

Atualize docs/CONTINUITY.md após mudanças relevantes. Mantenha o pacote portátil alinhado com o último estado verificado e sem segredos. Consulte docs/VOC_LAB_WORKFLOW.md para o fluxo detalhado e docs/APP_INVENTORY.md para o snapshot dos apps.

O AGENTS.md na raiz é a instrução de projeto a ser carregada quando Codex trabalha dentro deste repositório. Os documentos de docs/ são referências complementares e precisam ser lidos explicitamente. A orientação oficial do Codex descreve o carregamento de AGENTS.md no início do trabalho: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide.
