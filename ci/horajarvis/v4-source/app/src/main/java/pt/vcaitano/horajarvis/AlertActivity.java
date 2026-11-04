package pt.vcaitano.horajarvis;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

/** Aviso visual próprio. Não inclui publicidade real nem desbloqueia o ecrã. */
public final class AlertActivity extends Activity {
    public static final String EXTRA_PREVIEW = "preview";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean registered;
    private boolean preview;
    private final BroadcastReceiver voiceDone = new BroadcastReceiver() {
        @Override public void onReceive(Context ctx, Intent intent) {
            if (!preview) finish(); // Pré-visualização fica aberta até fechar manualmente.
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        preview = getIntent().getBooleanExtra(EXTRA_PREVIEW, false);
        if (Build.VERSION.SDK_INT >= 27) {
            setShowWhenLocked(!preview);
            setTurnScreenOn(!preview);
        } else if (!preview) {
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                    | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON);
        }
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setNavigationBarColor(0xFF080E18);

        String words = getIntent().getStringExtra(VoiceService.EXTRA_PHRASE);
        if (words == null || words.trim().isEmpty()) {
            words = PhraseGenerator.accordingToSettings(this, Calendar.getInstance());
        }
        String time = new SimpleDateFormat("HH:mm", Locale.ROOT).format(Calendar.getInstance().getTime());

        LinearLayout root = new LinearLayout(this);
        root.setBackgroundColor(0xFF090F1D);
        root.setOrientation(LinearLayout.VERTICAL);
        setContentView(root);
        // Percentuais medidos dentro da área útil (sem a barra de navegação).
        FrameLayout adArea = new FrameLayout(this);
        root.addView(adArea, new LinearLayout.LayoutParams(-1, 0, 7f));
        drawMockAd(adArea);

        LinearLayout message = new LinearLayout(this);
        message.setOrientation(LinearLayout.VERTICAL);
        message.setPadding(dp(18), dp(8), dp(18), dp(12));
        message.setBackgroundColor(0xFF142438);
        root.addView(message, new LinearLayout.LayoutParams(-1, 0, 3f));

        LinearLayout heading = new LinearLayout(this);
        heading.setGravity(Gravity.CENTER_VERTICAL);
        message.addView(heading, new LinearLayout.LayoutParams(-1, -2));
        TextView label = text("HORA", 11, 0xFF6AE5CD, true);
        heading.addView(label, new LinearLayout.LayoutParams(0, -2, 1f));
        TextView clock = text(time, 32, 0xFFFFFFFF, true);
        clock.setGravity(Gravity.END);
        heading.addView(clock);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setVerticalScrollBarEnabled(true);
        LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(-1, 0, 1f);
        scrollParams.topMargin = dp(4);
        message.addView(scroll, scrollParams);
        TextView spoken = text(words, 20, 0xFFEDF8F7, false);
        spoken.setGravity(Gravity.CENTER_VERTICAL);
        spoken.setLineSpacing(dp(3), 1.05f);
        spoken.setAutoSizeTextTypeUniformWithConfiguration(12, 21, 1,
                TypedValue.COMPLEX_UNIT_SP);
        scroll.addView(spoken, new ScrollView.LayoutParams(-1, -1));

        Button close = new Button(this);
        close.setAllCaps(false);
        close.setText(preview ? "FECHAR DEMONSTRAÇÃO" : "DISPENSAR AVISO");
        close.setTextSize(11);
        close.setTextColor(0xFF07141B);
        close.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        close.setBackground(round(0xFF6AE5CD, 14));
        LinearLayout.LayoutParams closeParams = new LinearLayout.LayoutParams(-1, dp(38));
        closeParams.topMargin = dp(4);
        message.addView(close, closeParams);
        close.setOnClickListener(v -> finish());

        if (!preview) {
            IntentFilter filter = new IntentFilter(VoiceService.ACTION_FINISHED);
            if (Build.VERSION.SDK_INT >= 33)
                registerReceiver(voiceDone, filter, Context.RECEIVER_NOT_EXPORTED);
            else registerReceiver(voiceDone, filter);
            registered = true;
            handler.postDelayed(this::finish, 28_000L);
        }
    }

    /** Elementos meramente ilustrativos, nunca um anúncio clicável ou de rede. */
    private void drawMockAd(FrameLayout container) {
        int[] backgrounds = {0xFF132647, 0xFF301C40, 0xFF173833};
        int[] accents = {0xFF70B6FF, 0xFFFECE89, 0xFF92F2CB};
        String[] titles = {"Um mundo de ideias", "Momentos que inspiram", "A sua próxima descoberta"};
        String[] bodies = {
                "Esta área mostra como ficará o espaço publicitário.",
                "Pré-visualização fictícia para avaliar o design.",
                "Nenhum conteúdo é patrocinado nesta demonstração."
        };
        int n = (int) ((System.currentTimeMillis() / 86_400_000L) % 3);
        LinearLayout ad = new LinearLayout(this);
        ad.setOrientation(LinearLayout.VERTICAL);
        ad.setGravity(Gravity.CENTER);
        ad.setPadding(dp(22), dp(24), dp(22), dp(24));
        ad.setBackground(new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{backgrounds[n], 0xFF09111F}));
        container.addView(ad, new FrameLayout.LayoutParams(-1, -1));

        TextView tag = text("PUBLICIDADE • SIMULAÇÃO", 12, accents[n], true);
        tag.setGravity(Gravity.CENTER);
        ad.addView(tag);
        FrameLayout graphic = new FrameLayout(this);
        LinearLayout.LayoutParams artParams = new LinearLayout.LayoutParams(-1, 0, 1f);
        artParams.topMargin = dp(30);
        artParams.bottomMargin = dp(24);
        graphic.setBackground(round(backgrounds[n], 34));
        ad.addView(graphic, artParams);
        TextView symbol = text(n == 0 ? "✦" : n == 1 ? "◈" : "◎", 94, accents[n], true);
        symbol.setGravity(Gravity.CENTER);
        graphic.addView(symbol, new FrameLayout.LayoutParams(-1, -1));
        TextView headline = text(titles[n], 25, 0xFFFAFAFF, true);
        headline.setGravity(Gravity.CENTER);
        ad.addView(headline);
        TextView subtitle = text(bodies[n], 14, 0xFFD4DEEE, false);
        subtitle.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams bodyParams = new LinearLayout.LayoutParams(-1, -2);
        bodyParams.topMargin = dp(12);
        ad.addView(subtitle, bodyParams);
        TextView disclaimer = text("ESPAÇO RESERVADO • SEM ANÚNCIOS REAIS", 9, 0xFFA9BBCB, true);
        disclaimer.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams foot = new LinearLayout.LayoutParams(-1, -2);
        foot.topMargin = dp(26);
        ad.addView(disclaimer, foot);
    }

    private TextView text(String t, int sp, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(t);
        view.setTextColor(color);
        view.setTextSize(sp);
        if (bold) view.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return view;
    }
    private GradientDrawable round(int color, int r) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(r));
        return d;
    }
    private int dp(int i) { return Math.round(i * getResources().getDisplayMetrics().density); }
    @Override protected void onDestroy() {
        handler.removeCallbacksAndMessages(null);
        if (registered) unregisterReceiver(voiceDone);
        super.onDestroy();
    }
}
