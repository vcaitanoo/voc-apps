package pt.vcaitano.horajarvis;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;

/** Disparado pelo AlarmManager, inclusive quando a tela está bloqueada. */
public final class AlarmReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || !TimeScheduler.ACTION_ANNOUNCE.equals(intent.getAction())) return;
        if (!AppSettings.load(context).enabled) return;

        // Agendar antes de falar impede perder o próximo horário caso o TTS falhe.
        TimeScheduler.replan(context);
        String phrase = PhraseGenerator.accordingToSettings(context, java.util.Calendar.getInstance());
        VoiceService.postTimeNotification(context, phrase); // Não depende do início do TTS.
        Intent serviceIntent = new Intent(context, VoiceService.class)
                .setAction(VoiceService.ACTION_ANNOUNCE)
                .putExtra(VoiceService.EXTRA_PHRASE, phrase);
        try {
            if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(serviceIntent);
            else context.startService(serviceIntent);
        } catch (RuntimeException error) {
            Log.e("HoraJarvis", "Android impediu o início da voz", error);
            // Mesmo neste caso, o próximo aviso permanece agendado.
        }
    }
}
