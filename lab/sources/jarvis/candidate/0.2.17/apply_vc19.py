from pathlib import Path
import shutil

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
MAIN = APP / 'src/main/java/pt/vcaitano/jarvis/MainActivity.kt'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'
LOGO = Path('lab/sources/jarvis/candidate/0.2.17/overrides/jarvis_logo.png')


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:120]!r}')
    path.write_text(text.replace(old, new, 1))

# Version: exact successor of VC18.
replace_once(BUILD, 'versionCode = 18', 'versionCode = 19')
replace_once(BUILD, 'versionName = "0.2.16"', 'versionName = "0.2.17"')

# Listening: explicit foreground button must accept normal speech, not require wake word.
replace_once(
    VOICE,
    'private const val RESTART_DELAY_MS = 450L\n        private const val BUSY_RESTART_DELAY_MS = 1_200L',
    'private const val RESTART_DELAY_MS = 1_800L\n        private const val BUSY_RESTART_DELAY_MS = 3_000L'
)
replace_once(
    VOICE,
    'putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 1_750L)\n            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1_400L)\n            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 320L)',
    'putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 2_500L)\n            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 1_800L)\n            putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS, 500L)'
)
replace_once(
    VOICE,
    'try {\n            r.cancel()\n            r.startListening(recognitionIntent())',
    'try {\n            r.startListening(recognitionIntent())'
)
replace_once(
    VOICE,
    'val now = System.currentTimeMillis()\n        val wakeMatch = WAKE_WORD.find(clean)',
    '''val now = System.currentTimeMillis()

        // When the user explicitly activates "Começar a ouvir" in the foreground,
        // every recognized phrase is intentional input. Wake-word gating remains
        // only for the background listening service.
        if (!managedByListeningService && continuousEnabled) {
            wakeConversationUntilMs = now + WAKE_WINDOW_MS
            waitingForReply = true
            listening = false
            onFinalText(clean)
            return
        }

        val wakeMatch = WAKE_WORD.find(clean)'''
)

# Brain client/UI: anonymous chat is valid. Do not report missing login or fake internet errors.
old_block = '''            var hadSession = AuthSessionStore.load(this@MainActivity) != null
            var failureStatus: Int? = null
            var failureDetail: String? = null
            var response: BrainClient.ChatResponse? = null

            try {
                val token = AuthSessionStore.validAccessToken(this@MainActivity)
                hadSession = token != null
                response = BrainClient.chat(token, text)
            } catch (e: BrainClient.ChatException) {
                failureStatus = e.httpStatus
                failureDetail = e.serverMessage
                if (e.httpStatus == 401) {
                    val renewed = AuthSessionStore.refreshedAccessToken(this@MainActivity)
                    if (renewed != null) {
                        try {
                            response = BrainClient.chat(renewed, text)
                            failureStatus = null
                            failureDetail = null
                            hadSession = true
                        } catch (e2: BrainClient.ChatException) {
                            failureStatus = e2.httpStatus
                            failureDetail = e2.serverMessage
                        }
                    }
                }
            }
'''
new_block = '''            var failureStatus: Int? = null
            var failureDetail: String? = null
            var response: BrainClient.ChatResponse? = null

            fun attemptChat(token: String?): BrainClient.ChatResponse? {
                repeat(2) { attempt ->
                    try {
                        val value = BrainClient.chat(token, text)
                        if (value != null) return value
                    } catch (e: BrainClient.ChatException) {
                        failureStatus = e.httpStatus
                        failureDetail = e.serverMessage
                        if (e.httpStatus !in 500..599 && e.httpStatus != 429) throw e
                    }
                    if (attempt == 0) Thread.sleep(450L)
                }
                return null
            }

            val token = AuthSessionStore.validAccessToken(this@MainActivity)
            try {
                response = attemptChat(token)
            } catch (e: BrainClient.ChatException) {
                failureStatus = e.httpStatus
                failureDetail = e.serverMessage
                if (e.httpStatus == 401) {
                    val renewed = AuthSessionStore.refreshedAccessToken(this@MainActivity)
                    response = if (renewed != null) {
                        runCatching { attemptChat(renewed) }.getOrNull()
                    } else null
                    if (response == null) {
                        // The resilient brain accepts anonymous chat; a stale login
                        // must never prevent the assistant from answering.
                        response = runCatching { attemptChat(null) }.getOrNull()
                    }
                }
            }

            if (response == null && token != null && failureStatus != 401) {
                response = runCatching { attemptChat(null) }.getOrNull()
            }
'''
replace_once(MAIN, old_block, new_block)
replace_once(
    MAIN,
    '''val sysText = when {
                        !hadSession -> "Preciso de login para pensar direito. Entra na aba de sessão com seu email e senha."
                        status == 401 -> "Sua sessão expirou e não consegui renová-la. Faz login de novo, por favor."
                        status == 429 -> "A cota das IAs do cérebro estourou agora. Espera alguns minutos e me chama de novo."
                        status != null && status in 500..599 ->
                            "O cérebro está fora do ar neste momento" + (detail?.let { " ($it)" } ?: "") + ". Tenta de novo em instantes."
                        else -> "Não consegui falar com o cérebro. Confere a internet e tenta de novo."
                    }''',
    '''val sysText = when {
                        status == 429 -> "O cérebro está temporariamente ocupado. Tenta novamente em instantes."
                        status != null && status in 500..599 -> "O cérebro não respondeu agora. Tenta novamente em instantes."
                        status == 401 -> "A sessão não foi aceita, mas o Jarvis também tentou o acesso direto. Tenta novamente."
                        else -> "O cérebro não respondeu a esta tentativa. Tenta novamente."
                    }'''
)

# Exact approved logo becomes launcher icon in every density folder.
if not LOGO.exists():
    raise SystemExit('approved Jarvis logo missing')
for folder in APP.glob('src/main/res/mipmap-*'):
    dest = folder / 'ic_launcher.png'
    if dest.exists():
        shutil.copyfile(LOGO, dest)
    round_dest = folder / 'ic_launcher_round.png'
    if round_dest.exists():
        shutil.copyfile(LOGO, round_dest)

print('VC19 patch applied')
