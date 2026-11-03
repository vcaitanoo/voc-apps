# CENTRAL VOC — índice permanente dos projetos

> Atualizado: 2026-11-01. Este documento é **público**. Não inserir credenciais, tokens, senhas, keystores, chaves privadas nem valores de Secrets.
>
> Objetivo: acesso pelo celular/PC, ChatGPT, Codex e outros agentes com permissão, sem depender de uma conversa específica.

## Acesso e links principais

| Finalidade | Endereço ou arquivo canônico |
| --- | --- |
| Hub e distribuição | https://github.com/vcaitanoo/voc-apps |
| Instruções do Codex | [AGENTS.md](../AGENTS.md) |
| Skill de desenvolvimento | [VOC Lab Master](../.agents/skills/voc-lab-master/SKILL.md) |
| Instruções do Projeto ChatGPT | [VOC Lab ChatGPT](VOC_LAB_CHATGPT_PROJECT_INSTRUCTIONS.md) |
| Estado do VOC Lab | [CONTINUAR_AQUI.md](../lab/CONTINUAR_AQUI.md) |
| Catálogo de candidatos e estáveis | [lab/catalog.json](../lab/catalog.json) |
| Catálogo oficial do VOC Manager | [manifest.json](../manifest.json) |
| Fluxo de atualização | [VOC_LAB_WORKFLOW.md](VOC_LAB_WORKFLOW.md) |
| Registro geral de continuidade | [CONTINUITY.md](CONTINUITY.md) |
| Inventário de apps | [APP_INVENTORY.md](APP_INVENTORY.md) |
| Guia de segredos/credenciais | [COFRE_VOC_GUIA.md](COFRE_VOC_GUIA.md) |
| Repositório privado do Cofre VOC (acesso autenticado) | [vcaitanoo/voc-cofre](https://github.com/vcaitanoo/voc-cofre) |

**Separação essencial:** `lab/catalog.json` destina-se ao VOC Lab, com `stable` e `candidate`; `manifest.json` pertence ao VOC Manager oficial. Publicar candidato no Lab não promove stable automaticamente.

## Projetos e código-fonte

| Projeto | Fonte / identificação a conferir |
| --- | --- |
| GPS 3D | https://github.com/vcaitanoo/gps-3d |
| VOC Lab (app Android) | [lab/](../lab/) |
| VOC Manager | [manager/](../manager/) |
| Jarvis | Verificar a fonte canônica e o checkpoint atual; artefatos históricos em `lab/sources/jarvis/`; não assumir que uma tentativa recente é aprovada |
| Damas | Consultar inventário e catálogo, confirmar repo da fonte e versão aprovada |
| Tela Sempre Ativa | Consultar inventário, catálogo e checkpoint da fonte confirmada |
| VOC TV | Consultar inventário, catálogo e repo de origem |
| Ache Aqui e outros projetos | Repositório próprio a confirmar; **não adicionar ao catálogo** por suposição |

## O que conservar de cada aplicativo

Manter um checkpoint por app, em documentação **sem segredos** e com evidências verificáveis:
1. Nome, repo/branch/commit da fonte e packageName.
2. Última **versão efetivamente aprovada pelo usuário**, com data/ambiente do teste; não inferir aprovação por Gradle ou catálogo.
3. versionCode, versionName, SHA-256 do APK/base, SHA-256 do certificado de assinatura e localização da cópia aprovada.
4. Identificação da candidata atual, o que mudou, quais testes foram realmente executados e quais ficaram pendentes.
5. Backlog de bugs, comportamentos a preservar, decisões do usuário, alertas de regressão e próximo passo.
6. Histórico de Play Console (maior versionCode já enviado) **apenas após verificação**.
7. Nomes/referências de Secrets e localização do cofre (sem os valores), com responsável pelo acesso e rotina de recuperação.

### Modelo copiável de checkpoint

```md
# CHECKPOINT — <app>
Atualizado: AAAA-MM-DD
Repo / branch / commit-fonte: NÃO VERIFICADO
Fonte da última versão aprovada: NÃO VERIFICADO
Aprovação do usuário e teste real: NÃO VERIFICADO
Package name: NÃO VERIFICADO
Stable: versionCode / versionName / SHA-256 APK: NÃO VERIFICADO
Certificado SHA-256: NÃO VERIFICADO
Candidate: versão / URL / SHA-256 / status: NÃO VERIFICADO
O que já funciona e deve ser preservado:
O que foi solicitado:
Arquivos alterados:
Build: NÃO VERIFICADO
Teste em dispositivo Android real: NÃO VERIFICADO
Último versionCode usado na Play: NÃO VERIFICADO
Local de credenciais (somente referência, não valor):
Ponto exato para continuar:
```

## Regra de trabalho entre celular, PC e IAs

- Usar este índice como **porta de entrada**. Ler instruções e checkpoint específico antes de editar apps.
- Sempre que algo de valor duradouro for confirmado (versão estável, SHA, assinatura, arquitetura, bug resolvido, setup, decisão, link oficial), atualizar a documentação apropriada no GitHub, sem divulgar segredos.
- Não tratar uma tentativa recente como base estável. Preservar a fonte da última versão aprovada e só promover candidato após confirmação real em Android.
- Após solicitação de alteração Android, o canal de entrega padrão é publicar o APK candidato **no VOC Lab**, nunca apenas entregar APK avulso, respeitando os requisitos técnicos.
- **Arquitetura exclusiva GitHub escolhida pelo proprietário:** documentação no repositório público; backups de chaves privadas somente criptografados antes de commit no repositório privado confirmado `vcaitanoo/voc-cofre` (estrutura preparada, backups não verificados); credenciais operacionais em GitHub Actions Secrets, sem acesso posterior ao valor. Nunca guardar valores confidenciais em texto puro em repos, arquivos, issues ou logs. Consultar [COFRE_VOC_GUIA.md](COFRE_VOC_GUIA.md).


## GPS 3D Auto — APK experimental isolado (03/11/2026)

- Estado: **teste técnico independente, NÃO é stable, não aprovado em carro Android Auto**.
- Repositório-fonte: [vcaitanoo/gps-3d](https://github.com/vcaitanoo/gps-3d); branch `feat/android-auto-test`, commit `e74c549f063c5ede23b7191c77089d1298ce88cf`; base GitHub `5f620b121335103d75d7a2c5097a44d99dd7e6e1`.
- Pacote **separado**: `pt.vcaitano.gps3d.auto`; `versionCode=1`, `versionName=0.1.0-auto-test`; app original `pt.vcaitano.gps3d` intocado.
- APK debug (9.496.946 bytes): https://github.com/vcaitanoo/gps-3d/releases/download/gps-3d-auto-test-v1-20261103/GPS-3D-Auto-0.1.0-vc1-debug.apk
- SHA-256 do APK: `c917572529ad48a9442c8a52a6ec5f2e71f7f291ebec706e40c214fda88c3ff2`.
- Certificado público debug SHA-256: `5a710c8048911525c477b13ed6055539d9a1cce9a38390f83004308b6f956af1`. **Chave privada temporária criada pelo runner do GitHub; sem backup verificável e sem GitHub Secret persistente.** Builds futuras não devem tentar atualizar este pacote com certificado diferente; instalar novamente depois de desinstalar, ou configurar uma chave persistente autorizada com backup criptografado no cofre.
- CI GitHub Actions: https://github.com/vcaitanoo/gps-3d/actions/runs/41727952664 — **SUCCESS**. Gradle `assembleDebug`, `aapt` package/version/CarAppService/NAVIGATION/ACCESS_SURFACE, DEX, `apksigner verify` e checksum SHA-256 confirmados.
- Integração: Android for Cars App Library 1.7.0, `NavigationTemplate`, `SurfaceCallback`, `VirtualDisplay` + `WebViewAssetLoader` apontando ao bundle GPS 3D; renderização 3D no carro, GPS, desempenho e navegação sincronizada **NÃO VERIFICADOS**.
- Distribuição Android Auto: instalação direta do APK no telefone pode não habilitar app de navegação na central. Para testar em veículo real, usar distribuição confiável da Google Play (Internal App Sharing / track interno), conforme política Android for Cars; **não afirmar que APK sideload é suficiente**.
- Fonte oficial GPS 3D e catálogos `lab/catalog.json` e `manifest.json` preservados. Nenhum AAB para Play criado. Último versionCode já submetido à Play para **este pacote novo**: NÃO VERIFICADO. Este APK nunca foi testado num Android físico nesta execução.


### GPS 3D Auto v0.2.0 / VC2 — teste isolado, 03/11/2026
- Pacote independente: `pt.vcaitano.gps3d.auto` (não substitui `pt.vcaitano.gps3d`).
- Fonte web do GPS 3D no `main` do repositório específico deriva do commit `87b1c92da2a3dbe4a6cc0d72760674fcc1cd68fc` da edição oficial. A comparação até `5f620b121335103d75d7a2c5097a44d99dd7e6e1` mostrou somente alterações de documentação e CI, sem alterar HTML, navegação ou modelos originais.
- Branch isolada de desenvolvimento `feat/android-auto-test`, commit V2 `ceb79c906794dc4705a9051f4cc9d38251be2352`. Implementação exclusivamente em arquivos novos sob `android-auto-test/` e workflows novos, preservando fontes principais, estável e candidato do VOC Lab.
- Diagnóstico da v0.1: a WebView Android Auto abria `/assets/public/index.html` mas o `WebViewAssetLoader` servia o Vite `/assets/index-*.js` a partir do caminho errado, impedindo inicializar o bridge do GPS e parte das camadas 3D. V2 corrige a tradução do caminho, habilita geolocalização na WebView, solicita permissão de localização no telefone e acrescenta sincronização **experimental** de rota entre a interface do telefone e o mapa na central.
- Apk v0.2.0 / versionCode 2 / 9.501.460 bytes; SHA256 `b2ec829557d27d1ed038870410df41f38e188cd4413e4430f40f7dbd622cbbc5`.
- Certificado debug v0.2.0 SHA-256 `bebb568460f41453f677475ca834c25833684003fab3ff0648f666a42e08e650`; diferente da v0.1 (depuração com keystore efêmero). **Desinstalar somente a v0.1 GPS 3D Auto antes de instalar a v0.2; não desinstalar a oficial.** Keystore não recuperável no fluxo debug do runner. Para futuras atualizações regulares, usar assinatura persistente com backup seguro devidamente autorizado.
- GitHub Actions `41734075387`: Gradle `assembleDebug` PASS; `aapt` manifest/package/versão/permissões/service, DEX, `apksigner verify`, recursos Vite/PMTiles/edifícios/igrejas/mercados/postos/scripts de sincronização e SHA-256 do APK PASS. Nenhuma execução Android real ou Android Auto comprovada; renderização/mapas, captação GPS no carro e sincronização efetiva ainda exigem testes físicos.
- Release privada: https://github.com/vcaitanoo/gps-3d/releases/tag/gps-3d-auto-test-v2-20261103
- **Download via Google Drive autenticado**, ZIP contendo exatamente o APK verificado e um arquivo `.sha256`: https://drive.google.com/file/d/1bV2P6V-DRX4k3icszyc7jFhwoHSZzFx-/view?usp=drivesdk . O APK extraído teve SHA-256 idêntico ao da compilação/release.
- Endereço alternativo no ChatGPT Library: `/VOC_LAB_Testes/GPS-3D-Auto-0.2.0-vc2-debug.apk`.
- Android Auto: teste em veículo pode requerer distribuição por trilha interna/compartilhamento interno da Play; APK instalado manualmente não garante exibição da categoria NAVIGATION na central. **Não publicar AAB**, promover stable ou alterar catálogo oficial sem validação e autorização. 
