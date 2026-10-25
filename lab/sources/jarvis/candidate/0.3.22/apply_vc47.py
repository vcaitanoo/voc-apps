#!/usr/bin/env python3
"""VC47 — Android microphone FGS crash guard; user-confirmed untagged Brazilian TTS voices.
Patch from published VC46 only. Preserve listening, cloud MP3, reminders, wakeword and data.
"""
from pathlib import Path
root=Path("jarvis0215/app")
BUILD=root/"build.gradle.kts"
MAIN=root/"src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
VOICE=root/"src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
SERVICE=root/"src/main/java/pt/vcaitano/jarvis/voice/JarvisListeningService.kt"
def swap(s,a,b,name):
    count=s.count(a)
    if count!=1:raise SystemExit("VC47: expected one "+name+", found "+str(count))
    return s.replace(a,b,1)
b=BUILD.read_text(encoding="utf-8")
b=swap(b,"versionCode = 46","versionCode = 47","VC")
b=swap(b,'versionName = "0.3.21"','versionName = "0.3.22"',"name")
BUILD.write_text(b,encoding="utf-8")
m=MAIN.read_text(encoding="utf-8")
m=swap(m,'''    override fun onStop() {
        if (listeningEnabled) voiceController.handoffToBackground()
        super.onStop()
    }''','''    // Android 14+: microphone foreground service must start while visible.
    override fun onPause() {
        if (listeningEnabled) {
            runCatching { voiceController.handoffToBackground() }
                .onFailure { android.util.Log.w("JarvisVoice", "Microphone background transition rejected", it) }
        }
        super.onPause()
    }

    override fun onStop() {
        super.onStop()
    }''',"early handoff")
m=swap(m,'''        voiceController.destroy()
        super.onDestroy()''','''        runCatching { voiceController.destroy() }
            .onFailure { android.util.Log.w("JarvisVoice", "Voice engine shutdown failed", it) }
        super.onDestroy()''',"safe Activity destruction")
m=swap(m,'    private var ownerEnrolled by mutableStateOf(false)\n','''    private var ownerEnrolled by mutableStateOf(false)
    private var availableJarvisVoices by mutableStateOf<List<VoiceController.VoiceOption>>(emptyList())
    private var checkingJarvisVoices by mutableStateOf(false)
    private var jarvisVoiceMessage by mutableStateOf("Ouça e selecione a voz masculina; não será escolhida uma voz feminina automaticamente.")
''',"settings voice state")
m=swap(m,'    private fun refreshState() {\n','''    private fun refreshInstalledVoices() {
        checkingJarvisVoices = true
        jarvisVoiceMessage = "Procurando vozes brasileiras no telefone..."
        voiceController.listBrazilianVoiceOptions { choices ->
            runOnUiThread {
                availableJarvisVoices = choices
                checkingJarvisVoices = false
                jarvisVoiceMessage = if (choices.isEmpty()) {
                    "Nenhuma voz brasileira instalada. Abra as opções de texto para fala do Android."
                } else {
                    "Ouça cada voz e selecione a masculina que deseja manter no Jarvis."
                }
            }
        }
    }

    private fun refreshState() {
''',"voice chooser callback")
menu='            item { SystemCard("Eventos locais pendentes", bufferedEvents.toString()) }\n'
card='''            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Selecionar voz masculina do Jarvis",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold)
                        Text("A voz da nuvem exige uma sessão ativa. Sem login, escolha uma voz brasileira instalada e confirme depois de ouvir.",
                            style = MaterialTheme.typography.bodySmall)
                        TextButton(enabled = !checkingJarvisVoices,
                            onClick = { refreshInstalledVoices() }) {
                            Text(if (checkingJarvisVoices) "Procurando..." else "Procurar vozes instaladas")
                        }
                        Text(jarvisVoiceMessage, style = MaterialTheme.typography.bodySmall)
                        availableJarvisVoices.forEach { item ->
                            Text(item.display, style = MaterialTheme.typography.bodySmall)
                            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                                TextButton(onClick = { voiceController.previewBrazilianVoice(item) }) {
                                    Text("Ouvir")
                                }
                                TextButton(onClick = {
                                    voiceController.chooseBrazilianVoice(item)
                                    jarvisVoiceMessage = "Voz escolhida e guardada. Volte à conversa para testar."
                                }) {
                                    Text("Usar esta voz")
                                }
                            }
                        }
                        TextButton(onClick = {
                            runCatching { startActivity(Intent("com.android.settings.TTS_SETTINGS")) }
                        }) { Text("Instalar vozes no Android") }
                    }
                }
            }
'''
m=swap(m,menu,menu+card,"new voice picker UI")
MAIN.write_text(m,encoding="utf-8")

s=SERVICE.read_text(encoding="utf-8")
s=swap(s,
'''fun start(context:Context){if(ContextCompat.checkSelfPermission(context,Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)return;ContextCompat.startForegroundService(context,Intent(context,JarvisListeningService::class.java).setAction(ACTION_START))}''',
'''fun start(context:Context){
            if(ContextCompat.checkSelfPermission(context,Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)return
            runCatching {
                ContextCompat.startForegroundService(context,Intent(context,JarvisListeningService::class.java).setAction(ACTION_START))
            }.onFailure { android.util.Log.w("JarvisVoice", "Android rejected background microphone start",it) }
        }''',"guard foreground startup")
s=swap(s,
'''startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY''',
'''val accepted=runCatching {
            startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar")
        }.onFailure {
            android.util.Log.w("JarvisVoice", "Android denied foreground microphone service",it)
        }.isSuccess
        if(!accepted){stopSelf(startId);return START_NOT_STICKY}
        acquireWakeLock()
        handler.removeCallbacksAndMessages(null)
        handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS)
        return START_STICKY''',"defensive onStartCommand")
s=swap(s,
'''private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}''',
'''private fun startForegroundNow(detail:String){
        val notification=buildNotification(detail)
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)
            startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)
        else startForeground(NOTIFICATION_ID,notification)
    }''',"format foreground method")
# Called by background controller callbacks; never allow an Android FGS update
# exception to crash the whole app process.
s=swap(s,
'private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}',
'''private fun runOnMain(block:()->Unit){
        val safe: () -> Unit = {
            runCatching(block).onFailure {
                android.util.Log.w("JarvisVoice","Foreground notification update rejected",it)
            }
            Unit
        }
        if(Looper.myLooper()==Looper.getMainLooper())safe() else handler.post { safe() }
    }''',"safe onMain notifications")
SERVICE.write_text(s,encoding="utf-8")

v=VOICE.read_text(encoding="utf-8")
v=swap(v,
'        tts?.stop()\n        tts?.shutdown()\n        tts = null\n        SpeechCoordinator.release(speechOwnerId)',
'        runCatching { tts?.stop() }\n        runCatching { tts?.shutdown() }\n        tts = null\n        SpeechCoordinator.release(speechOwnerId)',
"shutdown protected")
v=swap(v,
'''        val selected = voices.maxByOrNull(::score)?.takeIf { score(it) > Int.MIN_VALUE }''',
'''        val confirmedName = appContext.getSharedPreferences(
            "jarvis_original_male_voice_lock", Context.MODE_PRIVATE
        ).getString("voice_name", null)
        // Android often omits voice gender in metadata. Only an explicit user
        // confirmation lets us use an otherwise untagged PT-BR voice.
        val selected = if (confirmedName.isNullOrBlank()) {
            voices.maxByOrNull(::score)?.takeIf { score(it) > Int.MIN_VALUE }
        } else {
            voices.firstOrNull {
                it.name == confirmedName &&
                it.locale.language.equals("pt", ignoreCase = true) &&
                it.locale.country.equals("BR", ignoreCase = true)
            }
        }''',"honour user-chosen voice")
voice_api='''    data class VoiceOption(val name: String, val engineId: String, val display: String)

    fun listBrazilianVoiceOptions(callback: (List<VoiceOption>) -> Unit) {
        handler.post {
            val options = mutableListOf<VoiceOption>()
            val engines = listOf("", "com.samsung.SMT", "com.google.android.tts")
            fun scan(i: Int) {
                if (i >= engines.size || destroyed) {
                    callback(options.distinctBy { it.engineId + ":" + it.name })
                    return
                }
                var engine: TextToSpeech? = null
                var finished = false
                fun finish(status: Int) {
                    handler.post {
                        if (finished) return@post
                        finished = true
                        val active = engine
                        if (status == TextToSpeech.SUCCESS && active != null) {
                            val provider = engines[i].ifBlank { active.defaultEngine ?: "" }
                            val display = when {
                                provider.contains("samsung", true) -> "Samsung"
                                provider.contains("google", true) -> "Google"
                                else -> "Android"
                            }
                            runCatching { active.voices.orEmpty() }.getOrDefault(emptySet())
                                .filter {
                                    it.locale.language.equals("pt", true) &&
                                    it.locale.country.equals("BR", true)
                                }
                                .sortedBy { it.name }.take(16)
                                .forEach { option ->
                                    options += VoiceOption(option.name, provider, display + " • " + option.name)
                                }
                        }
                        runCatching { active?.shutdown() }
                        scan(i + 1)
                    }
                }
                val listener = TextToSpeech.OnInitListener { status -> finish(status) }
                runCatching {
                    engine = if (engines[i].isBlank()) TextToSpeech(appContext, listener)
                             else TextToSpeech(appContext, listener, engines[i])
                }.onFailure { finish(TextToSpeech.ERROR) }
                handler.postDelayed({ finish(TextToSpeech.ERROR) }, 4_000L)
            }
            scan(0)
        }
    }

    fun previewBrazilianVoice(option: VoiceOption) {
        handler.post {
            var engine: TextToSpeech? = null
            val listener = TextToSpeech.OnInitListener { status ->
                handler.post {
                    val active = engine ?: return@post
                    if (status != TextToSpeech.SUCCESS) {
                        runCatching { active.shutdown() }
                        return@post
                    }
                    val selected = runCatching { active.voices.orEmpty().firstOrNull {
                        it.name == option.name && it.locale.language.equals("pt", true) &&
                        it.locale.country.equals("BR", true)
                    } }.getOrNull()
                    if (selected == null) {
                        runCatching { active.shutdown() }
                        return@post
                    }
                    runCatching {
                        active.voice = selected
                        active.setSpeechRate(0.98f)
                        active.setPitch(0.76f)
                        active.setOnUtteranceProgressListener(object: UtteranceProgressListener() {
                            override fun onStart(utteranceId: String?) = Unit
                            override fun onDone(utteranceId: String?) {
                                handler.post { runCatching { active.shutdown() } }
                            }
                            @Deprecated("Deprecated in Java")
                            override fun onError(utteranceId: String?) {
                                handler.post { runCatching { active.shutdown() } }
                            }
                        })
                        active.speak("Olá! Eu sou o Jarvis. Esta é uma demonstração da minha voz.",
                            TextToSpeech.QUEUE_FLUSH, null, "jarvis-preview")
                    }.onFailure { runCatching { active.shutdown() } }
                }
            }
            runCatching {
                engine = if(option.engineId.isBlank()) TextToSpeech(appContext, listener)
                         else TextToSpeech(appContext, listener, option.engineId)
            }
        }
    }

    fun chooseBrazilianVoice(option: VoiceOption) {
        handler.post {
            appContext.getSharedPreferences("jarvis_original_male_voice_lock", Context.MODE_PRIVATE)
                .edit().putString("engine", option.engineId)
                .putString("voice_name", option.name)
                .apply()
            initializeTextToSpeech()
        }
    }

'''
v=swap(v,"    private fun initializeTextToSpeech(engineStep: Int = 0) {",
  voice_api+"    private fun initializeTextToSpeech(engineStep: Int = 0) {",
  "voice chooser implementation")
VOICE.write_text(v,encoding="utf-8")

checks=[
("versionCode = 47" in b,"versionCode"),
("override fun onPause()" in m and "override fun onStop() {\n        super.onStop()" in m,"foreground lifecycle"),
("availableJarvisVoices.forEach" in m and "previewBrazilianVoice(item)" in m,"voice UI"),
("Android rejected background microphone start" in s,"service start guard"),
("if(!accepted){stopSelf(startId);return START_NOT_STICKY}" in s,"fgs startup failure guard"),
("fun chooseBrazilianVoice" in v and "confirmedName" in v,"user-selected original voice"),
("playVerifiedMaleMp3" in v and "VoicePrint.matches" in v,"existing functions preserved")
]
for ok,name in checks:
    if not ok:raise SystemExit("VC47 invariant missing: "+name)
print("VC47_SOURCE_OK — fixed Android background foreground-service startup and added explicit user-auditioned voice selection")
