from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"

def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC34 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))

replace_once(BUILD, 'versionCode = 33', 'versionCode = 34', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.8"', 'versionName = "0.3.9"', 'versionName')

voice = VOICE.read_text()

# 1) Restore speech-oriented source priority. VC31 moved MIC ahead of
# VOICE_RECOGNITION; on the tested Galaxy this degraded speech capture.
old_sources='''        for (source in intArrayOf(
            MediaRecorder.AudioSource.MIC,
            MediaRecorder.AudioSource.VOICE_RECOGNITION
        )) {'''
new_sources='''        for (source in intArrayOf(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            MediaRecorder.AudioSource.MIC
        )) {'''
if old_sources not in voice:
    raise SystemExit('VC34 audio source order anchor missing')
voice=voice.replace(old_sources,new_sources,1)

# 2) Remove extra AGC/NS processing introduced in VC32. VOICE_RECOGNITION
# already gives the device permission to use its speech capture processing;
# stacking effects can distort consonants and word starts.
old_effects='''        val noiseSuppressor = runCatching {
            if (NoiseSuppressor.isAvailable()) {
                NoiseSuppressor.create(recorder.audioSessionId)?.apply { enabled = true }
            } else null
        }.getOrNull()
        val automaticGainControl = runCatching {
            if (AutomaticGainControl.isAvailable()) {
                AutomaticGainControl.create(recorder.audioSessionId)?.apply { enabled = true }
            } else null
        }.getOrNull()

        rawRecorder = recorder
        rawCaptureActive = true
        listening = true
        emit(State.LISTENING)
        onPartialText("")
'''
new_effects='''        // Start the microphone BEFORE telling the UI/user that Jarvis is
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
        rawCaptureActive = true
        listening = true
        emit(State.LISTENING)
        onPartialText("")
'''
if old_effects not in voice:
    raise SystemExit('VC34 VC32 audio-effects/start anchor missing')
voice=voice.replace(old_effects,new_effects,1)

# startRecording is now done before LISTENING is emitted.
old_thread_start='''            try {
                recorder.startRecording()
                while (
'''
new_thread_start='''            try {
                while (
'''
if old_thread_start not in voice:
    raise SystemExit('VC34 worker startRecording anchor missing')
voice=voice.replace(old_thread_start,new_thread_start,1)

# effects no longer exist.
voice=voice.replace('                runCatching { noiseSuppressor?.release() }\n','',1)
voice=voice.replace('                runCatching { automaticGainControl?.release() }\n','',1)

# 3) Keep more audio before trigger so the whole first word reaches Whisper.
voice=voice.replace(
    '            val calibrationFrames = 8 // ~320 ms\n',
    '            val calibrationFrames = 4 // ~160 ms; faster speech readiness\n',
    1,
)
voice=voice.replace(
    '            val preRollMaxBytes = SAMPLE_RATE * 2 * 6 / 10 // ~600 ms PCM16\n',
    '            val preRollMaxBytes = SAMPLE_RATE * 2 * 12 / 10 // ~1.2 s PCM16\n',
    1,
)

# Reduce dead gaps between silent capture cycles. VoicePrint still blocks
# non-owner audio before STT.
voice=voice.replace('startRecognitionSoon(180L)', 'startRecognitionSoon(40L)')
voice=voice.replace('startRecognitionSoon(120L)', 'startRecognitionSoon(40L)')
voice=voice.replace('startRecognitionSoon(90L)', 'startRecognitionSoon(40L)')

# 4) Restore historical local male TTS path: default Android TTS engine, no
# forced Samsung engine, historical cadence/pitch.
voice=voice.replace('initializeTextToSpeech(preferSamsung = true)', 'initializeTextToSpeech(preferSamsung = false)', 1)

old_engine='''        tts = if (preferSamsung) {
            // On Galaxy devices this is the Samsung TTS engine. The historical
            // Jarvis male voice is exposed by Samsung's pt-BR male voice pack.
            TextToSpeech(appContext, listener, "com.samsung.SMT")
        } else {
            TextToSpeech(appContext, listener)
        }
'''
new_engine='''        // Historical Jarvis behaviour: use the Android default TTS engine.
        // Forcing Samsung TTS made the tested device resolve to its female
        // default voice instead of the previously working PT-BR male voice.
        tts = TextToSpeech(appContext, listener)
'''
if old_engine not in voice:
    raise SystemExit('VC34 Samsung TTS engine anchor missing')
voice=voice.replace(old_engine,new_engine,1)

voice=voice.replace('            tts?.setSpeechRate(0.98f)\n', '            tts?.setSpeechRate(0.96f)\n', 1)
voice=voice.replace('            tts?.setPitch(if (maleReady) 0.94f else 0.80f)\n', '            tts?.setPitch(0.90f)\n', 1)
voice=voice.replace('        tts?.setPitch(if (maleReady) 0.94f else 0.80f)\n', '        tts?.setPitch(0.90f)\n', 1)
voice=voice.replace('        tts?.setSpeechRate(0.98f)\n', '        tts?.setSpeechRate(0.96f)\n', 1)

VOICE.write_text(voice)

final_build=BUILD.read_text()
final_voice=VOICE.read_text()
raw_start=final_voice.index('    private fun startRawForegroundCapture() {')
raw_end=final_voice.index('\n    private fun ', raw_start + 10)
raw_segment=final_voice[raw_start:raw_end]
checks=[
 ('versionCode = 34' in final_build and 'versionName = "0.3.9"' in final_build,'identity'),
 ('r.startListening(recognitionIntent())' not in final_voice,'SpeechRecognizer/beep'),
 (final_voice.index('MediaRecorder.AudioSource.VOICE_RECOGNITION') < final_voice.index('MediaRecorder.AudioSource.MIC'),'speech source priority'),
 ('AutomaticGainControl.create(recorder.audioSessionId)' not in final_voice,'AGC removed'),
 ('NoiseSuppressor.create(recorder.audioSessionId)' not in final_voice,'NS removed'),
 ('preRollMaxBytes = SAMPLE_RATE * 2 * 12 / 10' in final_voice,'1.2s pre-roll'),
 ('calibrationFrames = 4' in final_voice,'fast calibration'),
 ('recorder.startRecording()' in raw_segment and 'emit(State.LISTENING)' in raw_segment and raw_segment.index('recorder.startRecording()') < raw_segment.index('emit(State.LISTENING)'),'real recording before LISTENING'),
 ('TextToSpeech(appContext, listener, "com.samsung.SMT")' not in final_voice,'forced Samsung TTS removed'),
 ('TextToSpeech(appContext, listener)' in final_voice,'default historical TTS'),
 ('tts?.setSpeechRate(0.96f)' in final_voice,'historical rate'),
 ('tts?.setPitch(0.90f)' in final_voice,'historical pitch'),
 ('VoicePrint.matches(appContext, capturedPcm)' in final_voice,'owner voice gate preserved'),
]
for ok,label in checks:
    if not ok:
        raise SystemExit('VC34 validation failed: '+label)

print('VC34 applied: no first-word false LISTENING, 1.2s pre-roll, speech source restored, historical male TTS path')
