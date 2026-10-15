from pathlib import Path

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
VOICEPRINT = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"

def replace_once(path, old, new, label):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit("VC37 expected block missing: " + label)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(BUILD, 'versionCode = 36', 'versionCode = 37', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.11"', 'versionName = "0.3.12"', 'versionName')
voice = VOICE.read_text(encoding="utf-8")
replace_once(VOICE,
'''        val requestedEngine = when (engineStep) {
            0 -> "com.google.android.tts"
            1 -> "com.samsung.SMT"
            else -> null
        }''',
'''        val requestedEngine = when (engineStep) {
            0 -> null
            1 -> "com.google.android.tts"
            else -> "com.samsung.SMT"
        }''',
'default Android TTS engine first')
replace_once(VOICE,
'''            val maleReady = configurePortugueseVoice()
            if (!maleReady && engineStep < 2 && !destroyed) {
                runCatching { tts?.shutdown() }
                tts = null
                handler.post { initializeTextToSpeech(engineStep + 1) }
                return@OnInitListener
            }

            tts?.setSpeechRate(0.96f)
            // Real male voice keeps historical pitch. Only the final
            // compatibility fallback receives a deeper pitch.
            tts?.setPitch(if (maleReady) 0.90f else 0.76f)''',
'''            val maleReady = configurePortugueseVoice()
            if (!maleReady) {
                runCatching { tts?.shutdown() }
                tts = null
                if (engineStep < 2 && !destroyed) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                } else {
                    emit(State.ERROR)
                    onErrorMessage("Não encontrei uma voz masculina em português. Instale uma voz masculina nas definições de texto para voz do Android.")
                }
                return@OnInitListener
            }

            tts?.setSpeechRate(0.96f)
            tts?.setPitch(0.90f)''',
'no female TTS fallback')
replace_once(VOICE,
'''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(if (maleReady) 0.90f else 0.76f)
        tts?.setSpeechRate(0.96f)''',
'''        val maleReady = configurePortugueseVoice()
        if (!maleReady) {
            emit(State.ERROR)
            onErrorMessage("A resposta foi bloqueada porque não há uma voz masculina disponível.")
            return
        }
        tts?.setPitch(0.90f)
        tts?.setSpeechRate(0.96f)''',
'no female speech fallback')
VOICE.write_text(voice, encoding="utf-8")
vp = VOICEPRINT.read_text(encoding="utf-8")
old = 'private const val COS_PASS=0.91;private const val COS_STRICT=0.965;private const val PITCH_MIN_RATIO=0.78;private const val PITCH_MAX_RATIO=1.28'
new = 'private const val COS_PASS=0.70;private const val COS_STRICT=0.82;private const val PITCH_MIN_RATIO=0.55;private const val PITCH_MAX_RATIO=1.85'
replace_once(VOICEPRINT, old, new, 'VoicePrint thresholds')
build = BUILD.read_text(encoding="utf-8")
voice = VOICE.read_text(encoding="utf-8")
vp = VOICEPRINT.read_text(encoding="utf-8")
start = voice.index('    private fun startRawForegroundCapture() {')
end = voice.index('\n    private fun ', start + 10)
capture = voice[start:end]
if 'versionCode = 37' not in build or 'versionName = "0.3.12"' not in build: raise SystemExit('VC37 version validation failed')
if 'startListening(' in voice: raise SystemExit('VC37 SpeechRecognizer/beep returned')
if capture.index('MediaRecorder.AudioSource.MIC') > capture.index('MediaRecorder.AudioSource.VOICE_RECOGNITION'): raise SystemExit('VC37 MIC not primary')
if capture.index('recorder.startRecording()') > capture.index('emit(State.LISTENING)'): raise SystemExit('VC37 UI before microphone recording')
if capture.index('BrainClient.transcribe(token, wav)') > capture.index('VoicePrint.matches(appContext, capturedPcm)'): raise SystemExit('VC37 VoicePrint blocks transcription')
if 'COS_PASS=0.70' not in vp or 'COS_STRICT=0.82' not in vp: raise SystemExit('VC37 thresholds missing')
if 'if (!maleReady)' not in voice or 'setPitch(if (maleReady)' in voice: raise SystemExit('VC37 conditional female fallback remains')
print('VC37 source patch validated')
