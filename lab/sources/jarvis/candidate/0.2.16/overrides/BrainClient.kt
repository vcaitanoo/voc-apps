package pt.vcaitano.jarvis.network

import android.util.Base64
import org.json.JSONArray
import org.json.JSONObject
import pt.vcaitano.jarvis.BuildConfig
import java.net.HttpURLConnection
import java.net.URL
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

object BrainClient {
    private const val CONNECT_TIMEOUT_MS = 5_000
    private const val READ_TIMEOUT_MS = 35_000

    data class HealthStatus(
        val online: Boolean,
        val chatMode: String = "unknown",
        val providersConfigured: Int = 0,
        val providersAvailable: Int = 4
    )

    data class ChatResponse(
        val text: String,
        val mode: String,
        val provider: String?,
        val model: String?,
        val stages: List<String>,
        val providersConfigured: Int,
        val providersAvailable: Int,
        val cancelledReminderIds: List<String> = emptyList()
    )

    data class Reminder(
        val id: String,
        val title: String,
        val details: String?,
        val intervalMinutes: Int?,
        val nextFireAtMillis: Long
    )

    data class SpeechAudio(
        val pcm: ByteArray,
        val sampleRate: Int
    )

    class ChatException(val httpStatus: Int?, serverMessage: String?) :
        RuntimeException(serverMessage) {
        val serverMessage: String? = serverMessage
    }

    private val baseUrl: String
        get() = BuildConfig.BRAIN_BASE_URL.trim().trimEnd('/')

    private val voiceBaseUrl: String
        get() = baseUrl.substringBeforeLast('/') + "/jarvis-voice"

    val isConfigured: Boolean
        get() = baseUrl.startsWith("https://")

    fun healthStatus(): HealthStatus {
        if (!isConfigured) return HealthStatus(online = false)
        return runCatching {
            val (status, body) = request(baseUrl, "GET", "/health", null, null)
            if (status !in 200..299) return@runCatching HealthStatus(online = false)
            val json = JSONObject(body)
            HealthStatus(
                online = json.optString("status") == "ok",
                chatMode = json.optString("chatMode", "unknown"),
                providersConfigured = json.optInt("providersConfigured", 0),
                providersAvailable = json.optInt("providersAvailable", 4)
            )
        }.getOrElse { HealthStatus(online = false) }
    }

    fun health(): Boolean = healthStatus().online

    fun postEvent(accessToken: String, event: JSONObject): Boolean {
        if (!isConfigured || accessToken.isBlank()) return false
        return runCatching {
            request(baseUrl, "POST", "/v1/events", accessToken, event.toString()).first in 200..299
        }.getOrDefault(false)
    }

    fun chat(accessToken: String?, message: String): ChatResponse? {
        if (!isConfigured || message.isBlank()) return null
        val cleanMessage = message.trim()

        reminderManagementResponse(accessToken, cleanMessage)?.let { return it }
        reminderCancellationResponse(accessToken, cleanMessage)?.let { return it }

        val outboundMessage = if (cleanMessage.equals("Jarvis", ignoreCase = true)) {
            """
            O usuário apenas chamou você dizendo “Jarvis”. Responda em UMA frase muito curta, natural e oral, como uma confirmação de que você está atento e pronto para ouvir o que vem a seguir. Varie sempre a formulação; não use um bordão fixo. Leve em conta, quando fizer sentido, o horário atual, o contexto recente e memórias relevantes do usuário, sem forçar referências pessoais. Não explique o que está fazendo, não mencione TTS, não use markdown e não escreva rótulos como “texto para ser lido”.
            """.trimIndent()
        } else {
            cleanMessage
        }

        val messages = JSONArray().put(
            JSONObject().put("role", "user").put("content", outboundMessage)
        )
        val body = JSONObject().put("messages", messages)

        return runCatching {
            val (status, response) = request(baseUrl, "POST", "/v1/chat", accessToken, body.toString())
            if (status !in 200..299) {
                val serverMessage = runCatching {
                    JSONObject(response).optString("message").takeIf { it.isNotBlank() }
                }.getOrNull() ?: response.take(180).ifBlank { null }
                throw ChatException(status, serverMessage)
            }
            val json = JSONObject(response)
            val rawText = json.optString("text").takeIf { it.isNotBlank() } ?: return@runCatching null
            val text = sanitizeAssistantText(rawText)
            if (text.isBlank()) {
                return@runCatching ChatResponse(
                    text = "Tive um problema ao preparar a resposta. Tente perguntar novamente.",
                    mode = json.optString("mode", "unknown"),
                    provider = json.optString("provider").takeIf { it.isNotBlank() },
                    model = json.optString("model").takeIf { it.isNotBlank() },
                    stages = emptyList(),
                    providersConfigured = json.optInt("providersConfigured", 0),
                    providersAvailable = json.optInt("providersAvailable", 4)
                )
            }
            val stageArray = json.optJSONArray("stages") ?: JSONArray()
            val stages = buildList {
                for (index in 0 until stageArray.length()) {
                    stageArray.optString(index).trim().takeIf { it.isNotBlank() }?.let(::add)
                }
            }
            ChatResponse(
                text = text,
                mode = json.optString("mode", "unknown"),
                provider = json.optString("provider").takeIf { it.isNotBlank() },
                model = json.optString("model").takeIf { it.isNotBlank() },
                stages = stages,
                providersConfigured = json.optInt("providersConfigured", 0),
                providersAvailable = json.optInt("providersAvailable", 4)
            )
        }.getOrElse { error ->
            if (error is ChatException) throw error
            null
        }
    }

    private fun reminderManagementResponse(accessToken: String?, message: String): ChatResponse? {
        if (accessToken.isNullOrBlank()) return null
        val normalized = normalizeText(message)
        val health = healthStatus()

        if (looksLikeReminderListing(normalized)) {
            val reminders = activeReminders(accessToken)
            if (reminders.isEmpty()) return localActionResponse("Não encontrei lembretes ativos.", health)
            val now = System.currentTimeMillis()
            val lines = reminders.take(20).mapIndexed { index, reminder ->
                val overdue = reminder.nextFireAtMillis < now
                "\${index + 1}. \${reminder.title}, \${formatReminderDate(reminder.nextFireAtMillis)}\${if (overdue) ", em atraso" else ""}" +
                    (reminder.details?.takeIf { it.isNotBlank() }?.let { ". $it" } ?: "")
            }
            val intro = if (reminders.size == 1) "Você tem um lembrete ativo: " else "Você tem \${reminders.size} lembretes ativos: "
            val suffix = if (reminders.size > 20) " Estou mostrando os primeiros 20." else ""
            return localActionResponse(intro + lines.joinToString(". ") + "." + suffix, health)
        }

        if (!looksLikeReminderEdit(normalized)) return null
        val reminders = activeReminders(accessToken)
        if (reminders.isEmpty()) return localActionResponse("Não há lembretes ativos para alterar.", health)
        val targets = reminders.filter { reminder ->
            normalizeText(reminder.title).split(Regex("\\s+")).filter { it.length >= 4 }
                .any { word -> normalized.contains(word) }
        }
        if (targets.isEmpty()) {
            return localActionResponse("Não consegui identificar qual lembrete você quer alterar. Diga parte do nome e o novo horário.", health)
        }
        if (targets.size > 1) {
            return localActionResponse("Encontrei mais de um lembrete parecido: " +
                targets.take(5).joinToString("; ") { "\${it.title}, \${formatReminderDate(it.nextFireAtMillis)}" } +
                ". Diga qual deles quer alterar.", health)
        }

        val target = targets.first()
        val timeMatch = Regex("\\b(?:as|para as|pelas?)\\s*(\\d{1,2})(?:[:h](\\d{2}))?\\s*h?\\b").find(normalized)
        val saysToday = Regex("\\bhoje\\b").containsMatchIn(normalized)
        val saysTomorrow = Regex("\\bamanha\\b").containsMatchIn(normalized)
        if (timeMatch == null && !saysToday && !saysTomorrow) {
            return localActionResponse("Diga o novo dia ou horário, por exemplo: mude o lembrete \${target.title} para amanhã às 18h.", health)
        }

        val zone = ZoneId.systemDefault()
        val oldDateTime = Instant.ofEpochMilli(target.nextFireAtMillis).atZone(zone).toLocalDateTime()
        var date = when {
            saysTomorrow -> LocalDate.now(zone).plusDays(1)
            saysToday -> LocalDate.now(zone)
            else -> oldDateTime.toLocalDate()
        }
        val time = if (timeMatch != null) {
            val hour = timeMatch.groupValues[1].toIntOrNull()
            val minute = timeMatch.groupValues[2].takeIf { it.isNotBlank() }?.toIntOrNull() ?: 0
            if (hour == null || hour !in 0..23 || minute !in 0..59) {
                return localActionResponse("Esse horário não é válido. Use, por exemplo, 18h ou 18:30.", health)
            }
            LocalTime.of(hour, minute)
        } else oldDateTime.toLocalTime().withSecond(0).withNano(0)

        var newDateTime = LocalDateTime.of(date, time)
        if (!saysToday && !saysTomorrow && timeMatch != null &&
            newDateTime.atZone(zone).toInstant().toEpochMilli() <= System.currentTimeMillis()) {
            date = date.plusDays(1)
            newDateTime = LocalDateTime.of(date, time)
        }
        val newMillis = newDateTime.atZone(zone).toInstant().toEpochMilli()
        if (!updateReminderTime(accessToken, target.id, newMillis)) {
            return localActionResponse("Não consegui alterar esse lembrete agora. Ele continua como estava.", health)
        }
        return localActionResponse("Pronto. O lembrete \${target.title} foi alterado para \${formatReminderDate(newMillis)}.", health)
    }

    private fun looksLikeReminderListing(normalized: String): Boolean {
        val hasReminder = Regex("\\b(lembrete|lembretes|avisos?)\\b").containsMatchIn(normalized)
        val listIntent = Regex("\\b(lista|listar|liste|mostra|mostrar|mostre|quais|agenda|relembra|relembrar|relembre)\\b").containsMatchIn(normalized) ||
            Regex("\\b(o que tenho|tenho para fazer|tenho a fazer|proximos lembretes|lembretes de hoje|lembretes para hoje)\\b").containsMatchIn(normalized)
        return hasReminder && listIntent
    }

    private fun looksLikeReminderEdit(normalized: String): Boolean {
        val action = Regex("\\b(altere|alterar|altera|mude|mudar|muda|adia|adiar|adiante|remarque|remarcar|passa|passe|troque|trocar|atualize|atualizar)\\b")
        val objectWord = Regex("\\b(lembrete|lembretes|aviso|avisos)\\b")
        return action.containsMatchIn(normalized) && objectWord.containsMatchIn(normalized) && !looksLikeReminderCancellation(normalized)
    }

    private fun formatReminderDate(millis: Long): String {
        val formatter = DateTimeFormatter.ofPattern("d 'de' MMMM 'às' HH:mm", Locale("pt", "PT"))
        return runCatching { Instant.ofEpochMilli(millis).atZone(ZoneId.systemDefault()).format(formatter) }
            .getOrDefault("num horário não identificado")
    }

    private fun updateReminderTime(accessToken: String, id: String, millis: Long): Boolean {
        if (accessToken.isBlank() || id.isBlank()) return false
        return runCatching {
            val root = BuildConfig.SUPABASE_URL.trim().trimEnd('/')
            val encodedId = java.net.URLEncoder.encode(id, "UTF-8")
            val connection = (URL("$root/rest/v1/jarvis_reminders?id=eq.$encodedId&active=eq.true").openConnection() as HttpURLConnection).apply {
                requestMethod = "PATCH"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                doOutput = true
                setRequestProperty("Accept", "application/json")
                setRequestProperty("Content-Type", "application/json; charset=utf-8")
                setRequestProperty("Prefer", "return=representation")
                setRequestProperty("apikey", BuildConfig.SUPABASE_PUBLISHABLE_KEY)
                setRequestProperty("Authorization", "Bearer $accessToken")
            }
            try {
                connection.outputStream.bufferedWriter(Charsets.UTF_8).use {
                    it.write(JSONObject().put("next_fire_at", Instant.ofEpochMilli(millis).toString()).toString())
                }
                val status = connection.responseCode
                val stream = if (status in 200..299) connection.inputStream else connection.errorStream
                val response = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }.orEmpty()
                status in 200..299 && runCatching { JSONArray(response).length() > 0 }.getOrDefault(false)
            } finally { connection.disconnect() }
        }.getOrDefault(false)
    }

    private fun reminderCancellationResponse(accessToken: String?, message: String): ChatResponse? {
        if (accessToken.isNullOrBlank() || !looksLikeReminderCancellation(message)) return null

        val reminders = activeReminders(accessToken)
        val health = healthStatus()

        if (reminders.isEmpty()) {
            return localActionResponse(
                "Não há nenhum lembrete ativo para eu apagar.",
                health
            )
        }

        val normalizedMessage = normalizeText(message)
        val cancelAll = Regex("\\b(todos|todas|qualquer|quaisquer)\\b").containsMatchIn(normalizedMessage)
        if (cancelAll && reminders.size > 1) {
            val confirmed = Regex("\\b(confirmo|confirmar|confirmado|confirmada|sim apague|pode apagar|pode excluir)\\b")
                .containsMatchIn(normalizedMessage)
            if (!confirmed) {
                return localActionResponse(
                    "Isso vai apagar todos os \${reminders.size} lembretes ativos. Para confirmar, diga: confirmo apagar todos os lembretes.",
                    health
                )
            }
        }
        val targets = when {
            cancelAll -> reminders
            reminders.size == 1 -> reminders
            else -> reminders.filter { reminder ->
                val titleWords = normalizeText(reminder.title)
                    .split(Regex("\\s+"))
                    .filter { it.length >= 4 }
                titleWords.any { word -> normalizedMessage.contains(word) }
            }
        }

        if (targets.isEmpty()) {
            return localActionResponse(
                "Tenho mais de um lembrete ativo. Diga qual deles quer que eu apague.",
                health
            )
        }

        val cancelled = targets.filter { deactivateReminder(accessToken, it.id) }
        if (cancelled.size != targets.size) {
            return localActionResponse(
                "Não consegui apagar o lembrete agora. Tente novamente em instantes.",
                health
            )
        }

        val text = if (cancelled.size == 1) {
            "Pronto. Esqueci o lembrete “${cancelled.first().title}”."
        } else {
            "Pronto. Apaguei ${cancelled.size} lembretes ativos."
        }
        return localActionResponse(text, health, cancelled.map { it.id })
    }

    private fun looksLikeReminderCancellation(text: String): Boolean {
        val normalized = normalizeText(text)
        val action = Regex("\\b(esqueca|esquece|esquecer|apaga|apague|apagar|cancela|cancele|cancelar|remove|remova|remover|desativa|desative|desativar)\\b")
        val objectWord = Regex("\\b(lembrete|lembretes|aviso|avisos)\\b")
        return action.containsMatchIn(normalized) && objectWord.containsMatchIn(normalized)
    }

    private fun normalizeText(text: String): String {
        return java.text.Normalizer.normalize(text, java.text.Normalizer.Form.NFD)
            .replace(Regex("\\p{M}+"), "")
            .lowercase(Locale.ROOT)
    }

    private fun localActionResponse(
        text: String,
        health: HealthStatus,
        cancelledReminderIds: List<String> = emptyList()
    ): ChatResponse {
        return ChatResponse(
            text = sanitizeAssistantText(text),
            mode = if (health.online) health.chatMode else "local-action",
            provider = "jarvis-local",
            model = "reminder-action",
            stages = listOf("Executando"),
            providersConfigured = health.providersConfigured,
            providersAvailable = health.providersAvailable,
            cancelledReminderIds = cancelledReminderIds
        )
    }

    private fun deactivateReminder(accessToken: String, id: String): Boolean {
        if (id.isBlank()) return false
        return runCatching {
            val root = BuildConfig.SUPABASE_URL.trim().trimEnd('/')
            val connection = (URL("$root/rest/v1/rpc/jarvis_cancel_reminder").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                doOutput = true
                setRequestProperty("Accept", "application/json")
                setRequestProperty("Content-Type", "application/json; charset=utf-8")
                setRequestProperty("apikey", BuildConfig.SUPABASE_PUBLISHABLE_KEY)
                setRequestProperty("Authorization", "Bearer $accessToken")
            }
            try {
                connection.outputStream.bufferedWriter(Charsets.UTF_8).use {
                    it.write(JSONObject().put("p_id", id).toString())
                }
                connection.responseCode in 200..299
            } finally {
                connection.disconnect()
            }
        }.getOrDefault(false)
    }

    private fun sanitizeAssistantText(raw: String): String {
        var text = raw.trim()

        // Nunca apresentar raciocínio interno do modelo ao utilizador.
        text = text.replace(Regex("(?is)<think>.*?</think>"), "").trim()
        text = text.replace(Regex("(?is)<analysis>.*?</analysis>"), "").trim()

        val finalMarkers = listOf(
            Regex("(?im)^\\s*(?:resposta\\s+final|final\\s+answer|answer)\\s*[:\\-]\\s*"),
            Regex("(?im)^\\s*(?:resposta)\\s*[:\\-]\\s*")
        )
        for (marker in finalMarkers) {
            val match = marker.find(text)
            if (match != null && match.range.first > 0) {
                text = text.substring(match.range.last + 1).trim()
                break
            }
        }

        val suspiciousInternal = Regex(
            "(?is)^\\s*(?:analysis|reasoning|thoughts?|chain[- ]of[- ]thought|" +
                "o\\s+usu[aá]rio\\s+(?:quer|pediu|est[aá]\\s+pedindo)|" +
                "the\\s+user\\s+(?:wants|asks|is\\s+asking)|" +
                "we\\s+need\\s+to|i\\s+need\\s+to)\\b"
        )
        if (suspiciousInternal.containsMatchIn(text)) return ""

        val directivePatterns = listOf(
            Regex("(?is)\\*\\*\\s*texto\\s+para\\s+ser\\s+lido\\s+em\\s+voz\\s+(?:feminina|masculina)[^*]*\\*\\*\\s*:?"),
            Regex("(?is)texto\\s+para\\s+ser\\s+lido\\s+em\\s+voz\\s+(?:feminina|masculina)\\s*:?"),
            Regex("(?is)\\*\\*\\s*(?:instrução|instrucao)\\s+(?:de\\s+)?tts[^*]*\\*\\*\\s*:?"),
            Regex("(?is)^\\s*(?:tts|voz)\\s*:\\s*(?:feminina|masculina)\\s*[-—:]?\\s*")
        )
        directivePatterns.forEach { pattern -> text = text.replace(pattern, "").trim() }

        text = text.replace(Regex("(?iu)\\baviarei\\b"), "avisarei")

        if (
            text.length >= 2 &&
            ((text.startsWith('“') && text.endsWith('”')) ||
                (text.startsWith('"') && text.endsWith('"')))
        ) {
            text = text.substring(1, text.length - 1).trim()
        }

        return text
    }

    fun transcribe(accessToken: String?, wavBytes: ByteArray): String? {
        if (accessToken.isNullOrBlank() || wavBytes.isEmpty()) return null
        val encoded = Base64.encodeToString(wavBytes, Base64.NO_WRAP)
        val body = JSONObject().put("audioBase64", encoded).put("mimeType", "audio/wav")
        return runCatching {
            val (status, response) = request(voiceBaseUrl, "POST", "/transcribe", accessToken, body.toString())
            if (status !in 200..299) return@runCatching null
            JSONObject(response).optString("text").trim().takeIf { it.isNotBlank() }
        }.getOrNull()
    }

    fun synthesizeSpeech(accessToken: String?, text: String): SpeechAudio? {
        if (accessToken.isNullOrBlank() || text.isBlank()) return null
        val body = JSONObject().put("text", text.trim())
        repeat(2) { attempt ->
            val audio = runCatching {
                val (status, response) = request(voiceBaseUrl, "POST", "/speak", accessToken, body.toString())
                if (status !in 200..299) return@runCatching null
                val json = JSONObject(response)
                val encoded = json.optString("audioBase64")
                if (encoded.isBlank()) return@runCatching null
                SpeechAudio(
                    pcm = Base64.decode(encoded, Base64.DEFAULT),
                    sampleRate = json.optInt("sampleRate", 24_000).coerceAtLeast(8_000)
                )
            }.getOrNull()
            if (audio != null) return audio
            if (attempt == 0) Thread.sleep(350L)
        }
        return null
    }

    fun activeReminders(accessToken: String): List<Reminder> {
        if (accessToken.isBlank()) return emptyList()
        return runCatching {
            val (status, response) = request(baseUrl, "GET", "/v1/reminders/active", accessToken, null)
            if (status !in 200..299) return@runCatching emptyList()
            val rows = JSONObject(response).optJSONArray("reminders") ?: JSONArray()
            buildList {
                for (index in 0 until rows.length()) {
                    val row = rows.optJSONObject(index) ?: continue
                    val id = row.optString("id").trim()
                    val title = row.optString("title").trim()
                    val nextFireAt = row.optString("next_fire_at").trim()
                    if (id.isBlank() || title.isBlank() || nextFireAt.isBlank()) continue
                    val millis = runCatching {
                        OffsetDateTime.parse(nextFireAt).toInstant().toEpochMilli()
                    }.recoverCatching {
                        Instant.parse(nextFireAt).toEpochMilli()
                    }.getOrNull() ?: continue
                    add(
                        Reminder(
                            id = id,
                            title = title,
                            details = row.optString("details").takeIf { it.isNotBlank() },
                            intervalMinutes = if (row.isNull("interval_minutes")) null else row.optInt("interval_minutes").takeIf { it > 0 },
                            nextFireAtMillis = millis
                        )
                    )
                }
            }
        }.getOrDefault(emptyList())
    }

    fun markReminderFired(accessToken: String, id: String): Boolean {
        if (accessToken.isBlank() || id.isBlank()) return false
        val body = JSONObject().put("id", id)
        return runCatching {
            request(baseUrl, "POST", "/v1/reminders/fired", accessToken, body.toString()).first in 200..299
        }.getOrDefault(false)
    }

    private fun request(
        rootUrl: String,
        method: String,
        path: String,
        accessToken: String?,
        body: String?
    ): Pair<Int, String> {
        val connection = (URL("$rootUrl$path").openConnection() as HttpURLConnection).apply {
            requestMethod = method
            connectTimeout = CONNECT_TIMEOUT_MS
            readTimeout = READ_TIMEOUT_MS
            setRequestProperty("Accept", "application/json")
            if (!accessToken.isNullOrBlank()) setRequestProperty("Authorization", "Bearer $accessToken")
            if (body != null) {
                doOutput = true
                setRequestProperty("Content-Type", "application/json; charset=utf-8")
            }
        }

        try {
            if (body != null) connection.outputStream.bufferedWriter(Charsets.UTF_8).use { it.write(body) }
            val status = connection.responseCode
            val stream = if (status in 200..299) connection.inputStream else connection.errorStream
            val response = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }.orEmpty()
            return status to response
        } finally {
            connection.disconnect()
        }
    }
}
