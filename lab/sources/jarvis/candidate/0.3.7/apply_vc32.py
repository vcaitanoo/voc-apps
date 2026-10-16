from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
BRAIN = APP / "src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC32 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))


# VC32 is a strict successor of the physical-test VC29 -> VC31 line.
# Keep the silent AudioRecord architecture: SpeechRecognizer must not return.
replace_once(BUILD, 'versionCode = 31', 'versionCode = 32', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.6"', 'versionName = "0.3.7"', 'versionName')

voice = VOICE.read_text()
if 'import android.media.audiofx.AutomaticGainControl' not in voice:
    anchor = 'import android.media.AudioRecord\n'
    if anchor not in voice:
        raise SystemExit('VC32 AudioRecord import anchor missing')
    voice = voice.replace(
        anchor,
        anchor + 'import android.media.audiofx.AutomaticGainControl\nimport android.media.audiofx.NoiseSuppressor\n',
        1,
    )

start = voice.find('    private fun startRawForegroundCapture() {')
if start < 0:
    raise SystemExit('VC32 raw capture function missing')
end = voice.find('\n    private fun ', start + 10)
if end < 0:
    raise SystemExit('VC32 raw capture function boundary missing')
segment = voice[start:end]

# Samsung microphones can be quiet/noisy in raw 16 kHz mode. Use Android's
# own signal-processing effects when the device exposes them. These effects do
# not create a SpeechRecognizer session and therefore do not reintroduce the beep.
needle = '        rawRecorder = recorder\n'
if needle not in segment:
    raise SystemExit('VC32 rawRecorder assignment missing')
segment = segment.replace(
    needle,
    '''        val noiseSuppressor = runCatching {
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
''',
    1,
)

segment = segment.replace('            var totalFrames = 0\n            var noisePeak = 80.0\n',
                          '            var totalFrames = 0\n            var speechCandidateFrames = 0\n            var noisePeak = 80.0\n', 1)
segment = segment.replace('            val calibrationFrames = 6 // ~240 ms\n',
                          '            val calibrationFrames = 8 // ~320 ms\n', 1)
segment = segment.replace('            val preRollMaxBytes = SAMPLE_RATE * 2 * 4 / 10 // ~400 ms PCM16\n',
                          '            val preRollMaxBytes = SAMPLE_RATE * 2 * 6 / 10 // ~600 ms PCM16\n', 1)
segment = segment.replace('                        val speechThreshold = maxOf(170, minOf(850, (noisePeak * 2.25 + 70).toInt()))\n',
                          '                        val speechThreshold = maxOf(130, minOf(700, (noisePeak * 1.85 + 45).toInt()))\n', 1)
segment = segment.replace(
    '''                        if (totalFrames > 2 && peak >= speechThreshold) {
                            heardSpeech = true
                            while (preRoll.isNotEmpty()) pcm.write(preRoll.removeFirst())
                            preRollBytes = 0
                            silenceFrames = 0
                        }
''',
    '''                        if (totalFrames > 2 && peak >= speechThreshold) {
                            speechCandidateFrames += 1
                            if (speechCandidateFrames >= 2) {
                                heardSpeech = true
                                while (preRoll.isNotEmpty()) pcm.write(preRoll.removeFirst())
                                preRollBytes = 0
                                silenceFrames = 0
                            }
                        } else {
                            speechCandidateFrames = 0
                        }
''',
    1,
)
segment = segment.replace('                        val continuationThreshold = maxOf(110, (noisePeak * 1.45 + 35).toInt())\n',
                          '                        val continuationThreshold = maxOf(90, (noisePeak * 1.28 + 25).toInt())\n', 1)
segment = segment.replace('                        startRecognitionSoon(120L)\n',
                          '                        startRecognitionSoon(90L)\n', 1)
segment = segment.replace('                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(180L)\n',
                          '                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(120L)\n', 1)

release_anchor = '                runCatching { recorder.release() }\n'
if release_anchor not in segment:
    raise SystemExit('VC32 recorder release anchor missing')
segment = segment.replace(
    release_anchor,
    '                runCatching { noiseSuppressor?.release() }\n                runCatching { automaticGainControl?.release() }\n' + release_anchor,
    1,
)

voice = voice[:start] + segment + voice[end:]
VOICE.write_text(voice)

# Defense in depth: even if a model/provider ever returns hidden scratchpad in
# normal content, the Android client must never render or speak it.
brain = BRAIN.read_text()
anchor = '''        val directivePatterns = listOf(
'''
if anchor not in brain:
    raise SystemExit('VC32 BrainClient sanitization anchor missing')
reasoning_guard = '''        val leakedReasoning = Regex(
            "(?is)^\\\\s*(?:okay[,\\\\s]+)?(?:" +
                "the\\\\s+user\\\\s+(?:said|wrote|typed|asked|asks|wants|is\\\\s+asking)|" +
                "we\\\\s+need\\\\s+to|i\\\\s+(?:need|should|think)\\\\s+to|" +
                "let(?:'|’)s\\\\s+(?:think|see|check|analy[sz]e)|" +
                "maybe\\\\s+(?:the\\\\s+user|they)\\\\s+(?:mean|meant|said)|" +
                "analysis|reasoning|thoughts?|scratchpad|internal\\\\s+notes?)\\\\b"
        )
        val leakedReasoningBody = Regex(
            "(?is)\\\\b(?:the\\\\s+user\\\\s+(?:said|wrote|typed)|" +
                "the\\\\s+user(?:'|’)s\\\\s+message\\\\s+is|" +
                "maybe\\\\s+(?:the\\\\s+user|they)\\\\s+(?:mean|meant)|" +
                "we\\\\s+need\\\\s+to\\\\s+(?:answer|respond)|" +
                "i\\\\s+should\\\\s+(?:answer|respond))\\\\b"
        )
        if (leakedReasoning.containsMatchIn(text) || leakedReasoningBody.containsMatchIn(text.take(1800))) {
            return ""
        }

'''
brain = brain.replace(anchor, reasoning_guard + anchor, 1)
BRAIN.write_text(brain)

final_build = BUILD.read_text()
final_voice = VOICE.read_text()
final_brain = BRAIN.read_text()
checks = [
    ('versionCode = 32' in final_build and 'versionName = "0.3.7"' in final_build, 'identity'),
    ('r.startListening(recognitionIntent())' not in final_voice, 'SpeechRecognizer/beep source'),
    ('AutomaticGainControl.create(recorder.audioSessionId)' in final_voice, 'automatic gain control'),
    ('NoiseSuppressor.create(recorder.audioSessionId)' in final_voice, 'noise suppressor'),
    ('preRollMaxBytes = SAMPLE_RATE * 2 * 6 / 10' in final_voice, '600ms pre-roll'),
    ('speechCandidateFrames >= 2' in final_voice, 'speech confirmation'),
    ('speechThreshold = maxOf(130, minOf(700' in final_voice, 'more sensitive adaptive VAD'),
    ('explicitMale' in final_voice and 'com.samsung.SMT' in final_voice, 'male Samsung TTS'),
    ('the\\\\s+user\\\\s+(?:said|wrote|typed' in final_brain, 'reasoning leak guard'),
]
for ok, label in checks:
    if not ok:
        raise SystemExit('VC32 validation failed: ' + label)

print('VC32 applied: AGC + noise suppression + 600ms pre-roll + more sensitive VAD + reasoning leak guard')
