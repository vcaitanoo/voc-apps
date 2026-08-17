package pt.vcaitano.vocmanager;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public final class MainActivity extends Activity {
    private final ExecutorService executor = Executors.newFixedThreadPool(3);
    private final AtomicBoolean installBusy = new AtomicBoolean(false);
    private final Set<String> autoAttempted = new HashSet<>();
    private final BroadcastReceiver installFinishedReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            int status = intent.getIntExtra(
                    InstallResultReceiver.EXTRA_STATUS,
                    android.content.pm.PackageInstaller.STATUS_FAILURE
            );
            String packageName = intent.getStringExtra(InstallResultReceiver.EXTRA_PACKAGE);
            installBusy.set(false);
            activePackage = null;
            if (status == android.content.pm.PackageInstaller.STATUS_SUCCESS) {
                globalStatus.setText("Atualização instalada" + (packageName == null ? "" : ": " + packageName));
            } else {
                globalStatus.setText("A instalação não foi concluída");
            }
            loadCatalog();
        }
    };

    private LinearLayout appList;
    private TextView globalStatus;
    private ProgressBar topProgress;
    private CatalogApp pendingInstall;
    private List<CatalogApp> latestCatalog = java.util.Collections.emptyList();
    private String activePackage;
    private long lastCatalogLoad;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(16, 17, 20));
        if (Build.VERSION.SDK_INT >= 26) {
            getWindow().getDecorView().setSystemUiVisibility(0);
        }
        setContentView(buildUi());
        registerInstallReceiver();
        loadCatalog();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (pendingInstall != null && canInstallPackages() && !installBusy.get()) {
            CatalogApp app = pendingInstall;
            pendingInstall = null;
            startDownloadAndInstall(app);
            return;
        }
        if (lastCatalogLoad > 0) {
            loadCatalog();
        }
    }

    @Override
    protected void onDestroy() {
        try {
            unregisterReceiver(installFinishedReceiver);
        } catch (IllegalArgumentException ignored) {
            // Receiver already unregistered.
        }
        executor.shutdownNow();
        super.onDestroy();
    }

    private void registerInstallReceiver() {
        IntentFilter filter = new IntentFilter(InstallResultReceiver.ACTION_INSTALL_FINISHED);
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(installFinishedReceiver, filter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            //noinspection UnspecifiedRegisterReceiverFlag
            registerReceiver(installFinishedReceiver, filter);
        }
    }

    private View buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(244, 245, 247));

        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.VERTICAL);
        header.setPadding(dp(20), dp(20), dp(20), dp(16));
        header.setBackgroundColor(Color.rgb(16, 17, 20));

        TextView title = new TextView(this);
        title.setText("voc Manager");
        title.setTextColor(Color.WHITE);
        title.setTextSize(28);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        header.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Os teus apps num só lugar");
        subtitle.setTextColor(Color.rgb(190, 194, 201));
        subtitle.setTextSize(14);
        subtitle.setPadding(0, dp(4), 0, dp(12));
        header.addView(subtitle);

        LinearLayout headerActions = new LinearLayout(this);
        headerActions.setGravity(Gravity.CENTER_VERTICAL);

        Button refresh = new Button(this);
        refresh.setText("ATUALIZAR CATÁLOGO");
        refresh.setAllCaps(false);
        refresh.setOnClickListener(v -> loadCatalog());
        headerActions.addView(refresh, new LinearLayout.LayoutParams(0, dp(48), 1));

        topProgress = new ProgressBar(this);
        topProgress.setVisibility(View.GONE);
        LinearLayout.LayoutParams progressParams = new LinearLayout.LayoutParams(dp(36), dp(36));
        progressParams.setMargins(dp(12), 0, 0, 0);
        headerActions.addView(topProgress, progressParams);
        header.addView(headerActions);

        globalStatus = new TextView(this);
        globalStatus.setTextColor(Color.rgb(190, 194, 201));
        globalStatus.setTextSize(13);
        globalStatus.setPadding(0, dp(10), 0, 0);
        header.addView(globalStatus);

        root.addView(header, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        ));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);

        appList = new LinearLayout(this);
        appList.setOrientation(LinearLayout.VERTICAL);
        appList.setPadding(dp(14), dp(14), dp(14), dp(30));
        scroll.addView(appList);
        root.addView(scroll, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1
        ));

        return root;
    }

    private void loadCatalog() {
        topProgress.setVisibility(View.VISIBLE);
        globalStatus.setText("A consultar o catálogo no GitHub…");
        executor.execute(() -> {
            try {
                List<CatalogApp> apps = new CatalogClient().load();
                runOnUiThread(() -> {
                    lastCatalogLoad = System.currentTimeMillis();
                    topProgress.setVisibility(View.GONE);
                    globalStatus.setText(apps.size() + " app(s) no catálogo");
                    latestCatalog = apps;
                    renderApps(apps);
                    maybeStartAutomaticUpdate(apps);
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    topProgress.setVisibility(View.GONE);
                    globalStatus.setText("Falha ao carregar catálogo: " + shortMessage(e));
                });
            }
        });
    }

    private void renderApps(List<CatalogApp> apps) {
        appList.removeAllViews();
        for (CatalogApp app : apps) {
            appList.addView(buildAppCard(app));
        }
    }

    private void maybeStartAutomaticUpdate(List<CatalogApp> apps) {
        if (installBusy.get() || pendingInstall != null) return;

        for (CatalogApp app : apps) {
            if (!"published".equals(app.status)) continue;
            if (Build.VERSION.SDK_INT < app.minSdk) continue;
            if (app.apkUrl == null || app.sha256 == null || app.signatureSha256 == null) continue;

            InstalledInfo installed = getInstalledInfo(app.packageName);
            if (installed == null || installed.versionCode >= app.versionCode) continue;
            if (!app.signatureSha256.equalsIgnoreCase(installed.signatureSha256)) continue;

            String key = app.packageName + ":" + app.versionCode;
            if (!autoAttempted.add(key)) continue;

            globalStatus.setText("Atualização automática encontrada: " + app.name + " " + app.versionName);
            requestInstall(app);
            return;
        }
    }

    private View buildAppCard(CatalogApp app) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(18), dp(16), dp(18), dp(16));

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.WHITE);
        bg.setCornerRadius(dp(16));
        bg.setStroke(dp(1), Color.rgb(225, 227, 231));
        card.setBackground(bg);

        LinearLayout.LayoutParams cardParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
        );
        cardParams.setMargins(0, 0, 0, dp(12));
        card.setLayoutParams(cardParams);

        TextView name = new TextView(this);
        name.setText(app.name);
        name.setTextSize(20);
        name.setTextColor(Color.rgb(20, 21, 24));
        name.setTypeface(Typeface.DEFAULT_BOLD);
        card.addView(name);

        TextView description = new TextView(this);
        description.setText(app.description);
        description.setTextSize(14);
        description.setTextColor(Color.rgb(90, 94, 102));
        description.setPadding(0, dp(5), 0, dp(8));
        card.addView(description);

        InstalledInfo installed = getInstalledInfo(app.packageName);

        TextView version = new TextView(this);
        version.setText(versionLine(app, installed));
        version.setTextSize(13);
        version.setTextColor(Color.rgb(75, 79, 88));
        card.addView(version);

        TextView changelog = new TextView(this);
        changelog.setText(app.changelog);
        changelog.setTextSize(12);
        changelog.setTextColor(Color.rgb(115, 119, 127));
        changelog.setPadding(0, dp(6), 0, dp(12));
        card.addView(changelog);

        TextView cardStatus = new TextView(this);
        cardStatus.setTextSize(13);
        cardStatus.setTypeface(Typeface.DEFAULT_BOLD);
        cardStatus.setPadding(0, 0, 0, dp(8));
        card.addView(cardStatus);

        Button action = new Button(this);
        action.setAllCaps(false);
        card.addView(action, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                dp(50)
        ));

        configureAction(app, installed, action, cardStatus);
        return card;
    }

    private void configureAction(
            CatalogApp app,
            InstalledInfo installed,
            Button button,
            TextView status
    ) {
        if (app.packageName.equals(activePackage)) {
            status.setText(installed == null ? "A INSTALAR…" : "A ATUALIZAR…");
            status.setTextColor(Color.rgb(74, 102, 34));
            button.setText(installed == null ? "A INSTALAR…" : "A ATUALIZAR…");
            button.setEnabled(false);
            return;
        }

        if (Build.VERSION.SDK_INT < app.minSdk) {
            status.setText("INCOMPATÍVEL COM ESTE ANDROID");
            status.setTextColor(Color.rgb(180, 65, 65));
            button.setText("INDISPONÍVEL");
            button.setEnabled(false);
            return;
        }

        if (!"published".equals(app.status)) {
            status.setText("EM PREPARAÇÃO");
            status.setTextColor(Color.rgb(145, 108, 20));
            button.setText("EM BREVE");
            button.setEnabled(false);
            return;
        }

        if (app.apkUrl == null || app.sha256 == null || app.signatureSha256 == null) {
            status.setText("PUBLICAÇÃO INCOMPLETA");
            status.setTextColor(Color.rgb(180, 65, 65));
            button.setText("INDISPONÍVEL");
            button.setEnabled(false);
            return;
        }

        if (installed != null && !app.signatureSha256.equalsIgnoreCase(installed.signatureSha256)) {
            status.setText("ASSINATURA INSTALADA DIFERENTE");
            status.setTextColor(Color.rgb(180, 65, 65));
            button.setText("BLOQUEADO");
            button.setEnabled(false);
            return;
        }

        if (installed == null) {
            status.setText("NÃO INSTALADO");
            status.setTextColor(Color.rgb(74, 102, 34));
            button.setText("INSTALAR");
            button.setOnClickListener(v -> requestInstall(app));
            return;
        }

        if (installed.versionCode < app.versionCode) {
            status.setText("ATUALIZAÇÃO DISPONÍVEL");
            status.setTextColor(Color.rgb(74, 102, 34));
            button.setText("ATUALIZAR PARA " + app.versionName);
            button.setOnClickListener(v -> requestInstall(app));
            return;
        }

        status.setText("ATUALIZADO");
        status.setTextColor(Color.rgb(74, 102, 34));
        button.setText("ABRIR");
        button.setOnClickListener(v -> openPackage(app.packageName));
    }

    private String versionLine(CatalogApp app, InstalledInfo installed) {
        if (installed == null) {
            return app.versionName.isBlank()
                    ? "Ainda não publicado"
                    : "Disponível: " + app.versionName + " (" + app.versionCode + ")";
        }
        String available = app.versionName.isBlank()
                ? "—"
                : app.versionName + " (" + app.versionCode + ")";
        return "Instalada: " + installed.versionName + " (" + installed.versionCode + ")  •  Catálogo: " + available;
    }

    private void requestInstall(CatalogApp app) {
        if (installBusy.get()) {
            Toast.makeText(this, "Já existe uma instalação em andamento", Toast.LENGTH_SHORT).show();
            return;
        }

        if (!canInstallPackages()) {
            pendingInstall = app;
            Intent settings = new Intent(
                    Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + getPackageName())
            );
            Toast.makeText(
                    this,
                    "Autoriza o voc Manager a instalar apps e volta para continuar.",
                    Toast.LENGTH_LONG
            ).show();
            startActivity(settings);
            return;
        }

        startDownloadAndInstall(app);
    }

    private boolean canInstallPackages() {
        return Build.VERSION.SDK_INT < 26 || getPackageManager().canRequestPackageInstalls();
    }

    private void startDownloadAndInstall(CatalogApp app) {
        if (!installBusy.compareAndSet(false, true)) return;
        activePackage = app.packageName;
        topProgress.setVisibility(View.VISIBLE);
        globalStatus.setText("A preparar " + app.name + "…");
        renderApps(latestCatalog);

        executor.execute(() -> {
            try {
                File apk = downloadAndVerify(app);
                runOnUiThread(() -> globalStatus.setText("A instalar " + app.name + "…"));
                ApkInstaller.install(this, apk, app.packageName);
            } catch (Exception e) {
                installBusy.set(false);
                activePackage = null;
                runOnUiThread(() -> {
                    topProgress.setVisibility(View.GONE);
                    renderApps(latestCatalog);
                    Toast.makeText(
                            this,
                            "Não foi possível instalar: " + shortMessage(e),
                            Toast.LENGTH_LONG
                    ).show();
                });
                return;
            }
            runOnUiThread(() -> topProgress.setVisibility(View.GONE));
        });
    }

    private File downloadAndVerify(CatalogApp app) throws Exception {
        File folder = new File(getCacheDir(), "apks");
        if (!folder.exists() && !folder.mkdirs()) {
            throw new IllegalStateException("Não foi possível criar cache de APKs");
        }
        File target = new File(folder, app.id + "-" + app.versionCode + ".apk");

        HttpURLConnection connection = (HttpURLConnection) new URL(app.apkUrl).openConnection();
        connection.setConnectTimeout(10_000);
        connection.setReadTimeout(20_000);
        connection.setInstanceFollowRedirects(true);
        connection.setRequestProperty("User-Agent", "voc-Manager/1.0");
        int response = connection.getResponseCode();
        if (response < 200 || response >= 300) {
            connection.disconnect();
            throw new IllegalStateException("Download HTTP " + response);
        }

        long total = connection.getContentLengthLong();
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        long downloaded = 0;
        int lastPercent = -1;

        try (BufferedInputStream input = new BufferedInputStream(connection.getInputStream());
             FileOutputStream output = new FileOutputStream(target)) {
            byte[] buffer = new byte[64 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) {
                output.write(buffer, 0, read);
                digest.update(buffer, 0, read);
                downloaded += read;
                if (total > 0) {
                    int percent = (int) ((downloaded * 100L) / total);
                    if (percent >= lastPercent + 5 || percent == 100) {
                        lastPercent = percent;
                        int show = percent;
                        runOnUiThread(() -> globalStatus.setText(
                                "A baixar " + app.name + "… " + show + "%"
                        ));
                    }
                }
            }
        } finally {
            connection.disconnect();
        }

        String actualSha = hex(digest.digest());
        if (!actualSha.equalsIgnoreCase(app.sha256)) {
            //noinspection ResultOfMethodCallIgnored
            target.delete();
            throw new SecurityException("SHA-256 do APK não corresponde ao catálogo");
        }

        verifyArchive(app, target);
        return target;
    }

    private void verifyArchive(CatalogApp app, File apk) throws Exception {
        PackageInfo info;
        if (Build.VERSION.SDK_INT >= 33) {
            info = getPackageManager().getPackageArchiveInfo(
                    apk.getAbsolutePath(),
                    PackageManager.PackageInfoFlags.of(PackageManager.GET_SIGNING_CERTIFICATES)
            );
        } else {
            //noinspection deprecation
            info = getPackageManager().getPackageArchiveInfo(
                    apk.getAbsolutePath(),
                    PackageManager.GET_SIGNING_CERTIFICATES
            );
        }

        if (info == null) throw new SecurityException("APK inválido");
        if (!app.packageName.equals(info.packageName)) {
            throw new SecurityException("Package do APK não corresponde ao catálogo");
        }

        long archiveVersion = getLongVersionCode(info);
        if (archiveVersion != app.versionCode) {
            throw new SecurityException("VersionCode do APK não corresponde ao catálogo");
        }

        String signer = signingSha256(info);
        if (signer == null || !signer.equalsIgnoreCase(app.signatureSha256)) {
            throw new SecurityException("Assinatura do APK não corresponde ao catálogo");
        }
    }

    private InstalledInfo getInstalledInfo(String packageName) {
        try {
            PackageInfo info;
            if (Build.VERSION.SDK_INT >= 33) {
                info = getPackageManager().getPackageInfo(
                        packageName,
                        PackageManager.PackageInfoFlags.of(PackageManager.GET_SIGNING_CERTIFICATES)
                );
            } else {
                //noinspection deprecation
                info = getPackageManager().getPackageInfo(
                        packageName,
                        PackageManager.GET_SIGNING_CERTIFICATES
                );
            }
            return new InstalledInfo(
                    getLongVersionCode(info),
                    info.versionName == null ? "?" : info.versionName,
                    signingSha256(info)
            );
        } catch (PackageManager.NameNotFoundException ignored) {
            return null;
        } catch (Exception e) {
            return null;
        }
    }

    private static long getLongVersionCode(PackageInfo info) {
        if (Build.VERSION.SDK_INT >= 28) return info.getLongVersionCode();
        //noinspection deprecation
        return info.versionCode;
    }

    private static String signingSha256(PackageInfo info) throws Exception {
        if (info.signingInfo == null) return null;
        Signature[] signatures = info.signingInfo.hasMultipleSigners()
                ? info.signingInfo.getApkContentsSigners()
                : info.signingInfo.getSigningCertificateHistory();
        if (signatures == null || signatures.length == 0) return null;
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        return hex(digest.digest(signatures[0].toByteArray()));
    }

    private void openPackage(String packageName) {
        if (getPackageName().equals(packageName)) {
            Toast.makeText(this, "O voc Manager já está aberto", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent launch = getPackageManager().getLaunchIntentForPackage(packageName);
        if (launch == null) {
            Toast.makeText(this, "Não encontrei uma tela para abrir este app", Toast.LENGTH_LONG).show();
            return;
        }
        startActivity(launch);
    }

    private static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte b : bytes) out.append(String.format(Locale.US, "%02x", b));
        return out.toString();
    }

    private static String shortMessage(Throwable error) {
        String msg = error.getMessage();
        if (msg == null || msg.isBlank()) return error.getClass().getSimpleName();
        return msg.length() > 150 ? msg.substring(0, 150) : msg;
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private static final class InstalledInfo {
        final long versionCode;
        final String versionName;
        final String signatureSha256;

        InstalledInfo(long versionCode, String versionName, String signatureSha256) {
            this.versionCode = versionCode;
            this.versionName = versionName;
            this.signatureSha256 = signatureSha256;
        }
    }
}
