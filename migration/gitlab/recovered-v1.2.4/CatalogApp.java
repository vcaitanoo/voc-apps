package pt.vcaitano.vocmanager;

import org.json.JSONException;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

final class CatalogApp {
    static final String BILLING_FREE = "free";
    static final String BILLING_ONE_TIME = "one_time";
    static final String BILLING_SUBSCRIPTION = "subscription";

    final String id;
    final String name;
    final String packageName;
    final String category;
    final String description;
    final String status;
    final long versionCode;
    final String versionName;
    final int minSdk;
    final String distribution;
    final String playUrl;
    final String apkUrl;
    final List<ApkPart> apkParts;
    final String sha256;
    final String signatureSha256;
    final String iconUrl;
    final String changelog;
    final boolean mandatory;
    final String billingType;
    final int priceCents;
    final String currency;
    final String billingPeriod;
    final int trialDays;
    final String billingProvider;

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
            String distribution,
            String playUrl,
            String apkUrl,
            List<ApkPart> apkParts,
            String sha256,
            String signatureSha256,
            String iconUrl,
            String changelog,
            boolean mandatory,
            String billingType,
            int priceCents,
            String currency,
            String billingPeriod,
            int trialDays,
            String billingProvider
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
        this.distribution = distribution;
        this.playUrl = playUrl;
        this.apkUrl = apkUrl;
        this.apkParts = apkParts;
        this.sha256 = sha256;
        this.signatureSha256 = signatureSha256;
        this.iconUrl = iconUrl;
        this.changelog = changelog;
        this.mandatory = mandatory;
        this.billingType = billingType;
        this.priceCents = Math.max(0, priceCents);
        this.currency = currency;
        this.billingPeriod = billingPeriod;
        this.trialDays = Math.max(0, trialDays);
        this.billingProvider = billingProvider;
    }

    static CatalogApp fromJson(JSONObject o) throws JSONException {
        JSONObject monetization = o.optJSONObject("monetization");
        String billingType = BILLING_FREE;
        int priceCents = 0;
        String currency = "EUR";
        String billingPeriod = null;
        int trialDays = 0;
        String billingProvider = "none";

        if (monetization != null) {
            billingType = monetization.optString("type", BILLING_FREE);
            if (!BILLING_FREE.equals(billingType)
                    && !BILLING_ONE_TIME.equals(billingType)
                    && !BILLING_SUBSCRIPTION.equals(billingType)) {
                billingType = BILLING_FREE;
            }
            priceCents = Math.max(0, monetization.optInt("priceCents", 0));
            currency = monetization.optString("currency", "EUR");
            billingPeriod = nullable(monetization, "period");
            trialDays = Math.max(0, monetization.optInt("trialDays", 0));
            billingProvider = monetization.optString("provider", "none");
        }

        String distribution = o.optString("distribution", "apk").trim().toLowerCase(Locale.ROOT);
        if (!"play".equals(distribution)) distribution = "apk";

        String baseDescription = o.optString("description", "");
        String description = decorateDescription(
                baseDescription,
                billingType,
                priceCents,
                currency,
                billingPeriod
        );

        return new CatalogApp(
                o.getString("id"),
                o.getString("name"),
                o.getString("packageName"),
                o.optString("category", "app"),
                description,
                o.optString("status", "disabled"),
                o.optLong("versionCode", 0),
                o.optString("versionName", ""),
                o.optInt("minSdk", 28),
                distribution,
                nullable(o, "playUrl"),
                nullable(o, "apkUrl"),
                parseApkParts(o.optJSONArray("apkParts")),
                nullable(o, "sha256"),
                nullable(o, "signatureSha256"),
                nullable(o, "iconUrl"),
                o.optString("changelog", ""),
                o.optBoolean("mandatory", false),
                billingType,
                priceCents,
                currency,
                billingPeriod,
                trialDays,
                billingProvider
        );
    }

    boolean isPlayDistribution() {
        return "play".equals(distribution);
    }

    boolean hasApkParts() {
        return !apkParts.isEmpty();
    }

    boolean isSubscription() {
        return BILLING_SUBSCRIPTION.equals(billingType);
    }

    boolean isOneTimePurchase() {
        return BILLING_ONE_TIME.equals(billingType);
    }

    boolean isFree() {
        return BILLING_FREE.equals(billingType);
    }

    private static String decorateDescription(
            String base,
            String billingType,
            int priceCents,
            String currency,
            String billingPeriod
    ) {
        String pricing;
        if (BILLING_FREE.equals(billingType)) {
            pricing = "GRÁTIS";
        } else {
            String amount;
            if ("EUR".equalsIgnoreCase(currency)) {
                amount = String.format(new Locale("pt", "PT"), "%.2f €", priceCents / 100.0);
            } else {
                amount = String.format(Locale.US, "%.2f %s", priceCents / 100.0, currency);
            }

            if (BILLING_SUBSCRIPTION.equals(billingType)) {
                pricing = "P1M".equalsIgnoreCase(billingPeriod)
                        ? "Premium · " + amount + "/mês"
                        : "Premium · " + amount + " · subscrição";
            } else if (BILLING_ONE_TIME.equals(billingType)) {
                pricing = amount + " · compra única";
            } else {
                pricing = amount;
            }
        }

        if (base == null || base.isBlank()) return pricing;
        return base + "\n" + pricing;
    }

    private static String nullable(JSONObject o, String key) {
        if (!o.has(key) || o.isNull(key)) return null;
        String value = o.optString(key, null);
        return value == null || value.isBlank() ? null : value;
    }

    private static List<ApkPart> parseApkParts(JSONArray parts) throws JSONException {
        if (parts == null || parts.length() == 0) return Collections.emptyList();
        if (parts.length() > 40) throw new JSONException("APK com demasiadas partes");

        ArrayList<ApkPart> result = new ArrayList<>();
        for (int index = 0; index < parts.length(); index++) {
            JSONObject part = parts.optJSONObject(index);
            if (part == null) throw new JSONException("Parte APK inválida");
            String url = nullable(part, "url");
            String sha256 = nullable(part, "sha256");
            if (url == null || !url.startsWith("https://") || sha256 == null || !sha256.matches("[A-Fa-f0-9]{64}")) {
                throw new JSONException("Parte APK sem URL HTTPS ou hash válido");
            }
            result.add(new ApkPart(url, sha256.toLowerCase(Locale.ROOT)));
        }
        return Collections.unmodifiableList(result);
    }

    static final class ApkPart {
        final String url;
        final String sha256;

        ApkPart(String url, String sha256) {
            this.url = url;
            this.sha256 = sha256;
        }
    }
}
