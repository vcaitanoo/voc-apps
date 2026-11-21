# Divulgador Mobile — correção integrada VC5 / 0.1.4

## Origem e estado da base

- Base adotada: fonte candidata VC4 / 0.1.3 no repositório `vcaitanoo/voc-apps` da branch `main`, SHA Git de início `d42ebb1c34f11fa5384f2cd5e22f9556960aac37`.
- APK VC4 publicado: `apks/divulgador/candidate/Divulgador-Mobile-0.1.3-vc4.apk`.
- Package: `pt.vcaitano.divulgador`.
- Certificado VC4 SHA-256: `8229c3521273f75b900dec051b79ef5b678960b22735e13e12d0ff221959cd0a`.
- APK VC4 SHA-256: `9663a9528463e7c8785b95070b47226ed26221662b34b1308ea430602a932cfe`.
- O usuário instalou VC4, mas não confirmou todas as funções em teste físico; portanto, VC4 permanece candidata, não estável.

## Causa do defeito

- VC4 exportava CSV com `Email;Nome;Cidade;Idade` (delimitador `;`).
- O importador da mesma VC4 usava apenas delimitador `,`.
- O importador exigia simultaneamente cabeçalhos `Email` e `Consentimento`, coluna não criada pelo próprio gerador.
- Assim, arquivos gerados pela própria app não podiam ser carregados no divulgador.

## Alterações VC5

1. `GeneratorActivity.java`: ao exportar, chama codec único; novo botão `USAR NO DIVULGADOR` que grava CSV no cache privado e abre `SendActivity` com nome do arquivo, não transfere bytes em Intent.
2. `CsvFormat.java` (novo): exporta `Email;Nome;Cidade;Idade;Consentimento`, separador ponto e vírgula compatível com Excel PT, UTF-8 BOM, escape de campos, consentimento `nao` para contatos sintéticos; importa arquivos separados por `;`, `,` ou TAB, com aspas e campo multilinha.
3. `SendActivity.java`: aceita CSV com `Email` obrigatória, coluna `Consentimento` opcional, importa sem consentimento para a preparação da campanha, aplica autorização positiva apenas para envio real, exibe contagens/prévia, lê arquivo gerado automaticamente, mantém compatibilidade com contatos autorizados previamente salvos na VC4.
4. `MainActivity.kt`: novo atalho `IMPORTAR CSV E CONFIGURAR` que abre o selecionador de CSV dentro da tela de composição.
5. `app/build.gradle.kts`: apenas `versionCode=5` / `versionName=0.1.4`.
6. `csv-tests/CsvFormatTest.java`: testes de ida-e-volta, 5 colunas, separadores `;`, `,`, TAB, BOM, aspas, campos multilinha e ausência de consentimento fictício.
7. `.github/workflows/test-divulgador-vc5-csv-integrado.yml`: testes e compilação Gradle de APK DEBUG; **não publica no VOC Lab** antes da recuperação de assinatura compatível.

As demais funções de campanhas e as integrações do backend permanecem sem alteração no código-fonte.

## Assinaturas e publicação

**Bloqueio de segurança:** a VC4 instalada usa certificado com SHA-256 `8229c3521273f75b900dec051b79ef5b678960b22735e13e12d0ff221959cd0a` gerado pelo runner temporário. O workflow VC4 anterior não preservou a chave privada. O APK assinado não permite recuperar a chave privada.

A chave existente no Supabase Vault, com certificado `918b566590b49f691ec9880c95dd174a6c032b21f81dc66efcfac74d0de11aa8`, é da linha histórica VOC e **não assina atualizações por cima da VC4**.

Por isso, não publicar APK VC5 assinado com chave diferente como atualização; causaria `INSTALL_FAILED_UPDATE_INCOMPATIBLE`.

**Possibilidades válidas:**
- Recuperar o keystore privado exato da VC4, se existir backup, confirmar fingerprint e armazenar em GitHub Actions Secrets; então compilar e atualizar sem reinstalar.
- Se a chave privada VC4 não existir, estabelecer chave permanente, backup criptografado e pipeline reproduzível; **uma migração para essa identidade de assinatura é inevitável** (reinstalação ou pacote Android distinto). Depois, novas atualizações podem preservar os dados.

**Não declarar instalação/abertura validada no Android** antes do teste em dispositivo ou emulador real.
