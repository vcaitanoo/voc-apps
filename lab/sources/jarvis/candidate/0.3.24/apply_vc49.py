#!/usr/bin/env python3
"""VC49: reminder delivery and PT-BR male reminder voice on top of candidate VC48."""
from pathlib import Path
R=Path("jarvis0215/app")
root=R/"src/main/java/pt/vcaitano/jarvis"
def one(s,a,b,label):
    n=s.count(a)
    if n!=1: raise SystemExit("VC49 "+label+" expected 1, found "+str(n))
    return s.replace(a,b,1)
def patch(path,fn):
    old=path.read_text(encoding="utf-8")
    new=fn(old)
    if new==old: raise SystemExit("VC49 unchanged "+str(path))
    path.write_text(new,encoding="utf-8")
patch(R/"build.gradle.kts",lambda s:one(one(s,"versionCode = 48","versionCode = 49","versionCode"),'versionName = "0.3.23"','versionName = "0.3.24"',"versionName"))
parser=r'''package pt.vcaitano.jarvis.agent.reminder

import java.time.ZonedDateTime

data class ParsedReminderRequest(
    val content: String?,
    val triggerAtMillis: Long,
    val followUp: Boolean
)
object ReminderParser {
    private val verb=Regex("\\b(?:me\\s+)?lembr(?:e|a|ar)(?:-me)?\\b",RegexOption.IGNORE_CASE)
    private val time=Regex("\\b(?:às|as|ao|aos|pelas?|para\\s+as?)\\s*(\\d{1,2})(?:[:h](\\d{2}))?\\s*h?\\b",RegexOption.IGNORE_CASE)
    private val today=Regex("\\bhoje\\b",RegexOption.IGNORE_CASE)
    private val tomorrow=Regex("\\b(?:amanhã|amanha)\\b",RegexOption.IGNORE_CASE)
    private val relative=Regex("\\b(?:me\\s+)?lembr(?:e|a|ar)(?:-me)?(?:\\s+(?:novamente|de novo))?\\s+daqui\\s+a\\s+(\\d+|um|uma|dois|duas)\\s+(minutos?|horas?|dias?)(?:\\s+(?:de|para))?\\s*(.*)$",RegexOption.IGNORE_CASE)
    fun looksLikeReminderRequest(text:String):Boolean=verb.containsMatchIn(text)
    fun parse(text:String,now:ZonedDateTime=ZonedDateTime.now()):ParsedReminderRequest?{
        val clean=text.trim().trimEnd('.','!','?')
        relative.find(clean)?.let { m ->
            val n=number(m.groupValues[1])?:return null
            val unit=m.groupValues[2].lowercase()
            val at=when {
                unit.startsWith("minuto")->now.plusMinutes(n.toLong())
                unit.startsWith("hora")->now.plusHours(n.toLong())
                else->now.plusDays(n.toLong())
            }
            val content=m.groupValues[3].trim().takeIf { it.isNotBlank() }
            return ParsedReminderRequest(content,at.toInstant().toEpochMilli(),content==null)
        }
        // Natural speech, including "somente hoje, ao 12h me lembre de entrar no Codex".
        val command=verb.find(clean)?:return null
        val clock=time.find(clean)?:return null
        val h=clock.groupValues[1].toIntOrNull()?.takeIf { it in 0..23 }?:return null
        val min=clock.groupValues[2].toIntOrNull()?.takeIf { it in 0..59 }?:0
        var at=now.withHour(h).withMinute(min).withSecond(0).withNano(0)
        if(tomorrow.containsMatchIn(clean))at=at.plusDays(1)
        else if(!today.containsMatchIn(clean) && !at.isAfter(now))at=at.plusDays(1)
        val after=clean.substring(command.range.last+1)
            .replace(time," ").replace(today," ").replace(tomorrow," ")
            .trim().trimStart(',',' ',';',':')
            .replace(Regex("^(?:de|para|que)\\s+",RegexOption.IGNORE_CASE),"")
            .trim().takeIf { it.isNotBlank() }
        return ParsedReminderRequest(after,at.toInstant().toEpochMilli(),after==null)
    }
    private fun number(s:String):Int?=when(s.lowercase()){
        "um","uma"->1
        "dois","duas"->2
        else->s.toIntOrNull()?.takeIf { it in 1..100000 }
    }
}
'''
(root/"agent/reminder/ReminderParser.kt").write_text(parser,encoding="utf-8")
tools=root/"agent/tools/CoreTools.kt"
def fix_tools(s):
    s=one(s,"            ReminderParser.parse(input) != null -> 1.0","            ReminderParser.parse(input) != null -> 1.0\n            ReminderParser.looksLikeReminderRequest(input) -> 0.98","intercept incomplete reminder")
    s=one(s,
       '        val parsed = ReminderParser.parse(input) ?: return ToolResult("Não consegui identificar o horário do lembrete.")',
       '''        val parsed = ReminderParser.parse(input)
            ?: return ToolResult("Não consegui identificar o horário. Não agendei nada. Diga por exemplo: hoje às 12 me lembre de entrar no Codex.")
        if(parsed.triggerAtMillis <= System.currentTimeMillis()+1_000L)
            return ToolResult("O horário pedido para hoje já passou. Não criei o lembrete. Escolha um horário futuro.")''',
       "reject past and ambiguous")
    return s
patch(tools,fix_tools)
repository=root/"agent/reminder/ReminderRepository.kt"
patch(repository,lambda s:one(s,
'''        database.upsertReminder(entry)
        ReminderScheduler.schedule(appContext, entry)
        return entry''',
'''        database.upsertReminder(entry)
        try {
            ReminderScheduler.schedule(appContext, entry)
        } catch (error: Exception) {
            database.upsertReminder(entry.copy(
                state = ReminderState.CANCELLED,
                updatedAt = System.currentTimeMillis()
            ))
            throw error
        }
        return entry''',"roll back failed alarm"))
speech=root/"voice/ReminderSpeechService.kt"
def fix_speech(s):
    s=one(s,'        tts = TextToSpeech(applicationContext) { status ->',
    '''        val pinnedEngine=getSharedPreferences("jarvis_original_male_voice_lock",0)
            .getString("engine",null)?.takeIf { it.isNotBlank() }
        tts = TextToSpeech(applicationContext, { status ->''',"use approved voice engine")
    s=one(s,
'''            if (engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, ownerId) == TextToSpeech.ERROR) {
                stopSpeechAndSelf()
            }
        }''',
'''            if (engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, ownerId) == TextToSpeech.ERROR) {
                stopSpeechAndSelf()
            }
        }, pinnedEngine)''',"tts ctor")
    s=one(s,
'''        val selected = if (lockedName.isNullOrBlank()) {
            candidates.firstOrNull()
        } else {
            candidates.firstOrNull { it.name == lockedName }
        } ?: return false''',
'''        val selected = if(lockedName.isNullOrBlank())candidates.firstOrNull()
        else runCatching {engine.voices.orEmpty()}.getOrDefault(emptySet())
            .firstOrNull {
                it.name==lockedName &&
                it.locale.language.equals("pt",true) &&
                it.locale.country.equals("BR",true)
            } ?: return false''',"user approved voice without gender label")
    s=one(s,'            ContextCompat.startForegroundService(context, intent)',
    '''            runCatching { ContextCompat.startForegroundService(context, intent) }
                .onFailure { android.util.Log.w("JarvisReminder","Speech service denied",it) }''',"FGS safety")
    return s
patch(speech,fix_speech)
tests=r'''package pt.vcaitano.jarvis.agent.reminder
import org.junit.Test
import org.junit.Assert.*
import java.time.ZonedDateTime
import java.time.ZoneId

class ReminderParserTest {
    private val now=ZonedDateTime.of(2026,10,26,7,29,0,0,ZoneId.of("Europe/Lisbon"))
    @Test fun naturalOrderToday(){
        val r=ReminderParser.parse("somente hoje, ao 12h me lembre de entrar no codex",now)
        assertNotNull(r)
        assertEquals("entrar no codex",r!!.content)
        assertEquals(12,java.time.Instant.ofEpochMilli(r.triggerAtMillis).atZone(now.zone).hour)
    }
    @Test fun timeAfterRequest(){
        val r=ReminderParser.parse("me lembre de entrar no Codex hoje às 12:30",now)
        assertEquals("entrar no Codex",r!!.content)
        assertEquals(30,java.time.Instant.ofEpochMilli(r.triggerAtMillis).atZone(now.zone).minute)
    }
    @Test fun relative(){
        val r=ReminderParser.parse("me lembre daqui a 2 horas de beber água",now)
        assertEquals("beber água",r!!.content)
    }
    @Test fun todayPastDoesNotBecomeTomorrow(){
        val after=now.withHour(14)
        val r=ReminderParser.parse("hoje às 12 me lembre de abrir Codex",after)
        assertTrue(r!!.triggerAtMillis<after.toInstant().toEpochMilli())
    }
    @Test fun ambiguousCommandsNeverBecomeFakeConfirmations(){
        assertTrue(ReminderParser.looksLikeReminderRequest("me lembre mais tarde"))
        assertNull(ReminderParser.parse("me lembre mais tarde",now))
    }
}
'''
p=R/"src/test/java/pt/vcaitano/jarvis/agent/reminder/ReminderParserTest.kt";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(tests,encoding="utf-8")

# Keep full conversation across app restarts, rather than deleting every
# message beyond 80. SQLite persists history; the UI only loads recent turns.
# Older turns can still be recovered as lexical context, on-device.
store=root/"chat/ConversationStore.kt"
STORE=r'''package pt.vcaitano.jarvis.chat

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import org.json.JSONArray
import java.security.MessageDigest
import java.text.Normalizer
import java.util.Locale

data class ChatMessage(
    val role:String,
    val text:String,
    val createdAt:Long=System.currentTimeMillis()
)

object ConversationStore {
    private const val PREFS="jarvis_conversation"
    private const val KEY_MESSAGES="messages"
    private const val MIGRATED="sqlite_history_migrated"
    private val lock=Any()
    private var helper:HistoryDb?=null
    private class HistoryDb(ctx:Context):SQLiteOpenHelper(
        ctx.applicationContext,"jarvis-conversation.db",null,1
    ){
        override fun onCreate(db:SQLiteDatabase){
            db.execSQL("CREATE TABLE history (seq INTEGER PRIMARY KEY AUTOINCREMENT, digest TEXT UNIQUE NOT NULL, role TEXT NOT NULL, body TEXT NOT NULL, created_at INTEGER NOT NULL)")
            db.execSQL("CREATE INDEX history_created ON history(created_at DESC)")
        }
        override fun onUpgrade(db:SQLiteDatabase,oldVersion:Int,newVersion:Int)=Unit
    }
    private fun db(context:Context):SQLiteDatabase{
        if(helper==null)helper=HistoryDb(context)
        return helper!!.writableDatabase
    }
    private fun digest(message:ChatMessage):String{
        val bytes=MessageDigest.getInstance("SHA-256").digest(
            (message.createdAt.toString()+"\n"+message.role+"\n"+message.text).toByteArray(Charsets.UTF_8)
        )
        return bytes.take(16).joinToString("") { "%02x".format(it.toInt() and 255) }
    }
    private fun insert(db:SQLiteDatabase,m:ChatMessage){
        if(m.text.isBlank() || m.role !in setOf("user","jarvis","system"))return
        db.insertWithOnConflict("history",null,ContentValues().apply{
            put("digest",digest(m)); put("role",m.role)
            put("body",m.text);put("created_at",m.createdAt)
        },SQLiteDatabase.CONFLICT_IGNORE)
    }
    private fun migrate(context:Context, database:SQLiteDatabase){
        val prefs=context.getSharedPreferences(PREFS,Context.MODE_PRIVATE)
        if(prefs.getBoolean(MIGRATED,false))return
        val old=runCatching { JSONArray(prefs.getString(KEY_MESSAGES,"[]")?:"[]") }.getOrElse {JSONArray()}
        database.beginTransaction()
        try{
            for(i in 0 until old.length()){
                val v=old.optJSONObject(i)?:continue
                insert(database,ChatMessage(
                    role=v.optString("role"),text=v.optString("text"),
                    createdAt=v.optLong("created_at",System.currentTimeMillis())
                ))
            }
            database.setTransactionSuccessful()
        }finally{database.endTransaction()}
        prefs.edit().putBoolean(MIGRATED,true).apply()
    }
    fun load(context:Context):List<ChatMessage> = synchronized(lock){
        val database=db(context);migrate(context,database)
        val list=mutableListOf<ChatMessage>()
        database.rawQuery("SELECT role,body,created_at FROM history ORDER BY seq DESC LIMIT 180",null).use {c->
            while(c.moveToNext())list+=ChatMessage(c.getString(0),c.getString(1),c.getLong(2))
        }
        list.asReversed()
    }
    fun save(context:Context,messages:List<ChatMessage>){
        synchronized(lock){
            val database=db(context);migrate(context,database)
            // The old messages have already been stored. Only upsert the tail.
            messages.takeLast(12).forEach{insert(database,it)}
        }
    }
    fun relevant(context:Context,query:String,limit:Int=4):List<ChatMessage> = synchronized(lock){
        val tokens=keywords(query)
        if(tokens.isEmpty())return@synchronized emptyList()
        val database=db(context);migrate(context,database)
        val ranked=mutableListOf<Pair<ChatMessage,Double>>()
        database.rawQuery("SELECT role,body,created_at FROM history ORDER BY seq DESC LIMIT 3000",null).use{c->
            var inspected=0
            while(c.moveToNext()){
                inspected++
                // Do not inject last ~8 conversation turns again.
                if(inspected<=8)continue
                val role=c.getString(0);if(role !in setOf("user","jarvis"))continue
                val item=ChatMessage(role,c.getString(1),c.getLong(2))
                val shared=tokens.intersect(keywords(item.text)).size
                if(shared>0)ranked+=item to (shared.toDouble()/tokens.size + 0.04/(1.0+inspected/100.0))
            }
        }
        ranked.sortedByDescending{it.second}.take(limit.coerceIn(1,6))
            .map{it.first}.sortedBy{it.createdAt}
    }
    private fun keywords(input:String):Set<String>{
        val value=Normalizer.normalize(input,Normalizer.Form.NFD)
            .replace(Regex("\\p{M}+"),"").lowercase(Locale.ROOT)
        val stop=setOf("que","para","voce","eu","essa","esse","isso","quando","falamos","fala","uma","com","meu","minha","sobre","agora","hoje","mesmo","qual","lembrar")
        return value.split(Regex("[^a-z0-9]+")).filter{it.length>=3 && it !in stop}.toSet()
    }
    fun clear(context:Context){
        synchronized(lock){
            db(context).delete("history",null,null)
            context.getSharedPreferences(PREFS,Context.MODE_PRIVATE)
                .edit().remove(KEY_MESSAGES).putBoolean(MIGRATED,true).apply()
        }
    }
}
'''
store.write_text(STORE,encoding="utf-8")

activity=root/"MainActivity.kt"
def fix_context(s):
    before='''        val conversationForBrain = messages.toList().dropLast(1).takeLast(16)
            .filter { it.role == "user" || it.role == "jarvis" }
            .map {
                (if (it.role == "jarvis") "assistant" else "user") to it.text
            }'''
    after='''        val recentForBrain = messages.toList().dropLast(1).takeLast(8)
            .filter { it.role == "user" || it.role == "jarvis" }
            .map { (if (it.role == "jarvis") "assistant" else "user") to it.text }
        val olderRelevant = ConversationStore.relevant(this, text, 4)
            .filter { it.role == "user" || it.role == "jarvis" }
            .map { (if (it.role == "jarvis") "assistant" else "user") to it.text }
        val conversationForBrain = (olderRelevant + recentForBrain)
            .distinct().takeLast(12)'''
    return one(s,before,after,"restore forgotten older conversation")
patch(activity,fix_context)
print("VC49_DURABLE_MEMORY_READY: SQLite unlimited conversation history, searchable old turns")

print("VC49_REMINDER_CODE_READY parser/local alarm/male TTS plus five tests")
