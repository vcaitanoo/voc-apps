from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC27 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))


# VC27 is a strict incremental successor of VC26. The only runtime change is
# suppression of Android/Samsung SpeechRecognizer start/end tones.
replace_once(BUILD, 'versionCode = 26', 'versionCode = 27', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.1"', 'versionName = "0.3.2"', 'versionName')

voice = VOICE.read_text()

field_anchor = '    private var recognitionSystemVolumeBefore: Int? = null\n'
if field_anchor not in voice:
    raise SystemExit('VC27 recognition system-volume field anchor missing')
voice = voice.replace(
    field_anchor,
    field_anchor +
    '    private var recognitionMusicVolumeBefore: Int? = null\n'
    '    private var recognitionMusicMuteEpoch: Long = 0L\n',
    1,
)

helper_anchor = '    private fun silenceRecognitionTones() {'
if helper_anchor not in voice:
    raise SystemExit('VC27 silenceRecognitionTones helper anchor missing')

music_helper = '''    private fun muteRecognitionMusicWindow(durationMs: Long = 700L) {
        runCatching {
            val audio = appContext.getSystemService(android.content.Context.AUDIO_SERVICE) as android.media.AudioManager
            val stream = android.media.AudioManager.STREAM_MUSIC
            val epoch = ++recognitionMusicMuteEpoch
            if (recognitionMusicVolumeBefore == null) {
                recognitionMusicVolumeBefore = audio.getStreamVolume(stream)
            }
            val before = audio.getStreamVolume(stream)
            if (before > 0) audio.setStreamVolume(stream, 0, 0)
            handler.postDelayed({
                if (epoch != recognitionMusicMuteEpoch) return@postDelayed
                val previous = recognitionMusicVolumeBefore
                recognitionMusicVolumeBefore = null
                if (previous != null) runCatching { audio.setStreamVolume(stream, previous, 0) }
            }, durationMs)
        }
    }

'''
voice = voice.replace(helper_anchor, music_helper + helper_anchor, 1)

# Start beep: keep the existing SYSTEM-stream suppression from VC26 and add a
# short MUSIC-stream mute window immediately around startListening().
start_old = '            silenceRecognitionTones()\n            r.startListening(recognitionIntent())\n'
start_new = '            silenceRecognitionTones()\n            muteRecognitionMusicWindow(700L)\n            r.startListening(recognitionIntent())\n'
if start_old not in voice:
    raise SystemExit('VC27 startListening suppression anchor missing')
voice = voice.replace(start_old, start_new, 1)

# End beep: Samsung/Google recognizers can emit it on STREAM_MUSIC. Mute that
# stream at onEndOfSpeech, before final results are delivered.
if 'override fun onEndOfSpeech() {' in voice:
    voice = voice.replace(
        'override fun onEndOfSpeech() {\n',
        'override fun onEndOfSpeech() {\n                muteRecognitionMusicWindow(700L)\n',
        1,
    )
elif 'override fun onEndOfSpeech() = Unit' in voice:
    voice = voice.replace(
        'override fun onEndOfSpeech() = Unit',
        'override fun onEndOfSpeech() { muteRecognitionMusicWindow(700L) }',
        1,
    )
else:
    error_anchor = '            override fun onError(error: Int) {'
    if error_anchor not in voice:
        raise SystemExit('VC27 RecognitionListener onError anchor missing')
    voice = voice.replace(
        error_anchor,
        '            override fun onEndOfSpeech() {\n'
        '                muteRecognitionMusicWindow(700L)\n'
        '            }\n\n' + error_anchor,
        1,
    )

# Fallback for recognizers that skip onEndOfSpeech on error/final result. This
# does not alter recognition routing; it only covers the tiny tone window.
for callback in ('onError', 'onResults'):
    marker = f'            override fun {callback}'
    pos = voice.find(marker)
    if pos < 0:
        raise SystemExit(f'VC27 {callback} callback missing')
    brace = voice.find('{\n', pos)
    if brace < 0:
        raise SystemExit(f'VC27 {callback} callback body missing')
    insert_at = brace + 2
    nearby = voice[insert_at:insert_at + 120]
    if 'muteRecognitionMusicWindow' not in nearby:
        voice = voice[:insert_at] + '                muteRecognitionMusicWindow(700L)\n' + voice[insert_at:]

VOICE.write_text(voice)

final_build = BUILD.read_text()
final_voice = VOICE.read_text()
if 'versionCode = 27' not in final_build or 'versionName = "0.3.2"' not in final_build:
    raise SystemExit('VC27 identity validation failed')
if 'muteRecognitionMusicWindow(700L)\n            r.startListening' not in final_voice:
    raise SystemExit('VC27 start-tone suppression validation failed')
if 'override fun onEndOfSpeech()' not in final_voice or 'muteRecognitionMusicWindow(700L)' not in final_voice:
    raise SystemExit('VC27 end-tone suppression validation failed')
if 'val selected = male' not in final_voice:
    raise SystemExit('VC27 unexpectedly changed VC26 male voice policy')

print('VC27 applied: only SpeechRecognizer start/end tone suppression expanded to STREAM_MUSIC')
