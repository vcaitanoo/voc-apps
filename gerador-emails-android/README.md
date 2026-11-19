# Gerador de E-mails — Android

Aplicativo nativo, offline, que exporta dados sintéticos no formato CSV (`Nome,Email,Cidade,Idade`, UTF-8 com BOM).

- Modos: Gmail Brasil, Gmail Portugal, iCloud / Me / Mac, misto, domínio personalizado.
- Quantidade: 1 a 100.000, idades entre 0 e 120, seed opcional, exclusão de duplicações por arquivo.
- CSV salvo pelo seletor de arquivos do Android, sem permissão de armazenamento.
- Nenhuma permissão de Internet, contatos ou envio de e-mails.
- Os endereços são fictícios e podem coincidir com contas reais. Não são validados.

**Identificação:** `pt.vcaitano.geradoremail`; versionCode `1`; versionName `1.0.0`.

**Compilação:** Java 17, Gradle 8.10.2, Android Gradle Plugin 8.7.3, SDK 35. Executar `gradle :app:assembleDebug` na pasta deste projeto.

**Assinatura:** o APK de debug é assinado com certificado de depuração do ambiente de build. Não é uma assinatura de produção nem uma continuidade de app existente.

**Validação:** a compilação e a inspeção estrutural em CI não equivalem a testar a abertura no Android real.
