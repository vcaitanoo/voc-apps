from pathlib import Path
import re

ROOT = Path('jarvis0215')
APP = ROOT / 'app'
BUILD = APP / 'build.gradle.kts'
MAIN = APP / 'src/main/java/pt/vcaitano/jarvis/MainActivity.kt'
VOICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt'
SERVICE = APP / 'src/main/java/pt/vcaitano/jarvis/voice/JarvisListeningService.kt'
BRAIN = APP / 'src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt'
MANIFEST = APP / 'src/main/AndroidManifest.xml'


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'expected block missing in {path}: {old[:180]!r}')
    path.write_text(text.replace(old, new, 1))

# Version: exact successor of tested VC19.
replace_once(BUILD, 'versionCode = 19', 'versionCode = 20')
replace_once(BUILD, 'versionName = "0.2.17"', 'versionName = "0.2.18"')

# Foreground STT may be anonymous, matching the resilient anonymous brain policy.
replace_once(
    BRAIN,
    'if (accessToken.isNullOrBlank() || wavBytes.isEmpty()) return null',
    'if (wavBytes.isEmpty()) return null'
)

# The foreground button must NOT use Android/Samsung SpeechRecognizer. It uses raw AudioRecord,
# so there is no system recognition-session beep. SpeechRecognizer remains background-only.
replace_once(
    VOICE,
    '@Volatile private var wakeConversationUntilMs = 0L\n\n    private var recognizer: SpeechRecognizer? = null',
    '@Volatile private var wakeConversationUntilMs = 0L\n    @Volatile private var rawCaptureActive = false\n    @Volatile private var rawCaptureEpoch = 0\n\n    private var rawRecorder: AudioRecord? = null\n    private var recognizer: SpeechRecognizer? = null'
)

replace_once(
    VOICE,
    '        if (!managedByListeningService) JarvisListeningService.start(appContext)\n        startRecognitionSoon(0L)',
    '        if (!managedByListeningService) JarvisListeningService.stop(appContext)\n        startRecognitionSoon(if (managedByListeningService) 0L else 350L)'
)

# Public lifecycle handoff methods keep exactly one microphone owner at a time.
insert_after = '''    fun isContinuousEnabled(): Boolean = continuousEnabled\n'''
addition = '''\n    fun resumeForegroundListening() {\n        if (managedByListeningService || destroyed) return\n        JarvisListeningService.stop(appContext)\n        if (continuousEnabled && !waitingForReply && !speaking) {\n            startRecognitionSoon(650L)\n        }\n    }\n\n    fun handoffToBackground() {\n        if (managedByListeningService || destroyed) return\n        cancelRecognition()\n        if (continuousEnabled) JarvisListeningService.start(appContext)\n    }\n'''
text = VOICE.read_text()
if insert_after not in text:
    raise SystemExit('VoiceController lifecycle insertion point missing')
VOICE.write_text(text.replace(insert_after, insert_after + addition, 1))

old_start = '''    private fun startRecognitionNow() {\n        if (destroyed || !continuousEnabled || waitingForReply || speaking) return\n        if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {\n            emit(State.ERROR)\n            onErrorMessage("Permissão de microfone não concedida.")\n            return\n        }\n        val r = ensureRecognizer()\n        if (r == null) {\n            emit(State.ERROR)\n            onErrorMessage("Não encontrei um serviço de reconhecimento de voz no Android.")\n            return\n        }\n        try {\n            r.startListening(recognitionIntent())\n            listening = true\n            emit(State.LISTENING)\n        } catch (_: SecurityException) {\n            emit(State.ERROR)\n            onErrorMessage("O Android bloqueou o acesso ao microfone.")\n        } catch (_: Throwable) {\n            destroyRecognizerOnly()\n            startRecognitionSoon(BUSY_RESTART_DELAY_MS)\n        }\n    }\n'''
new_start = '''    private fun startRecognitionNow() {\n        if (destroyed || !continuousEnabled || waitingForReply || speaking) return\n        if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {\n            emit(State.ERROR)\n            onErrorMessage("Permissão de microfone não concedida.")\n            return\n        }\n\n        // Foreground mode intentionally avoids SpeechRecognizer. Samsung/Google recognition\n        // sessions may emit an audible start/end beep and repeated sessions can fight the\n        // background service. Raw AudioRecord is silent and gives this controller sole\n        // ownership of the microphone while the conversation screen is active.\n        if (!managedByListeningService) {\n            if (JarvisListeningService.isBackgroundControllerActive()) {\n                JarvisListeningService.stop(appContext)\n                startRecognitionSoon(700L)\n                return\n            }\n            startRawForegroundCapture()\n            return\n        }\n\n        val r = ensureRecognizer()\n        if (r == null) {\n            emit(State.ERROR)\n            onErrorMessage("Não encontrei um serviço de reconhecimento de voz no Android.")\n            return\n        }\n        try {\n            r.startListening(recognitionIntent())\n            listening = true\n            emit(State.LISTENING)\n        } catch (_: SecurityException) {\n            emit(State.ERROR)\n            onErrorMessage("O Android bloqueou o acesso ao microfone.")\n        } catch (_: Throwable) {\n            destroyRecognizerOnly()\n            startRecognitionSoon(BUSY_RESTART_DELAY_MS)\n        }\n    }\n\n    private fun startRawForegroundCapture() {\n        if (rawCaptureActive || destroyed || waitingForReply || speaking || !continuousEnabled) return\n        val minBuffer = AudioRecord.getMinBufferSize(\n            SAMPLE_RATE,\n            AudioFormat.CHANNEL_IN_MONO,\n            AudioFormat.ENCODING_PCM_16BIT\n        )\n        if (minBuffer <= 0) {\n            emit(State.ERROR)\n            onErrorMessage("Não consegui preparar o microfone do Jarvis.")\n            return\n        }\n\n        val recorder = try {\n            AudioRecord(\n                MediaRecorder.AudioSource.VOICE_RECOGNITION,\n                SAMPLE_RATE,\n                AudioFormat.CHANNEL_IN_MONO,\n                AudioFormat.ENCODING_PCM_16BIT,\n                maxOf(minBuffer * 2, FRAME_SAMPLES * 8)\n            )\n        } catch (_: Throwable) { null }\n\n        if (recorder == null || recorder.state != AudioRecord.STATE_INITIALIZED) {\n            runCatching { recorder?.release() }\n            emit(State.ERROR)\n            onErrorMessage("Não consegui abrir o microfone para ouvir.")\n            return\n        }\n\n        val epoch = ++rawCaptureEpoch\n        rawRecorder = recorder\n        rawCaptureActive = true\n        listening = true\n        emit(State.LISTENING)\n        onPartialText("")\n\n        Thread {\n            val pcm = ByteArrayOutputStream()\n            val buffer = ShortArray(FRAME_SAMPLES)\n            var heardSpeech = false\n            var silenceFrames = 0\n            var totalFrames = 0\n            val startTimeoutFrames = (SAMPLE_RATE * 10) / FRAME_SAMPLES\n            val maxFrames = (SAMPLE_RATE * 18) / FRAME_SAMPLES\n            val silenceStopFrames = (SAMPLE_RATE * 12 / 10) / FRAME_SAMPLES\n\n            try {\n                recorder.startRecording()\n                while (\n                    epoch == rawCaptureEpoch &&\n                    continuousEnabled &&\n                    !destroyed &&\n                    !waitingForReply &&\n                    !speaking &&\n                    totalFrames < maxFrames\n                ) {\n                    val read = recorder.read(buffer, 0, buffer.size)\n                    if (read <= 0) continue\n                    var peak = 0\n                    for (i in 0 until read) {\n                        val value = buffer[i].toInt()\n                        val abs = kotlin.math.abs(value)\n                        if (abs > peak) peak = abs\n                        pcm.write(value and 0xFF)\n                        pcm.write((value shr 8) and 0xFF)\n                    }\n                    totalFrames += 1\n                    if (peak >= 700) {\n                        heardSpeech = true\n                        silenceFrames = 0\n                    } else if (heardSpeech) {\n                        silenceFrames += 1\n                    }\n                    if (!heardSpeech && totalFrames >= startTimeoutFrames) break\n                    if (heardSpeech && silenceFrames >= silenceStopFrames) break\n                }\n            } catch (_: Throwable) {\n                // handled below; controller will silently retry while enabled\n            } finally {\n                runCatching { recorder.stop() }\n                runCatching { recorder.release() }\n                if (rawRecorder === recorder) rawRecorder = null\n            }\n\n            if (epoch != rawCaptureEpoch || destroyed) return@Thread\n            rawCaptureActive = false\n            listening = false\n\n            if (!heardSpeech || pcm.size() < SAMPLE_RATE / 2) {\n                handler.post {\n                    if (continuousEnabled && !waitingForReply && !speaking) {\n                        startRecognitionSoon(250L)\n                    } else publishIdleOrListening()\n                }\n                return@Thread\n            }\n\n            val wav = pcm16ToWav(pcm.toByteArray(), SAMPLE_RATE)\n            val token = AuthSessionStore.validAccessToken(appContext)\n            val text = BrainClient.transcribe(token, wav).orEmpty().trim()\n            handler.post {\n                if (epoch != rawCaptureEpoch || destroyed) return@post\n                if (text.isBlank()) {\n                    if (continuousEnabled && !waitingForReply && !speaking) startRecognitionSoon(350L)\n                    else publishIdleOrListening()\n                } else {\n                    routeTranscribedSpeech(text)\n                }\n            }\n        }.apply {\n            name = "jarvis-foreground-audio"\n            isDaemon = true\n            start()\n        }\n    }\n\n    private fun pcm16ToWav(pcm: ByteArray, sampleRate: Int): ByteArray {\n        val out = ByteArrayOutputStream(pcm.size + 44)\n        fun ascii(value: String) = value.forEach { out.write(it.code) }\n        fun le16(value: Int) { out.write(value and 0xFF); out.write((value ushr 8) and 0xFF) }\n        fun le32(value: Int) {\n            out.write(value and 0xFF); out.write((value ushr 8) and 0xFF)\n            out.write((value ushr 16) and 0xFF); out.write((value ushr 24) and 0xFF)\n        }\n        ascii("RIFF"); le32(36 + pcm.size); ascii("WAVE")\n        ascii("fmt "); le32(16); le16(1); le16(1); le32(sampleRate)\n        le32(sampleRate * 2); le16(2); le16(16)\n        ascii("data"); le32(pcm.size); out.write(pcm)\n        return out.toByteArray()\n    }\n'''
replace_once(VOICE, old_start, new_start)

replace_once(
    VOICE,
    '''    private fun cancelRecognition() {\n        runCatching { recognizer?.cancel() }\n        listening = false\n    }\n''',
    '''    private fun cancelRecognition() {\n        rawCaptureEpoch += 1\n        rawCaptureActive = false\n        val raw = rawRecorder\n        rawRecorder = null\n        runCatching { raw?.stop() }\n        runCatching { raw?.release() }\n        runCatching { recognizer?.cancel() }\n        listening = false\n    }\n'''
)

# Background service starts its own controller only after the Activity hands off ownership.
old_service = '''        startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();if(intent==null)handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY'''
new_service = '''        startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY'''
replace_once(SERVICE, old_service, new_service)

# Activity lifecycle: foreground owns raw mic; background service owns SpeechRecognizer.
replace_once(
    MAIN,
    'import pt.vcaitano.jarvis.voice.VoiceController\nimport pt.vcaitano.jarvis.voice.VoicePrint',
    'import pt.vcaitano.jarvis.voice.JarvisListeningService\nimport pt.vcaitano.jarvis.voice.VoiceController\nimport pt.vcaitano.jarvis.voice.VoicePrint'
)
replace_once(
    MAIN,
    '''    override fun onResume() {\n        super.onResume()\n        refreshState()\n    }\n\n    override fun onDestroy() {''',
    '''    override fun onResume() {\n        super.onResume()\n        JarvisListeningService.stop(this)\n        voiceController.resumeForegroundListening()\n        refreshState()\n    }\n\n    override fun onStop() {\n        if (listeningEnabled) voiceController.handoffToBackground()\n        super.onStop()\n    }\n\n    override fun onDestroy() {'''
)

# Keyboard must resize the window and the Compose content must respect the IME inset.
main_text = MAIN.read_text()
if 'import androidx.compose.foundation.layout.imePadding' not in main_text:
    main_text = main_text.replace('import androidx.compose.foundation.layout.height\n', 'import androidx.compose.foundation.layout.height\nimport androidx.compose.foundation.layout.imePadding\n', 1)
if 'import androidx.compose.animation.core.RepeatMode' not in main_text:
    main_text = main_text.replace('import androidx.activity.result.contract.ActivityResultContracts\n', '''import androidx.activity.result.contract.ActivityResultContracts\nimport androidx.compose.animation.core.RepeatMode\nimport androidx.compose.animation.core.animateFloat\nimport androidx.compose.animation.core.infiniteRepeatable\nimport androidx.compose.animation.core.rememberInfiniteTransition\nimport androidx.compose.animation.core.tween\n''', 1)
if 'import androidx.compose.ui.graphics.graphicsLayer' not in main_text:
    main_text = main_text.replace('import androidx.compose.ui.graphics.Color\n', 'import androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.graphics.graphicsLayer\n', 1)
main_text = main_text.replace('Column(modifier = Modifier.fillMaxSize()) {', 'Column(modifier = Modifier.fillMaxSize().imePadding()) {', 1)
MAIN.write_text(main_text)

manifest_text = MANIFEST.read_text()
if 'android:windowSoftInputMode=' not in manifest_text:
    manifest_text, n = re.subn(
        r'(<activity\b[^>]*android:name="\.MainActivity"[^>]*)(>)',
        r'\1 android:windowSoftInputMode="adjustResize"\2',
        manifest_text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit('MainActivity manifest entry missing')
MANIFEST.write_text(manifest_text)

# Remove voice enrollment controls from the initial presence card.
main_text = MAIN.read_text()
voice_start = '                HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.4f))\n\n                Row(\n'
start = main_text.find(voice_start)
if start < 0:
    raise SystemExit('initial voice enrollment block start missing')
function_close = '            }\n        }\n    }\n\n    @Composable\n    private fun JarvisOrb()'
end = main_text.find(function_close, start)
if end < 0:
    raise SystemExit('initial voice enrollment block end missing')
main_text = main_text[:start] + main_text[end:]
MAIN.write_text(main_text)

# Replace large circular orb with a compact animated rounded rectangle.
main_text = MAIN.read_text()
orb_start = main_text.find('    @Composable\n    private fun JarvisOrb() {')
orb_end = main_text.find('    @Composable\n    private fun ThinkingBubble()', orb_start)
if orb_start < 0 or orb_end < 0:
    raise SystemExit('JarvisOrb boundaries missing')
new_orb = '''    @Composable\n    private fun JarvisOrb() {\n        val accent = stateColor()\n        val transition = rememberInfiniteTransition(label = "jarvis-presence")\n        val pulse by transition.animateFloat(\n            initialValue = 0.96f,\n            targetValue = 1.0f,\n            animationSpec = infiniteRepeatable(\n                animation = tween(durationMillis = 900),\n                repeatMode = RepeatMode.Reverse\n            ),\n            label = "jarvis-pulse"\n        )\n        val glow by transition.animateFloat(\n            initialValue = 0.18f,\n            targetValue = 0.42f,\n            animationSpec = infiniteRepeatable(\n                animation = tween(durationMillis = 1150),\n                repeatMode = RepeatMode.Reverse\n            ),\n            label = "jarvis-glow"\n        )\n\n        Box(\n            modifier = Modifier\n                .fillMaxWidth(0.72f)\n                .height(68.dp)\n                .graphicsLayer {\n                    scaleX = pulse\n                    scaleY = 0.98f + ((pulse - 0.96f) * 0.5f)\n                }\n                .background(accent.copy(alpha = glow), RoundedCornerShape(22.dp)),\n            contentAlignment = Alignment.Center\n        ) {\n            Box(\n                modifier = Modifier\n                    .fillMaxWidth(0.90f)\n                    .height(46.dp)\n                    .background(Color(0xFF071017).copy(alpha = 0.72f), RoundedCornerShape(17.dp)),\n                contentAlignment = Alignment.Center\n            ) {\n                Row(\n                    horizontalArrangement = Arrangement.spacedBy(10.dp),\n                    verticalAlignment = Alignment.CenterVertically\n                ) {\n                    Box(\n                        modifier = Modifier\n                            .size(9.dp)\n                            .background(accent, CircleShape)\n                    )\n                    Text(\n                        "JARVIS",\n                        color = accent,\n                        fontWeight = FontWeight.Bold,\n                        style = MaterialTheme.typography.titleMedium\n                    )\n                    if (assistantState == AssistantState.THINKING) {\n                        CircularProgressIndicator(\n                            modifier = Modifier.size(18.dp),\n                            color = accent,\n                            strokeWidth = 2.dp\n                        )\n                    }\n                }\n            }\n        }\n    }\n\n'''
main_text = main_text[:orb_start] + new_orb + main_text[orb_end:]
MAIN.write_text(main_text)

# Put voice enrollment in Configurations/System screen.
main_text = MAIN.read_text()
notification_block = '''            item {\n                Button(\n                    onClick = {\n                        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))\n                    },\n                    modifier = Modifier.fillMaxWidth()\n                ) {\n                    Text("Configurar acesso às notificações")\n                }\n            }\n\n            item { HorizontalDivider() }'''
voice_settings = '''            item {\n                Button(\n                    onClick = {\n                        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))\n                    },\n                    modifier = Modifier.fillMaxWidth()\n                ) {\n                    Text("Configurar acesso às notificações")\n                }\n            }\n\n            item {\n                Card(\n                    modifier = Modifier.fillMaxWidth(),\n                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)\n                ) {\n                    Column(\n                        modifier = Modifier.padding(14.dp),\n                        verticalArrangement = Arrangement.spacedBy(9.dp)\n                    ) {\n                        Text(\n                            "Voz do Jarvis",\n                            style = MaterialTheme.typography.titleMedium,\n                            fontWeight = FontWeight.SemiBold\n                        )\n                        Text(\n                            when {\n                                enrollBusy -> "Fale naturalmente por alguns segundos…"\n                                ownerEnrolled -> "Sua voz está cadastrada."\n                                else -> "Cadastre sua voz para identificar o proprietário."\n                            },\n                            style = MaterialTheme.typography.bodySmall,\n                            color = MaterialTheme.colorScheme.onSurfaceVariant\n                        )\n                        Button(\n                            onClick = {\n                                val permission = ContextCompat.checkSelfPermission(\n                                    this@MainActivity,\n                                    Manifest.permission.RECORD_AUDIO\n                                )\n                                if (permission == PackageManager.PERMISSION_GRANTED) beginVoiceEnrollment()\n                                else enrollPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)\n                            },\n                            enabled = !enrollBusy,\n                            modifier = Modifier.fillMaxWidth()\n                        ) {\n                            Text(\n                                when {\n                                    enrollBusy -> "Gravando sua voz…"\n                                    ownerEnrolled -> "Recadastrar minha voz"\n                                    else -> "Cadastrar minha voz"\n                                }\n                            )\n                        }\n                        if (ownerEnrolled) {\n                            TextButton(\n                                onClick = {\n                                    VoicePrint.clear(this@MainActivity)\n                                    ownerEnrolled = false\n                                },\n                                modifier = Modifier.fillMaxWidth()\n                            ) {\n                                Text("Remover voz cadastrada")\n                            }\n                        }\n                    }\n                }\n            }\n\n            item { HorizontalDivider() }'''
if notification_block not in main_text:
    raise SystemExit('settings notification insertion block missing')
main_text = main_text.replace(notification_block, voice_settings, 1)
# The second tab is the configuration screen; make that explicit to the user.
main_text = main_text.replace('Text("Sistema")', 'Text("Configurações")', 2)
MAIN.write_text(main_text)

print('VC20 patch applied')
