from pathlib import Path
import re

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
VOICEPRINT = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoicePrint.kt"

def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC33 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))

replace_once(BUILD, 'versionCode = 32', 'versionCode = 33', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.7"', 'versionName = "0.3.8"', 'versionName')

vp = VOICEPRINT.read_text()
vp = vp.replace(
    'private const val COS_PASS=0.86;private const val COS_STRICT=0.93;private const val PITCH_MIN_RATIO=0.55;private const val PITCH_MAX_RATIO=1.85',
    'private const val COS_PASS=0.91;private const val COS_STRICT=0.965;private const val PITCH_MIN_RATIO=0.78;private const val PITCH_MAX_RATIO=1.28'
)

pattern = re.compile(
    r'    fun matches\(context:Context,pcmLe16:ByteArray\):Boolean\{.*?\}\n    private fun extract',
    re.S,
)
replacement = '''    fun matches(context:Context,pcmLe16:ByteArray):Boolean {
        val prefs=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE)
        val stored=prefs.getString(KEY_CEPSTRUM,null)?.takeIf{it.isNotBlank()}?:return false
        val features=extract(pcmLe16)?:return false
        val(mean,pitch)=features
        val json=runCatching{JSONArray(stored)}.getOrNull()?:return false
        val reference=DoubleArray(json.length()){json.optDouble(it)}
        if(reference.size!=mean.size||reference.isEmpty())return false

        var dot=0.0
        var normRef=0.0
        var normNew=0.0
        for(i in reference.indices){
            dot+=reference[i]*mean[i]
            normRef+=reference[i]*reference[i]
            normNew+=mean[i]*mean[i]
        }
        if(normRef<=1e-9||normNew<=1e-9)return false
        val cosine=dot/(sqrt(normRef)*sqrt(normNew)+1e-9)
        if(cosine>=COS_STRICT)return true

        val storedPitch=prefs.getString(KEY_PITCH,null)?.toDoubleOrNull()?:return false
        if(storedPitch<=1.0||pitch<=1.0)return false
        val ratio=pitch/storedPitch
        return cosine>=COS_PASS&&ratio in PITCH_MIN_RATIO..PITCH_MAX_RATIO
    }
    private fun extract'''
vp, count = pattern.subn(replacement, vp, count=1)
if count != 1:
    raise SystemExit('VC33 VoicePrint.matches replacement failed')
VOICEPRINT.write_text(vp)

voice = VOICE.read_text()
old = '''            val wav = pcm16ToWav(pcm.toByteArray(), SAMPLE_RATE)
            val token = AuthSessionStore.validAccessToken(appContext)
            val text = BrainClient.transcribe(token, wav).orEmpty().trim()
'''
new = '''            val capturedPcm = pcm.toByteArray()

            if (!VoicePrint.isEnrolled(appContext)) {
                handler.post {
                    emit(State.ERROR)
                    onErrorMessage("Cadastre sua voz nas Configurações para o Jarvis responder somente a você.")
                }
                return@Thread
            }
            if (!VoicePrint.matches(appContext, capturedPcm)) {
                handler.post {
                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(180L)
                    else publishIdleOrListening()
                }
                return@Thread
            }

            val wav = pcm16ToWav(capturedPcm, SAMPLE_RATE)
            val token = AuthSessionStore.validAccessToken(appContext)
            val text = BrainClient.transcribe(token, wav).orEmpty().trim()
'''
if old not in voice:
    raise SystemExit('VC33 pre-STT owner verification anchor missing')
voice = voice.replace(old, new, 1)
VOICE.write_text(voice)

final_build = BUILD.read_text()
final_voice = VOICE.read_text()
final_vp = VOICEPRINT.read_text()
checks = [
    ('versionCode = 33' in final_build and 'versionName = "0.3.8"' in final_build, 'identity'),
    ('r.startListening(recognitionIntent())' not in final_voice, 'SpeechRecognizer/beep source'),
    ('VoicePrint.isEnrolled(appContext)' in final_voice, 'enrollment gate'),
    ('VoicePrint.matches(appContext, capturedPcm)' in final_voice, 'owner gate'),
    (final_voice.index('VoicePrint.matches(appContext, capturedPcm)') < final_voice.index('BrainClient.transcribe(token, wav)'), 'owner gate ordering'),
    ('COS_PASS=0.91' in final_vp and 'COS_STRICT=0.965' in final_vp, 'strict MFCC thresholds'),
    ('PITCH_MIN_RATIO=0.78' in final_vp and 'PITCH_MAX_RATIO=1.28' in final_vp, 'strict pitch window'),
]
for ok, label in checks:
    if not ok:
        raise SystemExit('VC33 validation failed: ' + label)

print('VC33 applied: mandatory owner VoicePrint gate before STT + fail-closed biometric matching')
