# Divulgador Mobile — VC8 0.1.7 — Painel de Envios

## Base preservada
- Fonte anterior: `main` Git SHA `429de1ffff800f70ab2b4568c0835b1e45c69509`, derivada da VC7 candidata
- Package: `pt.vcaitano.divulgadormobile`
- Base APK: VC7 0.1.6, versionCode 7, SHA-256 `9460dc644e9680a4a17414a37923f4ff427090b271b234893bfc3567436d5fac`
- Certificado de release obrigatório SHA-256: `b159a98ffef27e280b29af85de8ec1a3ddf60898acc58d8d7d1fb1e1b1391006`
- Não instalar/debug ou modificar binários: usar fonte Gradle e assinatura original
- Usuário confirmou abrir a tela em Android real e mostrou foto, mas **não** confirmou envio Gmail

## Diagnóstico a partir da captura enviada em 21/11/2026
- Mensagem visível: `Sem destinatários autorizados para envio. E-mails gerados fictícios não ...`
- 1.953 contatos marcados `sem consentimento`, 0 colocados na fila, 0 enviados, 0 falhas
- A aplicação intencionalmente não manda e-mails para registros sem autorização, especialmente endereços sintéticos gerados para testes
- Não alterar nem inventar consentimento para permitir envio

## Mudanças pedidas
- `SendActivity.java`: incluir no **topo** do editor um painel com `Importados`, `Autorizados`, `Sem consentimento`, `Na fila`, `Enviados`, `Falhas`, barra percentual de envios concluídos, `Incerto`, `Bloqueados`, `Automático ativo/pausado` e avisos explicando fila vazia/falha
- Atualização automática do painel a cada 5 segundos enquanto o editor está em primeiro plano
- `app/build.gradle.kts`: alterar somente `versionCode=8` e `versionName=0.1.7`
- `.github/workflows/test-divulgador-mobile-vc8-dashboard.yml`: validação de código-fonte, CSV e APK estrutural
- Fluxos de contas Gmail, SMTP, campanhas, consentimento, fotos, geração CSV, fila SQLite e WorkManager permanecem sem alterações

## Regras de entrega
1. Compilar debug e release sem assinatura com Gradle
2. Verificar package, versão, manifesto, DEX e recursos
3. Assinar release com a **mesma chave** da VC7/VC6; verificar SHA-256 do certificado
4. Publicar APK no VOC Lab como **candidato** somente após verificações
5. Não relatar `envio Gmail real testado` sem teste efetivo com contas Google
6. Não promover a versão a estável antes da confirmação do usuário
