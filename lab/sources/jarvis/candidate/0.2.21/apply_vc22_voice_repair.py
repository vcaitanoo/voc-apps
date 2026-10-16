from pathlib import Path
import re

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'
MANIFEST = APP / 'src/main/AndroidManifest.xml'


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old!r}')
    path.write_text(text.replace(old, new, 1))

replace_once(BUILD, 'versionCode = 21', 'versionCode = 22')
replace_once(BUILD, 'versionName = "0.2.19"', 'versionName = "0.2.20"')

voice = VOICE.read_text()

# Use the standard Android/Google speech recognizer. Do not force on-device
# recognition because the Portuguese offline package may not be installed.
create_pattern = re.compile(
    r'    private fun createRecognizer\(\): SpeechRecognizer\? \{[\s\S]*?\n    \}\n\n    private fun ensureRecognizer\(\): SpeechRecognizer\? \{',
    re.M,
)
voice, n = create_pattern.subn(
    '''    private fun createRecognizer(): SpeechRecognizer? {
        recognizerIsOnDevice = false
        return runCatching { SpeechRecognizer.createSpeechRecognizer(appContext) }.getOrNull()
    }

    private fun ensureRecognizer(): SpeechRecognizer? {''',
    voice,
    count=1,
)
if n != 1:
    raise SystemExit('createRecognizer block not found')

field_anchor = '    private var recognizer: SpeechRecognizer? = null\n'
if field_anchor not in voice:
    raise SystemExit('recognizer field anchor missing')
voice = voice.replace(
    field_anchor,
    field_anchor + '    private var recognitionSystemVolumeBefore: Int? = null\n',
    1,
)

helper_anchor = '    private fun recognitionIntent(): Intent {'
helpers = '''    private fun silenceRecognitionTones() {
        if (managedByListeningService || recognitionSystemVolumeBefore != null) return
        runCatching {
            val audio = appContext.getSystemService(android.content.Context.AUDIO_SERVICE) as android.media.AudioManager
            val before = audio.getStreamVolume(android.media.AudioManager.STREAM_SYSTEM)
            recognitionSystemVolumeBefore = before
            if (before > 0) audio.setStreamVolume(android.media.AudioManager.STREAM_SYSTEM, 0, 0)
        }
    }

    private fun restoreRecognitionTones() {
        val before = recognitionSystemVolumeBefore ?: return
        recognitionSystemVolumeBefore = null
        runCatching {
            val audio = appContext.getSystemService(android.content.Context.AUDIO_SERVICE) as android.media.AudioManager
            audio.setStreamVolume(android.media.AudioManager.STREAM_SYSTEM, before, 0)
        }
    }

'''
if helper_anchor not in voice:
    raise SystemExit('recognitionIntent anchor missing')
voice = voice.replace(helper_anchor, helpers + helper_anchor, 1)

voice = voice.replace(
    '            override fun onError(error: Int) {\n                listening = false',
    '            override fun onError(error: Int) {\n                restoreRecognitionTones()\n                listening = false',
    1,
)
voice = voice.replace(
    '            override fun onResults(results: Bundle?) {\n                listening = false',
    '            override fun onResults(results: Bundle?) {\n                restoreRecognitionTones()\n                listening = false',
    1,
)

start_old = '''        try {
            r.startListening(recognitionIntent())
            listening = true
            emit(State.LISTENING)
        } catch (_: SecurityException) {
            emit(State.ERROR)
            onErrorMessage("O Android bloqueou o acesso ao microfone.")
        } catch (_: Throwable) {
            destroyRecognizerOnly()
            startRecognitionSoon(BUSY_RESTART_DELAY_MS)
        }
'''
start_new = '''        try {
            if (!managedByListeningService) silenceRecognitionTones()
            r.startListening(recognitionIntent())
            listening = true
            emit(State.LISTENING)
        } catch (_: SecurityException) {
            restoreRecognitionTones()
            emit(State.ERROR)
            onErrorMessage("O Android bloqueou o acesso ao microfone.")
        } catch (_: Throwable) {
            restoreRecognitionTones()
            destroyRecognizerOnly()
            if (managedByListeningService) startRecognitionSoon(BUSY_RESTART_DELAY_MS)
            else publishIdleOrListening()
        }
'''
if start_old not in voice:
    raise SystemExit('startListening block missing')
voice = voice.replace(start_old, start_new, 1)

cancel_old = '''    private fun cancelRecognition() {
        rawCaptureEpoch += 1
        rawCaptureActive = false
'''
cancel_new = '''    private fun cancelRecognition() {
        restoreRecognitionTones()
        rawCaptureEpoch += 1
        rawCaptureActive = false
'''
if cancel_old not in voice:
    raise SystemExit('cancelRecognition block missing')
voice = voice.replace(cancel_old, cancel_new, 1)

old_fg_error = '''                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                        startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else foregroundDelay)
                    else -> startRecognitionSoon(if (managedByListeningService) BUSY_RESTART_DELAY_MS else foregroundDelay)
'''
new_fg_error = '''                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> {
                        if (managedByListeningService) startRecognitionSoon(RESTART_DELAY_MS)
                        else publishIdleOrListening()
                    }
                    else -> {
                        if (managedByListeningService) startRecognitionSoon(BUSY_RESTART_DELAY_MS)
                        else publishIdleOrListening()
                    }
'''
if old_fg_error not in voice:
    raise SystemExit('foreground error retry block missing')
voice = voice.replace(old_fg_error, new_fg_error, 1)

old_blank = 'if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else 5_000L)'
new_blank = 'if (continuousEnabled && !waitingForReply && !speaking && managedByListeningService) startRecognitionSoon(RESTART_DELAY_MS)'
if old_blank not in voice:
    raise SystemExit('blank-result retry block missing')
voice = voice.replace(old_blank, new_blank, 1)

VOICE.write_text(voice)

manifest = MANIFEST.read_text()
perm = '<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />'
if perm not in manifest:
    root = re.search(r'<manifest\b[^>]*>', manifest, re.S)
    if not root:
        raise SystemExit('manifest root tag missing')
    pos = root.end()
    manifest = manifest[:pos] + '\n    ' + perm + manifest[pos:]
MANIFEST.write_text(manifest)

print('VC22 voice repair applied')
