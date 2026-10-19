# Inventário público do VOC Lab

Snapshot de identificação do catálogo em 2026-10-19. Use lab/catalog.json como fonte de verdade dos releases: este inventário evita duplicar URLs, hashes e metadados de versão.

## App VOC Lab

- Nome: VOC Lab.
- Package: pt.vcaitano.voclab.
- Fonte deste app: lab/ no repositório vcaitanoo/voc-apps.
- Catálogo de outros apps: lab/catalog.json.

## Apps presentes no catálogo do Lab

| ID | Nome | Package |
| --- | --- | --- |
| tela-sempre-ativa | Tela Sempre Ativa | pt.vcaitano.telasempreativa |
| voc-manager | VOC Manager | pt.vcaitano.vocmanager |
| voc-tv | VOC TV | pt.vcaitano.iptvia |
| damas | Damas | pt.vcaitano.damas |
| jarvis | Jarvis | pt.vcaitano.jarvis |
| gps-3d | GPS-3D | pt.vcaitano.gps3d |

lab/catalog.json contém as versões stable/candidate e metadados dos artefatos. Confirme os valores atuais antes de compilar ou publicar.

A fonte de cada app é independente. O catálogo não guarda sourceCommit. Confirme o repositório e a branch autorizados no início de uma tarefa, e associe o APK ao commit real que produziu a build.

Ache Aqui não aparece no catálogo observado. Não o adicione até confirmar a fonte Android, package, assinatura, versão e destino de publicação.
