from pathlib import Path
import re

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:180]!r}')
    path.write_text(text.replace(old, new, 1))

replace_once(BUILD, 'versionCode = 22', 'versionCode = 23')
replace_once(BUILD, 'versionName = "0.2.20"', 'versionName = "0.2.21"')

voice = VOICE.read_text()

old_restore = '''    private fun restoreRecognitionTones() {
        val before = recognitionSystemVolumeBefore ?: return
        recognitionSystemVolumeBefore = null
        runCatching {
            val audio = appContext.getSystemService(android.content.Context.AUDIO_SERVICE) as android.media.AudioManager
            audio.setStreamVolume(android.media.AudioManager.STREAM_SYSTEM, before, 0)
        }
    }
'''
new_restore = '''    private fun restoreRecognitionTones(force: Boolean = false) {
        if (!force && !managedByListeningService && continuousEnabled && !destroyed) return
        val before = recognitionSystemVolumeBefore ?: return
        recognitionSystemVolumeBefore = null
        runCatching {
            val audio = appContext.getSystemService(android.content.Context.AUDIO_SERVICE) as android.media.AudioManager
            audio.setStreamVolume(android.media.AudioManager.STREAM_SYSTEM, before, 0)
        }
    }
'''
if old_restore not in voice:
    raise SystemExit('VC22 restoreRecognitionTones block missing')
voice = voice.replace(old_restore, new_restore, 1)

old_handoff = '''    fun handoffToBackground() {
        if (managedByListeningService || destroyed) return
        cancelRecognition()
        if (continuousEnabled) JarvisListeningService.start(appContext)
    }
'''
new_handoff = '''    fun handoffToBackground() {
        if (managedByListeningService || destroyed) return
        cancelRecognition()
        restoreRecognitionTones(force = true)
        if (continuousEnabled) JarvisListeningService.start(appContext)
    }
'''
if old_handoff not in voice:
    raise SystemExit('handoffToBackground block missing')
voice = voice.replace(old_handoff, new_handoff, 1)

cloud_pattern = re.compile(
    r'''        Thread \{\n'''
    r'''            val token = AuthSessionStore\.validAccessToken\(appContext\)\n'''
    r'''            val chunks = splitForSpeech\(text\)\n'''
    r'''[\s\S]*?'''
    r'''        \}\.apply \{\n'''
    r'''            name = "[^"]+"\n'''
    r'''            isDaemon = true\n'''
    r'''            start\(\)\n'''
    r'''        \}\n''',
    re.M,
)
replacement = '''        // VC23: local TTS only. The cloud voice occasionally produced phonemes
        // not present in the displayed answer; local TTS reads the exact text.
        handler.post { speakWithMaleOnlyLocalFallback(text) }
'''
voice, count = cloud_pattern.subn(replacement, voice, count=1)
if count != 1:
    raise SystemExit('cloud response speech thread not found')

voice = voice.replace('setPitch(0.76f)', 'setPitch(0.90f)')
voice = voice.replace('setSpeechRate(0.98f)', 'setSpeechRate(0.96f)')

old_destroy = '''        destroyed = true
        continuousEnabled = false
        cancelRecognition()
'''
new_destroy = '''        destroyed = true
        continuousEnabled = false
        cancelRecognition()
        restoreRecognitionTones(force = true)
'''
if old_destroy in voice:
    voice = voice.replace(old_destroy, new_destroy, 1)

VOICE.write_text(voice)
print('VC23 silent-listening + exact local-TTS patch applied')
