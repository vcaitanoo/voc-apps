# VOC Trader Vision — assinatura permanente, referência canônica

**Package imutável:** `pt.vcaitano.tradervision.gestaoteste`.
**Primeira versão com assinatura permanente:** `0.3.0-demo` / `versionCode=3`.
**Certificado SHA-256 fixo:** `e52d1c13baa3a4e7f73b71cb7e15bc1fdd8709650aa64fe8a9b86bb26a5491f9`.
**Commit exato do código que gerou o APK:** `4425d13b64cf67c2b7c74afb215edbb627a2cb5d`.
**APK SHA-256:** `18d0c7f5ae76595bf2fe248c6a664807cf735b75991e0ac1969e101056a21f88`.
**APK:** `apks/voc-trader-vision-gestao-teste/candidate/VOC-Trader-Vision-0.3.0-demo-VC3.apk`.

## Backup e recuperação

O material de assinatura Android é uma keystore PKCS#12 gerada no GitHub Actions (run `41925752844`). Não foi escrito em claro no repositório, nem exposto em logs.

O backup cifrado com **RSA-OAEP-SHA256 + AES-256-GCM** foi validado no build e preservado no GitHub privado `vcaitanoo/voc-cofre`, caminho:

- `projetos/voc-trader-vision/keystore-vc3-permanent.encrypted.json`
- `projetos/voc-trader-vision/recovery-private-encrypted.pem` (chave de recuperação **também** cifrada sob senha do proprietário)

A chave pública de cifra é `trader-vision/security/recovery-public.pem` e pode ser divulgada. Nenhuma senha foi armazenada no GitHub. O proprietário recebeu um **kit de recuperação privado** contendo a frase-senha e a chave RSA cifrada; guardar offline. Sem essa senha/kit, não é possível prometer recuperação da keystore.

Para restaurar:

```bash
python3 -m pip install cryptography
python3 trader-vision/scripts/recover_signer.py \
  --backup keystore-vc3-permanent.encrypted.json \
  --private recovery-private-encrypted.pem \
  --output-dir ./secure-signer
```

A rotina valida o certificado contra o SHA-256 **PINNED_CERT** antes de declarar êxito.
**Nunca** enviar a senha para os logs, para o chat, para o repositório ou escrever texto puro da chave no Git. Após uso, apagar os arquivos locais decriptados.

No build futuro, configure `VOC_TRADER_KEYSTORE_FILE`, `VOC_TRADER_STORE_PASS`, `VOC_TRADER_KEY_PASS` no ambiente seguro que executará `gradle -p trader-vision clean :app:assembleRelease`. A configuração Gradle assina automaticamente com a identidade recuperada. Conferir com `apksigner verify --print-certs` e comparar com o certificado acima antes de distribuir. **Jamais gerar nova chave para futuras atualizações**.

## Distribuição e homologação

- No VOC Lab só existe a entrada `voc-trader-vision-gestao-teste` com o nome `VOC Trader Vision`, candidato VC3. Nenhuma stable foi promovida.
- A VC2 instalada usava **OUTRO certificado** `3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`. É indispensável uma **única desinstalação** da VC2 antes de instalar VC3; dados locais podem ser apagados.
- Não mudar `applicationId`, catálogo ID, certificado nem assinatura em futuras versões. Aumentar versionCode, publicar apenas em `candidate`, manter outras apps intactas.
- Validação atual: testes JDK, compilação Gradle, manifest/resources/DEX, assinatura, SHA-256 remoto e upload HTTPS aprovados no run `41925752844`. **Execução Android real e eficácia de sinais são NÃO TESTADAS**.
