from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
BRAIN = APP / "src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC29 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))


def replace_or_accept(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new, 1))
        return
    if new in text:
        return
    raise SystemExit(f"VC29 expected old/new block missing ({label}) in {path}")


# VC29 is a strict successor of VC28. Keep the silent AudioRecord listening path
# unchanged. The only functional fix is allowing that captured audio to reach the
# jarvis-voice /transcribe endpoint even when there is no Jarvis auth token.
replace_or_accept(BUILD, 'versionCode = 28', 'versionCode = 29', 'versionCode')
replace_or_accept(BUILD, 'versionName = "0.3.3"', 'versionName = "0.3.4"', 'versionName')

# Patch only the stale authorization guard. Canonical VC28 may already contain
# the anonymous-safe empty-audio-only guard because it descends from VC20.
replace_or_accept(
    BRAIN,
    'if (accessToken.isNullOrBlank() || wavBytes.isEmpty()) return null',
    'if (wavBytes.isEmpty()) return null',
    'anonymous STT guard',
)

final_build = BUILD.read_text()
final_brain = BRAIN.read_text()
final_voice = VOICE.read_text()

if 'versionCode = 29' not in final_build or 'versionName = "0.3.4"' not in final_build:
    raise SystemExit('VC29 identity validation failed')
if 'fun transcribe(accessToken: String?, wavBytes: ByteArray): String?' not in final_brain:
    raise SystemExit('VC29 transcribe function missing')
if 'if (accessToken.isNullOrBlank() || wavBytes.isEmpty()) return null' in final_brain:
    raise SystemExit('VC29 still blocks anonymous silent transcription')
if 'if (wavBytes.isEmpty()) return null' not in final_brain:
    raise SystemExit('VC29 empty-audio guard missing')
if 'r.startListening(recognitionIntent())' in final_voice:
    raise SystemExit('VC29 unexpectedly restored SpeechRecognizer and beep source')
if 'startRawForegroundCapture()' not in final_voice or 'BrainClient.transcribe(token, wav)' not in final_voice:
    raise SystemExit('VC29 silent AudioRecord transcription path missing')
if 'val selected = male' not in final_voice:
    raise SystemExit('VC29 unexpectedly changed male voice policy')

print('VC29 applied: silent AudioRecord kept; anonymous jarvis-voice transcription unblocked')
