package pt.vcaitano.horajarvis;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/** Apenas uma tela: dias, janela de horários, frequência e ativação. */
public final class MainActivity extends Activity {
    private static final int BACKGROUND = Color.rgb(11, 18, 32);
    private static final int PANEL = Color.rgb(21, 32, 49);
    private static final int ACCENT = Color.rgb(93, 224, 190);
    private static final int PALE = Color.rgb(238, 251, 248);
    private static final int MUTED = Color.rgb(164, 183, 193);
    private static final int REQUEST_NOTIFICATION = 53;
    private final Locale locale = new Locale("pt", "BR");

    private AppSettings prefs;
    private Switch master;
    private TextView statusText;
    private TextView nextText;
    private EditText intervalInput;
    private EditText customTimesInput;
    private Switch customModeSwitch;
    private Switch vibrationSwitch;
    private Switch conciseSpeechSwitch;
    private Switch customSpeechSwitch;
    private EditText customSpeechInput;
    private Switch fullScreenSwitch;
    private LinearLayout intervalPanel;
    private LinearLayout customPanel;
    private LinearLayout schedulePanel;
    private Button startButton;
    private Button endButton;
    private final TextView[] dayChips = new TextView[7];

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = AppSettings.load(this);
        buildUi();
        // Instalações novas têm permissões independentes: pedir na primeira abertura.
        getWindow().getDecorView().post(this::requestInitialPermissions);
    }

    @Override
    public void onResume() {
        super.onResume();
        TimeScheduler.replan(this); // O utilizador pode ter acabado de conceder alarmes exatos.
        updateStatus();
    }

    private void buildUi() {
        LinearLayout root = column();
        root.setBackgroundColor(BACKGROUND);
        if (Build.VERSION.SDK_INT >= 30) {
            root.setOnApplyWindowInsetsListener((v, insets) -> {
                android.graphics.Insets bars = insets.getInsets(WindowInsets.Type.systemBars());
                root.setPadding(0, bars.top, 0, bars.bottom);
                return insets;
            });
        }
        setContentView(root);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(false);
        scroll.setVerticalScrollBarEnabled(false);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        LinearLayout content = column();
        content.setPadding(dp(20), dp(22), dp(20), dp(24));
        scroll.addView(content);

        TextView eyebrow = text("●  ASSISTENTE DE HORÁRIOS", 12, ACCENT, true);
        content.addView(eyebrow);
        TextView title = text("HORA", 31, PALE, true);
        title.setLetterSpacing(0.09f);
        content.addView(withTop(title, 10));
        TextView introduction = text("O seu assistente anuncia as horas com voz e notificação, nos dias e horários que escolher.", 14, MUTED, false);
        content.addView(withTop(introduction, 8));

        LinearLayout stateCard = panel();
        content.addView(withTop(stateCard, 24));
        LinearLayout row = row();
        row.setGravity(Gravity.CENTER_VERTICAL);
        stateCard.addView(row);
        LinearLayout switchText = column();
        row.addView(switchText, new LinearLayout.LayoutParams(0, -2, 1));
        switchText.addView(text("Ativar avisos", 17, PALE, true));
        switchText.addView(withTop(text("Voz + notificação", 12, MUTED, false), 4));
        master = new Switch(this);
        master.setChecked(prefs.enabled);
        master.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        row.addView(master);
        statusText = text("", 12, MUTED, false);
        stateCard.addView(withTop(statusText, 16));

        content.addView(withTop(sectionTitle("DIAS DA SEMANA"), 24));
        TextView dayHelp = text("Toque nos dias em que deseja receber os avisos.", 12, MUTED, false);
        content.addView(withTop(dayHelp, 6));
        LinearLayout dayBox = panel();
        content.addView(withTop(dayBox, 12));
        LinearLayout dayRow1 = row();
        LinearLayout dayRow2 = row();
        dayBox.addView(dayRow1);
        dayBox.addView(withTop(dayRow2, 8));
        String[] dayNames = {"SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"};
        for (int i = 0; i < 7; i++) {
            final int dayIndex = i;
            TextView chip = text(dayNames[i], 12, PALE, true);
            chip.setGravity(Gravity.CENTER);
            chip.setPadding(dp(8), dp(12), dp(8), dp(12));
            LinearLayout.LayoutParams chipParams = new LinearLayout.LayoutParams(0, -2, 1);
            if (i != 0 && i != 4) chipParams.leftMargin = dp(8);
            (i < 4 ? dayRow1 : dayRow2).addView(chip, chipParams);
            chip.setOnClickListener(v -> {
                prefs.daysMask ^= (1 << dayIndex);
                updateDays();
            });
            dayChips[i] = chip;
        }
        updateDays();

        content.addView(withTop(sectionTitle("HORÁRIO DOS AVISOS"), 24));
        LinearLayout schedule = panel();
        schedulePanel = schedule;
        content.addView(withTop(schedule, 12));
        LinearLayout timeRow = row();
        schedule.addView(timeRow);
        LinearLayout leftTime = column();
        timeRow.addView(leftTime, new LinearLayout.LayoutParams(0, -2, 1));
        leftTime.addView(text("COMEÇAR ÀS", 11, MUTED, true));
        startButton = timeButton(formatMinutes(prefs.startMinute));
        leftTime.addView(withTop(startButton, 8));
        LinearLayout rightTime = column();
        LinearLayout.LayoutParams rightParams = new LinearLayout.LayoutParams(0, -2, 1);
        rightParams.leftMargin = dp(14);
        timeRow.addView(rightTime, rightParams);
        rightTime.addView(text("TERMINAR ÀS", 11, MUTED, true));
        endButton = timeButton(formatMinutes(prefs.endMinute));
        rightTime.addView(withTop(endButton, 8));
        startButton.setOnClickListener(v -> openTimePicker(true));
        endButton.setOnClickListener(v -> openTimePicker(false));
        schedule.addView(withTop(text("Se a hora final for igual ou anterior à inicial, os avisos continuam até ao dia seguinte.", 12, MUTED, false), 12));

        content.addView(withTop(sectionTitle("FREQUÊNCIA"), 24));
        LinearLayout frequency = panel();
        intervalPanel = frequency;
        content.addView(withTop(frequency, 12));
        frequency.addView(text("Repetir a cada", 14, PALE, true));
        LinearLayout intervalRow = row();
        intervalRow.setGravity(Gravity.CENTER_VERTICAL);
        frequency.addView(withTop(intervalRow, 10));
        intervalInput = new EditText(this);
        intervalInput.setInputType(InputType.TYPE_CLASS_NUMBER);
        intervalInput.setSingleLine(true);
        intervalInput.setText(String.valueOf(prefs.intervalMinute));
        intervalInput.setTextSize(22);
        intervalInput.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        intervalInput.setTextColor(PALE);
        intervalInput.setSelectAllOnFocus(true);
        intervalInput.setGravity(Gravity.CENTER);
        intervalInput.setPadding(dp(12), dp(10), dp(12), dp(10));
        intervalInput.setBackground(rounded(Color.rgb(31, 47, 65), dp(12), 0));
        intervalRow.addView(intervalInput, new LinearLayout.LayoutParams(dp(116), dp(54)));
        TextView minutes = text("minutos", 16, MUTED, false);
        LinearLayout.LayoutParams minutesParams = new LinearLayout.LayoutParams(-2, -2);
        minutesParams.leftMargin = dp(14);
        intervalRow.addView(minutes, minutesParams);
        frequency.addView(withTop(text("Exemplos: 15, 30, 60 ou 120 minutos. Aceita de 15 a 720 minutos.", 12, MUTED, false), 12));

        content.addView(withTop(sectionTitle("HORÁRIOS PERSONALIZADOS"), 24));
        LinearLayout mode = panel();
        content.addView(withTop(mode, 12));
        LinearLayout modeRow = row();
        modeRow.setGravity(Gravity.CENTER_VERTICAL);
        mode.addView(modeRow);
        modeRow.addView(text("Usar horários livres", 16, PALE, true), new LinearLayout.LayoutParams(0, -2, 1));
        customModeSwitch = new Switch(this);
        customModeSwitch.setChecked(prefs.customMode);
        customModeSwitch.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        modeRow.addView(customModeSwitch);
        mode.addView(withTop(text("Ativado: ignora a frequência e utiliza somente as horas da lista nos dias marcados.", 12, MUTED, false), 6));
        customPanel = panel();
        content.addView(withTop(customPanel, 10));
        customPanel.addView(text("HORAS EXATAS (HH:MM)", 12, ACCENT, true));
        customTimesInput = new EditText(this);
        customTimesInput.setText(prefs.customTimes);
        customTimesInput.setTextColor(PALE);
        customTimesInput.setTextSize(16);
        customTimesInput.setHint("13:00, 15:00, 16:50, 17:00");
        customTimesInput.setHintTextColor(MUTED);
        customTimesInput.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        customTimesInput.setMinLines(2);
        customTimesInput.setMaxLines(5);
        customTimesInput.setPadding(dp(12), dp(14), dp(12), dp(14));
        customTimesInput.setBackground(rounded(Color.rgb(31,47,65), dp(12), 0));
        customPanel.addView(withTop(customTimesInput, 10));
        Button addTime = secondaryButton("+ ADICIONAR HORÁRIO");
        customPanel.addView(withTop(addTime, 10));
        addTime.setOnClickListener(v -> new TimePickerDialog(this, (picker, hour, minute) -> {
            String current = customTimesInput.getText().toString().trim();
            String time = String.format(Locale.ROOT, "%02d:%02d", hour, minute);
            try { customTimesInput.setText(CustomTimes.normalize(current.isEmpty() ? time : current + ", " + time)); }
            catch (IllegalArgumentException invalid) { customTimesInput.setError(invalid.getMessage()); }
        }, 13, 0, true).show());
        customPanel.addView(withTop(text("Pode inserir quantos horários desejar, separados por vírgulas. Para remover, apague a hora da lista.", 12, MUTED, false), 8));
        customModeSwitch.setOnCheckedChangeListener((button, selected) -> updateModeVisibility());
        updateModeVisibility();

        content.addView(withTop(sectionTitle("FORMA DE FALAR A HORA"), 24));
        LinearLayout speechOptions = panel();
        content.addView(withTop(speechOptions, 12));
        LinearLayout speechRow = row();
        speechRow.setGravity(Gravity.CENTER_VERTICAL);
        speechOptions.addView(speechRow);
        speechRow.addView(text("Fala curta (só a hora)", 15, PALE, true), new LinearLayout.LayoutParams(0, -2, 1));
        conciseSpeechSwitch = new Switch(this);
        conciseSpeechSwitch.setChecked(prefs.conciseSpeech);
        conciseSpeechSwitch.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        speechRow.addView(conciseSpeechSwitch);
        speechOptions.addView(withTop(text("Sem frases personalizadas: ativado diz só a hora; desativado usa as 15.360 combinações existentes.", 12, MUTED, false), 8));

        // Terceira opção, independente das formas de falar existentes.
        LinearLayout personalSpeech = panel();
        content.addView(withTop(personalSpeech, 12));
        LinearLayout customSpeechRow = row();
        customSpeechRow.setGravity(Gravity.CENTER_VERTICAL);
        personalSpeech.addView(customSpeechRow);
        customSpeechRow.addView(text("Usar frases personalizadas", 15, PALE, true),
                new LinearLayout.LayoutParams(0, -2, 1));
        customSpeechSwitch = new Switch(this);
        customSpeechSwitch.setChecked(prefs.customSpeech);
        customSpeechSwitch.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        customSpeechRow.addView(customSpeechSwitch);
        personalSpeech.addView(withTop(text("Escreva o que será falado junto da hora. Pode ter uma frase geral ou uma diferente em cada horário.", 12, MUTED, false), 8));
        customSpeechInput = new EditText(this);
        customSpeechInput.setText(prefs.customSpeechLines);
        customSpeechInput.setTextColor(PALE);
        customSpeechInput.setTextSize(15);
        customSpeechInput.setHint("Olá, {hora}. Tudo bem?\n11:00 | Olá, {hora}. Hora de tirar a parenterica da geladeira.\n17:00 | Olha, {hora}. Melhor buscar seu filho na creche.");
        customSpeechInput.setHintTextColor(MUTED);
        customSpeechInput.setInputType(InputType.TYPE_CLASS_TEXT
                | InputType.TYPE_TEXT_FLAG_MULTI_LINE | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        customSpeechInput.setMinLines(4);
        customSpeechInput.setMaxLines(8);
        customSpeechInput.setPadding(dp(12), dp(14), dp(12), dp(14));
        customSpeechInput.setBackground(rounded(Color.rgb(31, 47, 65), dp(12), 0));
        personalSpeech.addView(withTop(customSpeechInput, 12));
        personalSpeech.addView(withTop(text("Use {hora} para inserir a hora atual na frase. Sem {hora}, o app diz a hora antes do texto. Em linhas com HH:MM | mensagem, a frase toca naquele horário SE ele estiver programado nos seus avisos. Nos outros horários continuam as opções curta ou variada.", 12, MUTED, false), 10));

        content.addView(withTop(sectionTitle("NOTIFICAÇÕES E TELA"), 24));
        LinearLayout options = panel();
        content.addView(withTop(options, 12));
        LinearLayout vibrationRow = row();
        vibrationRow.setGravity(Gravity.CENTER_VERTICAL);
        options.addView(vibrationRow);
        vibrationRow.addView(text("Vibrar no relógio e telemóvel", 15, PALE, true), new LinearLayout.LayoutParams(0,-2,1));
        vibrationSwitch = new Switch(this);
        vibrationSwitch.setChecked(prefs.vibrate);
        vibrationSwitch.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        vibrationRow.addView(vibrationSwitch);
        options.addView(withTop(text("Depende das permissões de notificação e das definições do smartwatch.", 12, MUTED, false), 6));
        LinearLayout screenRow = row();
        screenRow.setGravity(Gravity.CENTER_VERTICAL);
        options.addView(withTop(screenRow, 18));
        screenRow.addView(text("Tela de aviso ao anunciar", 15, PALE, true), new LinearLayout.LayoutParams(0,-2,1));
        fullScreenSwitch = new Switch(this);
        fullScreenSwitch.setChecked(prefs.fullScreen);
        fullScreenSwitch.setThumbTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        screenRow.addView(fullScreenSwitch);
        options.addView(withTop(text("Na tela bloqueada, mostra um aviso sem anúncios quando o Android autorizar. Com o telemóvel em uso, pode aparecer só uma notificação destacada.", 12, MUTED, false), 6));
        Button screenPermission = secondaryButton("⚙  PERMISSÃO DE TELA DE AVISO");
        options.addView(withTop(screenPermission, 12));
        screenPermission.setOnClickListener(v -> openFullScreenPermission());

        LinearLayout info = panel();
        content.addView(withTop(info, 22));
        info.addView(text("VOZ ESTILO JARVIS", 12, ACCENT, true));
        info.addView(withTop(text("“Senhor, agora são 14 horas em ponto.”", 15, PALE, false), 7));
        info.addView(withTop(text("Voz portuguesa do telemóvel, com tom grave. A disponibilidade de uma voz masculina depende do motor de fala instalado.", 12, MUTED, false), 6));

        Button saveButton = primaryButton("SALVAR CONFIGURAÇÃO");
        content.addView(withTop(saveButton, 22));
        saveButton.setOnClickListener(v -> saveSettings());
        Button previewNotice = secondaryButton("◉  VISUALIZAR AVISO + ANÚNCIO FICTÍCIO");
        content.addView(withTop(previewNotice, 12));
        previewNotice.setOnClickListener(v -> previewNoticeScreen());
        content.addView(withTop(text("A demonstração inclui 70% de publicidade fictícia e 30% com a hora e a frase completa. Nenhum anúncio real será mostrado na tela bloqueada.", 12, MUTED, false), 6));
        Button testButton = secondaryButton("▶  TESTAR VOZ AGORA");
        content.addView(withTop(testButton, 10));
        testButton.setOnClickListener(v -> previewVoice());
        Button testNotification = secondaryButton("🔔  TESTAR NOTIFICAÇÃO AGORA");
        content.addView(withTop(testNotification, 10));
        testNotification.setOnClickListener(v -> previewNotification());
        nextText = text("", 13, ACCENT, true);
        nextText.setGravity(Gravity.CENTER);
        content.addView(withTop(nextText, 16));

        Button permissionButton = secondaryButton("⚙  PERMISSÕES DE ALARMES");
        content.addView(withTop(permissionButton, 16));
        permissionButton.setOnClickListener(v -> requestPermissionsIfNeeded());
        content.addView(withTop(text("Para maior fiabilidade, permita notificações, Alarmes e lembretes e coloque o app em Bateria sem restrições. O modo Não incomodar pode impedir voz e vibração. Anúncios não são exibidos sobre outros apps nem na tela bloqueada.", 12, MUTED, false), 14));

        updateStatus();
    }

    private void openTimePicker(boolean start) {
        int existing = start ? prefs.startMinute : prefs.endMinute;
        new TimePickerDialog(this, (picker, hour, minute) -> {
            int time = hour * 60 + minute;
            if (start) {
                prefs.startMinute = time;
                startButton.setText(formatMinutes(time));
            } else {
                prefs.endMinute = time;
                endButton.setText(formatMinutes(time));
            }
        }, existing / 60, existing % 60, true).show();
    }

    private void saveSettings() {
        String raw = intervalInput.getText().toString().trim();
        int interval = prefs.intervalMinute;
        if (!customModeSwitch.isChecked()) {
            try { interval = Integer.parseInt(raw); }
            catch (NumberFormatException ex) {
                intervalInput.setError("Insira um número de minutos.");
                return;
            }
            if (interval < 15 || interval > 720) {
                intervalInput.setError("Escolha entre 15 e 720 minutos.");
                return;
            }
        }
        String normalizedTimes = prefs.customTimes;
        if (customModeSwitch.isChecked()) {
            try {
                normalizedTimes = CustomTimes.normalize(customTimesInput.getText().toString());
                if (normalizedTimes.isEmpty()) {
                    customTimesInput.setError("Adicione pelo menos um horário.");
                    return;
                }
            } catch (IllegalArgumentException error) {
                customTimesInput.setError(error.getMessage());
                return;
            }
        }
        String personalLines = customSpeechInput.getText().toString().trim();
        if (customSpeechSwitch.isChecked()) {
            try {
                PhraseGenerator.validateCustomLines(personalLines);
            } catch (IllegalArgumentException error) {
                customSpeechInput.setError(error.getMessage());
                return;
            }
        }
        if (master.isChecked() && prefs.daysMask == 0) {
            Toast.makeText(this, "Selecione pelo menos um dia.", Toast.LENGTH_LONG).show();
            return;
        }
        prefs.enabled = master.isChecked();
        prefs.intervalMinute = interval;
        prefs.customMode = customModeSwitch.isChecked();
        prefs.customTimes = normalizedTimes;
        prefs.vibrate = vibrationSwitch.isChecked();
        prefs.fullScreen = fullScreenSwitch.isChecked();
        prefs.conciseSpeech = conciseSpeechSwitch.isChecked();
        prefs.customSpeech = customSpeechSwitch.isChecked();
        prefs.customSpeechLines = personalLines;
        prefs.save(this);
        customTimesInput.setText(normalizedTimes);
        TimeScheduler.replan(this);
        Toast.makeText(this, "Configuração salva!", Toast.LENGTH_SHORT).show();
        updateStatus();
        if (prefs.enabled) requestPermissionsIfNeeded();
    }

    /** Uma instalação com package novo não herda permissões nem horários de outra instalação. */
    private void requestInitialPermissions() {
        android.content.SharedPreferences asked = getSharedPreferences("horajarvis_permissions", MODE_PRIVATE);
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
                && !asked.getBoolean("asked_notification", false)) {
            asked.edit().putBoolean("asked_notification", true).apply();
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQUEST_NOTIFICATION);
            return;
        }
        if (!TimeScheduler.preciseAlarmsAllowed(this) && !asked.getBoolean("asked_exact_alarm", false)) {
            asked.edit().putBoolean("asked_exact_alarm", true).apply();
            openExactPermission();
        }
    }

    private boolean notificationsAllowed() {
        android.app.NotificationManager nm =
                (android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm == null || !nm.areNotificationsEnabled()) return false;
        return Build.VERSION.SDK_INT < 33
                || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED;
    }

    private void requestPermissionsIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQUEST_NOTIFICATION);
        } else if (!notificationsAllowed()) {
            try {
                Intent settings = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS);
                settings.putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName());
                startActivity(settings);
            } catch (RuntimeException ex) {
                startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                        Uri.parse("package:" + getPackageName())));
            }
        } else if (!TimeScheduler.preciseAlarmsAllowed(this)) {
            openExactPermission();
        } else {
            Toast.makeText(this, "Notificações e alarmes exatos autorizados.", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_NOTIFICATION) {
            TimeScheduler.replan(this);
            updateStatus();
            // Em seguida solicitar o acesso especial aos alarmes, uma só vez na primeira abertura.
            requestInitialPermissions();
        }
    }

    private void openExactPermission() {
        if (Build.VERSION.SDK_INT < 31 || TimeScheduler.preciseAlarmsAllowed(this)) {
            Toast.makeText(this, "Permissão de alarmes exatos já ativa.", Toast.LENGTH_SHORT).show();
            return;
        }
        try {
            Intent intent = new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                    Uri.parse("package:" + getPackageName()));
            startActivity(intent);
        } catch (Exception ex) {
            startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + getPackageName())));
        }
    }

    private void updateModeVisibility() {
        if (customModeSwitch == null || customPanel == null) return;
        boolean custom = customModeSwitch.isChecked();
        customPanel.setVisibility(custom ? View.VISIBLE : View.GONE);
        intervalPanel.setVisibility(custom ? View.GONE : View.VISIBLE);
        schedulePanel.setVisibility(custom ? View.GONE : View.VISIBLE);
    }

    private void openFullScreenPermission() {
        if (Build.VERSION.SDK_INT < 34) {
            Toast.makeText(this, "Esta versão do Android controla a tela de alarme automaticamente.", Toast.LENGTH_LONG).show();
            return;
        }
        android.app.NotificationManager nm = (android.app.NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm != null && nm.canUseFullScreenIntent()) {
            Toast.makeText(this, "Permissão de tela de alarme já ativa.", Toast.LENGTH_SHORT).show();
            return;
        }
        try {
            Intent intent = new Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,
                    Uri.parse("package:" + getPackageName()));
            startActivity(intent);
        } catch (RuntimeException ex) {
            startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + getPackageName())));
        }
    }

    private String previewPhrase() {
        AppSettings current = AppSettings.load(this);
        current.conciseSpeech = conciseSpeechSwitch.isChecked();
        current.customSpeech = customSpeechSwitch.isChecked();
        current.customSpeechLines = customSpeechInput.getText().toString().trim();
        if (current.customSpeech) {
            try {
                PhraseGenerator.validateCustomLines(current.customSpeechLines);
            } catch (IllegalArgumentException error) {
                customSpeechInput.setError(error.getMessage());
                return null;
            }
        }
        return PhraseGenerator.forSettings(this, Calendar.getInstance(), current);
    }

    private void previewNoticeScreen() {
        // Pré-visualização explícita: usa a frase digitada sem exigir salvar.
        String words = previewPhrase();
        if (words == null) return;
        Intent i = new Intent(this, AlertActivity.class);
        i.putExtra(VoiceService.EXTRA_PHRASE, words);
        i.putExtra(AlertActivity.EXTRA_PREVIEW, true);
        startActivity(i);
    }

    private void previewNotification() {
        if (!notificationsAllowed()) {
            Toast.makeText(this, "Notificações bloqueadas. Autorize para testar.", Toast.LENGTH_LONG).show();
            requestPermissionsIfNeeded();
            return;
        }
        String words = previewPhrase();
        if (words == null) return;
        VoiceService.postTimeNotification(this, words);
        Toast.makeText(this, "Notificação de teste enviada. Confira também o relógio.", Toast.LENGTH_LONG).show();
    }

    private void previewVoice() {
        String words = previewPhrase();
        if (words == null) return;
        Intent intent = new Intent(this, VoiceService.class)
                .setAction(VoiceService.ACTION_TEST)
                .putExtra(VoiceService.EXTRA_PHRASE, words);
        try {
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(intent);
            else startService(intent);
        } catch (RuntimeException ex) {
            Toast.makeText(this, "Android não permitiu iniciar a voz: " + ex.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void updateDays() {
        for (int i = 0; i < 7; i++) {
            if (dayChips[i] == null) continue;
            boolean selected = (prefs.daysMask & (1 << i)) != 0;
            dayChips[i].setTextColor(selected ? BACKGROUND : MUTED);
            dayChips[i].setBackground(rounded(selected ? ACCENT : Color.rgb(31, 47, 65), dp(12), 0));
        }
    }

    private void updateStatus() {
        if (statusText == null) return;
        AppSettings saved = AppSettings.load(this);
        if (!saved.enabled) {
            statusText.setText("○  Avisos desligados: ative e toque em SALVAR CONFIGURAÇÃO.");
            statusText.setTextColor(MUTED);
        } else if (!notificationsAllowed()) {
            statusText.setText("⚠  Notificações bloqueadas: autorize para receber no telemóvel/relógio.");
            statusText.setTextColor(Color.rgb(255, 204, 137));
        } else if (!TimeScheduler.preciseAlarmsAllowed(this)) {
            statusText.setText("⚠  Horários aproximados. Autorize Alarmes e lembretes.");
            statusText.setTextColor(Color.rgb(255, 204, 137));
        } else {
            statusText.setText("●  Ativo • avisos programados");
            statusText.setTextColor(ACCENT);
        }
        if (nextText != null) nextText.setText(TimeScheduler.prettyNext(this));
    }

    private static String formatMinutes(int minutes) {
        return String.format(Locale.ROOT, "%02d:%02d", minutes / 60, minutes % 60);
    }

    private LinearLayout column() {
        LinearLayout ll = new LinearLayout(this);
        ll.setOrientation(LinearLayout.VERTICAL);
        return ll;
    }

    private LinearLayout row() {
        LinearLayout ll = new LinearLayout(this);
        ll.setOrientation(LinearLayout.HORIZONTAL);
        return ll;
    }

    private LinearLayout panel() {
        LinearLayout ll = column();
        ll.setPadding(dp(16), dp(17), dp(16), dp(17));
        ll.setBackground(rounded(PANEL, dp(18), 0));
        return ll;
    }

    private TextView sectionTitle(String value) { return text(value, 13, ACCENT, true); }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView tv = new TextView(this);
        tv.setText(value);
        tv.setTextSize(sp);
        tv.setTextColor(color);
        if (bold) tv.setTypeface(Typeface.create("sans-serif-medium", Typeface.BOLD));
        tv.setLineSpacing(dp(3), 1f);
        return tv;
    }

    private Button timeButton(String value) {
        Button btn = secondaryButton(value);
        btn.setTextSize(20);
        return btn;
    }

    private Button primaryButton(String value) {
        Button btn = new Button(this);
        btn.setText(value);
        btn.setTextSize(14);
        btn.setTextColor(BACKGROUND);
        btn.setAllCaps(false);
        btn.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        btn.setBackground(rounded(ACCENT, dp(14), 0));
        btn.setMinHeight(dp(54));
        btn.setPadding(dp(12), dp(8), dp(12), dp(8));
        return btn;
    }

    private Button secondaryButton(String value) {
        Button btn = new Button(this);
        btn.setText(value);
        btn.setTextSize(14);
        btn.setTextColor(PALE);
        btn.setAllCaps(false);
        btn.setBackground(rounded(Color.rgb(32, 51, 69), dp(14), 0));
        btn.setMinHeight(dp(50));
        btn.setPadding(dp(12), dp(8), dp(12), dp(8));
        return btn;
    }

    private GradientDrawable rounded(int color, int radius, int stroke) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(color);
        drawable.setCornerRadius(radius);
        if (stroke != 0) drawable.setStroke(dp(1), stroke);
        return drawable;
    }

    private <T extends View> T withTop(T view, int margin) {
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1, -2);
        lp.topMargin = dp(margin);
        view.setLayoutParams(lp);
        return view;
    }

    private int dp(int value) { return Math.round(getResources().getDisplayMetrics().density * value); }
}
