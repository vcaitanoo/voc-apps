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

# Exact successor of VC20. Only listening changes.
replace_once(BUILD, 'versionCode = 20', 'versionCode = 21')
replace_once(BUILD, 'versionName = "0.2.18"', 'versionName = "0.2.19"')

# VC20 proved the background service can be stopped before foreground listening.
# Cloud STT providers are currently unavailable, so foreground uses Android's
# recognizer directly instead of raw-audio -> server transcription.
old_foreground = '''        // Foreground mode intentionally avoids SpeechRecognizer. Samsung/Google recognition
        // sessions may emit an audible start/end beep and repeated sessions can fight the
        // background service. Raw AudioRecord is silent and gives this controller sole
        // ownership of the microphone while the conversation screen is active.
        if (!managedByListeningService) {
            if (JarvisListeningService.isBackgroundControllerActive()) {
                JarvisListeningService.stop(appContext)
                startRecognitionSoon(700L)
                return
            }
            startRawForegroundCapture()
            return
        }

        val r = ensureRecognizer()
'''
new_foreground = '''        // Foreground and background never own the microphone at the same time.
        // Prefer Android's on-device recognizer when available; it avoids the broken
        // cloud-STT dependency and keeps recognition local on supported devices.
        if (!managedByListeningService && JarvisListeningService.isBackgroundControllerActive()) {
            JarvisListeningService.stop(appContext)
            startRecognitionSoon(700L)
            return
        }

        val r = ensureRecognizer()
'''
replace_once(VOICE, old_foreground, new_foreground)

# Foreground must not enter a rapid retry loop. A failed/no-match recognition waits
# several seconds before the next session; this prevents Samsung's repeated beep loop.
old_error = '''                when (error) {
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> {
                        emit(State.ERROR)
                        onErrorMessage("O Android bloqueou o acesso ao microfone.")
                    }
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY,
                    SpeechRecognizer.ERROR_CLIENT,
                    SpeechRecognizer.ERROR_SERVER_DISCONNECTED -> {
                        destroyRecognizerOnly()
                        startRecognitionSoon(BUSY_RESTART_DELAY_MS)
                    }
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> {
                        onErrorMessage(
                            if (recognizerIsOnDevice) "O reconhecimento de voz local falhou; vou tentar novamente."
                            else "O serviço de reconhecimento de voz do Android ficou sem rede; vou tentar novamente."
                        )
                        startRecognitionSoon(BUSY_RESTART_DELAY_MS)
                    }
                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> startRecognitionSoon(RESTART_DELAY_MS)
                    else -> startRecognitionSoon(BUSY_RESTART_DELAY_MS)
                }
'''
new_error = '''                val foregroundDelay = 5_000L
                when (error) {
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> {
                        emit(State.ERROR)
                        onErrorMessage("O Android bloqueou o acesso ao microfone.")
                    }
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY,
                    SpeechRecognizer.ERROR_CLIENT,
                    SpeechRecognizer.ERROR_SERVER_DISCONNECTED -> {
                        destroyRecognizerOnly()
                        startRecognitionSoon(if (managedByListeningService) BUSY_RESTART_DELAY_MS else foregroundDelay)
                    }
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> {
                        if (managedByListeningService) {
                            onErrorMessage(
                                if (recognizerIsOnDevice) "O reconhecimento de voz local falhou; vou tentar novamente."
                                else "O serviço de reconhecimento de voz do Android ficou sem rede; vou tentar novamente."
                            )
                        }
                        startRecognitionSoon(if (managedByListeningService) BUSY_RESTART_DELAY_MS else foregroundDelay)
                    }
                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                        startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else foregroundDelay)
                    else -> startRecognitionSoon(if (managedByListeningService) BUSY_RESTART_DELAY_MS else foregroundDelay)
                }
'''
replace_once(VOICE, old_error, new_error)

# Blank foreground results also wait instead of immediately opening another session.
replace_once(
    VOICE,
    'if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(RESTART_DELAY_MS)',
    'if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(if (managedByListeningService) RESTART_DELAY_MS else 5_000L)'
)

print('VC21 local-listening patch applied')
