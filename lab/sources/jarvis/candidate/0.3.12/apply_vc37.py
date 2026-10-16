from pathlib import Path
import re

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
VOICEPRINT = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC37 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(BUILD, "versionCode = 36", "versionCode = 37", "versionCode")
replace_once(BUILD, 'versionName = "0.3.11"', 'versionName = "0.3.12"', "versionName")

# Restore the voice engine which provided Jarvis's historical male voice on
# Samsung phones. Google TTS and Android's configured default remain fallbacks.
replace_once(
    VOICE,
    '''        val requestedEngine = when (engineStep) {
            0 -> "com.google.android.tts"
            1 -> "com.samsung.SMT"
            else -> null
        }''',
    '''        val requestedEngine = when (engineStep) {
            0 -> "com.samsung.SMT"
            1 -> "com.google.android.tts"
            else -> null
        }''',
    "restore Samsung male TTS as first choice",
)

# TTS must not fail silently when all engines fail to initialize. Keep trying
# available engines and report a clear Portuguese error only after the last one.
replace_once(
    VOICE,
    '''            if (status != TextToSpeech.SUCCESS) {
                runCatching { tts?.shutdown() }
                tts = null
                if (engineStep < 2 && !destroyed) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                }
                return@OnInitListener
            }''',
    '''            if (status != TextToSpeech.SUCCESS) {
                runCatching { tts?.shutdown() }
                tts = null
                ttsReady = false
                if (engineStep < 2 && !destroyed) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                } else if (!destroyed) {
                    handler.post {
                        emit(State.ERROR)
                        onErrorMessage("Não consegui iniciar o mecanismo de voz do Android. Verifique se o serviço de texto para voz está ativado.")
                    }
                }
                return@OnInitListener
            }''',
    "report TTS initialization failure",
)

# Runtime TTS state permits delayed initialization and reliable fallback/replay.
replace_once(
    VOICE,
    "    private var tts: TextToSpeech? = null\n",
    "    private var tts: TextToSpeech? = null\n"
    "    @Volatile private var ttsReady = false\n"
    "    @Volatile private var lastSpeechText: String? = null\n"
    "    @Volatile private var activeTtsEngineStep = 0\n",
    "TTS state fields",
)

# The state fields are above the initializer, so every attempted engine records
# its identity and starts in an unready state.
replace_once(
    VOICE,
    "    private fun initializeTextToSpeech(engineStep: Int = 0) {\n",
    "    private fun initializeTextToSpeech(engineStep: Int = 0) {\n"
    "        activeTtsEngineStep = engineStep\n"
    "        ttsReady = false\n",
    "TTS engine state",
)

# Require a genuine male Portuguese voice. Try Samsung -> Google -> system
# default, and fail explicitly instead of silently returning a written-only reply.
replace_once(
    VOICE,
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
                ttsReady = false
                if (engineStep < 2 && !destroyed) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                } else if (!destroyed) {
                    handler.post {
                        emit(State.ERROR)
                        onErrorMessage("Não encontrei uma voz masculina em português nos mecanismos de voz disponíveis. Verifique as vozes instaladas no Samsung TTS ou no Google TTS.")
                    }
                }
                return@OnInitListener
            }

            ttsReady = true
            tts?.setSpeechRate(0.96f)
            tts?.setPitch(0.90f)''',
    "mandatory male voice and explicit failure",
)

# Voice metadata is not sufficient: confirm that Android accepted the exact
# selected male voice. If assignment failed, try the next engine instead.
replace_once(
    VOICE,
    '''        if (selected != null) {
            val applied = runCatching {
                engine.voice = selected
                engine.voice?.name == selected.name
            }.getOrDefault(false)
            if (applied) return true
        }
        return false''',
    '''        if (selected != null) {
            val applied = runCatching {
                engine.voice = selected
                engine.voice?.name == selected.name
            }.getOrDefault(false)
            if (applied) return true
        }
        return false''',
    "confirm selected male voice was applied",
)

# Even if the TTS constructor itself throws (for example, an uninstalled engine
# package), move to the next engine instead of crashing or remaining silent.
replace_once(
    VOICE,
    '''        tts = if (requestedEngine != null) {
            TextToSpeech(appContext, listener, requestedEngine)
        } else {
            TextToSpeech(appContext, listener)
        }''',
    '''        tts = try {
            if (requestedEngine != null) {
                TextToSpeech(appContext, listener, requestedEngine)
            } else {
                TextToSpeech(appContext, listener)
            }
        } catch (_: Throwable) {
            ttsReady = false
            if (engineStep < 2 && !destroyed) {
                handler.post { initializeTextToSpeech(engineStep + 1) }
            } else if (!destroyed) {
                handler.post {
                    emit(State.ERROR)
                    onErrorMessage("Não consegui abrir nenhum mecanismo de voz disponível neste telemóvel.")
                }
            }
            null
        }''',
    "catch TTS engine constructor failure",
)

# When synthesis fails during playback, initialize the next engine and replay
# the same response. Ignore stale callbacks from an engine already replaced.
replace_once(
    VOICE,
    '''                @Deprecated("Deprecated in Java")
                override fun onError(utteranceId: String?) {
                    handler.post {
                        SpeechCoordinator.release(speechOwnerId)
                        speaking = false
                        waitingForReply = false
                        onErrorMessage("Não consegui reproduzir a resposta em voz alta.")
                        publishIdleOrListening()
                    }
                }''',
    '''                @Deprecated("Deprecated in Java")
                override fun onError(utteranceId: String?) {
                    handleTtsPlaybackError(engineStep)
                }

                override fun onError(utteranceId: String?, errorCode: Int) {
                    handleTtsPlaybackError(engineStep)
                }''',
    "retry TTS after playback error",
)

# Insert the shared fallback handler before voice configuration.
replace_once(
    VOICE,
    "    private fun configurePortugueseVoice(): Boolean {",
    '''    private fun handleTtsPlaybackError(engineStep: Int) {
        handler.post {
            if (destroyed || activeTtsEngineStep != engineStep) return@post
            val retryText = lastSpeechText
            if (engineStep < 2 && !retryText.isNullOrBlank()) {
                ttsReady = false
                runCatching { tts?.stop() }
                runCatching { tts?.shutdown() }
                tts = null
                initializeTextToSpeech(engineStep + 1)
                handler.postDelayed({ speakWithMaleOnlyLocalFallback(retryText, 0) }, 350L)
                return@post
            }

            SpeechCoordinator.release(speechOwnerId)
            speaking = false
            waitingForReply = false
            emit(State.ERROR)
            onErrorMessage("Não consegui reproduzir a resposta em voz alta, mesmo após tentar os mecanismos de voz disponíveis.")
            publishIdleOrListening()
        }
    }

    private fun configurePortugueseVoice(): Boolean {''',
    "shared TTS playback fallback",
)

# VoicePrint must reject an unregistered speaker before the audio is sent to
# speech transcription. This stops TV/background speech from reaching the brain.
replace_once(
    VOICE,
    '''            val capturedPcm = pcm.toByteArray()
            val wav = pcm16ToWav(capturedPcm, SAMPLE_RATE)
            val token = AuthSessionStore.validAccessToken(appContext)
            val text = BrainClient.transcribe(token, wav).orEmpty().trim()

            if (text.isNotBlank()) {
                if (!VoicePrint.isEnrolled(appContext)) {
                    handler.post {
                        emit(State.ERROR)
                        onErrorMessage("Cadastre sua voz nas Configurações para o Jarvis responder somente a você.")
                    }
                    return@Thread
                }
                if (!VoicePrint.matches(appContext, capturedPcm)) {
                    handler.post {
                        if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(60L)
                        else publishIdleOrListening()
                    }
                    return@Thread
                }
            }''',
    '''            val capturedPcm = pcm.toByteArray()

            if (!VoicePrint.isEnrolled(appContext)) {
                handler.post {
                    emit(State.ERROR)
                    onErrorMessage("Cadastre sua voz nas Configurações para o Jarvis responder somente a você.")
                }
                return@Thread
            }
            if (!VoicePrint.matches(appContext, capturedPcm)) {
                handler.post {
                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(120L)
                    else publishIdleOrListening()
                }
                return@Thread
            }

            val wav = pcm16ToWav(capturedPcm, SAMPLE_RATE)
            val token = AuthSessionStore.validAccessToken(appContext)
            val text = BrainClient.transcribe(token, wav).orEmpty().trim()''',
    "VoicePrint gate before cloud transcription",
)

# Moderate the VoicePrint threshold: the VC37 candidate had been lowered to
# 0.70/0.82, too permissive for TV/background speech. Restore the established
# baseline 0.86/0.93 while keeping its original pitch tolerance for the owner.
replace_once(
    VOICEPRINT,
    "private const val COS_PASS=0.91;private const val COS_STRICT=0.965;private const val PITCH_MIN_RATIO=0.78;private const val PITCH_MAX_RATIO=1.28",
    "private const val COS_PASS=0.86;private const val COS_STRICT=0.93;private const val PITCH_MIN_RATIO=0.55;private const val PITCH_MAX_RATIO=1.85",
    "restore balanced VoicePrint threshold",
)

# Track text waiting for speech and wait for asynchronous TTS initialization.
voice = VOICE.read_text(encoding="utf-8")
speech_start = voice.find("    private fun speakWithMaleOnlyLocalFallback(text: String, attempt: Int = 0) {")
if speech_start < 0:
    raise SystemExit("VC37 expected speech function missing")
speech_end = voice.find("\n    private fun ", speech_start + 10)
if speech_end < 0:
    raise SystemExit("VC37 speech function end missing")
speech = voice[speech_start:speech_end]
speech = speech.replace(
    "    private fun speakWithMaleOnlyLocalFallback(text: String, attempt: Int = 0) {\n",
    "    private fun speakWithMaleOnlyLocalFallback(text: String, attempt: Int = 0) {\n"
    "        lastSpeechText = text\n",
    1,
)
if "        if (tts == null) {" not in speech:
    raise SystemExit("VC37 TTS-not-ready check missing")
speech = speech.replace("        if (tts == null) {", "        if (tts == null || !ttsReady) {", 1)
speech = speech.replace("            if (attempt < 8) {", "            if (attempt < 20) {", 1)
old_sync_error = '''            } else {
                speaking = false
                waitingForReply = false
                onErrorMessage("Não consegui iniciar a leitura em voz alta.")
                publishIdleOrListening()
            }'''
if old_sync_error not in speech:
    raise SystemExit("VC37 synchronous speak error block missing")
speech = speech.replace(old_sync_error, '''            } else {
                handleTtsPlaybackError(activeTtsEngineStep)
            }''', 1)
voice = voice[:speech_start] + speech + voice[speech_end:]
VOICE.write_text(voice, encoding="utf-8")

# Verify exact source invariants so a stale/mismatched base cannot produce an APK.
build = BUILD.read_text(encoding="utf-8")
voice = VOICE.read_text(encoding="utf-8")
vp = VOICEPRINT.read_text(encoding="utf-8")
raw_start = voice.index("    private fun startRawForegroundCapture() {")
raw_end = voice.index("\n    private fun ", raw_start + 10)
capture = voice[raw_start:raw_end]
checks = [
    ("applicationId = \"pt.vcaitano.jarvis\"" in build, "package"),
    ("versionCode = 37" in build and 'versionName = "0.3.12"' in build, "identity"),
    ("startListening(" not in voice, "AudioRecord capture retained without SpeechRecognizer beeps"),
    (capture.index("MediaRecorder.AudioSource.MIC") < capture.index("MediaRecorder.AudioSource.VOICE_RECOGNITION"), "MIC primary"),
    (capture.index("recorder.startRecording()") < capture.index("emit(State.LISTENING)"), "microphone starts before listening status"),
    (capture.index("VoicePrint.matches(appContext, capturedPcm)") < capture.index("BrainClient.transcribe(token, wav)"), "VoicePrint blocks background transcription"),
    ("COS_PASS=0.86" in vp and "COS_STRICT=0.93" in vp, "balanced VoicePrint threshold"),
    ('0 -> "com.samsung.SMT"' in voice and '1 -> "com.google.android.tts"' in voice, "historical Samsung TTS priority"),
    ("ttsReady" in voice and "handleTtsPlaybackError(engineStep)" in voice, "TTS readiness and fallback"),
    ("lastSpeechText" in voice and "speakWithMaleOnlyLocalFallback(retryText, 0)" in voice, "retry same answer after TTS failure"),
    ('engine.voice?.name == selected.name' in voice, "explicit male voice actually applied"),
    ('europeanPortuguese = Locale("pt", "PT")' in voice, "PT-PT locale retained"),
    ('country == "PT") value += 12_000' in voice, "PT-PT priority retained"),
]
for ok, label in checks:
    if not ok:
        raise SystemExit("VC37 validation failed: " + label)

print("VC37 source patch validated: male TTS fallback, VoicePrint gate and error recovery")
