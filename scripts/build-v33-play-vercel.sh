#!/usr/bin/env bash
set -euo pipefail
ROOT="$PWD"
WORK="$ROOT/.tsa-play-work"
SRC="$WORK/src"
OUT="$ROOT/lab/builds/tela-sempre-ativa/v33-restored-play"
TOOLS="$WORK/tools"
rm -rf "$WORK" "$OUT"
mkdir -p "$SRC" "$OUT" "$TOOLS"

# 1) JDK 17
curl -fL --retry 3 --retry-delay 2 'https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse' -o "$WORK/jdk17.tar.gz"
mkdir -p "$TOOLS/jdk17-unpack"
tar -xzf "$WORK/jdk17.tar.gz" -C "$TOOLS/jdk17-unpack"
JDIR="$(find "$TOOLS/jdk17-unpack" -mindepth 1 -maxdepth 1 -type d | head -n1)"
export JAVA_HOME="$JDIR"
export PATH="$JAVA_HOME/bin:$PATH"
java -version

# 2) Android SDK 36
export ANDROID_HOME="$TOOLS/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
mkdir -p "$ANDROID_HOME/cmdline-tools"
curl -fL --retry 3 --retry-delay 2 'https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip' -o "$WORK/cmdtools.zip"
unzip -q "$WORK/cmdtools.zip" -d "$WORK/cmdtools"
mkdir -p "$ANDROID_HOME/cmdline-tools/latest"
cp -a "$WORK/cmdtools/cmdline-tools/." "$ANDROID_HOME/cmdline-tools/latest/"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
yes | sdkmanager --licenses >/dev/null 2>&1 || true
sdkmanager 'platforms;android-36' 'build-tools;36.0.0' 'platform-tools'

# 3) Restore verified V29 checkpoint
curl -fL --retry 3 --retry-delay 2 'https://drive.usercontent.google.com/download?id=1qMKPWJ9RLcmcfAUhZVLV_GVXGusuCIAH&export=download&confirm=t' -o "$WORK/base.tar.xz"
echo '40469bae71d6667e731816cc5624f20c96031bf277f4ccb6eacae0c959d45f0f  '"$WORK/base.tar.xz" | sha256sum -c -
tar -xJf "$WORK/base.tar.xz" -C "$SRC"
chmod +x "$SRC/gradlew"

# 4) Reapply the exact documented V33 source delta recovered from the final V33 line
printf '%s' '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' | base64 -d | gzip -dc > "$WORK/v33.patch"
echo '9dd7534e10e2d1b6236c0b0302142292ee34382f199c2eda7e32f549e5d07dee  '"$WORK/v33.patch" | sha256sum -c -
cd "$SRC"
git apply "$WORK/v33.patch"

# Verify V33 code tree before changing only release metadata
echo '58aadb2be1199669ceb1982fe3e2d910b12fd5b292b7d5bddef68afeeed5f1c3  app/build.gradle' | sha256sum -c -
echo 'c8b50379d4d6d6e00d723631c0047483c98239915dd9cea8e1dc3ef6a6911404  app/src/main/java/pt/vcaitano/telasempreativa/AodActivity.java' | sha256sum -c -
echo 'c440b8fddb2045ecba621ba458e9a891a6fdaafe3ee2531c52b43b34c0c72279  app/src/main/java/pt/vcaitano/telasempreativa/MediaNotificationService.java' | sha256sum -c -
grep -q "applicationId 'pt.vcaitano.telasempreativa'" app/build.gradle
grep -q 'versionCode 33' app/build.gradle
grep -q "versionName '1.0.27-test'" app/build.gradle
grep -q 'setOnLongClickListener' app/src/main/java/pt/vcaitano/telasempreativa/AodActivity.java
grep -q 'performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)' app/src/main/java/pt/vcaitano/telasempreativa/AodActivity.java
grep -q 'requestDismissKeyguard' app/src/main/java/pt/vcaitano/telasempreativa/AodActivity.java
grep -q 'getLaunchIntentForPackage' app/src/main/java/pt/vcaitano/telasempreativa/MediaNotificationService.java

# 5) ONLY requested Play metadata change
python3 - <<'PY2'
from pathlib import Path
p=Path('app/build.gradle')
s=p.read_text()
s2=s.replace('versionCode 33','versionCode 20260901',1).replace("versionName '1.0.27-test'","versionName '1.0.28'",1)
if s2==s: raise SystemExit('version metadata replacement failed')
p.write_text(s2)
PY2
grep -nE 'applicationId|versionCode|versionName' app/build.gradle

# Record exact final source before any build output exists
FINAL_SOURCE_SHA="$(find . -type f -not -path './.gradle/*' -not -path './app/build/*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}')"

# 6) APK FIRST from final source
./gradlew clean assembleRelease --no-daemon --stacktrace
APK_UNSIGNED="$(find app/build/outputs/apk/release -type f -name '*.apk' | head -n1)"
test -s "$APK_UNSIGNED"

# 7) Same historical signing key; credentials read from user's Drive file, never stored here
KEY="$WORK/tela_sempre_ativa_v1.jks"
README="$WORK/signing-readme.txt"
curl -fL --retry 3 --retry-delay 2 'https://drive.usercontent.google.com/download?id=1TfGb0ofAVWupoDZwiAwFIdGuaGVivKWI&export=download&confirm=t' -o "$KEY"
curl -fL --retry 3 --retry-delay 2 'https://drive.usercontent.google.com/download?id=1EIaAAdAkzu78VUtYS3cJttY_IfxDQtdN&export=download&confirm=t' -o "$README"
echo 'c2fbe75c95dec92e3612c9a186dfa654ed0427aa9aeac2ea2caa4b1de749ab03  '"$KEY" | sha256sum -c -
PASS="$(sed -n 's/^Senha do ficheiro: //p' "$README" | head -n1 | sed 's/[[:space:]]*$//')"
KEYPASS="$(sed -n 's/^Senha da chave: //p' "$README" | head -n1 | sed 's/[[:space:]]*$//')"
test -n "$PASS" && test -n "$KEYPASS"
export PASS KEYPASS
keytool -list -v -keystore "$KEY" -alias telaativa -storepass:env PASS > "$WORK/keyinfo.txt"
CERT="$(sed -n 's/.*SHA256: //p' "$WORK/keyinfo.txt" | head -n1 | tr -d ':' | tr '[:upper:]' '[:lower:]')"
test "$CERT" = 'f3e732553e25bb86bc5ca7c2aa5a0a6f9f9e798d9def964338a744f399b01d3a'

BT="$ANDROID_HOME/build-tools/36.0.0"
"$BT/zipalign" -p -f 4 "$APK_UNSIGNED" "$WORK/aligned.apk"
APK="$OUT/TelaSempreAtiva_V33_RESTAURADA_v1.0.28_vc20260901.apk"
"$BT/apksigner" sign --ks "$KEY" --ks-key-alias telaativa --ks-pass env:PASS --key-pass env:KEYPASS --out "$APK" "$WORK/aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$APK" | tee "$OUT/APK_ASSINATURA.txt"
"$BT/aapt" dump badging "$APK" | tee "$OUT/APK_BADGING.txt"
grep -q "package: name='pt.vcaitano.telasempreativa' versionCode='20260901' versionName='1.0.28'" "$OUT/APK_BADGING.txt"
grep -q 'Signer #1 certificate SHA-256 digest: f3e732553e25bb86bc5ca7c2aa5a0a6f9f9e798d9def964338a744f399b01d3a' "$OUT/APK_ASSINATURA.txt"
unzip -l "$APK" | grep -q 'AndroidManifest.xml'
unzip -l "$APK" | grep -q 'classes.dex'
unzip -l "$APK" | grep -q 'resources.arsc'

# 8) Only after APK structural validation, build AAB from EXACT same final source
./gradlew bundleRelease --no-daemon --stacktrace
AAB_UNSIGNED="$(find app/build/outputs/bundle/release -type f -name '*.aab' | head -n1)"
test -s "$AAB_UNSIGNED"
AAB="$OUT/TelaSempreAtiva_V33_RESTAURADA_v1.0.28_vc20260901.aab"
jarsigner -keystore "$KEY" -storepass:env PASS -keypass:env KEYPASS -signedjar "$AAB" "$AAB_UNSIGNED" telaativa
jarsigner -verify -verbose -certs "$AAB" > "$OUT/AAB_ASSINATURA.txt"
grep -q 'jar verified.' "$OUT/AAB_ASSINATURA.txt"
unzip -l "$AAB" > "$OUT/AAB_CONTEUDO.txt"
grep -q 'base/manifest/AndroidManifest.xml' "$OUT/AAB_CONTEUDO.txt"
grep -q 'base/dex/classes.dex' "$OUT/AAB_CONTEUDO.txt"
grep -q 'base/resources.pb' "$OUT/AAB_CONTEUDO.txt"

# 9) Continuity package from exact same final source
cat > RECUPERACAO_PLAY_V33.txt <<EOF
TELA SEMPRE ATIVA — V33 RESTAURADA PARA GOOGLE PLAY
Base comportamental: V33 recuperada do VOC Lab
Base V29 checkpoint SHA-256: 40469bae71d6667e731816cc5624f20c96031bf277f4ccb6eacae0c959d45f0f
V33 delta SHA-256: 9dd7534e10e2d1b6236c0b0302142292ee34382f199c2eda7e32f549e5d07dee
packageName: pt.vcaitano.telasempreativa
versionCode: 20260901
versionName: 1.0.28
certificado SHA-256: f3e732553e25bb86bc5ca7c2aa5a0a6f9f9e798d9def964338a744f399b01d3a
Código do popup preservado da V33 recuperada; apenas app/build.gradle teve versionCode/versionName alterados para esta release.
Final source tree SHA-256: $FINAL_SOURCE_SHA
Validação: compilação e estrutura verificadas. Execução em Android real NÃO testada por este build remoto.
EOF
zip -qr "$OUT/TelaSempreAtiva_V33_RESTAURADA_FONTE_vc20260901.zip" . -x '.gradle/*' 'app/build/*' 'build/*'

APK_SHA="$(sha256sum "$APK" | awk '{print $1}')"
AAB_SHA="$(sha256sum "$AAB" | awk '{print $1}')"
SRC_ZIP_SHA="$(sha256sum "$OUT/TelaSempreAtiva_V33_RESTAURADA_FONTE_vc20260901.zip" | awk '{print $1}')"
cat > "$OUT/VALIDACAO_V33_PLAY.txt" <<EOF
TELA SEMPRE ATIVA — V33 RESTAURADA PARA GOOGLE PLAY
packageName: pt.vcaitano.telasempreativa
versionCode: 20260901
versionName: 1.0.28
Fonte recuperada original ZIP SHA-256: 39db11b13405c7326c3355e1b3355f84a131cae515d4ec0f19c98117053542a1
Base V29 checkpoint SHA-256: 40469bae71d6667e731816cc5624f20c96031bf277f4ccb6eacae0c959d45f0f
V33 delta SHA-256: 9dd7534e10e2d1b6236c0b0302142292ee34382f199c2eda7e32f549e5d07dee
Final source tree SHA-256: $FINAL_SOURCE_SHA
Certificado SHA-256: $CERT
APK SHA-256: $APK_SHA
AAB SHA-256: $AAB_SHA
Fonte final ZIP SHA-256: $SRC_ZIP_SHA
Ficheiro de código alterado para Play: app/build.gradle (somente versionCode/versionName)
AodActivity.java: preservado exatamente da V33 recuperada
MediaNotificationService.java: preservado exatamente da V33 recuperada
APK: compilado, assinado e validado estruturalmente antes do AAB
AAB: gerado da mesma fonte final, assinado e validado estruturalmente
Execução em Android real/emulador: NÃO TESTADA neste build remoto
EOF
sha256sum "$APK" "$AAB" "$OUT/TelaSempreAtiva_V33_RESTAURADA_FONTE_vc20260901.zip" > "$OUT/SHA256SUMS.txt"

# Keep output directory clean; no source secrets included
rm -rf "$WORK"
