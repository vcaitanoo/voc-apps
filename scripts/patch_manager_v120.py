from pathlib import Path

PATH = Path('manager/app/src/main/java/pt/vcaitano/vocmanager/MainActivity.java')
text = PATH.read_text(encoding='utf-8')


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one match, found {count}: {old[:80]!r}')
    text = text.replace(old, new, 1)


replace_once(
    'import android.app.Activity;\nimport android.content.Intent;\n',
    'import android.app.Activity;\nimport android.content.BroadcastReceiver;\nimport android.content.Context;\nimport android.content.Intent;\nimport android.content.IntentFilter;\n'
)

replace_once(
    'import java.util.List;\nimport java.util.Locale;\n',
    'import java.util.HashSet;\nimport java.util.List;\nimport java.util.Locale;\nimport java.util.Set;\n'
)

replace_once(
    '''    private final ExecutorService executor = Executors.newFixedThreadPool(3);
    private final AtomicBoolean installBusy = new AtomicBoolean(false);

    private LinearLayout appList;
''',
    '''    private final ExecutorService executor = Executors.newFixedThreadPool(3);
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
'''
)

replace_once(
    '''    private CatalogApp pendingInstall;
    private long lastCatalogLoad;
''',
    '''    private CatalogApp pendingInstall;
    private List<CatalogApp> latestCatalog = java.util.Collections.emptyList();
    private String activePackage;
    private long lastCatalogLoad;
'''
)

replace_once(
    '''        setContentView(buildUi());
        loadCatalog();
''',
    '''        setContentView(buildUi());
        registerInstallReceiver();
        loadCatalog();
'''
)

replace_once(
    '''        if (lastCatalogLoad > 0 && System.currentTimeMillis() - lastCatalogLoad > 2_000) {
            loadCatalog();
        }
''',
    '''        if (lastCatalogLoad > 0) {
            loadCatalog();
        }
'''
)

replace_once(
    '''    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }
''',
    '''    @Override
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
'''
)

replace_once(
    '''                    globalStatus.setText(apps.size() + " app(s) no catálogo");
                    renderApps(apps);
''',
    '''                    globalStatus.setText(apps.size() + " app(s) no catálogo");
                    latestCatalog = apps;
                    renderApps(apps);
                    maybeStartAutomaticUpdate(apps);
'''
)

replace_once(
    '''    private void renderApps(List<CatalogApp> apps) {
        appList.removeAllViews();
        for (CatalogApp app : apps) {
            appList.addView(buildAppCard(app));
        }
    }

    private View buildAppCard(CatalogApp app) {
''',
    '''    private void renderApps(List<CatalogApp> apps) {
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
'''
)

replace_once(
    '''    private void configureAction(
            CatalogApp app,
            InstalledInfo installed,
            Button button,
            TextView status
    ) {
        if (Build.VERSION.SDK_INT < app.minSdk) {
''',
    '''    private void configureAction(
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
'''
)

replace_once(
    '''    private void startDownloadAndInstall(CatalogApp app) {
        if (!installBusy.compareAndSet(false, true)) return;
        topProgress.setVisibility(View.VISIBLE);
        globalStatus.setText("A preparar " + app.name + "…");

        executor.execute(() -> {
            try {
                File apk = downloadAndVerify(app);
                runOnUiThread(() -> globalStatus.setText("A abrir instalador do Android…"));
                ApkInstaller.install(this, apk, app.packageName);
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(
                        this,
                        "Não foi possível instalar: " + shortMessage(e),
                        Toast.LENGTH_LONG
                ).show());
            } finally {
                installBusy.set(false);
                runOnUiThread(() -> topProgress.setVisibility(View.GONE));
            }
        });
    }
''',
    '''    private void startDownloadAndInstall(CatalogApp app) {
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
'''
)

PATH.write_text(text, encoding='utf-8')
print('Manager v1.2.0 auto-update patch applied')
