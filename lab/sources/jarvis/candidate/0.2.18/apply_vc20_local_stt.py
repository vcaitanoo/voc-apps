from pathlib import Path

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:160]!r}')
    path.write_text(text.replace(old, new, 1))

# Local offline recognizer. No cloud audio/API balance is required for foreground listening.
replace_once(
    BUILD,
    'dependencies {\n',
    'dependencies {\n    implementation("com.alphacephei:vosk-android:0.3.75@aar")\n    implementation("net.java.dev.jna:jna:5.18.1@aar")\n'
)

text = VOICE.read_text()
text = text.replace('import pt.vcaitano.jarvis.network.BrainClient\n', 'import pt.vcaitano.jarvis.network.BrainClient\nimport org.json.JSONObject\nimport org.vosk.Model\nimport org.vosk.Recognizer\nimport java.io.File\nimport java.io.FileOutputStream\n', 1)
VOICE.write_text(text)

replace_once(
    VOICE,
    '''            val wav = pcm16ToWav(pcm.toByteArray(), SAMPLE_RATE)\n            val token = AuthSessionStore.validAccessToken(appContext)\n            val text = BrainClient.transcribe(token, wav).orEmpty().trim()\n            handler.post {''',
    '''            val text = transcribeForegroundLocally(pcm.toByteArray()).trim()\n            handler.post {'''
)

insert_before = '''    private fun pcm16ToWav(pcm: ByteArray, sampleRate: Int): ByteArray {'''
local_stt = r'''    private fun transcribeForegroundLocally(pcm: ByteArray): String {
        if (pcm.isEmpty()) return ""
        return try {
            val modelDir = ensureLocalVoskModel()
            val model = Model(modelDir.absolutePath)
            try {
                val recognizer = Recognizer(model, SAMPLE_RATE.toFloat())
                try {
                    recognizer.acceptWaveForm(pcm, pcm.size)
                    val payload = recognizer.finalResult
                    JSONObject(payload).optString("text").trim()
                } finally {
                    runCatching { recognizer.close() }
                }
            } finally {
                runCatching { model.close() }
            }
        } catch (_: Throwable) {
            ""
        }
    }

    @Synchronized
    private fun ensureLocalVoskModel(): File {
        val root = File(appContext.filesDir, LOCAL_VOSK_DIR)
        val marker = File(root, ".ready-vc20")
        if (marker.isFile) return root

        if (root.exists()) root.deleteRecursively()
        root.mkdirs()
        copyAssetTree(LOCAL_VOSK_ASSET, root)
        marker.writeText("vosk-model-small-pt-0.3")
        return root
    }

    private fun copyAssetTree(assetPath: String, target: File) {
        val children = appContext.assets.list(assetPath).orEmpty()
        if (children.isEmpty()) {
            target.parentFile?.mkdirs()
            appContext.assets.open(assetPath).use { input ->
                FileOutputStream(target).use { output -> input.copyTo(output) }
            }
            return
        }
        target.mkdirs()
        children.forEach { child ->
            copyAssetTree("$assetPath/$child", File(target, child))
        }
    }

'''
text = VOICE.read_text()
if insert_before not in text:
    raise SystemExit('pcm16ToWav insertion point missing')
VOICE.write_text(text.replace(insert_before, local_stt + insert_before, 1))

# Constants are inside the existing companion object.
replace_once(
    VOICE,
    '        private const val FRAME_SAMPLES = 640\n',
    '        private const val FRAME_SAMPLES = 640\n        private const val LOCAL_VOSK_ASSET = "vosk-model-small-pt-0.3"\n        private const val LOCAL_VOSK_DIR = "vosk-model-small-pt-0.3"\n'
)

print('VC20 local STT patch applied')
