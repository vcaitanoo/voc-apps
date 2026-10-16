from pathlib import Path

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:180]!r}')
    path.write_text(text.replace(old, new, 1))

# Exact successor of VC21.
replace_once(BUILD, 'versionCode = 21', 'versionCode = 22')
replace_once(BUILD, 'versionName = "0.2.19"', 'versionName = "0.2.20"')

# Samsung/Android SpeechRecognizer may play system start/end tones. VC22 keeps the
# working local recognizer from VC21 but suppresses only the short recognition-tone
# window, restoring the user's media volume immediately afterwards.
voice = VOICE.read_text()
if 'import android.media.AudioManager' not in voice:
    voice = voice.replace('import android.media.AudioRecord\n', 'import android.media.AudioRecord\nimport android.media.AudioManager\n', 1)
VOICE.write_text(voice)

replace_once(
    VOICE,
    '    private var recognizer: SpeechRecognizer? = null\n',
    '    private var recognizer: SpeechRecognizer? = null\n    private var recognitionVolumeBeforeMute: Int? = null\n    private var recognitionMuteEpoch = 0\n'
)

helper_anchor = '    private fun startRecognitionNow() {\n'
helper = '''    private fun muteRecognitionToneWindow(durationMs: Long = 850L) {\n        if (managedByListeningService) return\n        val audio = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager ?: return\n        val stream = AudioManager.STREAM_MUSIC\n        val epoch = ++recognitionMuteEpoch\n        if (recognitionVolumeBeforeMute == null) {\n            recognitionVolumeBeforeMute = runCatching { audio.getStreamVolume(stream) }.getOrNull()\n        }\n        runCatching { audio.setStreamVolume(stream, 0, 0) }\n        handler.postDelayed({\n            if (epoch != recognitionMuteEpoch) return@postDelayed\n            val previous = recognitionVolumeBeforeMute\n            recognitionVolumeBeforeMute = null\n            if (previous != null) runCatching { audio.setStreamVolume(stream, previous, 0) }\n        }, durationMs)\n    }\n\n    private fun restoreRecognitionToneVolume() {\n        if (managedByListeningService) return\n        val previous = recognitionVolumeBeforeMute ?: return\n        recognitionVolumeBeforeMute = null\n        ++recognitionMuteEpoch\n        val audio = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager ?: return\n        runCatching { audio.setStreamVolume(AudioManager.STREAM_MUSIC, previous, 0) }\n    }\n\n'''
text = VOICE.read_text()
if helper_anchor not in text:
    raise SystemExit('startRecognitionNow anchor missing')
VOICE.write_text(text.replace(helper_anchor, helper + helper_anchor, 1))

# Mute only during the recognizer start tone window.
replace_once(
    VOICE,
    '        try {\n            r.startListening(recognitionIntent())\n            listening = true\n',
    '        try {\n            muteRecognitionToneWindow()\n            r.startListening(recognitionIntent())\n            listening = true\n'
)

# Before end/error callbacks can trigger Samsung's end tone, suppress that short window too.
replace_once(
    VOICE,
    '            override fun onError(error: Int) {\n                listening = false\n',
    '            override fun onError(error: Int) {\n                if (!managedByListeningService) muteRecognitionToneWindow(950L)\n                listening = false\n'
)
replace_once(
    VOICE,
    '            override fun onResults(results: Bundle?) {\n                listening = false\n',
    '            override fun onResults(results: Bundle?) {\n                if (!managedByListeningService) muteRecognitionToneWindow(950L)\n                listening = false\n'
)

# Do not open another recognizer session just because silence/no-match happened.
# A foreground session now restarts only after a real result has been routed or when
# the user explicitly starts listening again. This removes the repeated beep loop.
replace_once(
    VOICE,
    '                    SpeechRecognizer.ERROR_NO_MATCH,\n                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->\n                        startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else foregroundDelay)\n                    else -> startRecognitionSoon(if (managedByListeningService) BUSY_RESTART_DELAY_MS else foregroundDelay)\n',
    '                    SpeechRecognizer.ERROR_NO_MATCH,\n                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> {\n                        if (managedByListeningService) startRecognitionSoon(RESTART_DELAY_MS)\n                        else publishIdleOrListening()\n                    }\n                    else -> {\n                        if (managedByListeningService) startRecognitionSoon(BUSY_RESTART_DELAY_MS)\n                        else publishIdleOrListening()\n                    }\n'
)
replace_once(
    VOICE,
    'if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else 5_000L)',
    'if (continuousEnabled && !waitingForReply && !speaking) { if (managedByListeningService) startRecognitionSoon(RESTART_DELAY_MS) else publishIdleOrListening() }'
)

# Voice output: the cloud PCM path was the source of occasional garbled/foreign-sounding
# fragments while the written answer was correct. Keep the exact written answer and use
# Android TTS for speech until the cloud audio format is validated end-to-end.
old_speak = '''        Thread {\n            val token = AuthSessionStore.validAccessToken(appContext)\n            val chunks = splitForSpeech(text)\n            val cloudAudio = if (token.isNullOrBlank()) {\n                emptyList()\n            } else {\n                chunks.map { chunk -> BrainClient.synthesizeSpeech(token, chunk) }\n            }\n            val cloudReady = cloudAudio.size == chunks.size && cloudAudio.all { it != null }\n            if (cloudReady && voiceOutputEnabled && !destroyed) {\n                val played = cloudAudio.filterNotNull().all { audio ->\n                    voiceOutputEnabled && !destroyed && playPcm(audio.pcm, audio.sampleRate)\n                }\n                handler.post {\n                    if (played) finishSpeaking() else speakWithMaleOnlyLocalFallback(text)\n                }\n            } else {\n                handler.post { speakWithMaleOnlyLocalFallback(text) }\n            }\n        }.apply {'''
new_speak = '''        Thread {\n            // VC22 intentionally disables the unverified raw cloud-PCM playback path.\n            // The local Android TTS receives exactly the sanitized text shown on screen,\n            // eliminating corrupted chunks that sounded like foreign/garbled words.\n            handler.post {\n                if (voiceOutputEnabled && !destroyed) speakWithMaleOnlyLocalFallback(text)\n                else finishSpeaking()\n            }\n        }.apply {'''
replace_once(VOICE, old_speak, new_speak)

# Always restore the user's media volume when recognition is cancelled/destroyed.
replace_once(
    VOICE,
    '    private fun cancelRecognition() {\n        rawCaptureEpoch += 1\n',
    '    private fun cancelRecognition() {\n        restoreRecognitionToneVolume()\n        rawCaptureEpoch += 1\n'
)

print('VC22 silent-recognition + clean-speech patch applied')
