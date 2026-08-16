package pt.vcaitano.vocmanager;

import org.json.JSONObject;

final class CatalogApp {
    final String id;
    final String name;
    final String packageName;
    final String category;
    final String description;
    final String status;
    final long versionCode;
    final String versionName;
    final int minSdk;
    final String apkUrl;
    final String sha256;
    final String signatureSha256;
    final String iconUrl;
    final String changelog;
    final boolean mandatory;

    private CatalogApp(
            String id,
            String name,
            String packageName,
            String category,
            String description,
            String status,
            long versionCode,
            String versionName,
            int minSdk,
            String apkUrl,
            String sha256,
            String signatureSha256,
            String iconUrl,
            String changelog,
            boolean mandatory
    ) {
        this.id = id;
        this.name = name;
        this.packageName = packageName;
        this.category = category;
        this.description = description;
        this.status = status;
        this.versionCode = versionCode;
        this.versionName = versionName;
        this.minSdk = minSdk;
        this.apkUrl = apkUrl;
        this.sha256 = sha256;
        this.signatureSha256 = signatureSha256;
        this.iconUrl = iconUrl;
        this.changelog = changelog;
        this.mandatory = mandatory;
    }

    static CatalogApp fromJson(JSONObject o) {
        return new CatalogApp(
                o.getString("id"),
                o.getString("name"),
                o.getString("packageName"),
                o.optString("category", "app"),
                o.optString("description", ""),
                o.optString("status", "disabled"),
                o.optLong("versionCode", 0),
                o.optString("versionName", ""),
                o.optInt("minSdk", 26),
                nullable(o, "apkUrl"),
                nullable(o, "sha256"),
                nullable(o, "signatureSha256"),
                nullable(o, "iconUrl"),
                o.optString("changelog", ""),
                o.optBoolean("mandatory", false)
        );
    }

    private static String nullable(JSONObject o, String key) {
        if (!o.has(key) || o.isNull(key)) return null;
        String value = o.optString(key, null);
        return value == null || value.isBlank() ? null : value;
    }
}
