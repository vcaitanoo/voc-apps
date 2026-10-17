from pathlib import Path
import re

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC42 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_regex(text: str, pattern: str, replacement: str, label: str, count: int = 1) -> str:
    result, n = re.subn(pattern, replacement, text, count=count, flags=re.S)
    if n != count:
        raise SystemExit(f"VC42 expected {count} match(es) for {label}, found {n}")
    return result


# VC42 / 0.3.17 is based on the known-good VC39 chain, deliberately skipping
# VC40's regression that allowed an untagged (female-default) voice.
replace_once(BUILD, "versionCode = 39", "versionCode = 42", "versionCode")
replace_once(BUILD, 'versionName = "0.3.14"', 'versionName = "0.3.17"', "versionName")

voice = VOICE.read_text(encoding="utf-8")

# Brazilian Portuguese only. Do not let a Portuguese-from-Portugal voice score
# higher than PT-BR, and do not accept arbitrary locales as the voice fallback.
replace_once(
    VOICE,
    '''        // Preferir PT-PT; aceitar pt-BR se for a unica opcao instalada.
        runCatching {
            if (engine.isLanguageAvailable(europeanPortuguese) >= TextToSpeech.LANG_AVAILABLE) {
                engine.setLanguage(europeanPortuguese)
            } else {
                engine.setLanguage(brazilianPortuguese)
            }
        }''',
    '''        // Jarvis speech output must remain Brazilian Portuguese.
        runCatching { engine.setLanguage(brazilianPortuguese) }''',
    "force pt-BR TTS locale",
)
replace_once(
    VOICE,
    '''            // PT-PT passa a valer mais que pt-BR; a brasileira continua aceitavel
            // como recurso para nunca perder a voz masculina.
            if (language == "pt" && country == "PT") value += 12_000
            else if (language == "pt" && country == "BR") value += 10_000
            else if (language == "pt") value += 6_000''',
    '''            // Only a positively identified Brazilian Portuguese male voice is valid.
            if (language == "pt" && country == "BR") value += 12_000
            else return Int.MIN_VALUE''',
    "strict pt-BR-only male voice scoring",
)

replace_once(
    VOICE,
    '''            if (language == "pt" && country == "BR") value += 12_000
            else return Int.MIN_VALUE
            else return Int.MIN_VALUE''',
    '''            if (language == "pt" && country == "BR") value += 12_000
            else return Int.MIN_VALUE''',
    "remove duplicated non-PT-BR guard",
)


voice = VOICE.read_text(encoding="utf-8")  # Re-read changes written by replace_once above

# If the requested engine has no explicitly male PT-BR voice, continue trying
# the next engine; after the final attempt, return quietly instead of showing
# a voice-failure banner or accepting the engine's female default.
voice = replace_regex(
    voice,
    r'''else if \(!destroyed\) \{
\s*handler\.post \{
\s*emit\(State\.ERROR\)
\s*onErrorMessage\("Não encontrei uma voz masculina em português nos mecanismos de voz disponíveis\. Verifique as vozes instaladas no Samsung TTS ou no Google TTS\."\)
\s*\}
\s*\}''',
    'else if (!destroyed) {\n                    handler.post { publishIdleOrListening() }\n                }',
    "suppress missing male voice notification",
)

# Silence TTS-specific failures in the UI; keep the normal idle/listening reset.
voice = replace_regex(
    voice,
    r'''emit\(State\.ERROR\)
\s*onErrorMessage\("(?:Não consegui iniciar o mecanismo de voz do Android\. Verifique se o serviço de texto para voz está ativado\.|Não consegui abrir nenhum mecanismo de voz disponível neste telemóvel\.|Não consegui reproduzir a resposta em voz alta, mesmo após tentar os mecanismos de voz disponíveis\.|Não consegui reproduzir a resposta em voz alta\.)"\)''',
    'publishIdleOrListening()',
    "suppress TTS init/playback warnings",
    count=3,
)
voice = voice.replace('onErrorMessage("Não consegui iniciar a leitura em voz alta.")', '/* TTS falhou; não mostrar aviso de voz ao utilizador. */')
voice = voice.replace('onErrorMessage("Não encontrei uma voz masculina em português nos mecanismos de voz disponíveis. Verifique as vozes instaladas no Samsung TTS ou no Google TTS.")', '/* Sem voz masculina disponível: não usar voz feminina nem mostrar aviso. */')

# The speak path must independently refuse to synthesize unless it can reselect
# a real male PT-BR voice. Pitch is not used as a substitute for voice gender.
old_speak = '''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(if (maleReady) 0.90f else 0.76f)
        tts?.setSpeechRate(0.96f)'''
new_speak = '''        if (!configurePortugueseVoice()) {
            speaking = false
            waitingForReply = false
            publishIdleOrListening()
            return
        }
        tts?.setPitch(0.90f)
        tts?.setSpeechRate(0.96f)'''
replace_once(VOICE, old_speak, new_speak, "refuse any non-male speech synthesis")

# Remove legacy validation/UI callbacks for the male-only engine selection.
for forbidden in [
    "Não encontrei uma voz masculina em português nos mecanismos de voz disponíveis.",
    "Não consegui iniciar o mecanismo de voz do Android.",
    "Não consegui abrir nenhum mecanismo de voz disponível neste telemóvel.",
    "Não consegui reproduzir a resposta em voz alta",
    "Não consegui iniciar a leitura em voz alta.",
]:
    if forbidden in voice:
        # No visible voice-failure messages in the compiled controller.
        voice = voice.replace(forbidden, "/* mensagem de voz desativada */")

REMINDER = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/ReminderSpeechService.kt"
reminder = REMINDER.read_text(encoding="utf-8")

# Scheduled reminders use a separate Android TTS service. Apply the same
# strict PT-BR male-only rule there; never use a pitch-deepened female default.
reminder = replace_regex(
    reminder,
    r'''            configurePortugueseVoice\(engine\)
            engine\.setSpeechRate\(0\.96f\)
            engine\.setPitch\(0\.90f\)''',
    '''            if (!configurePortugueseVoice(engine)) {
                runCatching { engine.stop() }
                runCatching { engine.shutdown() }
                tts = null
                stopSpeechAndSelf()
                return@TextToSpeech
            }
            engine.setSpeechRate(0.96f)
            engine.setPitch(0.90f)''',
    "strict reminder TTS voice",
)
reminder = replace_regex(
    reminder,
    r'    private fun configurePortugueseVoice\(engine: TextToSpeech\)(?:: Boolean)? \{[\s\S]*?\n    \}',
    '''    private fun configurePortugueseVoice(engine: TextToSpeech): Boolean {
        val ptBr = Locale("pt", "BR")
        val languageReady = runCatching {
            engine.setLanguage(ptBr) >= TextToSpeech.LANG_AVAILABLE
        }.getOrDefault(false)
        if (!languageReady) return false

        fun explicitMale(voice: android.speech.tts.Voice): Boolean {
            val normalized = (voice.name + " " + voice.features.joinToString(" ")).lowercase(Locale.ROOT)
            if (listOf("female", "feminina", "mulher", "woman", "_f00", "-f00", "#female_").any(normalized::contains)) return false
            return listOf("male", "masculino", "homem", "#male_", "_m00", "-m00", "_m01", "-m01", "_m02", "-m02", "_m03", "-m03").any(normalized::contains)
        }

        val candidates = runCatching {
            engine.voices.orEmpty()
                .filter {
                    it.locale.language.equals("pt", ignoreCase = true) &&
                    it.locale.country.equals("BR", ignoreCase = true) &&
                    explicitMale(it)
                }
                .sortedWith(
                    compareByDescending<android.speech.tts.Voice> { if (it.name.contains("#male_", ignoreCase = true)) 1 else 0 }
                        .thenByDescending { it.quality }
                        .thenBy { it.isNetworkConnectionRequired }
                )
        }.getOrDefault(emptyList())
        val selected = candidates.firstOrNull() ?: return false
        return runCatching {
            engine.voice = selected
            engine.voice?.name == selected.name &&
                engine.voice?.locale?.language.equals("pt", ignoreCase = true) &&
                engine.voice?.locale?.country.equals("BR", ignoreCase = true)
        }.getOrDefault(false)
    }''',
    "replace reminder voice selector",
)
REMINDER.write_text(reminder, encoding="utf-8")

# Prefer Google TTS first, where Brazilian male voices are commonly explicitly tagged.
voice = voice.replace('0 -> "com.samsung.SMT"', '0 -> "com.google.android.tts"', 1)
voice = voice.replace('1 -> "com.google.android.tts"', '1 -> "com.samsung.SMT"', 1)
VOICE.write_text(voice, encoding="utf-8")

build = BUILD.read_text(encoding="utf-8")
voice = VOICE.read_text(encoding="utf-8")
checks = [
    ("versionCode = 42" in build and 'versionName = "0.3.17"' in build, "identity"),
    ('0 -> "com.google.android.tts"' in voice and '1 -> "com.samsung.SMT"' in voice, "Google explicit male voice engine first"),
    ('country == "BR") value += 12_000' in voice, "PT-BR first"),
    ('else return Int.MIN_VALUE' in voice, "non-PT-BR voices rejected"),
    ('explicitMale' in voice and 'female' in voice, "explicit male selector retained"),
    ('configureFallbackPortugueseVoice' not in voice, "regressive untagged voice fallback absent"),
    ('tts?.setPitch(0.90f)' in voice, "historic male pitch restored"),
    ('onErrorMessage("Não encontrei uma voz masculina' not in voice, "no male-voice failure notice"),
    ('onErrorMessage("Não consegui reproduzir a resposta em voz alta' not in voice, "no TTS playback failure notice"),
    ('onErrorMessage("Não consegui iniciar a leitura em voz alta.' not in voice, "no TTS startup failure notice"),
]
for ok, label in checks:
    if not ok:
        raise SystemExit("VC42 validation failed: " + label)

print("VC42 validated: explicit male PT-BR only; Google TTS first; female/default fallback removed; no voice-failure notices")
