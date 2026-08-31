package pt.vcaitano.voclab;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageInstaller;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final String CATALOG_URL = "https://raw.githubusercontent.com/vcaitanoo/voc-apps/main/lab/catalog.json";
    private static final String INSTALL_STATUS_ACTION = "pt.vcaitano.voclab.INSTALL_STATUS";

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private LinearLayout appsContainer;
    private TextView statusText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();
        handleInstallerResult(getIntent());
        refreshCatalog();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleInstallerResult(intent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (appsContainer != null) {
            refreshCatalog();
        }
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }

    private void buildUi() {
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18), dp(22), dp(18), dp(28));
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("VOC Lab");
        title.setTextSize(30);
        title.setGravity(Gravity.CENTER_HORIZONTAL);
        root.addView(title, matchWrap());

        TextView subtitle = new TextView(this);
        subtitle.setText("Canal privado para instalar e testar APKs.\nESTÁVEL = aprovado • CANDIDATO = em teste");
        subtitle.setTextSize(15);
        subtitle.setGravity(Gravity.CENTER_HORIZONTAL);
        subtitle.setPadding(0, dp(6), 0, dp(12));
        root.addView(subtitle, matchWrap());

        Button refresh = new Button(this);
        refresh.setText("ATUALIZAR LISTA");
        refresh.setOnClickListener(v -> refreshCatalog());
        root.addView(refresh, matchWrap());

        statusText = new TextView(this);
        statusText.setText("A carregar catálogo...");
        statusText.setPadding(0, dp(10), 0, dp(10));
        root.addView(statusText, matchWrap());

        appsContainer = new LinearLayout(this);
        appsContainer.setOrientation(LinearLayout.VERTICAL);
        root.addView(appsContainer, matchWrap());

        setContentView(scroll);
    }

    private void refreshCatalog() {
        if (statusText == null) return;
        statusText.setText("A carregar catálogo...");
        executor.execute(() -> {
            try {
                List<LabApp> apps = loadCatalog();
                runOnUiThread(() -> renderApps(apps));
            } catch (Exception e) {
                runOnUiThread(() -> statusText.setText("Falha ao carregar catálogo: " + e.getMessage()));
            }
        });
    }

    private List<LabApp> loadCatalog() throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(CATALOG_URL + "?t=" + System.currentTimeMillis()).openConnection();
        connection.setConnectTimeout(10_000);
        connection.setReadTimeout(15_000);
        connection.setUseCaches(false);
        connection.setRequestProperty("Cache-Control", "no-cache");
        connection.setRequestProperty("User-Agent", "VOC-Lab/1.0");
        int code = connection.getResponseCode();
        if (code < 200 || code >= 300) throw new IllegalStateException("HTTP " + code);
        String text;
        try (InputStream input = new BufferedInputStream(connection.getInputStream())) {
            java.io.ByteArrayOutputStream output = new java.io.ByteArrayOutputStream();
            byte[] buffer = new byte[16 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) output.write(buffer, 0, read);
            text = new String(output.toByteArray(), StandardCharsets.UTF_8);
        } finally {
            connection.disconnect();
        }
        JSONObject root = new JSONObject(text);
        if (root.optInt("schemaVersion", -1) != 1) throw new IllegalStateException("schemaVersion inválida");
        JSONArray array = root.getJSONArray("apps");
        List<LabApp> result = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            LabApp app = LabApp.fromJson(array.getJSONObject(i));
            if (app.enabled) result.add(app);
        }
        return result;
    }

    private void renderApps(List<LabApp> apps) {
        appsContainer.removeAllViews();
        statusText.setText("Catálogo atualizado • " + apps.size() + " apps");
        for (LabApp app : apps) appsContainer.addView(buildCard(app));
    }

    private View buildCard(LabApp app) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(14), dp(14), dp(14), dp(14));
        LinearLayout.LayoutParams cardParams = matchWrap();
        cardParams.setMargins(0, dp(7), 0, dp(7));
        card.setLayoutParams(cardParams);
        card.setBackgroundColor(0xffeeeeee);

        TextView name = new TextView(this);
        name.setText(app.name);
        name.setTextSize(21);
        card.addView(name, matchWrap());

        long installedCode = installedVersionCode(app.packageName);
        String installedLabel = installedCode < 0 ? "não instalado" : installedVersionName(app.packageName) + " (" + installedCode + ")";
        TextView details = new TextView(this);
        StringBuilder text = new StringBuilder();
        text.append("Instalado: ").append(installedLabel).append("\n");
        text.append("Estável: ").append(app.stable.versionName).append(" (").append(app.stable.versionCode).append(")");
        if (app.candidate != null) {
            text.append("\nCANDIDATO: ").append(app.candidate.versionName).append(" (").append(app.candidate.versionCode).append(")");
            if (!app.candidate.notes.isEmpty()) text.append("\nAlteração: ").append(app.candidate.notes);
        } else text.append("\nCandidato: nenhum");
        details.setText(text.toString());
        details.setTextSize(14);
        details.setPadding(0, dp(7), 0, dp(7));
        card.addView(details, matchWrap());

        Release target = app.candidate != null ? app.candidate : app.stable;
        Button action = new Button(this);
        if (target.apkUrl == null || target.apkUrl.isEmpty()) {
            action.setText("APK AINDA NÃO PUBLICADO");
            action.setEnabled(false);
        } else if (installedCode >= target.versionCode) {
            action.setText("ABRIR");
            action.setOnClickListener(v -> openApp(app.packageName));
        } else {
            action.setText(app.candidate != null ? (installedCode < 0 ? "INSTALAR CANDIDATO" : "ATUALIZAR PARA CANDIDATO") : (installedCode < 0 ? "INSTALAR" : "ATUALIZAR"));
            action.setOnClickListener(v -> startInstall(app, target, action));
        }
        card.addView(action, matchWrap());
        return card;
    }

    private void startInstall(LabApp app, Release release, Button button) {
        if (!getPackageManager().canRequestPackageInstalls()) {
            Toast.makeText(this, "Autorize o VOC Lab a instalar apps e tente novamente.", Toast.LENGTH_LONG).show();
            startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + getPackageName())));
            return;
        }
        button.setEnabled(false);
        button.setText("A DESCARREGAR...");
        executor.execute(() -> {
            try {
                File apk = downloadAndValidate(app, release);
                installWithPackageInstaller(app.packageName, apk);
                runOnUiThread(() -> { button.setEnabled(true); button.setText("CONFIRMAR INSTALAÇÃO"); });
            } catch (Exception e) {
                runOnUiThread(() -> { button.setEnabled(true); button.setText("TENTAR NOVAMENTE"); Toast.makeText(this, "Falha: " + e.getMessage(), Toast.LENGTH_LONG).show(); });
            }
        });
    }

    private File downloadAndValidate(LabApp app, Release release) throws Exception {
        if (release.apkUrl == null || release.apkUrl.isEmpty()) throw new IllegalStateException("APK sem URL");
        File dir = new File(getCacheDir(), "apks");
        if (!dir.exists() && !dir.mkdirs()) throw new IllegalStateException("Não foi possível criar cache");
        File apk = new File(dir, app.id + "-" + release.versionCode + ".apk");
        HttpURLConnection connection = (HttpURLConnection) new URL(release.apkUrl).openConnection();
        connection.setConnectTimeout(15_000);
        connection.setReadTimeout(60_000);
        connection.setInstanceFollowRedirects(true);
        connection.setRequestProperty("User-Agent", "VOC-Lab/1.0");
        int code = connection.getResponseCode();
        if (code < 200 || code >= 300) throw new IllegalStateException("Download HTTP " + code);
        try (InputStream input = new BufferedInputStream(connection.getInputStream()); OutputStream output = new FileOutputStream(apk)) {
            byte[] buffer = new byte[64 * 1024]; int read; while ((read = input.read(buffer)) != -1) output.write(buffer, 0, read);
        } finally { connection.disconnect(); }
        String actualSha = sha256(apk);
        if (!release.sha256.isEmpty() && !actualSha.equalsIgnoreCase(release.sha256)) { apk.delete(); throw new IllegalStateException("SHA-256 do APK não confere"); }
        PackageInfo archive = getPackageManager().getPackageArchiveInfo(apk.getAbsolutePath(), PackageManager.GET_SIGNING_CERTIFICATES);
        if (archive == null) throw new IllegalStateException("APK inválido");
        if (!app.packageName.equals(archive.packageName)) throw new IllegalStateException("Package diferente: " + archive.packageName);
        if (archive.getLongVersionCode() != release.versionCode) throw new IllegalStateException("versionCode diferente: " + archive.getLongVersionCode());
        if (!release.signatureSha256.isEmpty() && !signerSha256(archive).equalsIgnoreCase(release.signatureSha256)) throw new IllegalStateException("Assinatura do APK não confere");
        return apk;
    }

    private void installWithPackageInstaller(String packageName, File apk) throws Exception {
        PackageInstaller installer = getPackageManager().getPackageInstaller();
        PackageInstaller.SessionParams params = new PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL);
        params.setAppPackageName(packageName);
        int sessionId = installer.createSession(params);
        PackageInstaller.Session session = installer.openSession(sessionId);
        try (InputStream input = new FileInputStream(apk); OutputStream output = session.openWrite("base.apk", 0, apk.length())) {
            byte[] buffer = new byte[64 * 1024]; int read; while ((read = input.read(buffer)) != -1) output.write(buffer, 0, read); session.fsync(output);
        }
        Intent statusIntent = new Intent(this, MainActivity.class); statusIntent.setAction(INSTALL_STATUS_ACTION);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, sessionId, statusIntent, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_MUTABLE);
        session.commit(pendingIntent.getIntentSender()); session.close();
    }

    private void handleInstallerResult(Intent intent) {
        if (intent == null || !INSTALL_STATUS_ACTION.equals(intent.getAction())) return;
        int status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE);
        if (status == PackageInstaller.STATUS_PENDING_USER_ACTION) {
            Intent confirm = intent.getParcelableExtra(Intent.EXTRA_INTENT);
            if (confirm != null) startActivity(confirm);
            return;
        }
        if (status == PackageInstaller.STATUS_SUCCESS) { Toast.makeText(this, "Instalação concluída.", Toast.LENGTH_LONG).show(); refreshCatalog(); }
        else { String message = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE); Toast.makeText(this, "Instalação falhou: " + (message == null ? status : message), Toast.LENGTH_LONG).show(); }
    }

    private void openApp(String packageName) {
        Intent launch = getPackageManager().getLaunchIntentForPackage(packageName);
        if (launch == null) Toast.makeText(this, "Não foi possível abrir o app.", Toast.LENGTH_LONG).show(); else startActivity(launch);
    }
    private long installedVersionCode(String packageName) { try { return getPackageManager().getPackageInfo(packageName, 0).getLongVersionCode(); } catch (Exception e) { return -1; } }
    private String installedVersionName(String packageName) { try { String name = getPackageManager().getPackageInfo(packageName, 0).versionName; return name == null ? "?" : name; } catch (Exception e) { return "?"; } }
    private static String sha256(File file) throws Exception { MessageDigest digest = MessageDigest.getInstance("SHA-256"); try (InputStream input = new FileInputStream(file)) { byte[] buffer = new byte[64 * 1024]; int read; while ((read = input.read(buffer)) != -1) digest.update(buffer, 0, read); } return hex(digest.digest()); }
    private static String signerSha256(PackageInfo archive) throws Exception { if (archive.signingInfo == null) throw new IllegalStateException("APK sem assinatura"); android.content.pm.Signature[] signatures = archive.signingInfo.getApkContentsSigners(); if (signatures == null || signatures.length == 0) throw new IllegalStateException("APK sem certificado"); CertificateFactory factory = CertificateFactory.getInstance("X.509"); X509Certificate certificate = (X509Certificate) factory.generateCertificate(new java.io.ByteArrayInputStream(signatures[0].toByteArray())); return hex(MessageDigest.getInstance("SHA-256").digest(certificate.getEncoded())); }
    private static String hex(byte[] bytes) { StringBuilder builder = new StringBuilder(bytes.length * 2); for (byte b : bytes) builder.append(String.format(Locale.US, "%02x", b)); return builder.toString(); }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private LinearLayout.LayoutParams matchWrap() { return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT); }

    private static final class LabApp {
        final String id, name, packageName; final boolean enabled; final Release stable, candidate;
        private LabApp(String id, String name, String packageName, boolean enabled, Release stable, Release candidate) { this.id=id; this.name=name; this.packageName=packageName; this.enabled=enabled; this.stable=stable; this.candidate=candidate; }
        static LabApp fromJson(JSONObject o) throws Exception { JSONObject s=o.getJSONObject("stable"), c=o.optJSONObject("candidate"); return new LabApp(o.getString("id"),o.getString("name"),o.getString("packageName"),o.optBoolean("enabled",true),Release.fromJson(s),c==null?null:Release.fromJson(c)); }
    }
    private static final class Release {
        final long versionCode; final String versionName, apkUrl, sha256, signatureSha256, notes;
        private Release(long versionCode,String versionName,String apkUrl,String sha256,String signatureSha256,String notes){this.versionCode=versionCode;this.versionName=versionName;this.apkUrl=apkUrl;this.sha256=sha256;this.signatureSha256=signatureSha256;this.notes=notes;}
        static Release fromJson(JSONObject o) throws Exception { return new Release(o.getLong("versionCode"),o.getString("versionName"),o.optString("apkUrl",""),o.optString("sha256",""),o.optString("signatureSha256",""),o.optString("notes","")); }
    }
}
