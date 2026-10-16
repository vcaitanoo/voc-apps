from pathlib import Path
import re

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC28 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))


# VC28 is a strict successor of VC27. No UI, TTS, AI, memory, reminders,
# networking, wake-word routing or app actions are changed here.
replace_once(BUILD, 'versionCode = 27', 'versionCode = 28', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.2"', 'versionName = "0.3.3"', 'versionName')

voice = VOICE.read_text()

# Samsung/Google can generate an audible recognition-session tone outside the
# app's normal audio-stream control. VC26/VC27 attempted to mute that tone, but
# the physical-device test proved the tone survives. The only deterministic way
# to remove it is to stop opening SpeechRecognizer sessions.
#
# The canonical source already contains the silent AudioRecord capture path
# (startRawForegroundCapture), which sends captured WAV audio through the Jarvis
# transcription backend. Use that same path in foreground and background.
pattern = re.compile(
    r'    private fun startRecognitionNow\(\) \{[\s\S]*?\n    \}\n\n    private fun startRawForegroundCapture\(\) \{',
    re.M,
)
replacement = '''    private fun startRecognitionNow() {
        if (destroyed || !continuousEnabled || waitingForReply || speaking) return
        if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            emit(State.ERROR)
            onErrorMessage("Permissão de microfone não concedida.")
            return
        }

        // Keep one microphone owner when the conversation screen returns to the
        // foreground. AudioRecord itself is silent and does not open a Samsung/
        // Google SpeechRecognizer session, so there is no start/end recognition beep.
        if (!managedByListeningService && JarvisListeningService.isBackgroundControllerActive()) {
            JarvisListeningService.stop(appContext)
            startRecognitionSoon(700L)
            return
        }

        startRawForegroundCapture()
    }

    private fun startRawForegroundCapture() {'''
voice, count = pattern.subn(replacement, voice, count=1)
if count != 1:
    raise SystemExit('VC28 startRecognitionNow block not found exactly once')

VOICE.write_text(voice)

final_build = BUILD.read_text()
final_voice = VOICE.read_text()
if 'versionCode = 28' not in final_build or 'versionName = "0.3.3"' not in final_build:
    raise SystemExit('VC28 identity validation failed')
if 'startRawForegroundCapture()\n    }\n\n    private fun startRawForegroundCapture()' not in final_voice:
    raise SystemExit('VC28 silent AudioRecord routing validation failed')
if 'r.startListening(recognitionIntent())' in final_voice:
    raise SystemExit('VC28 still contains a live SpeechRecognizer startListening call')
if 'BrainClient.transcribe(token, wav)' not in final_voice:
    raise SystemExit('VC28 silent transcription path missing')
if 'val selected = male' not in final_voice:
    raise SystemExit('VC28 unexpectedly changed VC26 male voice policy')

print('VC28 applied: SpeechRecognizer session removed from listening; silent AudioRecord capture used in foreground/background')
