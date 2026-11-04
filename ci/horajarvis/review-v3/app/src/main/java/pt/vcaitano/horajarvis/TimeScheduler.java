package pt.vcaitano.horajarvis;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;
import java.util.List;

/** Sempre programa APENAS o próximo aviso; o BroadcastReceiver agenda o seguinte. */
public final class TimeScheduler {
    public static final String ACTION_ANNOUNCE = "pt.vcaitano.horajarvis.ANNOUNCE";
    private static final int REQUEST_CODE = 5031;

    private TimeScheduler() { }

    private static PendingIntent alarmIntent(Context context) {
        Intent intent = new Intent(context, AlarmReceiver.class).setAction(ACTION_ANNOUNCE);
        return PendingIntent.getBroadcast(context, REQUEST_CODE, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    public static boolean preciseAlarmsAllowed(Context context) {
        AlarmManager manager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        return manager != null && (Build.VERSION.SDK_INT < 31 || manager.canScheduleExactAlarms());
    }

    public static void replan(Context context) {
        AlarmManager manager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (manager == null) return;
        PendingIntent pending = alarmIntent(context);
        manager.cancel(pending);
        AppSettings config = AppSettings.load(context);
        if (!config.enabled) return;
        long next = findNext(config, System.currentTimeMillis());
        if (next <= 0L) return;

        // Se o Android não autorizar alarmes exatos, continua no modo aproximado.
        try {
            if (preciseAlarmsAllowed(context)) {
                manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, next, pending);
            } else {
                manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, next, pending);
            }
        } catch (SecurityException denied) {
            manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, next, pending);
        }
    }

    /** Encontra a próxima ocorrência, incluindo janelas que passam da meia-noite. */
    public static long findNext(AppSettings config, long nowMillis) {
        if (!config.enabled || config.daysMask == 0) return -1;

        if (config.customMode) {
            List<Integer> times;
            try { times = CustomTimes.parse(config.customTimes); }
            catch (IllegalArgumentException invalid) { return -1; }
            if (times.isEmpty()) return -1;
            Calendar dayStart = Calendar.getInstance();
            dayStart.setTimeInMillis(nowMillis);
            dayStart.set(Calendar.HOUR_OF_DAY, 0);
            dayStart.set(Calendar.MINUTE, 0);
            dayStart.set(Calendar.SECOND, 0);
            dayStart.set(Calendar.MILLISECOND, 0);
            for (int dayOffset = 0; dayOffset < 8; dayOffset++) {
                int weekdayBit = (dayStart.get(Calendar.DAY_OF_WEEK) + 5) % 7;
                if ((config.daysMask & (1 << weekdayBit)) != 0) {
                    for (int minute : times) {
                        Calendar candidate = (Calendar) dayStart.clone();
                        candidate.add(Calendar.MINUTE, minute);
                        long target = candidate.getTimeInMillis();
                        if (target > nowMillis) return target;
                    }
                }
                dayStart.add(Calendar.DAY_OF_MONTH, 1);
            }
            return -1;
        }

        Calendar day = Calendar.getInstance();
        day.setTimeInMillis(nowMillis);
        day.set(Calendar.HOUR_OF_DAY, 0);
        day.set(Calendar.MINUTE, 0);
        day.set(Calendar.SECOND, 0);
        day.set(Calendar.MILLISECOND, 0);
        day.add(Calendar.DAY_OF_MONTH, -1); // Inclui intervalo noturno iniciado ontem.

        long closest = Long.MAX_VALUE;
        for (int offset = -1; offset <= 7; offset++) {
            int weekdayBit = (day.get(Calendar.DAY_OF_WEEK) + 5) % 7;
            if ((config.daysMask & (1 << weekdayBit)) != 0) {
                Calendar start = (Calendar) day.clone();
                start.add(Calendar.MINUTE, config.startMinute);
                Calendar end = (Calendar) day.clone();
                end.add(Calendar.MINUTE, config.endMinute);
                if (config.endMinute <= config.startMinute) {
                    end.add(Calendar.DAY_OF_MONTH, 1);
                }

                // A cadência é ancorada na hora inicial: 08:00, 09:00, 10:00, etc.
                Calendar candidate = (Calendar) start.clone();
                if (candidate.getTimeInMillis() <= nowMillis) {
                    long elapsed = nowMillis - candidate.getTimeInMillis();
                    int pastIntervals = (int) (elapsed / (config.intervalMinute * 60_000L)) + 1;
                    candidate.add(Calendar.MINUTE, pastIntervals * config.intervalMinute);
                }
                long target = candidate.getTimeInMillis();
                if (target > nowMillis && target <= end.getTimeInMillis() && target < closest) {
                    closest = target;
                }
            }
            day.add(Calendar.DAY_OF_MONTH, 1);
        }
        return closest == Long.MAX_VALUE ? -1 : closest;
    }

    public static String prettyNext(Context context) {
        AppSettings config = AppSettings.load(context);
        if (!config.enabled) return "Avisos desativados";
        long next = findNext(config, System.currentTimeMillis());
        if (next <= 0) return "Selecione pelo menos um dia";
        SimpleDateFormat format = new SimpleDateFormat("EEE, dd/MM 'às' HH:mm", new Locale("pt", "BR"));
        return "Próximo aviso: " + format.format(new Date(next));
    }
}
