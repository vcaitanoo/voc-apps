# Continuidade — VOC Lab

Atualizado em 2026-10-19.

## Objetivo

Manter instruções versionadas para compreender o repositório VOC Apps, preservar stable/candidate e verificar a cadeia de distribuição do VOC Lab.

## Estado

- Repositório observado: https://github.com/vcaitanoo/voc-apps.
- A documentação inicial acrescenta instruções de raiz e referências operacionais. Nenhum app foi alterado, compilado, testado em dispositivo ou publicado por esta missão.
- lab/catalog.json é a referência atual para stable/candidate do VOC Lab. manifest.json é um catálogo separado do voc Manager.
- A fonte do app VOC Lab e o workflow de build têm informação divergente sobre o estado do próprio app. Reconcile essa evidência antes de uma nova build.
- A associação do endpoint principal de catálogo ao deployment ativo ainda precisa de confirmação.
- O acesso ao conteúdo e às políticas do armazenamento Supabase não foi confirmado.

## Próximos passos

1. Ao começar uma tarefa de app, leia AGENTS.md, docs/APP_INVENTORY.md, docs/VOC_LAB_WORKFLOW.md e lab/CONTINUAR_AQUI.md.
2. Confirme o repositório e o commit-fonte da versão stable.
3. Resolva as divergências de versão antes de compilar.
4. Verifique URL, APK, package, versão, SHA-256 e certificado antes de alterar o catálogo.
5. Teste instalação e comportamento em dispositivo antes de marcar uma versão como funcional.

As instruções de AGENTS.md são carregadas como instruções do projeto quando Codex trabalha no repositório. Os documentos de docs/ complementam essas instruções e precisam ser lidos explicitamente.
