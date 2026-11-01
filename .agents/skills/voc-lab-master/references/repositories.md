# Repositórios, responsabilidade e leitura contextual

- Hub VOC: `https://github.com/vcaitanoo/voc-apps` (repositório de catálogo e parte dos projetos). O `AGENTS.md` existente é a regra de repositório: **nunca sobrescrever** com esta skill.
- Lab Android: `lab/` (`pt.vcaitano.voclab`). Catálogo de teste: `lab/catalog.json` (`stable`, `candidate`). O front-end pode estar em `docs/voc-lab/`; verificar deploy real.
- Manager Android: `manager/` (`pt.vcaitano.vocmanager`). Catálogo oficial distinto: `manifest.json`.
- GPS 3D: `https://github.com/vcaitanoo/gps-3d` com fonte própria (`android-app/` e recursos web). Não presumir que o commit `main` seja a fonte do último APK testado.
- Outros apps registrados no catálogo do Lab podem incluir Damas, Jarvis, Tela Sempre Ativa e VOC TV. Ler a lista atual em vez de fixar IDs/versões deste documento.
- Projetos adicionais (Ache Aqui etc.) devem ser descobertos no repo correto. Nunca adicioná-los ao Lab por suposição.

**Divergências conhecidas na documentação:** o histórico de `lab/CONTINUAR_AQUI.md` pode estar atrasado em relação a `lab/catalog.json` e ao feedback mais recente do usuário. `docs/VOC_LAB_WORKFLOW.md` avisa que o app Lab, workflow CI e deploy podem divergir. Resolver antes de publicar, sem promover candidate implicitamente.

**Política de versões:** os hashes/versionCodes apresentados em documentação antiga são snapshots e não devem ser copiados como dados atuais. Consultar catálogo, base de código e histórico de Play Console na tarefa concreta. Referir o usuário e a evidência de teste Android quando uma versão foi aprovada.
