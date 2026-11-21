# Divulgador Mobile VC9 (0.1.8) — simulação de campanha

## Base verificada
- Repositório `vcaitanoo/voc-apps`, fonte `main` inicial `d9ac26970774d01e3b54899605c28cfe029338f2`.
- Pacote imutável: `pt.vcaitano.divulgadormobile`.
- Candidato instalado pelo usuário: VC8 (0.1.7), `versionCode 8`, SHA-256 `18dc17baedf0df88d9d259fcdb4e8aa37c8f79d95bc3e2685a057283645c1969`.
- Assinatura de distribuição VC6-VC8, SHA-256 do certificado: `b159a98ffef27e280b29af85de8ec1a3ddf60898acc58d8d7d1fb1e1b1391006`. Não gerar outra chave.
- Não há confirmação de envio real de emails pelo usuário, portanto não tornar a VC8 estável só com compilação.

## Diagnóstico do caso concreto
- Captura de 2026-11-21: 2.847 registros importados, 0 autorizados, 2.847 sem consentimento, 0 envios. Toast: sem destinatários autorizados.
- O gerador inventa identificadores de endereço com `@gmail.com` e outros domínios existentes. Algumas combinações podem ser caixas reais; não existe verificação de propriedade nem autorização.
- A fila real corretamente recusa entradas sem consentimento. Não habilitar envio massivo não solicitado.

## Alterações restritas VC9
- `CampaignSimulation.java` (novo): processa a lista importada/gerada **localmente, sem rede, Gmail ou SMTP**, com barra percentual e contadores de processados, pendentes e duplicados. Pausa, continua e fecha. Não toca na fila real, banco ou dados de autorização.
- `SendActivity.java`: botão `TESTAR LISTA GERADA (SIMULAÇÃO SEM ENVIO)` junto da importação e orientação clara; mantém toda a lógica de envio real, gerador, fotos e dashboard VC8 intacta.
- `app/build.gradle.kts`: somente VC9 (versionCode 9 / versionName 0.1.8).
- `.github/workflows/test-divulgador-mobile-vc9-simulacao.yml`: confere ausência de APIs de disparo na simulação, restaura teste de CSV e compila com Gradle.

## Implantação
- Assinar a release gerada do mesmo código-fonte VC9 com o keystore PKCS12 original, recuperado do backup criptografado autorizado pela conta, sem expor chave/senha em GitHub.
- Verificar fingerprint, package, versionCode, versionName, DEX, manifesto e recursos antes de oferecer update.
- Publicar no VOC Lab somente como candidata; não desinstalar VC8 e não afirmar Android real testado.
- O objetivo da simulação é testar interface/percurso e contadores. Não representa entrega real de e-mail.
