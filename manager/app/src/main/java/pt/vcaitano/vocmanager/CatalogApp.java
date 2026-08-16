package pt.vcaitano.vocmanager;

import org.json.JSONException;
import org.json.JSONObject;

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
    final String apkUrl;
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
            String apkUrl,
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
        this.apkUrl = apkUrl;
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

        return new CatalogApp(
                o.getString("id"),
                o.getString("name"),
                o.getString("packageName"),
                o.optString("category", "app"),
                o.optString("description", ""),
                o.optString("status", "disabled"),
                o.optLong("versionCode", 0),
                o.optString("versionName", ""),
                o.optInt("minSdk", 28),
                nullable(o, "apkUrl"),
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

    boolean isSubscription() {
        return BILLING_SUBSCRIPTION.equals(billingType);
    }

    boolean isOneTimePurchase() {
        return BILLING_ONE_TIME.equals(billingType);
    }

    boolean isFree() {
        return BILLING_FREE.equals(billingType);
    }

    private static String nullable(JSONObject o, String key) {
        if (!o.has(key) || o.isNull(key)) return null;
        String value = o.optString(key, null);
        return value == null || value.isBlank() ? null : value;
    }
}
