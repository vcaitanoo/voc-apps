package pt.vcaitano.vocmanager;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.IntentSender;
import android.content.pm.PackageInstaller;
import android.os.Build;

import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;

final class ApkInstaller {
    private ApkInstaller() {}

    static void install(Context context, File apk, String packageName) throws Exception {
        PackageInstaller installer = context.getPackageManager().getPackageInstaller();
        PackageInstaller.SessionParams params =
                new PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL);
        params.setAppPackageName(packageName);
        if (Build.VERSION.SDK_INT >= 33) {
            params.setPackageSource(PackageInstaller.PACKAGE_SOURCE_STORE);
        }

        int sessionId = installer.createSession(params);
        try (PackageInstaller.Session session = installer.openSession(sessionId);
             FileInputStream input = new FileInputStream(apk);
             OutputStream output = session.openWrite("base.apk", 0, apk.length())) {

            byte[] buffer = new byte[64 * 1024];
            int read;
            while ((read = input.read(buffer)) != -1) {
                output.write(buffer, 0, read);
            }
            session.fsync(output);

            Intent resultIntent = new Intent(context, InstallResultReceiver.class)
                    .setAction(InstallResultReceiver.ACTION_INSTALL_STATUS)
                    .putExtra(InstallResultReceiver.EXTRA_PACKAGE, packageName);

            PendingIntent pendingIntent = PendingIntent.getBroadcast(
                    context,
                    sessionId,
                    resultIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_MUTABLE
            );
            IntentSender statusReceiver = pendingIntent.getIntentSender();
            session.commit(statusReceiver);
        } catch (Exception e) {
            installer.abandonSession(sessionId);
            throw e;
        }
    }
}
