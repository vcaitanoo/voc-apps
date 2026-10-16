from pathlib import Path
import re

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC35 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))

replace_once(BUILD, 'versionCode = 34', 'versionCode = 35', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.9"', 'versionName = "0.3.10"', 'versionName')

voice = VOICE.read_text()

# 1) Return to the capture topology that still physically heard the user:
# MIC primary, VOICE_RECOGNITION only as fallback.
replace_once(
    VOICE,
    '''        for (source in intArrayOf(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            MediaRecorder.AudioSource.MIC
        )) {''',
    '''        for (source in intArrayOf(
            MediaRecorder.AudioSource.MIC,
            MediaRecorder.AudioSource.VOICE_RECOGNITION
        )) {''',
    'MIC primary source',
)
voice = VOICE.read_text()

# 2) Restore device AGC/NS, but keep VC34's important fix: AudioRecord is
# actually started BEFORE LISTENING is emitted to UI/user.
old_start = '''        // Start the microphone BEFORE telling the UI/user that Jarvis is
        // listening. Previously LISTENING was emitted first and AudioRecord was
        // started only inside the worker thread, which clipped the first word.
        try {
            recorder.startRecording()
        } catch (_: Throwable) {
            runCatching { recorder.release() }
            emit(State.ERROR)
            onErrorMessage("Não consegui iniciar o microfone para ouvir.")
            return
        }

        rawRecorder = recorder
'''
new_start = '''        val noiseSuppressor = runCatching {
            if (NoiseSuppressor.isAvailable()) {
                NoiseSuppressor.create(recorder.audioSessionId)?.apply { enabled = true }
            } else null
        }.getOrNull()
        val automaticGainControl = runCatching {
            if (AutomaticGainControl.isAvailable()) {
                AutomaticGainControl.create(recorder.audioSessionId)?.apply { enabled = true }
            } else null
        }.getOrNull()

        // Do not announce LISTENING until the microphone is already recording.
        try {
            recorder.startRecording()
        } catch (_: Throwable) {
            runCatching { noiseSuppressor?.release() }
            runCatching { automaticGainControl?.release() }
            runCatching { recorder.release() }
            emit(State.ERROR)
            onErrorMessage("Não consegui iniciar o microfone para ouvir.")
            return
        }

        rawRecorder = recorder
'''
if old_start not in voice:
    raise SystemExit('VC35 recorder start block missing')
voice = voice.replace(old_start, new_start, 1)

# Release effects together with recorder inside raw capture.
raw_start = voice.index('    private fun startRawForegroundCapture() {')
raw_end = voice.index('\n    private fun ', raw_start + 10)
segment = voice[raw_start:raw_end]
release_anchor = '                runCatching { recorder.release() }\n'
release_pos = segment.rfind(release_anchor)
if release_pos < 0:
    raise SystemExit('VC35 recorder release anchor missing')
segment = (
    segment[:release_pos]
    + '                runCatching { noiseSuppressor?.release() }\n'
    + '                runCatching { automaticGainControl?.release() }\n'
    + release_anchor
    + segment[release_pos + len(release_anchor):]
)
voice = voice[:raw_start] + segment + voice[raw_end:]

# 3) VoicePrint must protect the brain, not prevent transcription diagnostics.
# Transcribe first, then reject non-owner speech before routeTranscribedSpeech().
old_gate = '''            val capturedPcm = pcm.toByteArray()

            if (!VoicePrint.isEnrolled(appContext)) {
                handler.post {
                    emit(State.ERROR)
                    onErrorMessage("Cadastre sua voz nas Configurações para o Jarvis responder somente a você.")
                }
                return@Thread
            }
            if (!VoicePrint.matches(appContext, capturedPcm)) {
                handler.post {
                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(40L)
                    else publishIdleOrListening()
                }
                return@Thread
            }

            val wav = pcm16ToWav(capturedPcm, SAMPLE_RATE)
            val token = AuthSessionStore.validAccessToken(appContext)
            val text = BrainClient.transcribe(token, wav).orEmpty().trim()
'''
new_gate = '''            val capturedPcm = pcm.toByteArray()
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
            }
'''
if old_gate not in voice:
    raise SystemExit('VC35 VoicePrint pre-STT gate anchor missing')
voice = voice.replace(old_gate, new_gate, 1)

# 4) Deterministic TTS engine order. Try Google male PT-BR first, then
# Samsung male PT-BR, then the Android default engine only as compatibility.
voice = voice.replace('initializeTextToSpeech(preferSamsung = false)', 'initializeTextToSpeech()', 1)

pattern = re.compile(
    r'    private fun initializeTextToSpeech\(preferSamsung: Boolean\) \{.*?\n    private fun configurePortugueseVoice\(\): Boolean \{',
    re.S,
)
replacement = '''    private fun initializeTextToSpeech(engineStep: Int = 0) {
        val requestedEngine = when (engineStep) {
            0 -> "com.google.android.tts"
            1 -> "com.samsung.SMT"
            else -> null
        }

        val listener = TextToSpeech.OnInitListener { status ->
            if (status != TextToSpeech.SUCCESS) {
                runCatching { tts?.shutdown() }
                tts = null
                if (engineStep < 2 && !destroyed) {
                    handler.post { initializeTextToSpeech(engineStep + 1) }
                }
                return@OnInitListener
            }

            val maleReady = configurePortugueseVoice()
            if (!maleReady && engineStep < 2 && !destroyed) {
                runCatching { tts?.shutdown() }
                tts = null
                handler.post { initializeTextToSpeech(engineStep + 1) }
                return@OnInitListener
            }

            tts?.setSpeechRate(0.96f)
            // Real male voice keeps historical pitch. Only the final
            // compatibility fallback receives a deeper pitch.
            tts?.setPitch(if (maleReady) 0.90f else 0.76f)
            tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
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
                    handler.post {
                        SpeechCoordinator.release(speechOwnerId)
                        speaking = false
                        waitingForReply = false
                        onErrorMessage("Não consegui reproduzir a resposta em voz alta.")
                        publishIdleOrListening()
                    }
                }
            })
        }

        tts = if (requestedEngine != null) {
            TextToSpeech(appContext, listener, requestedEngine)
        } else {
            TextToSpeech(appContext, listener)
        }
    }

    private fun configurePortugueseVoice(): Boolean {'''
voice, count = pattern.subn(replacement, voice, count=1)
if count != 1:
    raise SystemExit('VC35 TTS initialization replacement failed')

# Speaking path must preserve real-male preference and historical cadence.
voice = voice.replace(
    '''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(0.90f)
        tts?.setSpeechRate(0.96f)
''',
    '''        val maleReady = configurePortugueseVoice()
        tts?.setPitch(if (maleReady) 0.90f else 0.76f)
        tts?.setSpeechRate(0.96f)
''',
    1,
)

VOICE.write_text(voice)

final_build = BUILD.read_text()
final_voice = VOICE.read_text()
raw_start = final_voice.index('    private fun startRawForegroundCapture() {')
raw_end = final_voice.index('\n    private fun ', raw_start + 10)
raw_segment = final_voice[raw_start:raw_end]
brain_call = raw_segment.index('BrainClient.transcribe(token, wav)')
owner_call = raw_segment.index('VoicePrint.matches(appContext, capturedPcm)')
checks = [
    ('versionCode = 35' in final_build and 'versionName = "0.3.10"' in final_build, 'identity'),
    ('r.startListening(recognitionIntent())' not in final_voice, 'SpeechRecognizer/beep source'),
    (final_voice.index('MediaRecorder.AudioSource.MIC') < final_voice.index('MediaRecorder.AudioSource.VOICE_RECOGNITION'), 'MIC primary'),
    ('AutomaticGainControl.create(recorder.audioSessionId)' in raw_segment, 'AGC restored'),
    ('NoiseSuppressor.create(recorder.audioSessionId)' in raw_segment, 'NS restored'),
    ('preRollMaxBytes = SAMPLE_RATE * 2 * 12 / 10' in raw_segment, '1.2s pre-roll preserved'),
    ('recorder.startRecording()' in raw_segment and raw_segment.index('recorder.startRecording()') < raw_segment.index('emit(State.LISTENING)'), 'recording before LISTENING'),
    (brain_call >= 0 and owner_call > brain_call, 'VoicePrint moved after STT'),
    ('TextToSpeech(appContext, listener, "com.google.android.tts")' not in final_voice, 'constructor remains requestedEngine based'),
    ('"com.google.android.tts"' in final_voice and '"com.samsung.SMT"' in final_voice, 'Google/Samsung TTS fallback chain'),
    ('#male_' in final_voice and '_m00' in final_voice and 'explicitMale' in final_voice, 'explicit male voice selection'),
    ('tts?.setSpeechRate(0.96f)' in final_voice, 'historical speech rate'),
    ('0.76f' in final_voice, 'deep compatibility fallback'),
]
for ok, label in checks:
    if not ok:
        raise SystemExit('VC35 validation failed: ' + label)

print('VC35 applied: hearing path restored, VoicePrint after STT, deterministic male TTS engine chain')
