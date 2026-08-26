package pt.vcaitano.vocmanager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

final class CatalogClient {
    static final String CATALOG_URL =
            "https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/manifest.json";

    // Last known-good public catalog snapshot. It is intentionally usable when GitHub Raw
    // has a transient DNS/TLS/network failure so the Manager never falls back to the old
    // v0.14/coming-soon state. The live catalog remains authoritative whenever reachable.
    private static final String FALLBACK_CATALOG = "{"
            + "\"schemaVersion\":1,"
            + "\"apps\":["
            + "{"
            + "\"id\":\"voc-manager\","
            + "\"name\":\"voc Manager\","
            + "\"packageName\":\"pt.vcaitano.vocmanager\","
            + "\"category\":\"system\","
            + "\"description\":\"Instala, abre e atualiza os apps voc.\","
            + "\"status\":\"coming_soon\","
            + "\"versionCode\":4,"
            + "\"versionName\":\"1.2.0\","
            + "\"minSdk\":28,"
            + "\"apkUrl\":null,"
            + "\"sha256\":null,"
            + "\"signatureSha256\":\"918b566590b49f691ec9880c95dd174a6c032b21f81dc66efcfac74d0de11aa8\","
            + "\"iconUrl\":null,"
            + "\"changelog\":\"voc Manager 1.2.0.\","
            + "\"mandatory\":false,"
            + "\"monetization\":{"
            + "\"type\":\"free\","
            + "\"priceCents\":0,"
            + "\"currency\":\"EUR\","
            + "\"period\":null,"
            + "\"trialDays\":0,"
            + "\"provider\":\"none\""
            + "}"
            + "},"
            + "{"
            + "\"id\":\"voc-tv\","
            + "\"name\":\"voc TV\","
            + "\"packageName\":\"pt.vcaitano.iptvia\","
            + "\"category\":\"entertainment\","
            + "\"description\":\"Pesquisa inteligente e reprodução de filmes, séries, TV ao vivo e vídeos públicos com assistência de IA.\","
            + "\"status\":\"published\","
            + "\"versionCode\":18,"
            + "\"versionName\":\"0.18.0\","
            + "\"minSdk\":26,"
            + "\"apkUrl\":\"https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/voc-tv/v0.18/vocTV-v0.18.apk\","
            + "\"sha256\":\"2ca9767b0466286fb6aeb04ac7859c3b89f773dd3a7df9773ca8f238d99619f2\","
            + "\"signatureSha256\":\"629c7b0942460a5d484ec938cc3e0a4e32a6a489572cd179fb94e43cefa05b2e\","
            + "\"iconUrl\":\"https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/icons/voc-tv.webp\","
            + "\"changelog\":\"voc TV v0.18.\","
            + "\"mandatory\":false,"
            + "\"monetization\":{"
            + "\"type\":\"subscription\","
            + "\"priceCents\":150,"
            + "\"currency\":\"EUR\","
            + "\"period\":\"P1M\","
            + "\"trialDays\":0,"
            + "\"provider\":\"pending\""
            + "}"
            + "},"
            + "{"
            + "\"id\":\"damas\","
            + "\"name\":\"Damas\","
            + "\"packageName\":\"pt.vcaitano.damas\","
            + "\"category\":\"games\","
            + "\"description\":\"Jogo de damas com adversário de IA avançado e modo online para jogar contra amigos.\","
            + "\"status\":\"published\","
            + "\"versionCode\":1,"
            + "\"versionName\":\"1.0.0\","
            + "\"minSdk\":23,"
            + "\"apkUrl\":\"https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/damas/v1.0/Damas-v1.0.0.apk\","
            + "\"sha256\":\"45f6eb4931519bf129bff48dca266bf9ca264e0a0891f3c9295789d234f82730\","
            + "\"signatureSha256\":\"07df7362d3a99e638d54ce97e35328b6ca415f44481198ff2f6cf47bbadb9269\","
            + "\"iconUrl\":\"https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/icons/damas.webp\","
            + "\"changelog\":\"Damas v1.0.0.\","
            + "\"mandatory\":false,"
            + "\"monetization\":{"
            + "\"type\":\"free\","
            + "\"priceCents\":0,"
            + "\"currency\":\"EUR\","
            + "\"period\":null,"
            + "\"trialDays\":0,"
            + "\"provider\":\"none\""
            + "}"
            + "},"
            + "{"
            + "\"id\":\"jarvis\","
            + "\"name\":\"Jarvis\","
            + "\"packageName\":\"pt.vcaitano.jarvis\","
            + "\"category\":\"productivity\","
            + "\"description\":\"Assistente pessoal com voz, texto, lembretes e contexto do dispositivo.\","
            + "\"status\":\"published\","
            + "\"versionCode\":9,"
            + "\"versionName\":\"0.2.7\","
            + "\"minSdk\":26,"
            + "\"apkUrl\":\"https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/apks/jarvis/v0.2.7/Jarvis-0.2.7.apk\","
            + "\"sha256\":\"200e7d7882292da02b8bbd7d54d0f5bcc992e532a6e4146aee2227602cf85f9b\","
            + "\"signatureSha256\":\"ba12569f844825cb434ae73b98deab84febd83694b4ccf1487b4af4dc59fd2fb\","
            + "\"iconUrl\":null,"
            + "\"changelog\":\"Jarvis 0.2.7 — reconhecimento de voz migrado para o SpeechRecognizer do Android, com preferência por reconhecimento no dispositivo; estado de escuta persistente e correção do VoicePrint. Mantém as restantes funções da 0.2.6.\","
            + "\"mandatory\":false,"
            + "\"monetization\":{"
            + "\"type\":\"free\","
            + "\"priceCents\":0,"
            + "\"currency\":\"EUR\","
            + "\"period\":null,"
            + "\"trialDays\":0,"
            + "\"provider\":\"none\""
            + "}"
            + "}"
            + "]"
            + "}";

    List<CatalogApp> load() throws Exception {
        Exception lastFailure = null;
        for (int attempt = 0; attempt < 3; attempt++) {
            try {
                return loadRemote();
            } catch (Exception remoteFailure) {
                lastFailure = remoteFailure;
                if (attempt < 2) {
                    try {
                        Thread.sleep(250L * (attempt + 1));
                    } catch (InterruptedException interrupted) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }

        // Keep the Manager useful during temporary catalog/network failures.
        // A last-known-good snapshot is safer than the previous obsolete v0.14 snapshot.
        if (lastFailure != null) {
            android.util.Log.w("vocManager", "Using fallback catalog: " + lastFailure.getClass().getSimpleName());
        }
        return parseCatalog(FALLBACK_CATALOG);
    }

    private List<CatalogApp> loadRemote() throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(CATALOG_URL).openConnection();
        connection.setConnectTimeout(8_000);
        connection.setReadTimeout(8_000);
        connection.setInstanceFollowRedirects(true);
        connection.setUseCaches(false);
        connection.setRequestProperty("Accept", "application/json");
        connection.setRequestProperty("Cache-Control", "no-cache, no-store");
        connection.setRequestProperty("Pragma", "no-cache");
        connection.setRequestProperty("User-Agent", "voc-Manager/1.2");

        int code = connection.getResponseCode();
        if (code < 200 || code >= 300) {
            connection.disconnect();
            throw new IllegalStateException("Catálogo HTTP " + code);
        }

        try (BufferedInputStream input = new BufferedInputStream(connection.getInputStream());
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[16 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) {
                output.write(buffer, 0, read);
            }
            return parseCatalog(new String(output.toByteArray(), StandardCharsets.UTF_8));
        } finally {
            connection.disconnect();
        }
    }

    private static List<CatalogApp> parseCatalog(String json) throws Exception {
        JSONObject root = new JSONObject(json);
        if (root.optInt("schemaVersion", -1) != 1) {
            throw new IllegalStateException("Versão de catálogo não suportada");
        }

        JSONArray apps = root.getJSONArray("apps");
        List<CatalogApp> result = new ArrayList<>();
        for (int i = 0; i < apps.length(); i++) {
            CatalogApp app = CatalogApp.fromJson(apps.getJSONObject(i));
            if (!"disabled".equals(app.status)) {
                result.add(app);
            }
        }
        return result;
    }
}
