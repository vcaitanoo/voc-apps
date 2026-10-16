from pathlib import Path
import re
import shutil

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'
MANIFEST = APP / 'src/main/AndroidManifest.xml'
RES = APP / 'src/main/res'
LOGO = Path('lab/sources/jarvis/candidate/0.2.22/overrides/jarvis_logo.png')


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:180]!r}')
    path.write_text(text.replace(old, new, 1))


# Exact successor of VC23. No listening/beep logic is modified in VC24.
replace_once(BUILD, 'versionCode = 23', 'versionCode = 24')
replace_once(BUILD, 'versionName = "0.2.21"', 'versionName = "0.2.22"')

voice = VOICE.read_text()

# -----------------------------------------------------------------------------
# SPOKEN RESPONSE ONLY
# VC23 could become silent when the installed TTS engine did not expose a voice
# whose NAME explicitly contained "male". Prefer a PT-BR male voice, but never
# refuse to speak merely because that metadata is absent.
# -----------------------------------------------------------------------------
configure_pattern = re.compile(
    r'    private fun configureBrazilianMaleVoice\(\): Boolean \{[\s\S]*?\n    \}\n\n'
    r'    private fun splitForSpeech',
    re.M,
)
configure_replacement = '''    private fun configureBrazilianMaleVoice(): Boolean {
        val engine = tts ?: return false
        runCatching { engine.setLanguage(brazilianPortuguese) }

        fun isMale(name: String): Boolean {
            val normalized = name.lowercase(Locale.ROOT)
            return listOf("male", "masculino", "homem", " man ", "_man_", "-man-").any(normalized::contains)
        }
        fun isFemale(name: String): Boolean {
            val normalized = name.lowercase(Locale.ROOT)
            return listOf("female", "feminina", "mulher", "woman").any(normalized::contains)
        }

        val voices = runCatching { engine.voices?.toList().orEmpty() }.getOrDefault(emptyList())
        val ptBr = voices.filter {
            it.locale.language.equals("pt", ignoreCase = true) &&
                it.locale.country.equals("BR", ignoreCase = true)
        }
        val male = ptBr
            .filter { isMale(it.name) && !isFemale(it.name) }
            .sortedWith(compareByDescending<android.speech.tts.Voice> { it.quality }.thenBy { it.isNetworkConnectionRequired })
            .firstOrNull()
        val anyPtBr = ptBr
            .sortedWith(compareByDescending<android.speech.tts.Voice> { it.quality }.thenBy { it.isNetworkConnectionRequired })
            .firstOrNull()
        val anyPortuguese = voices
            .filter { it.locale.language.equals("pt", ignoreCase = true) }
            .sortedWith(compareByDescending<android.speech.tts.Voice> { it.quality }.thenBy { it.isNetworkConnectionRequired })
            .firstOrNull()
        val selected = male ?: anyPtBr ?: anyPortuguese
        if (selected != null) runCatching { engine.voice = selected }
        return true
    }

    private fun splitForSpeech'''
voice, count = configure_pattern.subn(configure_replacement, voice, count=1)
if count != 1:
    raise SystemExit('VC23 local TTS voice selector not found')

speak_pattern = re.compile(
    r'    private fun speakWithMaleOnlyLocalFallback\(text: String\) \{[\s\S]*?\n    \}\n\n'
    r'    private fun finishSpeaking\(\) \{',
    re.M,
)
speak_replacement = '''    private fun speakWithMaleOnlyLocalFallback(text: String, attempt: Int = 0) {
        if (!voiceOutputEnabled || destroyed) {
            finishSpeaking()
            return
        }
        if (tts == null) {
            if (attempt < 8) {
                handler.postDelayed({ speakWithMaleOnlyLocalFallback(text, attempt + 1) }, 250L)
            } else {
                speaking = false
                waitingForReply = false
                onErrorMessage("O mecanismo de voz do Android não ficou pronto.")
                publishIdleOrListening()
            }
            return
        }

        configureBrazilianMaleVoice()
        tts?.setPitch(0.90f)
        tts?.setSpeechRate(0.96f)
        val result = tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "jarvis-response")
        if (result == null || result == TextToSpeech.ERROR) {
            if (attempt < 2) {
                handler.postDelayed({ speakWithMaleOnlyLocalFallback(text, attempt + 1) }, 300L)
            } else {
                speaking = false
                waitingForReply = false
                onErrorMessage("Não consegui iniciar a leitura em voz alta.")
                publishIdleOrListening()
            }
        }
    }

    private fun finishSpeaking() {'''
voice, count = speak_pattern.subn(speak_replacement, voice, count=1)
if count != 1:
    raise SystemExit('VC23 local TTS speaking function not found')

VOICE.write_text(voice)

# -----------------------------------------------------------------------------
# APPROVED LAUNCHER LOGO ONLY
# Use the valid approved logo copied from the user's Library. Rebuild both legacy
# density launchers and Android 8+ adaptive launchers, then explicitly point the
# manifest at those resources.
# -----------------------------------------------------------------------------
if not LOGO.exists() or LOGO.stat().st_size < 1000:
    raise SystemExit('approved Jarvis logo missing or invalid')

for folder in RES.glob('mipmap-*'):
    if 'anydpi' in folder.name:
        continue
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LOGO, folder / 'ic_launcher.png')
    shutil.copyfile(LOGO, folder / 'ic_launcher_round.png')

drawable_nodpi = RES / 'drawable-nodpi'
drawable_nodpi.mkdir(parents=True, exist_ok=True)
shutil.copyfile(LOGO, drawable_nodpi / 'jarvis_launcher_logo.png')

drawable = RES / 'drawable'
drawable.mkdir(parents=True, exist_ok=True)
(drawable / 'jarvis_launcher_foreground.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<inset xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/jarvis_launcher_logo"
    android:inset="12%" />
''')

adaptive = RES / 'mipmap-anydpi-v26'
adaptive.mkdir(parents=True, exist_ok=True)
adaptive_xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/black" />
    <foreground android:drawable="@drawable/jarvis_launcher_foreground" />
</adaptive-icon>
'''
(adaptive / 'ic_launcher.xml').write_text(adaptive_xml)
(adaptive / 'ic_launcher_round.xml').write_text(adaptive_xml)

manifest = MANIFEST.read_text()
match = re.search(r'<application\b[^>]*>', manifest, re.S)
if not match:
    raise SystemExit('application tag missing')
tag = match.group(0)
if 'android:icon=' in tag:
    tag = re.sub(r'android:icon="[^"]+"', 'android:icon="@mipmap/ic_launcher"', tag, count=1)
else:
    tag = tag[:-1] + '\n        android:icon="@mipmap/ic_launcher">'
if 'android:roundIcon=' in tag:
    tag = re.sub(r'android:roundIcon="[^"]+"', 'android:roundIcon="@mipmap/ic_launcher_round"', tag, count=1)
else:
    tag = tag[:-1] + '\n        android:roundIcon="@mipmap/ic_launcher_round">'
manifest = manifest[:match.start()] + tag + manifest[match.end():]
MANIFEST.write_text(manifest)

print('VC24 applied: spoken TTS restored + approved launcher logo restored')
