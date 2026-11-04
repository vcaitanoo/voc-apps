package pt.vcaitano.horajarvis;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioAttributes;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Log;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;
import java.util.Set;

/** Serviço curto: acorda CPU, apresenta notificação e fala enquanto a tela está bloqueada. */
public final class VoiceService extends Service implements TextToSpeech.OnInitListener {
    public static final String ACTION_ANNOUNCE = "pt.vcaitano.horajarvis.VOICE_ANNOUNCE";
    public static final String ACTION_TEST = "pt.vcaitano.horajarvis.VOICE_TEST";

    public static final String ACTION_FINISHED = "pt.vcaitano.horajarvis.VOICE_FINISHED";
    public static final String EXTRA_PHRASE = "phrase";
    private static final String CHANNEL_ANNOUNCE_ON = "horajarvis_avisos_v2_vibra";
    private static final String CHANNEL_ANNOUNCE_OFF = "horajarvis_avisos_v2_sem_vibrar";
    private static final String CHANNEL_RUNNING = "horajarvis_execucao_v1";
    private static final int ID_RUNNING = 4001;
    private static final int ID_ANNOUNCEMENT = 4002;
    private static final Locale PORTUGUESE_BR = new Locale("pt", "BR");

    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextToSpeech tts;
    private PowerManager.WakeLock wakeLock;
    private AudioManager audioManager;
    private AudioFocusRequest audioFocusRequest;
    private boolean preview;
    private boolean finishing;
    private String phrase;

    @Override
    public void onCreate() {
        super.onCreate();
        createChannels();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Se o serviço estiver em uso, reinicia um único anúncio, sem sobreposição.
        finishing = false;
        preview = intent != null && ACTION_TEST.equals(intent.getAction());
        Calendar now = Calendar.getInstance();
        phrase = intent != null ? intent.getStringExtra(EXTRA_PHRASE) : null;
        if (phrase == null || phrase.isEmpty()) phrase = PhraseGenerator.accordingToSettings(this, now);
        Notification running = makeNotification(CHANNEL_RUNNING, "Hora Jarvis", "A preparar anúncio de voz…", true);
        startForeground(ID_RUNNING, running);

        if (wakeLock == null) {
            PowerManager power = (PowerManager) getSystemService(POWER_SERVICE);
            if (power != null) {
                wakeLock = power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "HoraJarvis:Announcement");
                wakeLock.setReferenceCounted(false);
            }
        }
        if (wakeLock != null && !wakeLock.isHeld()) wakeLock.acquire(30_000L);
        requestAudioFocus();
        if (tts != null) {
            tts.stop();
            speak();
        } else {
            tts = new TextToSpeech(getApplicationContext(), this);
        }
        // Proteção contra motores de voz que não concluem a inicialização/reprodução.
        handler.removeCallbacksAndMessages(null);
        handler.postDelayed(this::finish, 25_000L);
        return START_NOT_STICKY;
    }

    /** Notificação independente do TTS; canais novos para vibração de wearable. */
    public static void postTimeNotification(android.content.Context context, String phrase) {
        if (Build.VERSION.SDK_INT >= 33
                && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) return;
        NotificationManager nm = (NotificationManager) context.getSystemService(NOTIFICATION_SERVICE);
        if (nm == null) return;
        createReminderChannels(nm);
        AppSettings config = AppSettings.load(context);
        String channel = config.vibrate ? CHANNEL_ANNOUNCE_ON : CHANNEL_ANNOUNCE_OFF;
        String time = new SimpleDateFormat("HH:mm", PORTUGUESE_BR).format(Calendar.getInstance().getTime());
        long now = System.currentTimeMillis();
        int requestId = (int) ((now / 1000L) & 0x7FFFFFFF);
        Intent openIntent = new Intent(context, AlertActivity.class)
                .putExtra(EXTRA_PHRASE, phrase)
                .putExtra(AlertActivity.EXTRA_PREVIEW, true);
        PendingIntent open = PendingIntent.getActivity(context, requestId, openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder notification = new Notification.Builder(context, channel)
                .setSmallIcon(R.drawable.ic_hour)
                .setContentTitle(time + " • Hora Jarvis")
                .setContentText(phrase)
                .setStyle(new Notification.BigTextStyle().bigText(phrase))
                .setContentIntent(open)
                .setAutoCancel(true)
                .setCategory(Notification.CATEGORY_ALARM)
                .setWhen(now)
                .setShowWhen(true)
                .setVisibility(Notification.VISIBILITY_PUBLIC)
                .setTimeoutAfter(180_000L)
                .setOnlyAlertOnce(false);
        if (config.fullScreen && (Build.VERSION.SDK_INT < 34 || nm.canUseFullScreenIntent())) {
            Intent clock = new Intent(context, AlertActivity.class)
                    .putExtra(EXTRA_PHRASE, phrase)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            PendingIntent full = PendingIntent.getActivity(context, requestId + 100_000, clock,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            notification.setFullScreenIntent(full, true);
        }
        // ID próprio para cada aviso: o relógio vê um evento novo, não uma atualização silenciosa.
        nm.notify(requestId, notification.build());
    }

    private static void createReminderChannels(NotificationManager nm) {
        NotificationChannel vib = new NotificationChannel(CHANNEL_ANNOUNCE_ON,
                "Avisos de hora • vibrar", NotificationManager.IMPORTANCE_HIGH);
        vib.setDescription("Aviso de hora com vibração no telemóvel e relógio compatível");
        vib.setSound(null, null);
        vib.enableVibration(true);
        vib.setVibrationPattern(new long[]{0, 350, 160, 350});
        vib.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
        nm.createNotificationChannel(vib);
        NotificationChannel quiet = new NotificationChannel(CHANNEL_ANNOUNCE_OFF,
                "Avisos de hora • sem vibração", NotificationManager.IMPORTANCE_HIGH);
        quiet.setDescription("Aviso de hora sem vibração");
        quiet.setSound(null, null);
        quiet.enableVibration(false);
        quiet.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
        nm.createNotificationChannel(quiet);
    }

    @Override
    public void onInit(int status) {
        if (finishing) return;
        if (status != TextToSpeech.SUCCESS || tts == null) {
            Log.e("HoraJarvis", "Motor de texto para fala indisponível");
            finish();
            return;
        }
        int language = tts.setLanguage(PORTUGUESE_BR);
        if (language == TextToSpeech.LANG_NOT_SUPPORTED || language == TextToSpeech.LANG_MISSING_DATA) {
            language = tts.setLanguage(new Locale("pt", "PT"));
        }
        if (language == TextToSpeech.LANG_NOT_SUPPORTED || language == TextToSpeech.LANG_MISSING_DATA) {
            Log.e("HoraJarvis", "Não há voz portuguesa instalada");
            finish();
            return;
        }
        selectMaleVoiceIfAvailable();
        tts.setSpeechRate(0.91f);
        tts.setPitch(0.82f);
        tts.setAudioAttributes(new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ALARM)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build());
        tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String utteranceId) { }
            @Override public void onDone(String utteranceId) { handler.post(VoiceService.this::finish); }
            @Override public void onError(String utteranceId) { handler.post(VoiceService.this::finish); }
        });
        speak();
    }

    /** Nem todos os motores TTS disponibilizam voz masculina; não fingimos ter a voz original. */
    private void selectMaleVoiceIfAvailable() {
        if (tts == null) return;
        Set<android.speech.tts.Voice> installed = tts.getVoices();
        if (installed == null) return;
        android.speech.tts.Voice fallback = null;
        for (android.speech.tts.Voice voice : installed) {
            if (!"pt".equalsIgnoreCase(voice.getLocale().getLanguage())
                    || voice.isNetworkConnectionRequired()) continue;
            if (fallback == null || "BR".equalsIgnoreCase(voice.getLocale().getCountry())) fallback = voice;
            String name = voice.getName().toLowerCase(Locale.ROOT);
            if ("BR".equalsIgnoreCase(voice.getLocale().getCountry())
                    && (name.contains("male") && !name.contains("female")
                    || name.contains("masculino") || name.contains("masculina"))) {
                tts.setVoice(voice);
                return;
            }
        }
        if (fallback != null) tts.setVoice(fallback);
    }

    private void speak() {
        if (tts == null || finishing) return;
        int result = tts.speak(phrase, TextToSpeech.QUEUE_FLUSH, null, "horajarvis-voice");
        if (result == TextToSpeech.ERROR) finish();
    }

    private Notification makeNotification(String channel, String title, String body, boolean ongoing) {
        Intent openIntent = new Intent(this, MainActivity.class);
        PendingIntent open = PendingIntent.getActivity(this, 100, openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, channel)
                .setSmallIcon(R.drawable.ic_hour)
                .setContentTitle(title)
                .setContentText(body)
                .setStyle(new Notification.BigTextStyle().bigText(body))
                .setContentIntent(open)
                .setAutoCancel(!ongoing)
                .setOngoing(ongoing)
                .setCategory(ongoing ? Notification.CATEGORY_SERVICE : Notification.CATEGORY_REMINDER)
                .setWhen(System.currentTimeMillis())
                .setShowWhen(true)
                .build();
    }

    private void createChannels() {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm == null) return;
        createReminderChannels(nm);
        NotificationChannel running = new NotificationChannel(CHANNEL_RUNNING,
                "Reprodução de voz", NotificationManager.IMPORTANCE_LOW);
        running.setSound(null, null);
        nm.createNotificationChannel(running);
    }

    private void requestAudioFocus() {
        audioManager = (AudioManager) getSystemService(AUDIO_SERVICE);
        if (audioManager == null) return;
        audioFocusRequest = new AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK)
                .setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build())
                .build();
        audioManager.requestAudioFocus(audioFocusRequest);
    }

    private void finish() {
        if (finishing) return;
        finishing = true;
        sendBroadcast(new Intent(ACTION_FINISHED).setPackage(getPackageName()));
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    @Override
    public void onDestroy() {
        finishing = true;
        handler.removeCallbacksAndMessages(null);
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        if (audioManager != null && audioFocusRequest != null)
            audioManager.abandonAudioFocusRequest(audioFocusRequest);
        if (wakeLock != null && wakeLock.isHeld()) wakeLock.release();
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}
