from pathlib import Path

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC40 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(BUILD, "versionCode = 39", "versionCode = 40", "versionCode")
replace_once(BUILD, 'versionName = "0.3.14"', 'versionName = "0.3.15"', "versionName")

old_init = '''            val maleReady = configurePortugueseVoice()
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
            tts?.setPitch(0.90f)'''
new_init = '''            val explicitMaleReady = configurePortugueseVoice()
            if (!explicitMaleReady) configureFallbackPortugueseVoice()

            // Do not disable Jarvis just because Android did not label a
            // Portuguese voice as male. Prefer an installed Portuguese voice
            // and use a deeper pitch; preserve the historic pitch for a tagged male voice.
            ttsReady = true
            tts?.setSpeechRate(0.94f)
            tts?.setPitch(if (explicitMaleReady) 0.90f else 0.66f)'''
replace_once(VOICE, old_init, new_init, "mandatory male voice rejection")

replace_once(
    VOICE,
    "    private fun configurePortugueseVoice(): Boolean {",
    '''    private fun configureFallbackPortugueseVoice(): Boolean {
        val engine = tts ?: return false
        val candidates = runCatching {
            engine.voices
                .filter { it.locale.language.equals("pt", ignoreCase = true) }
                .sortedWith(
                    compareBy<android.speech.tts.Voice>(
                        {
                            val n = it.name.lowercase()
                            if (n.contains("male") || n.contains("_m00") || n.contains("#male_")) 0 else 1
                        },
                        {
                            when (it.locale.country.uppercase()) {
                                "PT" -> 0
                                "BR" -> 1
                                else -> 2
                            }
                        },
                        { it.isNetworkConnectionRequired },
                        { it.name }
                    )
                )
        }.getOrDefault(emptyList())

        for (voice in candidates) {
            val applied = runCatching {
                engine.voice = voice
                engine.voice?.name == voice.name
            }.getOrDefault(false)
            if (applied) return true
        }

        return runCatching {
            engine.setLanguage(europeanPortuguese) >= TextToSpeech.LANG_AVAILABLE ||
                engine.setLanguage(brazilianPortuguese) >= TextToSpeech.LANG_AVAILABLE
        }.getOrDefault(false)
    }

    private fun configurePortugueseVoice(): Boolean {''',
    "Portuguese voice fallback selector"
)

replace_once(
    VOICE,
    '''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(if (maleReady) 0.90f else 0.76f)
        tts?.setSpeechRate(0.96f)''',
    '''        val explicitMaleReady = configurePortugueseVoice()
        if (!explicitMaleReady) configureFallbackPortugueseVoice()
        tts?.setPitch(if (explicitMaleReady) 0.90f else 0.66f)
        tts?.setSpeechRate(0.94f)''',
    "speak path fallback"
)

replace_once(
    VOICE,
    "if (attempt < 20)",
    "if (attempt < 60)",
    "allow slower Android TTS initialization"
)

voice = VOICE.read_text(encoding="utf-8")
build = BUILD.read_text(encoding="utf-8")
checks = [
    ("versionCode = 40" in build and 'versionName = "0.3.15"' in build, "identity"),
    ("configureFallbackPortugueseVoice" in voice, "Portuguese voice fallback"),
    ("tts?.setPitch(if (explicitMaleReady) 0.90f else 0.66f)" in voice, "deeper fallback pitch"),
    ("Não encontrei uma voz masculina em português" not in voice, "old hard failure removed"),
    ('0 -> "com.samsung.SMT"' in voice and '1 -> "com.google.android.tts"' in voice, "Samsung-first engine order retained"),
    ("ttsReady = true" in voice, "TTS readiness retained"),
]
for ok, label in checks:
    if not ok:
        raise SystemExit("VC40 validation failed: " + label)

print("VC40 source patch validated: Portuguese voice fallback; no hard stop for untagged voices")
