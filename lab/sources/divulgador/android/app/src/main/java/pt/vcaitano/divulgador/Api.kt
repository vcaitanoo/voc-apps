package pt.vcaitano.divulgador

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

const val DIVULGADOR_BASE_URL =
    "https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/divulgador-api"

private const val SUPABASE_ANON_KEY =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW5ub3hwZXNuaHRtbXZya2VuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0Mjk1ODEsImV4cCI6MjEwMzAwNTU4MX0.qjxxRzOzDNj9UwOzKOJ5BEOHl-9TfSpE9nDl7wkf2zo"

data class Stats(
    val total: Int,
    val sent: Int,
    val queued: Int,
    val skipped: Int,
    val failed: Int
)

data class Campaign(
    val id: String,
    val name: String,
    val link: String,
    val description: String,
    val audience: String,
    val state: String,
    val stats: Stats
)

data class Health(
    val status: String,
    val dryRun: Boolean,
    val aiConfigured: Boolean,
    val emailConfigured: Boolean,
    val realSendReady: Boolean
)

class Api(private var baseUrl: String = DIVULGADOR_BASE_URL) {

    private val http = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    fun setBase(url: String) {
        baseUrl = url.trim().trimEnd('/')
    }

    private fun url(path: String): String {
        if (baseUrl.isBlank()) throw IOException("Servidor nao configurado")
        return "$baseUrl$path"
    }

    private fun request(path: String): Request.Builder =
        Request.Builder()
            .url(url(path))
            .header("apikey", SUPABASE_ANON_KEY)
            .header("Authorization", "Bearer $SUPABASE_ANON_KEY")
            .header("Accept", "application/json")

    private fun requireSuccess(code: Int, body: String): String {
        if (code !in 200..299) {
            throw IOException("HTTP " + code + ": " + body.take(200))
        }
        return body
    }

    private fun parseStats(o: JSONObject?) = Stats(
        o?.optInt("total") ?: 0,
        o?.optInt("sent") ?: 0,
        o?.optInt("queued") ?: 0,
        o?.optInt("skipped") ?: 0,
        o?.optInt("failed") ?: 0
    )

    private fun parseCampaign(o: JSONObject) = Campaign(
        o.getString("id"),
        o.optString("name"),
        o.optString("link"),
        o.optString("description"),
        o.optString("audience"),
        o.optString("state", "active"),
        parseStats(o.optJSONObject("stats"))
    )

    suspend fun health(): Health = withContext(Dispatchers.IO) {
        http.newCall(request("/health").get().build()).execute().use { r ->
            val body = requireSuccess(r.code, r.body?.string().orEmpty())
            val o = JSONObject(body)
            Health(
                o.optString("status"),
                o.optBoolean("dryRun", true),
                o.optBoolean("aiConfigured"),
                o.optBoolean("emailConfigured"),
                o.optBoolean("realSendReady")
            )
        }
    }

    suspend fun list(): List<Campaign> = withContext(Dispatchers.IO) {
        http.newCall(request("/api/campaigns").get().build()).execute().use { r ->
            val body = requireSuccess(r.code, r.body?.string().orEmpty())
            val arr = JSONArray(body)
            (0 until arr.length()).map { parseCampaign(arr.getJSONObject(it)) }
        }
    }

    suspend fun create(
        name: String,
        link: String,
        description: String,
        audience: String,
        dailyCap: Int
    ): String = withContext(Dispatchers.IO) {
        val payload = JSONObject()
            .put("name", name)
            .put("link", link)
            .put("description", description)
            .put("audience", audience)
            .put("daily_cap", dailyCap)
            .toString()
            .toRequestBody("application/json".toMediaType())
        http.newCall(request("/api/campaigns").post(payload).build()).execute().use { r ->
            val body = requireSuccess(r.code, r.body?.string().orEmpty())
            JSONObject(body).getString("id")
        }
    }

    suspend fun setState(id: String, state: String) = withContext(Dispatchers.IO) {
        val payload = JSONObject()
            .put("state", state)
            .toString()
            .toRequestBody("application/json".toMediaType())
        http.newCall(request("/api/campaigns/$id/state").post(payload).build()).execute().use { r ->
            requireSuccess(r.code, r.body?.string().orEmpty())
        }
    }

    suspend fun delete(id: String) = withContext(Dispatchers.IO) {
        http.newCall(request("/api/campaigns/$id").delete().build()).execute().use { r ->
            requireSuccess(r.code, r.body?.string().orEmpty())
        }
    }
}
