#!/usr/bin/env bash
set -euo pipefail

ROOT="$PWD"
BUILD_ROOT="$ROOT/.jarvis-build-vc26"
TMP="$BUILD_ROOT/tmp"
SOURCE="$BUILD_ROOT/source"
SDK="$BUILD_ROOT/android-sdk"
OUT="$ROOT/dist"
ENDPOINT='https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-build-oidc'
APK_NAME='Jarvis-0.3.1-vc26.apk'

test -n "${VERCEL_OIDC_TOKEN:-}" || {
  echo 'VERCEL_OIDC_TOKEN não está disponível neste build.' >&2
  exit 1
}

rm -rf "$BUILD_ROOT"
mkdir -p "$TMP" "$SDK/platforms" "$SDK/build-tools" "$SDK/licenses" "$SOURCE" "$OUT"
rm -f "$OUT/$APK_NAME" "$OUT/Jarvis-0.3.1-vc26.sha256.txt" "$OUT/build-info.json" "$OUT/catalog.json" "$OUT/manifest.json"
cp "$ROOT/lab/catalog.json" "$OUT/catalog.json"
cp "$ROOT/manifest.json" "$OUT/manifest.json"
python3 -m json.tool "$OUT/catalog.json" >/dev/null
python3 -m json.tool "$OUT/manifest.json" >/dev/null

echo '[1/10] Reconstruindo a fonte canônica VC25 e aplicando somente a correção VC26...'
cat lab/sources/jarvis/candidate/0.2.15/source.part.* > "$TMP/source.b64"
base64 -d "$TMP/source.b64" > "$TMP/source.zip"
echo '1370f787b2488ef3ccaf5c20ec88ccf2b96442c51407a308e5304fe8a9ae2f55  '"$TMP/source.zip" | sha256sum -c -
unzip -q "$TMP/source.zip" -d "$SOURCE"
cp lab/sources/jarvis/candidate/0.2.15/overrides/VoicePrint.kt "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"

ln -s "$SOURCE" "$ROOT/jarvis0215"
cleanup() { rm -f "$ROOT/jarvis0215"; }
trap cleanup EXIT
python3 lab/sources/jarvis/candidate/0.2.16/apply_vc18.py
python3 lab/sources/jarvis/candidate/0.2.17/apply_vc19.py
python3 lab/sources/jarvis/candidate/0.2.18/apply_vc20.py
python3 lab/sources/jarvis/candidate/0.2.19/apply_vc21.py
python3 lab/sources/jarvis/candidate/0.2.21/apply_vc22_voice_repair.py
python3 lab/sources/jarvis/candidate/0.2.21/apply_vc23.py
python3 lab/sources/jarvis/candidate/0.2.22/apply_vc24.py
python3 lab/sources/jarvis/candidate/0.3.0/apply_vc25.py
python3 lab/sources/jarvis/candidate/0.3.1/apply_vc26.py

echo '[2/10] Validando identidade e escopo estrito da VC26...'
grep -q 'applicationId = "pt.vcaitano.jarvis"' "$SOURCE/app/build.gradle.kts"
grep -q 'versionCode = 26' "$SOURCE/app/build.gradle.kts"
grep -q 'versionName = "0.3.1"' "$SOURCE/app/build.gradle.kts"
grep -q 'val selected = male' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'if (recognitionSystemVolumeBefore != null) return' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
if grep -q 'managedByListeningService || recognitionSystemVolumeBefore != null' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo 'VALIDATION_FAILED: serviço de fundo ainda excluído da supressão de bip' >&2
  exit 1
fi
if grep -q 'if (!managedByListeningService) silenceRecognitionTones()' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo 'VALIDATION_FAILED: startRecognition ainda exclui o serviço de fundo' >&2
  exit 1
fi
grep -q 'interface AiProvider' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/agent/ai/AiProvider.kt"
grep -q 'interface MemoryRepository' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/agent/memory/MemoryRepository.kt"
grep -q 'WakeWordDetector' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'ReminderBootReceiver' "$SOURCE/app/src/main/AndroidManifest.xml"
grep -q 'android:icon="@mipmap/ic_launcher"' "$SOURCE/app/src/main/AndroidManifest.xml"

echo '[3/10] Preparando Java 17...'
if command -v java >/dev/null 2>&1 && java -version 2>&1 | grep -Eq 'version "(17|18|19|20|21)'; then
  JAVA_BIN="$(dirname "$(readlink -f "$(command -v java)")")"
  export JAVA_HOME="$(dirname "$JAVA_BIN")"
else
  curl -fL --retry 4 --retry-all-errors 'https://api.adoptium.net/v3/binary/latest/17/ga/linux/x64/jdk/hotspot/normal/eclipse' -o "$TMP/jdk17.tar.gz"
  mkdir -p "$TMP/jdk"
  tar -xzf "$TMP/jdk17.tar.gz" -C "$TMP/jdk" --strip-components=1
  export JAVA_HOME="$TMP/jdk"
fi
export PATH="$JAVA_HOME/bin:$PATH"
java -version

echo '[4/10] Preparando Gradle 9.5.1 oficial...'
if command -v gradle >/dev/null 2>&1 && gradle --version | grep -q 'Gradle 9.5.1'; then
  GRADLE_BIN="$(command -v gradle)"
else
  curl -fL --retry 4 --retry-all-errors 'https://downloads.gradle.org/distributions/gradle-9.5.1-bin.zip' -o "$TMP/gradle.zip"
  echo 'bafc141b619ad6350fd975fc903156dd5c151998cc8b058e8c1044ab5f7b031f  '"$TMP/gradle.zip" | sha256sum -c -
  unzip -q "$TMP/gradle.zip" -d "$TMP"
  GRADLE_BIN="$TMP/gradle-9.5.1/bin/gradle"
fi

echo '[5/10] Preparando Android SDK 37...'
curl -fL --retry 4 --retry-all-errors 'https://dl.google.com/android/repository/platform-37.0_r02.zip' -o "$TMP/platform37.zip"
mkdir -p "$TMP/platform37"
unzip -q "$TMP/platform37.zip" -d "$TMP/platform37"
PDIR="$(find "$TMP/platform37" -type f -name android.jar -printf '%h\n' | head -n1)"
mkdir -p "$SDK/platforms/android-37"
cp -a "$PDIR/." "$SDK/platforms/android-37/"
curl -fL --retry 4 --retry-all-errors 'https://dl.google.com/android/repository/build-tools_r37_linux.zip' -o "$TMP/bt37.zip"
mkdir -p "$TMP/bt37"
unzip -q "$TMP/bt37.zip" -d "$TMP/bt37"
BDIR="$(find "$TMP/bt37" -type f \( -name aapt -o -name aapt2 \) -printf '%h\n' | head -n1)"
mkdir -p "$SDK/build-tools/37.0.0"
cp -a "$BDIR/." "$SDK/build-tools/37.0.0/"
printf '%s\n' 8933bad161af4178b1185d1a37fbf41ea5269c55 d56f5187479451eabf01fb78af6dfcb131a6481e 24333f8a63b6825ea9c5514f83c2829b004d1fee > "$SDK/licenses/android-sdk-license"
export ANDROID_HOME="$SDK" ANDROID_SDK_ROOT="$SDK"
printf 'sdk.dir=%s\n' "$SDK" > "$SOURCE/local.properties"

echo '[6/10] Obtendo a assinatura histórica por OIDC efêmero...'
curl -fsSL --retry 4 --retry-all-errors \
  -H "Authorization: Bearer $VERCEL_OIDC_TOKEN" \
  -H 'x-action: signing' \
  "$ENDPOINT" -o "$TMP/signing.json"
python3 - "$TMP/signing.json" "$TMP" <<'PY'
import base64, json, pathlib, shlex, sys
p = pathlib.Path(sys.argv[1])
tmp = pathlib.Path(sys.argv[2])
data = json.loads(p.read_text())
if isinstance(data, list): data = data[0]
if isinstance(data, dict) and isinstance(data.get("result"), dict): data = data["result"]
for key in ("keystoreB64", "password", "alias"):
    if not isinstance(data, dict) or not data.get(key): raise SystemExit("missing signing field " + key)
(tmp / "jarvis-release.jks").write_bytes(base64.b64decode(data["keystoreB64"]))
(tmp / "signing.env").write_text(
    "export JARVIS_STORE_PASSWORD=" + shlex.quote(str(data["password"])) + "\n"
    "export JARVIS_KEY_PASSWORD=" + shlex.quote(str(data["password"])) + "\n"
    "export JARVIS_KEY_ALIAS=" + shlex.quote(str(data["alias"])) + "\n"
    "export JARVIS_KEYSTORE_PATH=" + shlex.quote(str(tmp / "jarvis-release.jks")) + "\n"
)
PY
source "$TMP/signing.env"
rm -f "$TMP/signing.json" "$TMP/signing.env"
echo '0f642fb4658dd2b3989b2208aeb88479e9bd5a35dca913d6da9cee3e8079a9bc  '"$TMP/jarvis-release.jks" | sha256sum -c -

echo '[7/10] Executando testes unitários e compilando SOMENTE o APK release...'
cd "$SOURCE"
"$GRADLE_BIN" --no-daemon :app:testDebugUnitTest :app:assembleRelease --stacktrace
cd "$ROOT"
cp "$SOURCE/app/build/outputs/apk/release/app-release.apk" "$OUT/$APK_NAME"

echo '[8/10] Validando APK: package, versão, DEX, recursos e assinatura...'
"$SDK/build-tools/37.0.0/aapt" dump badging "$OUT/$APK_NAME" > "$TMP/badging.txt"
"$SDK/build-tools/37.0.0/aapt" dump resources "$OUT/$APK_NAME" > "$TMP/resources.txt"
"$SDK/build-tools/37.0.0/apksigner" verify --verbose --print-certs "$OUT/$APK_NAME" > "$TMP/apksigner.txt"
require_fixed() {
  local pattern="$1" file="$2" label="$3"
  if ! grep -Fq "$pattern" "$file"; then echo "VALIDATION_FAILED: $label" >&2; exit 1; fi
  echo "VALIDATION_OK: $label"
}
require_fixed_ci() {
  local pattern="$1" file="$2" label="$3"
  if ! grep -Fiq "$pattern" "$file"; then echo "VALIDATION_FAILED: $label" >&2; exit 1; fi
  echo "VALIDATION_OK: $label"
}
require_fixed "name='pt.vcaitano.jarvis' versionCode='26' versionName='0.3.1'" "$TMP/badging.txt" 'package/version'
require_fixed_ci 'f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2' "$TMP/apksigner.txt" 'historical certificate'
require_fixed 'Verified using v2 scheme (APK Signature Scheme v2): true' "$TMP/apksigner.txt" 'APK Signature Scheme v2'
require_fixed 'Verified using v3 scheme (APK Signature Scheme v3): true' "$TMP/apksigner.txt" 'APK Signature Scheme v3'
unzip -Z1 "$OUT/$APK_NAME" > "$TMP/apk-files.txt"
require_fixed 'classes.dex' "$TMP/apk-files.txt" 'APK DEX'
require_fixed 'resources.arsc' "$TMP/apk-files.txt" 'APK resource table'
require_fixed 'AndroidManifest.xml' "$TMP/apk-files.txt" 'APK manifest'
require_fixed 'pt.vcaitano.jarvis:mipmap/ic_launcher:' "$TMP/resources.txt" 'launcher resource'
require_fixed 'pt.vcaitano.jarvis:mipmap/ic_launcher_round:' "$TMP/resources.txt" 'round launcher resource'

echo '[9/10] Registrando hash e metadados do APK VC26...'
APK_SHA="$(sha256sum "$OUT/$APK_NAME" | cut -d' ' -f1)"
echo "APK_SHA256=$APK_SHA"
printf '%s  %s\n' "$APK_SHA" "$APK_NAME" > "$OUT/Jarvis-0.3.1-vc26.sha256.txt"
python3 - "$OUT/build-info.json" "$APK_SHA" <<'PY'
import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({
    "version": "0.3.1",
    "versionCode": 26,
    "package": "pt.vcaitano.jarvis",
    "apk": "Jarvis-0.3.1-vc26.apk",
    "apkSha256": sys.argv[2],
    "certificateSha256": "f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2",
    "source": "canonical patches through VC25 + apply_vc26.py",
    "scope": ["strict male PT-BR response voice", "background recognition tone suppression"],
    "aabBuilt": False
}, indent=2) + "\n")
PY

echo '[10/10] VC26 APK compilado e validado estruturalmente; AAB NÃO foi gerado e APK NÃO foi publicado nesta etapa.'
echo 'VC26_APK_BUILD_OK'
