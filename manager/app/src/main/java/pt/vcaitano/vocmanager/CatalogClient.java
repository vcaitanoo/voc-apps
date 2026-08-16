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

    List<CatalogApp> load() throws Exception {
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

            JSONObject root = new JSONObject(
                    new String(output.toByteArray(), StandardCharsets.UTF_8)
            );
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
        } finally {
            connection.disconnect();
        }
    }
}
