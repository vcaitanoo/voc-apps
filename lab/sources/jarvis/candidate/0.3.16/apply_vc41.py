from pathlib import Path
import re

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC41 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_regex(text: str, pattern: str, replacement: str, label: str, count: int = 1) -> str:
    result, n = re.subn(pattern, replacement, text, count=count, flags=re.S)
    if n != count:
        raise SystemExit(f"VC41 expected {count} match(es) for {label}, found {n}")
    return result


# VC41 / 0.3.16 is based on the known-good VC39 chain, deliberately skipping
# VC40's regression that allowed an untagged (female-default) voice.
replace_once(BUILD, "versionCode = 39", "versionCode = 41", "versionCode")
replace_once(BUILD, 'versionName = "0.3.14"', 'versionName = "0.3.16"', "versionName")

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

VOICE.write_text(voice, encoding="utf-8")

build = BUILD.read_text(encoding="utf-8")
voice = VOICE.read_text(encoding="utf-8")
checks = [
    ("versionCode = 41" in build and 'versionName = "0.3.16"' in build, "identity"),
    ('0 -> "com.samsung.SMT"' in voice and '1 -> "com.google.android.tts"' in voice, "Samsung male voice engine first"),
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
        raise SystemExit("VC41 validation failed: " + label)

print("VC41 validated: explicit male PT-BR only; Samsung first; female/default fallback removed; no voice-failure notices")
