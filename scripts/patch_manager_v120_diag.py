from pathlib import Path

p = Path('manager/app/src/main/java/pt/vcaitano/vocmanager/MainActivity.java')
text = p.read_text(encoding='utf-8')


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'Expected one match, got {count}: {old[:100]!r}')
    text = text.replace(old, new, 1)


replace_once(
'''    private void maybeStartAutomaticUpdate(List<CatalogApp> apps) {
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
''',
'''    private void maybeStartAutomaticUpdate(List<CatalogApp> apps) {
        if (installBusy.get() || pendingInstall != null) {
            android.util.Log.i("vocManager", "Auto-update skipped: installer busy or permission flow pending");
            return;
        }

        for (CatalogApp app : apps) {
            if (!"published".equals(app.status)) continue;
            if (Build.VERSION.SDK_INT < app.minSdk) continue;
            if (app.apkUrl == null || app.sha256 == null || app.signatureSha256 == null) continue;

            InstalledInfo installed = getInstalledInfo(app.packageName);
            if (installed == null) continue;
            android.util.Log.i(
                    "vocManager",
                    "Auto-update check " + app.packageName
                            + " installed=" + installed.versionCode
                            + " catalog=" + app.versionCode
                            + " signerMatch=" + app.signatureSha256.equalsIgnoreCase(installed.signatureSha256)
            );
            if (installed.versionCode >= app.versionCode) continue;
            if (!app.signatureSha256.equalsIgnoreCase(installed.signatureSha256)) continue;

            String key = app.packageName + ":" + app.versionCode;
            if (!autoAttempted.add(key)) continue;

            android.util.Log.i("vocManager", "Auto-update starting for " + key);
            globalStatus.setText("Atualização automática encontrada: " + app.name + " " + app.versionName);
            requestInstall(app);
            return;
        }
    }
''')

replace_once(
'''        if (Build.VERSION.SDK_INT < app.minSdk) {
''',
'''        if (getPackageName().equals(app.packageName)
                && installed != null
                && !"published".equals(app.status)) {
            status.setText("ATUALIZADO");
            status.setTextColor(Color.rgb(74, 102, 34));
            button.setText("ABRIR");
            button.setEnabled(true);
            button.setOnClickListener(v -> openPackage(app.packageName));
            return;
        }

        if (Build.VERSION.SDK_INT < app.minSdk) {
''')

replace_once(
'''        if (!canInstallPackages()) {
            pendingInstall = app;
''',
'''        if (!canInstallPackages()) {
            android.util.Log.w("vocManager", "Install permission missing for " + app.packageName);
            pendingInstall = app;
''')

replace_once(
'''        startDownloadAndInstall(app);
    }
''',
'''        android.util.Log.i("vocManager", "Install permission available for " + app.packageName);
        startDownloadAndInstall(app);
    }
''')

replace_once(
'''        activePackage = app.packageName;
        topProgress.setVisibility(View.VISIBLE);
''',
'''        activePackage = app.packageName;
        android.util.Log.i("vocManager", "Downloading update for " + app.packageName + " versionCode=" + app.versionCode);
        topProgress.setVisibility(View.VISIBLE);
''')

p.write_text(text, encoding='utf-8')
print('diagnostic + self-card patch applied')
