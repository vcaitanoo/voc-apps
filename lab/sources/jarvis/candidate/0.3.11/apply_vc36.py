from pathlib import Path
import re

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
BRAIN = APP / "src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC36 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(BUILD, 'versionCode = 35', 'versionCode = 36', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.10"', 'versionName = "0.3.11"', 'versionName')

# ---------------------------------------------------------------------------
# Portugues de Portugal, mantendo a voz masculina.
#
# A selecao de voz e o que o dono pediu explicitamente para preservar, por isso
# a logica "isMale" fica intacta. O que muda e o locale: de pt-BR para pt-PT.
#
# A selectiva de voz masculina exigia country == BR, o que em primeiro lugar
# praticamente nao encontrava voz PT-PT instalada. Passa a aceitar PT-PT
# primeiro e pt-BR como recurso, para nunca perder a voz masculina se o
# dispositivo so tiver a brasileira.
# ---------------------------------------------------------------------------
replace_once(
    VOICE,
    'private val brazilianPortuguese = Locale("pt", "BR")',
    '''private val europeanPortuguese = Locale("pt", "PT")
    // Recurso: alguns dispositivos so tem voz pt-BR instalada. Serve para ter
    // sempre uma voz masculina, mesmo que a pt-PT nao exista.
    private val brazilianPortuguese = Locale("pt", "BR")''',
    'pt-PT locale',
)

replace_once(
    VOICE,
    '''        runCatching { engine.setLanguage(brazilianPortuguese) }
''',
    '''        // Preferir PT-PT; aceitar pt-BR se for a unica opcao instalada.
        runCatching {
            if (engine.isLanguageAvailable(europeanPortuguese) >= TextToSpeech.LANG_AVAILABLE) {
                engine.setLanguage(europeanPortuguese)
            } else {
                engine.setLanguage(brazilianPortuguese)
            }
        }
''',
    'engine language',
)

# O score dava 10_000 a pt-BR e 6_000 a qualquer outro pt, o que tornava
# praticamente impossivel escolher uma voz PT-PT mesmo quando existe.
replace_once(
    VOICE,
    '''            if (language == "pt" && country == "BR") value += 10_000
            else if (language == "pt") value += 6_000''',
    '''            // PT-PT passa a valer mais que pt-BR; a brasileira continua aceitavel
            // como recurso para nunca perder a voz masculina.
            if (language == "pt" && country == "PT") value += 12_000
            else if (language == "pt" && country == "BR") value += 10_000
            else if (language == "pt") value += 6_000''',
    'male voice scoring',
)

# ---------------------------------------------------------------------------
# A resposta ao "Jarvis" estava escrita para uma persona que ja nao e a nossa.
# Dizia "usuario", pedia confirmacao de que estava atento e autorizava
# referencias a contexto sem como as usar. Reescrita para a persona actual:
# pt-PT, sem bordao fixo, sem "estou aqui", sem mencoes a infraestrutura.
# ---------------------------------------------------------------------------
replace_once(
    BRAIN,
    '''            O usuário apenas chamou você dizendo “Jarvis”. Responda em UMA frase muito curta, natural e oral, como uma confirmação de que você está atento e pronto para ouvir o que vem a seguir. Varie sempre a formulação; não use um bordão fixo. Leve em conta, quando fizer sentido, o horário atual, o contexto recente e memórias relevantes do usuário, sem forçar referências pessoais. Não explique o que está fazendo, não mencione TTS, não use markdown e não escreva rótulos como “texto para ser lido”.''',
    '''            O dono chamou-te pelo nome, sem dizer mais nada. Nao respondas ao nome como se fosse uma pergunta: confirma que estas atento e pronto para ouvir o que vem a seguir.
            Regras desta resposta:
            - UMA frase. Curta. Oral. Nada de listas, nada de markdown, nada de aspas.
            - Nao digas "estou aqui" nem "podes falar" nem "em que posso ajudar". Usa outras palavras.
            - Cada vez uma formula diferente. Nao tenhas um bordao fixo.
            - Se souberes algo concreto e recente do dono (um lembrete proximo, algo em atraso), podes menciona-lo em meia frase. Uma so. Nunca despejares a agenda.
            - Nao anuncies o que estas a fazer nem menciones infraestrutura, audio ou modelos.
            - Portugues de Portugal.''',
    'wake-word ack prompt',
)

print("VC36 / 0.3.11 source prepared")
