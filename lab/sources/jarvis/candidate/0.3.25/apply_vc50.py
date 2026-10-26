#!/usr/bin/env python3
"""VC50: personal spoken reminders and truthful AI/memory UI on top of VC49."""
from pathlib import Path
R=Path("jarvis0215/app")
root=R/"src/main/java/pt/vcaitano/jarvis"
def one(s,a,b,label):
    n=s.count(a)
    if n!=1:raise SystemExit("VC50 expected "+label+" once, got "+str(n))
    return s.replace(a,b,1)
def patch(path,fn):
    old=path.read_text(encoding="utf-8")
    new=fn(old)
    if old==new:raise SystemExit("VC50 no change: "+str(path))
    path.write_text(new,encoding="utf-8")
patch(R/"build.gradle.kts",lambda s:one(one(s,
    "versionCode = 49","versionCode = 50","code"),
    'versionName = "0.3.24"','versionName = "0.3.25"',"name"))

speech=root/"voice/ReminderSpeechService.kt"
def patch_speech(s):
    s=one(s,'import android.app.Service',
    '''import android.app.Service
import android.media.MediaPlayer
import pt.vcaitano.jarvis.auth.AuthSessionStore
import pt.vcaitano.jarvis.network.BrainClient
import java.io.File''',"imports")
    s=one(s,'    private var tts: TextToSpeech? = null',
      '    private var tts: TextToSpeech? = null\n    private var mp3Player: MediaPlayer? = null\n    private var tempAudio: File? = null',"player state")
    s=one(s,
    '''        runCatching { tts?.shutdown() }
        tts = null
        owner?.let(SpeechCoordinator::release)''',
    '''        runCatching { tts?.shutdown() }
        tts = null
        runCatching { mp3Player?.release() }
        mp3Player = null
        runCatching { tempAudio?.delete() }
        tempAudio = null
        owner?.let(SpeechCoordinator::release)''',"onDestroy cleanup")
    s=one(s,
    '''        speak(buildSpokenReminder(content, triggerAt), reminderId.ifBlank { startId.toString() })
        return START_NOT_STICKY''',
    '''        val personalized = buildSpokenReminder(content, triggerAt)
        val speechId = reminderId.ifBlank { startId.toString() }
        val token = AuthSessionStore.validAccessToken(applicationContext)
        if (!token.isNullOrBlank()) {
            Thread {
                val audio = runCatching {
                    BrainClient.synthesizeSpeech(token, personalized)?.pcm
                }.getOrNull()
                handler.post {
                    if (!playOriginalMaleMp3(audio, speechId)) speak(personalized, speechId)
                }
            }.apply { name = "jarvis-reminder-male-voice"; isDaemon = true; start() }
        } else {
            speak(personalized, speechId)
        }
        return START_NOT_STICKY''',"original male cloud first")
    s=one(s,'    private fun speak(text: String, reminderId: String) {',
    '''    private fun playOriginalMaleMp3(bytes: ByteArray?, reminderId: String): Boolean {
        if (bytes == null || bytes.size !in 200..8_000_000) return false
        val header = bytes.size >= 3 &&
            ((bytes[0] == 'I'.code.toByte() && bytes[1] == 'D'.code.toByte() && bytes[2] == '3'.code.toByte()) ||
            ((bytes[0].toInt() and 255) == 255 && (bytes[1].toInt() and 224) == 224))
        if (!header) return false
        return runCatching {
            val file=File.createTempFile("jarvis-male-reminder-", ".mp3", cacheDir)
            tempAudio=file
            file.writeBytes(bytes)
            val player=MediaPlayer()
            mp3Player=player
            val owner="reminder:$reminderId"
            currentOwnerId=owner
            SpeechCoordinator.claim(owner) { handler.post { stopSpeechAndSelf() } }
            player.setAudioAttributes(AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build())
            player.setDataSource(file.absolutePath)
            player.setOnCompletionListener { handler.post { stopSpeechAndSelf() } }
            player.setOnErrorListener { _, _, _ ->
                handler.post { stopSpeechAndSelf() }
                true
            }
            player.prepare()
            player.start()
            true
        }.getOrElse {
            runCatching { mp3Player?.release() }
            mp3Player=null
            runCatching { tempAudio?.delete() }
            tempAudio=null
            currentOwnerId?.let(SpeechCoordinator::release)
            currentOwnerId=null
            false
        }
    }

    private fun speak(text: String, reminderId: String) {''',"play same original male mp3")
    s=one(s,
        '.setUsage(AudioAttributes.USAGE_ALARM)',
        '.setUsage(AudioAttributes.USAGE_MEDIA)',
        "match Jarvis media volume rather than separate alarm slider")
    s=one(s,
        '        return "Vítor, já são $spokenTime. Lembrete: $content."',
        '''        val prefs=getSharedPreferences("jarvis_reminder_personality",MODE_PRIVATE)
        val i=prefs.getInt("next",0)
        prefs.edit().putInt("next",(i+1)%4).apply()
        return when(i%4) {
            0 -> "Vítor, chegou a hora! Você me pediu para lembrar de $content. Já são $spokenTime."
            1 -> "Ei, Vítor! Tenho um recado importante: está na hora de $content."
            2 -> "Vítor, lembra do nosso combinado? É hora de $content. Estou te avisando."
            else -> "Vítor, passando para lembrar. Já são $spokenTime, hora de $content."
        }''',"different natural phrases")
    s=one(s,'.setContentTitle("Lembrete do Jarvis")',
          '.setContentTitle("Vítor, o Jarvis tem um recado!")',
          "foreground personalized reminder")
    return s
patch(speech,patch_speech)

receiver=root/"system/ReminderReceiver.kt"
def patch_receiver(s):
    s=one(s,'.setContentTitle(title)',
          '.setContentTitle("Vítor, é o Jarvis! Lembrete")',"notification title")
    s=one(s,'.setContentText(details ?: "Lembrete do Jarvis")',
          '.setContentText("Chegou a hora de ${details ?: title}")',"notification summary")
    s=one(s,'.bigText(details ?: "Lembrete do Jarvis")',
          '.bigText("Vítor, chegou a hora de ${details ?: title}. Você me pediu para avisar!")',
          "notification expanded personalized")
    return s
patch(receiver,patch_receiver)

activity=root/"MainActivity.kt"
def patch_activity(s):
    s=one(s,
      'SystemCard("IAs", "$providersConfigured configuradas de $providersAvailable preparadas")',
      '''SystemCard("IAs",
              if (providersAvailable >= 2 && providersConfigured >= 2) "OpenRouter e Groq disponíveis"
              else "OpenRouter ativo • Groq precisa de credencial"
          )''',"show real provider names/status")
    s=one(s,'SystemCard("Memória", "${savedMemories.size} itens locais cifrados")',
          'SystemCard("Memória", "${messages.size} mensagens • ${savedMemories.size} fatos salvos")',
          "separate conversation from personal fact memory")
    return s
patch(activity,patch_activity)
print("VC50_SPOKEN_MALE_REMINDERS_READY; PERSONALITY_4_VARIANTS; AI_MEMORY_STATUS_TRUTHFUL")
