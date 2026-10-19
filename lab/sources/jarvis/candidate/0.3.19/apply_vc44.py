from pathlib import Path
import re

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"VC44 expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


build = BUILD.read_text(encoding="utf-8")
build = replace_once(build, "versionCode = 43", "versionCode = 44", "versionCode")
build = replace_once(build, 'versionName = "0.3.18"', 'versionName = "0.3.19"', "versionName")
BUILD.write_text(build, encoding="utf-8")

voice = VOICE.read_text(encoding="utf-8")
voice = replace_once(
    voice,
    "    @Volatile private var activeTtsEngineStep = 0\n",
    "    @Volatile private var activeTtsEngineStep = 0\n"
    "    @Volatile private var ttsInitializationGeneration = 0\n"
    "    @Volatile private var ttsInitializationInProgress = false\n",
    "TTS initialization generation",
)

# Restore the historic Samsung male voice as the first engine. Google is tried
# second, then Android's configured engine only if it also exposes an explicit
# male pt-BR voice.
voice = replace_once(
    voice,
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
    "historic Samsung-first engine order",
)

# A TTS provider may never call OnInitListener on some Android builds. Bound
# each attempt, reject stale callbacks, and move to the next engine safely.
pattern = re.compile(
    r"    private fun initializeTextToSpeech\(engineStep: Int = 0\) \{.*?\n    \}\n\n    private fun handleTtsPlaybackError",
    re.S,
)
replacement = r'''    private fun initializeTextToSpeech(engineStep: Int = 0) {
        if (destroyed) return

        val attemptId = ++ttsInitializationGeneration
        activeTtsEngineStep = engineStep
        ttsInitializationInProgress = true
        ttsReady = false
        val previous = tts
        tts = null
        runCatching { previous?.stop() }
        runCatching { previous?.shutdown() }

        val requestedEngine = when (engineStep) {
            0 -> "com.samsung.SMT"
            1 -> "com.google.android.tts"
            else -> null
        }

        var candidate: TextToSpeech? = null
        var attemptFinished = false

        fun failAttempt() {
            handler.post {
                if (attemptId != ttsInitializationGeneration || destroyed || attemptFinished) return@post
                attemptFinished = true
                runCatching { candidate?.stop() }
                runCatching { candidate?.shutdown() }
                if (tts === candidate) tts = null
                ttsReady = false

                if (engineStep < 2) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                } else {
                    ttsInitializationInProgress = false
                    publishIdleOrListening()
                }
            }
        }

        val listener = TextToSpeech.OnInitListener { status ->
            handler.post {
                if (attemptId != ttsInitializationGeneration || destroyed) {
                    runCatching { candidate?.shutdown() }
                    return@post
                }
                if (attemptFinished) return@post

                val readyEngine = candidate
                if (status != TextToSpeech.SUCCESS || readyEngine == null) {
                    failAttempt()
                    return@post
                }

                tts = readyEngine
                if (!configurePortugueseVoice()) {
                    failAttempt()
                    return@post
                }

                attemptFinished = true
                ttsInitializationInProgress = false
                ttsReady = true
                readyEngine.setSpeechRate(0.96f)
                readyEngine.setPitch(0.90f)
                readyEngine.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {
                        handler.post {
                            speaking = true
                            emit(State.SPEAKING)
                        }
                    }

                    override fun onDone(utteranceId: String?) {
                        if (utteranceId == finalUtteranceId) {
                            handler.post { finishSpeaking() }
                        }
                    }

                    @Deprecated("Deprecated in Java")
                    override fun onError(utteranceId: String?) {
                        handleTtsPlaybackError(engineStep)
                    }

                    override fun onError(utteranceId: String?, errorCode: Int) {
                        handleTtsPlaybackError(engineStep)
                    }
                })
            }
        }

        try {
            candidate = if (requestedEngine != null) {
                TextToSpeech(appContext, listener, requestedEngine)
            } else {
                TextToSpeech(appContext, listener)
            }
            tts = candidate
        } catch (_: Throwable) {
            failAttempt()
            return
        }

        handler.postDelayed({
            if (attemptId == ttsInitializationGeneration && !destroyed && !attemptFinished) {
                failAttempt()
            }
        }, 6_000L)
    }

    private fun handleTtsPlaybackError'''
voice, count = pattern.subn(replacement, voice)
if count != 1:
    raise SystemExit(f"VC44 expected one TTS initializer; found {count}")

voice = replace_once(
    voice,
    "            if (attempt < 20) {\n                handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 250L)\n            } else {\n                speaking = false\n                waitingForReply = false\n                onErrorMessage(\"O mecanismo de voz do Android não ficou pronto.\")\n                publishIdleOrListening()\n            }",
    "            if (!ttsInitializationInProgress && attempt == 0) initializeTextToSpeech()\n            if (attempt < 80) {\n                handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 250L)\n            } else {\n                speaking = false\n                waitingForReply = false\n                onErrorMessage(\"Não encontrei uma voz masculina em português do Brasil. Ative a voz masculina do Samsung TTS ou do Google TTS nas definições de texto para voz.\")\n                publishIdleOrListening()\n            }",
    "bounded male-only TTS initialization wait",
)

voice = replace_once(
    voice,
    '''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(if (maleReady) 0.90f else 0.76f)
        tts?.setSpeechRate(0.96f)''',
    '''        if (!configurePortugueseVoice()) {
            if (activeTtsEngineStep < 2) {
                ttsReady = false
                initializeTextToSpeech(activeTtsEngineStep + 1)
                handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 350L)
            } else {
                speaking = false
                waitingForReply = false
                onErrorMessage("Não encontrei uma voz masculina em português do Brasil. Ative a voz masculina do Samsung TTS ou do Google TTS nas definições de texto para voz.")
                publishIdleOrListening()
            }
            return
        }
        tts?.setPitch(0.90f)
        tts?.setSpeechRate(0.96f)''',
    "fail closed when explicit male voice is unavailable",
)

# Remove obsolete unreachable fallback comments after the strict false return.
voice = voice.replace(
    '''        return false

        // Do not deliberately switch to an unspecified PT-BR voice here: on the
        // tested Samsung that resolves to the female default. Keep pt-BR locale
        // and use a lower pitch only as the last-resort compatibility path.
        return false''',
    "        return false",
)

required = [
    'versionCode = 44',
    'versionName = "0.3.19"',
]
build = BUILD.read_text(encoding="utf-8")
missing = [item for item in required if item not in build]
if missing:
    raise SystemExit("VC44 version identity missing: " + ", ".join(missing))

required_voice = [
    '0 -> "com.samsung.SMT"',
    '1 -> "com.google.android.tts"',
    "ttsInitializationGeneration",
    "ttsInitializationInProgress",
    "6_000L",
    "attempt < 80",
    "if (!configurePortugueseVoice())",
    "ttsInitializationInProgress",
    "explicitMale",
]
missing = [item for item in required_voice if item not in voice]
if missing:
    raise SystemExit("VC44 male-voice recovery invariants missing: " + ", ".join(missing))
if 'tts?.setPitch(if (maleReady)' in voice:
    raise SystemExit("VC44 must never synthesize using an unverified voice")
if "startListening(" in voice:
    raise SystemExit("VC44 must preserve silent AudioRecord capture")
VOICE.write_text(voice, encoding="utf-8")

print("VC44 applied: historical Samsung-first male voice, bounded engine recovery, and no unverified/female synthesis")
