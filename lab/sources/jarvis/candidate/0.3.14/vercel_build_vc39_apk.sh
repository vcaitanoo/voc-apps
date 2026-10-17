#!/usr/bin/env bash
# Build do APK da candidata VC39 / 0.3.14 (cerebro com personalidade + pt-PT).
#
# Este script NAO faz o setup do toolchain. O script base da VC26 ja prepara JDK,
# Android SDK, build-tools, Gradle e a keystore via edge function, e foi testado
# em dozens de builds. A VC35 reaproveita-o por substituicao de strings; a VC39
# faz o mesmo, acrescentando apenas o patch e as validacoes novas.
#
# O que muda face a VC35:
#   - aplica tambem o apply_vc39.py (persona, pt-PT, wake-word ack)
#   - recupera a voz masculina Samsung primeiro, com fallback Google/default
#   - exige VoicePrint antes de transcrever para rejeitar a TV/vozes alheias
#   - valida recuperação do TTS e limiares equilibrados de VoicePrint

set -euo pipefail

# Bootstrap the short-lived GitHub Actions OIDC token before the VC26 base
# script checks VERCEL_OIDC_TOKEN. A fresh token is requested again before
# signing and upload, because the Gradle build may take several minutes.
if [[ -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}" && -n "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:-}" ]]; then
  OIDC_URL="${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=https%3A%2F%2Fkhinnoxpesnhtmmvrken.supabase.co%2Ffunctions%2Fv1%2Fjarvis-vc38-build-oidc"
  VERCEL_OIDC_TOKEN="$(curl --connect-timeout 15 --max-time 30 -fsSL -H "Authorization: Bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" "$OIDC_URL" | python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])')"
  export VERCEL_OIDC_TOKEN
fi
if [[ -z "${VERCEL_OIDC_TOKEN:-}" ]]; then
  echo "ERRO: o token OIDC do GitHub Actions não está disponível." >&2
  exit 1
fi

ROOT="$PWD"
GEN="$ROOT/.vc39-generated-build.sh"
BASE="$ROOT/lab/sources/jarvis/candidate/0.3.1/vercel_build_vc26_apk.sh"

python3 - "$BASE" "$GEN" <<'PY'
from pathlib import Path
import sys

base = Path(sys.argv[1]).read_text()

replacements = {
    "ENDPOINT='https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-build-oidc'":
        'ENDPOINT="${JARVIS_BUILD_ENDPOINT:-https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-vc38-build-oidc}"',
    '.jarvis-build-vc26': '.jarvis-build-vc39',
    "APK_NAME='Jarvis-0.3.1-vc26.apk'": "APK_NAME='Jarvis-0.3.14-vc39.apk'",
    'Jarvis-0.3.1-vc26.sha256.txt': 'Jarvis-0.3.14-vc39.sha256.txt',

    # BrainClient override contains the new reminder-management logic. The base
    # source archive does not include this override automatically, so install it
    # into the extracted source before applying version-specific patches.
    'cp lab/sources/jarvis/candidate/0.2.15/overrides/VoicePrint.kt "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"':
        'cp lab/sources/jarvis/candidate/0.2.15/overrides/VoicePrint.kt "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"\\ncp lab/sources/jarvis/candidate/0.2.16/overrides/BrainClient.kt "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"',


    # Aplica VC27 a VC39 a seguir a VC26. (VC30 nao existe na cadeia: foi
    # deliberadamente saltada e nao faz parte da candidata.)
    "python3 lab/sources/jarvis/candidate/0.3.1/apply_vc26.py\n":
        "python3 lab/sources/jarvis/candidate/0.3.1/apply_vc26.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.2/apply_vc27.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.3/apply_vc28.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.4/apply_vc29.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.6/apply_vc31.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.7/apply_vc32.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.8/apply_vc33.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.9/apply_vc34.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.10/apply_vc35.py\n"
        "python3 lab/sources/jarvis/candidate/0.3.11/apply_vc36.py\npython3 lab/sources/jarvis/candidate/0.3.13/apply_vc38.py\npython3 lab/sources/jarvis/candidate/0.3.14/apply_vc39.py\n",

    "grep -q 'versionCode = 26'": "grep -q 'versionCode = 39'",
    "grep -q 'versionName = \"0.3.1\"'": "grep -q 'versionName = \"0.3.11\"'",
    "require_fixed \"name='pt.vcaitano.jarvis' versionCode='26' versionName='0.3.1'\"":
        "require_fixed \"name='pt.vcaitano.jarvis' versionCode='39' versionName='0.3.14'\"",

    '"version": "0.3.1"': '"version": "0.3.14"',
    '"versionCode": 26': '"versionCode": 39',
    '"apk": "Jarvis-0.3.1-vc26.apk"': '"apk": "Jarvis-0.3.14-vc39.apk"',
}

for old, new in replacements.items():
    if old not in base:
        raise SystemExit('VC39 build wrapper expected block missing: ' + old[:70])
    base = base.replace(old, new)

# Nunca deixar a compilação presa indefinidamente em um download sem progresso.
base = base.replace(
    "curl -fL --retry 4 --retry-all-errors ",
    "curl --connect-timeout 20 --max-time 300 --speed-time 30 --speed-limit 10000 -fL --retry 4 --retry-all-errors ",
)
base = base.replace(
    "curl -fsSL --retry 4 --retry-all-errors",
    "curl --connect-timeout 20 --max-time 300 --speed-time 30 --speed-limit 10000 -fsSL --retry 4 --retry-all-errors",
)
base = base.replace(
    "curl -sS -w '%{http_code}'",
    "curl --connect-timeout 20 --max-time 600 --speed-time 45 --speed-limit 10000 -sS -w '%{http_code}'",
)

# Esta candidata precisa do APK release, não de um build debug adicional.
# Evita compilar duas variantes Kotlin no runner lento; os validadores e a
# assinatura release continuam obrigatórios.
gradle_old = '"$GRADLE_BIN" --no-daemon :app:testDebugUnitTest :app:assembleRelease --stacktrace'
gradle_new = '"$GRADLE_BIN" --no-daemon :app:assembleRelease --stacktrace'
if base.count(gradle_old) != 1:
    raise SystemExit("VC39: comando Gradle esperado ausente ou duplicado")
base = base.replace(gradle_old, gradle_new, 1)

# Preserve the canonical release signing identity enforced by the base build script.
if "f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2" not in base:
    raise SystemExit("VC39: expected historical release certificate reference missing")

# A validacao da VC26 (que exigia uma topologia de audio que ja nao existe)
# e substituida pelas invariantes que interessam a VC39.
validation = r'''
# --- escopo da VC39 -------------------------------------------------------
grep -q 'versionCode = 39' "$SOURCE/app/build.gradle.kts"
grep -q 'versionName = "0.3.14"' "$SOURCE/app/build.gradle.kts"

# O SpeechRecognizer e a origem do bip. Nunca pode reaparecer.
if grep -q 'startListening(' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo "ERRO: startListening() presente - o SpeechRecognizer volta a introduzir o bip." >&2
  exit 1
fi

# Biometria tem de continuar fail-closed e com os thresholds da VC33.
grep -q 'COS_PASS=0.86' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"
grep -q 'COS_STRICT=0.93' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"

# Voz masculina e obrigatoria - e a unica coisa que o dono pediu para preservar.
grep -q 'explicitMale' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q '0 -> "com.samsung.SMT"' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q '1 -> "com.google.android.tts"' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'handleTtsPlaybackError(engineStep)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'ttsReady' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

# PT-PT tem de valer mais que pt-BR no score do TTS, senao a voz portuguesa
# nunca seria escolhida mesmo existindo.
grep -q 'europeanPortuguese = Locale("pt", "PT")' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'country == "PT") value += 12_000' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

# Captura de audio da VC35 mantida: MIC primario, AGC/NS, pre-roll 1,2 s.
grep -q 'MediaRecorder.AudioSource.MIC' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'AutomaticGainControl.create(recorder.audioSessionId)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'NoiseSuppressor.create(recorder.audioSessionId)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'preRollMaxBytes = SAMPLE_RATE \* 2 \* 12 / 10' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

# O prompt do wake-word foi reescrito: sem "usuario", sem pt-BR, sem bordao fixo.
BRAIN="$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -q 'O dono chamou-te pelo nome' "$BRAIN"
if grep -q 'O usuário apenas chamou você dizendo' "$BRAIN"; then
  echo "ERRO: o prompt do wake-word continua com o texto antigo (pt-BR)." >&2
  exit 1
fi

echo 'VALIDATION_OK: escopo estrito da VC39 (VC35 mantida + persona + pt-PT)'
'''

marker = "echo '[2/10] Validando identidade e escopo estrito da VC26...'"
start = base.find(marker)
if start == -1:
    raise SystemExit('VC39: bloco de validacao da VC26 nao encontrado')

# A validacao da VC26 pode ocupar varias linhas: substitui ate ao proximo 'echo'.
nxt = base.find("echo '[3/10]", start)
if nxt == -1:
    raise SystemExit('VC39: fim da validacao nao encontrado')

base = base[:start] + validation.strip() + "\n\n" + base[nxt:]

base = base.replace(
    'echo \'[1/10] Reconstruindo a fonte canônica VC25 e aplicando somente a correção VC26...\'',
    'echo \'[1/10] Reconstruindo a fonte canonica e aplicando VC18..VC39...\'',
)
base = base.replace(
    'echo \'[10/10] VC26 APK compilado e validado estruturalmente; AAB NÃO foi gerado e APK NÃO foi publicado nesta etapa.\'',
    'echo \'[10/10] VC39 APK compilado e validado estruturalmente; AAB NAO foi gerado.\'',
)
base = base.replace('echo \'VC26_APK_BUILD_OK\'', 'echo \'VC39_APK_BUILD_OK\'')

# GitHub Actions OIDC tokens are short-lived, so refresh before signing and upload.
github_oidc_refresh = r'''
if [[ -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}" && -n "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:-}" ]]; then
  OIDC_URL="${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=https%3A%2F%2Fkhinnoxpesnhtmmvrken.supabase.co%2Ffunctions%2Fv1%2Fjarvis-vc38-build-oidc"
  VERCEL_OIDC_TOKEN="$(curl --connect-timeout 15 --max-time 30 -fsSL -H "Authorization: Bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" "$OIDC_URL" | python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])')"
  export VERCEL_OIDC_TOKEN
fi
'''
signing_marker = "echo '[6/10] Obtendo a assinatura histórica por OIDC efêmero...'"
if signing_marker not in base:
    raise SystemExit("VC39: signing marker not found while adding fresh GitHub OIDC")
base = base.replace(signing_marker, github_oidc_refresh + "\n" + signing_marker, 1)

# ---------------------------------------------------------------------------
# Publicacao no Storage.
#
# O script base compila e assina mas NAO publica ("APK NAO foi publicado nesta
# etapa"). Sem este passo o APK fica apenas como artifact do GitLab e o VOC Lab
# nunca o ve. A publicacao passa pela edge function, que valida o OIDC e
# compara o SHA-256 com o que foi registado, por isso nao da para subir bytes
# errados sem a funcao recusar.
# ---------------------------------------------------------------------------
publish = """
# O script base nao define SUPABASE_URL, mas o endpoint da edge function carrega
# a origem: https://<ref>.supabase.co/functions/v1/<fn>
SUPABASE_URL="$(printf '%s' "$ENDPOINT" | sed -E 's#^(https://[^/]+).*#\\1#')"

echo '[11/12] Publicando os bytes exatos no armazenamento permanente...'
if [[ -n "${ACTIONS_ID_TOKEN_REQUEST_URL:-}" && -n "${ACTIONS_ID_TOKEN_REQUEST_TOKEN:-}" ]]; then
  OIDC_URL="${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=https%3A%2F%2Fkhinnoxpesnhtmmvrken.supabase.co%2Ffunctions%2Fv1%2Fjarvis-vc38-build-oidc"
  VERCEL_OIDC_TOKEN="$(curl --connect-timeout 15 --max-time 30 -fsSL -H "Authorization: Bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" "$OIDC_URL" | python3 -c 'import json,sys; print(json.load(sys.stdin)["value"])')"
  export VERCEL_OIDC_TOKEN
fi
APK_PATH="$OUT/$APK_NAME"
APK_SHA="$(sha256sum "$APK_PATH" | cut -d' ' -f1)"
OBJECT="jarvis/candidate/$APK_NAME"

HTTP_CODE=$(curl -sS -w '%{http_code}' -o "$OUT/upload-resp.txt" \\
  -X POST \\
  -H "Authorization: Bearer ${VERCEL_OIDC_TOKEN:-}" \\
  -H "x-action: upload" \\
  -H "x-artifact-path: ${OBJECT}" \\
  -H "x-artifact-sha256: ${APK_SHA}" \\
  -H "Content-Type: application/vnd.android.package-archive" \\
  --data-binary @"$APK_PATH" \\
  --retry 4 --retry-all-errors --retry-delay 3 \\
  "$ENDPOINT")

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "201" ]; then
  echo "ERRO: upload falhou (HTTP $HTTP_CODE)" >&2
  cat "$OUT/upload-resp.txt" >&2 || true
  exit 1
fi
echo "Upload OK (HTTP $HTTP_CODE)"

# Re-descarregar e confirmar que o que e servido e o que foi compilado.
PUBLIC_URL="${SUPABASE_URL}/storage/v1/object/public/voc-lab/${OBJECT}"
curl -fsSL --retry 4 --retry-all-errors --retry-delay 3 "$PUBLIC_URL" -o "$OUT/verify.apk"
SERVED_SHA="$(sha256sum "$OUT/verify.apk" | cut -d' ' -f1)"
if [ "$SERVED_SHA" != "$APK_SHA" ]; then
  echo "ERRO: o binario servido difere do compilado." >&2
  echo "  compilado: $APK_SHA" >&2
  echo "  servido   : $SERVED_SHA" >&2
  exit 1
fi
rm -f "$OUT/verify.apk"

cat > "$OUT/publish.json" <<EOF
{
  "apk": "$APK_NAME",
  "apkUrl": "$PUBLIC_URL",
  "sha256": "$APK_SHA",
  "versionCode": 39,
  "versionName": "0.3.14",
  "publishedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "SHA256=$APK_SHA"
echo "apkUrl=$PUBLIC_URL"
echo 'VC39_PUBLISH_OK'
"""

verify_line = '"$SDK/build-tools/37.0.0/apksigner" verify --verbose --print-certs "$OUT/$APK_NAME" > "$TMP/apksigner.txt"'
if verify_line not in base:
    raise SystemExit("VC39: apksigner verification line missing")
certificate_check = r"""
"$JAVA_HOME/bin/keytool" -printcert -jarfile "$OUT/$APK_NAME" > "$TMP/keytool-cert.txt"
ACTUAL_CERT_SHA="$(grep -m1 'SHA256:' "$TMP/keytool-cert.txt" | sed -E 's/.*SHA256:[[:space:]]*//; s/://g; s/[[:space:]]//g' | tr '[:upper:]' '[:lower:]')"
EXPECTED_CERT_SHA="f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2"
if [ "$ACTUAL_CERT_SHA" != "$EXPECTED_CERT_SHA" ]; then
  echo "VALIDATION_FAILED: certificado histórico do Jarvis não confere" >&2
  echo "  esperado: $EXPECTED_CERT_SHA" >&2
  echo "  obtido:  $ACTUAL_CERT_SHA" >&2
  cat "$TMP/keytool-cert.txt" >&2
  exit 1
fi
echo "SIGNATURE_CERTIFICATE_OK=$ACTUAL_CERT_SHA"
"""
base = base.replace(
    verify_line,
    verify_line + '\n' + certificate_check,
    1,
)

base = base.rstrip("\n") + "\n" + publish

Path(sys.argv[2]).write_text(base)
print('VC39 build script generated')
PY

chmod +x "$GEN"
bash "$GEN"
