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
            + "\"versionCode\":0,"
            + "\"versionName\":\"\","
            + "\"minSdk\":28,"
            + "\"apkUrl\":null,"
            + "\"sha256\":null,"
            + "\"signatureSha256\":null,"
            + "\"iconUrl\":null,"
            + "\"changelog\":\"Primeira versão do voc Manager em preparação.\","
            + "\"mandatory\":false"
            + "},"
            + "{"
            + "\"id\":\"voc-tv\","
            + "\"name\":\"voc TV\","
            + "\"packageName\":\"pt.vcaitano.iptvia\","
            + "\"category\":\"entertainment\","
            + "\"description\":\"Pesquisa e reprodução de conteúdo com assistência de IA.\","
            + "\"status\":\"coming_soon\","
            + "\"versionCode\":14,"
            + "\"versionName\":\"0.14.0\","
            + "\"minSdk\":26,"
            + "\"apkUrl\":null,"
            + "\"sha256\":null,"
            + "\"signatureSha256\":\"629c7b0942460a5d484ec938cc3e0a4e32a6a489572cd179fb94e43cefa05b2e\","
            + "\"iconUrl\":null,"
            + "\"changelog\":\"voc TV v0.14 em preparação.\","
            + "\"mandatory\":false"
            + "}"
            + "]"
            + "}";

    List<CatalogApp> load() throws Exception {
        try {
            return loadRemote();
        } catch (Exception remoteFailure) {
            // Keep the Manager usable during temporary DNS/network outages.
            // The bundled catalog never contains private credentials and is refreshed
            // whenever the application itself is updated.
            return parseCatalog(FALLBACK_CATALOG);
        }
    }

    private List<CatalogApp> loadRemote() throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(CATALOG_URL).openConnection();
        connection.setConnectTimeout(8_000);
        connection.setReadTimeout(8_000);
        connection.setInstanceFollowRedirects(true);
        connection.setRequestProperty("Accept", "application/json");
        connection.setRequestProperty("Cache-Control", "no-cache");
        connection.setRequestProperty("User-Agent", "voc-Manager/1.0");

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
