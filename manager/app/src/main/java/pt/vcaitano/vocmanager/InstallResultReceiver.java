package pt.vcaitano.vocmanager;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInstaller;
import android.os.Build;
import android.widget.Toast;

public final class InstallResultReceiver extends BroadcastReceiver {
    static final String ACTION_INSTALL_STATUS = "pt.vcaitano.vocmanager.INSTALL_STATUS";
    static final String EXTRA_PACKAGE = "package_name";

    @Override
    public void onReceive(Context context, Intent intent) {
        int status = intent.getIntExtra(
                PackageInstaller.EXTRA_STATUS,
                PackageInstaller.STATUS_FAILURE
        );
        String message = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE);

        if (status == PackageInstaller.STATUS_PENDING_USER_ACTION) {
            Intent confirmIntent;
            if (Build.VERSION.SDK_INT >= 33) {
                confirmIntent = intent.getParcelableExtra(Intent.EXTRA_INTENT, Intent.class);
            } else {
                //noinspection deprecation
                confirmIntent = intent.getParcelableExtra(Intent.EXTRA_INTENT);
            }
            if (confirmIntent != null) {
                confirmIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                context.startActivity(confirmIntent);
            }
            return;
        }

        if (status == PackageInstaller.STATUS_SUCCESS) {
            Toast.makeText(context, "Instalação concluída", Toast.LENGTH_LONG).show();
            return;
        }

        String detail = message == null || message.isBlank() ? "erro " + status : message;
        Toast.makeText(context, "Falha na instalação: " + detail, Toast.LENGTH_LONG).show();
    }
}
