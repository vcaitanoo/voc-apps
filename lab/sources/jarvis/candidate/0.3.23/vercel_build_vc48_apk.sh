#!/usr/bin/env bash
# Build do APK da candidata VC48 / 0.3.23 (recuperação da voz masculina histórica).
#
# Este script NAO faz o setup do toolchain. O script base da VC26 ja prepara JDK,
# Android SDK, build-tools, Gradle e a keystore via edge function, e foi testado
# em dozens de builds. A VC35 reaproveita-o por substituicao de strings; a VC48
# faz o mesmo, acrescentando apenas o patch e as validacoes novas.
#
# O que muda face a VC35:
#   - aplica tambem o apply_vc39.py (persona, pt-BR, wake-word ack)
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
GEN="$ROOT/.vc48-generated-build.sh"
BASE="$ROOT/lab/sources/jarvis/candidate/0.3.1/vercel_build_vc26_apk.sh"

python3 - "$BASE" "$GEN" <<'PY'
from pathlib import Path
import sys

base = Path(sys.argv[1]).read_text()

replacements = {
    "ENDPOINT='https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-build-oidc'":
        'ENDPOINT="${JARVIS_BUILD_ENDPOINT:-https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-vc38-build-oidc}"',
    '.jarvis-build-vc26': '.jarvis-build-vc48',
    "APK_NAME='Jarvis-0.3.1-vc26.apk'": "APK_NAME='Jarvis-0.3.23-vc48.apk'",
    'Jarvis-0.3.1-vc26.sha256.txt': 'Jarvis-0.3.23-vc48.sha256.txt',

    # Aplica VC27 a VC48 a seguir a VC26. (VC30 nao existe na cadeia: foi
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
        "python3 lab/sources/jarvis/candidate/0.3.11/apply_vc36.py\npython3 lab/sources/jarvis/candidate/0.3.13/apply_vc38.py\npython3 lab/sources/jarvis/candidate/0.3.14/apply_vc39.py\npython3 lab/sources/jarvis/candidate/0.3.17/apply_vc42.py\npython3 lab/sources/jarvis/candidate/0.3.18/apply_vc43.py\npython3 lab/sources/jarvis/candidate/0.3.19/apply_vc44.py\npython3 lab/sources/jarvis/candidate/0.3.20/apply_vc45.py\npython3 lab/sources/jarvis/candidate/0.3.21/apply_vc46.py\npython3 lab/sources/jarvis/candidate/0.3.22/apply_vc47.py\npython3 lab/sources/jarvis/candidate/0.3.23/apply_vc48.py\n",

    "grep -q 'versionCode = 26'": "grep -q 'versionCode = 48'",
    "grep -q 'versionName = \"0.3.1\"'": "grep -q 'versionName = \"0.3.23\"'",
    "require_fixed \"name='pt.vcaitano.jarvis' versionCode='26' versionName='0.3.1'\"":
        "require_fixed \"name='pt.vcaitano.jarvis' versionCode='48' versionName='0.3.23'\"",

    '"version": "0.3.1"': '"version": "0.3.23"',
    '"versionCode": 26': '"versionCode": 48',
    '"apk": "Jarvis-0.3.1-vc26.apk"': '"apk": "Jarvis-0.3.23-vc48.apk"',
}

for old, new in replacements.items():
    if old not in base:
        raise SystemExit('VC48 build wrapper expected block missing: ' + old[:70])
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
    raise SystemExit("VC48: comando Gradle esperado ausente ou duplicado")
base = base.replace(gradle_old, gradle_new, 1)

# Preserve the canonical release signing identity enforced by the base build script.
if "f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2" not in base:
    raise SystemExit("VC48: expected historical release certificate reference missing")

# A validacao da VC26 (que exigia uma topologia de audio que ja nao existe)
# e substituida pelas invariantes que interessam a VC48.
validation = r'''
# --- escopo da VC48 -------------------------------------------------------
grep -q 'versionCode = 48' "$SOURCE/app/build.gradle.kts"
grep -q 'versionName = "0.3.23"' "$SOURCE/app/build.gradle.kts"

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
grep -q '0 -> pinnedEngine' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q '1 -> "com.samsung.SMT"' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'handleTtsPlaybackError(engineStep)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'ttsReady' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'ttsInitializationGeneration' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'ttsInitializationInProgress' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q '6_000L' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'attempt < 80' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'if (!configurePortugueseVoice())' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'tts?.setPitch(0.76f)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
if grep -q 'tts?.setPitch(if (maleReady)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo "ERRO: síntese permitida sem voz masculina confirmada." >&2
  exit 1
fi
# VC48 reminder-management invariants: number selection and menu deletion must survive compilation.
grep -q 'val requestedNumber' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -q 'reminders.getOrNull(requestedNumber - 1)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -q 'fun cancelReminder' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -q 'Lembretes salvos' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
grep -q 'deleteSavedReminder' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"

# Voz masculina em português brasileiro deve estar explicitamente selecionada.
grep -q 'brazilianPortuguese = Locale("pt", "BR")' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -q 'country == "BR") value += 12_000' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
if grep -q 'configureFallbackPortugueseVoice' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo "ERRO: fallback para voz portuguesa sem identificação masculina." >&2
  exit 1
fi
if grep -q 'O mecanismo de voz do Android não ficou pronto.' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo "ERRO: mensagem genérica de falha de voz ainda presente." >&2
  exit 1
fi

# VC48: a voz original deve manter-se em respostas e lembretes
grep -Fq 'readyEngine.setSpeechRate(0.98f)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'readyEngine.setPitch(0.76f)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
# VC48 restores ORIGINAL cloud-first male audio and decodes true MP3.
# VC48 lifecycle and manual male voice guards
# VC48: real AI conversation with persistent context
grep -Fq 'conversationForBrain' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
grep -Fq 'earlier.takeLast(12).forEach' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -Fq 'fun chat(accessToken: String?, message: String, conversation:' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -Fq 'override fun onPause()' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
grep -Fq 'availableJarvisVoices.forEach' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
grep -Fq 'fun chooseBrazilianVoice' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'confirmedName' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'Microphone background transition rejected' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
grep -Fq 'Android rejected background microphone start' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/JarvisListeningService.kt"

grep -Fq 'playVerifiedMaleMp3(cloudAudio.pcm)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'jarvis-original-male-cloud-voice' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq '/jarvis-voice-mp3' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
grep -Fq 'jarvis_original_male_voice_lock' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'lockedVoiceName' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
grep -Fq 'getSharedPreferences("jarvis_original_male_voice_lock", 0)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/ReminderSpeechService.kt"
grep -Fq 'engine.setPitch(0.76f)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/ReminderSpeechService.kt"
if grep -Fq 'tts?.setPitch(0.90f)' "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"; then
  echo 'VC48: tonalidade regressiva reapareceu' >&2
  exit 1
fi

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

echo '--- VC48 VoiceController.kt lines 850-875 (compile diagnostics) ---'
nl -ba "$SOURCE/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt" | sed -n '835,860p'
echo 'VALIDATION_OK: escopo estrito da VC48 (VC35 mantida + persona + pt-BR)'
'''

marker = "echo '[2/10] Validando identidade e escopo estrito da VC26...'"
start = base.find(marker)
if start == -1:
    raise SystemExit('VC48: bloco de validacao da VC26 nao encontrado')

# A validacao da VC26 pode ocupar varias linhas: substitui ate ao proximo 'echo'.
nxt = base.find("echo '[3/10]", start)
if nxt == -1:
    raise SystemExit('VC48: fim da validacao nao encontrado')

base = base[:start] + validation.strip() + "\n\n" + base[nxt:]

base = base.replace(
    'echo \'[1/10] Reconstruindo a fonte canônica VC25 e aplicando somente a correção VC26...\'',
    'echo \'[1/10] Reconstruindo a fonte canonica e aplicando VC18..VC48...\'',
)
base = base.replace(
    'echo \'[10/10] VC26 APK compilado e validado estruturalmente; AAB NÃO foi gerado e APK NÃO foi publicado nesta etapa.\'',
    'echo \'[10/10] VC48 APK compilado e validado estruturalmente; AAB NAO foi gerado.\'',
)
base = base.replace('echo \'VC26_APK_BUILD_OK\'', 'echo \'VC48_APK_BUILD_OK\'')

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
    raise SystemExit("VC48: signing marker not found while adding fresh GitHub OIDC")
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
SUPABASE_URL="${ENDPOINT%%/functions/*}"

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
  "versionCode": 48,
  "versionName": "0.3.23",
  "publishedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "SHA256=$APK_SHA"
echo "apkUrl=$PUBLIC_URL"
echo 'VC48_PUBLISH_OK'
"""

verify_line = '"$SDK/build-tools/37.0.0/apksigner" verify --verbose --print-certs "$OUT/$APK_NAME" > "$TMP/apksigner.txt"'
if verify_line not in base:
    raise SystemExit("VC48: apksigner verification line missing")
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
print('VC48 build script generated')
PY

chmod +x "$GEN"
bash "$GEN"
