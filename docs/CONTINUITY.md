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


## VOC Lab — recuperacao de catalogo (2026-11-04)
- Falha relatada: Hora Jarvis 1.2.0-LAB nao aparecia no VOC Lab instalado, embora `lab/catalog.json` na branch main contenha `hora-jarvis` com candidato VC3 e APK SHA-256 `085f61d80bef2826ecb68bcb537732dfa6bb395dbedcb24432cbb5b41d9f913e`.
- Diagnostico: cliente Android da fonte consulta primeiro `https://temporary-snappy-redwood-yqm3s0d.vercel.app/catalog.json` e nao compara com GitHub se esse endpoint responder com catalogo antigo. Endpoint Vercel original sem projeto acessivel na conta conectada; espelho nao sincronizado.
- Correcao preparada: priorizar `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json` e manter Vercel como fallback em branch `fix/voc-lab-catalog-github-first-20261103`. Fonte-fix inicial `7a410c45e6f101d826bd33011e6bd5a90d1e3759`; candidata Android original (package `pt.vcaitano.voclab`, versionCode 4, versionName 1.0.3) NAO distribuida pois faltam os Secrets `VOC_LAB_KEYSTORE_B64`/senha; manter certificado esperado SHA-256 `9822c1bf439a0790b5dfd58f97ec972735d4bcfa3b591a455760fa62d5fd5380`, nao gerar chave substituta para o pacote oficial.
- Recuperacao temporaria: branch fonte `fix/voc-lab-catalog-github-first-20261103`, commit `99ed879a3d806c7bf2c2d23c21de5b39bfc8d2a6`, gerou app separadamente instalavel `pt.vcaitano.voclab.emergencia`, VC4/1.0.3, label `VOC Lab — Atualizado`, build Gradle debug + estrutura e assinatura validadas, APK SHA-256 `8a6c9428a0195075f8494b16cbfd89e4544c8f1d3dd89527e46523ffa9fa5fa0`.
- APK de recuperacao publico HTTPS: `https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/apks/voc-lab-emergencia/VOC-Lab-Atualizado-1.0.3-VC4.apk`; URL verificada pelo proprio workflow mediante download e comparacao byte-a-byte em `https://github.com/vcaitanoo/voc-apps/actions/runs/41743646813`.
- Estado: somente TESTE, nao aprovado em Android real, assinatura debug temporaria do runner sem identidade para futuras atualizacoes; nao e a stable do VOC Lab. Codigo original e stable nao alterados, `manifest.json` nao alterado, `lab/catalog.json` mantido.
- Proxima etapa: recuperar keystore original com backup privado valido e Secrets, compilar a correção sob pacote oficial com mesmo certificado, validar em Android e so depois distribuir o app oficial. Evitar substituir oficialmente a assinatura por debug.
