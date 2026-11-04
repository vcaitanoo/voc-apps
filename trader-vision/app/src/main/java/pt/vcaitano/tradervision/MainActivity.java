package pt.vcaitano.tradervision;

import android.Manifest;
import android.app.Activity;
import android.content.ComponentName;
import android.content.pm.PackageManager;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.Locale;

public final class MainActivity extends Activity {
    private static final int CAPTURE_REQUEST=77;
    private static final int NOTIFICATION_REQUEST=87;
    private boolean startupPermissions=true;
    private boolean askedAccessibility=false,askedOverlay=false,askedCapture=false,askedNotifications=false;
    private boolean externalSettingsPending=false,pausedForSettings=false;
    private SharedPreferences prefs;
    private LinearLayout root;
    private EditText balance,stake,risk,expiry,timeframe,score,minCandles,maxTrades;
    private CheckBox demo,automatic;
    private TextView status, managementInfo;

    static double getD(SharedPreferences p,String key,double def){
        try{return Double.parseDouble(p.getString(key,String.valueOf(def)).replace(',','.'));}
        catch(Exception e){return def;}
    }
    static int getI(SharedPreferences p,String key,int def){
        try{return Integer.parseInt(p.getString(key,String.valueOf(def)));}
        catch(Exception e){return def;}
    }
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        prefs=getSharedPreferences("vision",MODE_PRIVATE);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(14,22,34));
        root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(18),dp(18),dp(24));scroll.addView(root);setContentView(scroll);
        TextView title=label("VOC TRADER VISION",23,0xff72e6bd,true);root.addView(title);
        root.addView(label("V0.4.0 · Entrada DEMO · Hezilex no Chrome",13,0xffd0dae5,false));
        root.addView(label("O bot captura pixels do gráfico, aplica estratégias e somente pode tocar se tiver todos os controles verificados.",13,0xffa4b8cd,false));

        demo=new CheckBox(this);demo.setText("Estou usando CONTA DEMO na Hezilex");
        demo.setTextColor(Color.WHITE);demo.setChecked(prefs.getBoolean("demo",false));root.addView(demo);
        automatic=new CheckBox(this);automatic.setText("Autorizar cliques de entrada APENAS na demo");
        automatic.setTextColor(Color.WHITE);automatic.setChecked(prefs.getBoolean("auto",false));root.addView(automatic);

        balance=field("Saldo demo (€)", "balance","29.48",true);
        stake=field("Entrada calculada automaticamente (€)","stake","1.00",true);
        stake.setFocusable(false);
        stake.setClickable(false);
        risk=field("Risco máximo por operação (%)","risk","1",true);
        expiry=field("Expiração pretendida (minutos)","expiry","5",false);
        timeframe=field("Período de cada vela no gráfico (minutos)","tf","5",false);
        score=field("Nota técnica mínima para considerar entrada (0–100)","score","78",false);
        minCandles=field("Velas mínimas identificadas","candles","22",false);
        maxTrades=field("Máximo de entradas por dia","maxTrades","8",false);

        managementInfo=label("",12,0xffffce83,false);
        root.addView(managementInfo);
        android.text.TextWatcher watcher=new android.text.TextWatcher(){
            @Override public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            @Override public void onTextChanged(CharSequence s,int start,int before,int count){updateCalculatedStake();}
            @Override public void afterTextChanged(android.text.Editable e){}
        };
        balance.addTextChangedListener(watcher);
        risk.addTextChangedListener(watcher);
        updateCalculatedStake();
        Button save=button("GUARDAR CONFIGURAÇÃO",0xff236f8c);
        save.setOnClickListener(v->save());
        Button a11y=button("1. ATIVAR ACESSIBILIDADE",0xff36506c);root.addView(a11y);
        a11y.setOnClickListener(v->startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        Button overlay=button("2. PERMITIR PAINEL SOBRE OUTRAS APPS",0xff36506c);root.addView(overlay);
        overlay.setOnClickListener(v->{Intent i=new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,Uri.parse("package:"+getPackageName()));startActivity(i);});
        Button capture=button("3. AUTORIZAR CAPTURA E INICIAR",0xff168453);root.addView(capture);
        capture.setOnClickListener(v->requestCaptureConsent());
        Button browser=button("4. ABRIR HEZILEX NO CHROME",0xff287bbd);root.addView(browser);
        browser.setOnClickListener(v->{
            Intent i=new Intent(Intent.ACTION_VIEW,Uri.parse("https://app.hezilex.com/traderoom"));
            i.setPackage("com.android.chrome");
            try{startActivity(i);}catch(Exception e){i.setPackage(null);startActivity(i);}
        });
        // Configurações ficam embaixo das permissões e do acesso ao gráfico.
        root.addView(save);
        Button stop=button("PARAR CAPTURA E TOQUES",0xff9a3638);root.addView(stop);
        stop.setOnClickListener(v->{
            Intent i=new Intent(this,VisionService.class);i.setAction(VisionService.ACTION_STOP);
            startService(i);msg("Paragem solicitada");
        });
        root.addView(label("Resultados registrados manualmente (não estimados pelo gráfico)",14,0xffdbe7f4,true));
        Button win=button("MARCAR WIN",0xff147b58);root.addView(win);
        win.setOnClickListener(v->mark(true));
        Button loss=button("MARCAR LOSS",0xffa44343);root.addView(loss);
        loss.setOnClickListener(v->mark(false));
        status=label("",13,0xffffffff,false);root.addView(status);
        updateStatus();
    }
    private int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}
    private GradientDrawable bg(int color){
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(9));return d;
    }
    private TextView label(String text,int size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(text);t.setTextSize(size);t.setTextColor(color);
        t.setPadding(dp(3),dp(8),dp(3),dp(7));
        if(bold)t.setTypeface(null,Typeface.BOLD);return t;
    }
    private EditText field(String name,String key,String def,boolean decimal){
        root.addView(label(name,13,0xffc8d8e9,true));
        EditText e=new EditText(this);e.setSingleLine(true);
        e.setText(prefs.getString(key,def));e.setTextColor(Color.WHITE);
        e.setTextSize(16);e.setPadding(dp(12),dp(7),dp(12),dp(7));
        e.setInputType(InputType.TYPE_CLASS_NUMBER|(decimal?InputType.TYPE_NUMBER_FLAG_DECIMAL:0));
        e.setBackground(bg(0xff26384b));root.addView(e);
        return e;
    }
    private Button button(String txt,int color){
        Button b=new Button(this);b.setText(txt);b.setAllCaps(false);
        b.setTextColor(Color.WHITE);b.setBackground(bg(color));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(50));
        lp.topMargin=dp(9);b.setLayoutParams(lp);return b;
    }
    private void updateCalculatedStake(){
        if(balance==null||risk==null||stake==null||managementInfo==null)return;
        double saldo=parseNumber(balance.getText().toString());
        double percentual=parseNumber(risk.getText().toString());
        RiskManager.Plan plan=RiskManager.calculate(saldo,percentual);
        if(!plan.valid){
            stake.setText("0.00");
            managementInfo.setText("Informe saldo de pelo menos €1 e risco percentual válido. Nenhuma operação poderá ser executada.");
        } else {
            stake.setText(String.format(Locale.US,"%.2f",plan.stake));
            managementInfo.setText(String.format(Locale.US,
                "Gestão automática: mínimo Hezilex €1,00; alvo %.2f%%. Entrada €%.2f, risco efetivo %.2f%% da banca.%s\n"+
                "Na Hezilex, o campo Valor precisa coincidir com €%.2f; esta versão não altera o campo automaticamente.",
                percentual,plan.stake,plan.effectiveRiskPercent,
                plan.aboveTarget?" ATENÇÃO: o mínimo de €1 ultrapassa o risco alvo.":"",
                plan.stake));
        }
    }
    private static double parseNumber(String v){
        try{return Double.parseDouble(v.replace(',','.'));}
        catch(Exception e){return Double.NaN;}
    }
    private void save(){
        updateCalculatedStake();
        prefs.edit()
          .putString("balance",balance.getText().toString().replace(',','.'))
          .putString("stake",stake.getText().toString().replace(',','.'))
          .putString("risk",risk.getText().toString().replace(',','.'))
          .putString("expiry",expiry.getText().toString())
          .putString("tf",timeframe.getText().toString())
          .putString("score",score.getText().toString())
          .putString("candles",minCandles.getText().toString())
          .putString("maxTrades",maxTrades.getText().toString())
          .putBoolean("demo",demo.isChecked())
          .putBoolean("auto",automatic.isChecked())
          .apply();
        msg("Parâmetros guardados. Captura e automação são permissões separadas.");
        updateStatus();
    }
    private void mark(boolean win){
        String day=java.time.LocalDate.now().toString();
        if(!day.equals(prefs.getString("day","")))prefs.edit().putString("day",day).putInt("wins",0).putInt("losses",0).putInt("trades",0).apply();
        prefs.edit().putInt(win?"wins":"losses",prefs.getInt(win?"wins":"losses",0)+1).apply();
        updateStatus();
    }
    private void msg(String s){android.widget.Toast.makeText(this,s,android.widget.Toast.LENGTH_LONG).show();}
    private void updateStatus(){
        String day=java.time.LocalDate.now().toString();
        int w=day.equals(prefs.getString("day",""))?prefs.getInt("wins",0):0;
        int l=day.equals(prefs.getString("day",""))?prefs.getInt("losses",0):0;
        int t=day.equals(prefs.getString("day",""))?prefs.getInt("trades",0):0;
        if(status!=null)status.setText(String.format(Locale.US,
            "Operações tentadas hoje: %d | WIN: %d | LOSS: %d\n"+
            "Acessibilidade: %s | Captura: %s\n"+
            "Estado: fase experimental; execução real no dispositivo ainda não validada.",
            t,w,l,TapService.INSTANCE==null?"desligada":"ligada",
            VisionService.running?"ativa":"parada"));
    }
    private boolean accessibilityEnabled(){
        String list=Settings.Secure.getString(getContentResolver(),
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
        if(list==null)return false;
        String component=new ComponentName(this,TapService.class).flattenToString();
        return list.toLowerCase(Locale.ROOT).contains(component.toLowerCase(Locale.ROOT))
            ||TapService.INSTANCE!=null;
    }
    private void askStartupPermissions(){
        if(!startupPermissions||isFinishing()||externalSettingsPending)return;
        if(Build.VERSION.SDK_INT>=33
             &&checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED
             &&!askedNotifications){
            askedNotifications=true;
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},NOTIFICATION_REQUEST);
            return;
        }
        if(!Settings.canDrawOverlays(this)&&!askedOverlay){
            askedOverlay=true;
            externalSettingsPending=true;
            Intent overlaySettings=new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:"+getPackageName()));
            startActivity(overlaySettings);
            return;
        }
        if(!accessibilityEnabled()&&!askedAccessibility){
            askedAccessibility=true;
            externalSettingsPending=true;
            startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
            return;
        }
        // Android always requires an explicit user grant for each new capture.
        // Never start capturing or tapping before overlay/accessibility are ready.
        if(Settings.canDrawOverlays(this)&&accessibilityEnabled()
           &&!VisionService.running&&!askedCapture){
            askedCapture=true;
            requestCaptureConsent();
            return;
        }
        startupPermissions=false;
        updateStatus();
    }
    private void requestCaptureConsent(){
        if(!Settings.canDrawOverlays(this)){
            msg("Primeiro permita o painel sobre outros aplicativos.");
            return;
        }
        if(!accessibilityEnabled()){
            msg("Primeiro ative a acessibilidade do VOC Trader Vision.");
            return;
        }
        save();
        MediaProjectionManager manager=(MediaProjectionManager)
            getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        startActivityForResult(manager.createScreenCaptureIntent(),CAPTURE_REQUEST);
    }
    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] results){
        super.onRequestPermissionsResult(requestCode,permissions,results);
        if(requestCode==NOTIFICATION_REQUEST&&root!=null){
            root.postDelayed(this::askStartupPermissions,350L);
        }
    }
    @Override protected void onPause(){
        if(externalSettingsPending)pausedForSettings=true;
        super.onPause();
    }
    @Override protected void onResume(){
        super.onResume();
        if(externalSettingsPending && pausedForSettings){
            externalSettingsPending=false;
            pausedForSettings=false;
        }
        if(status!=null)updateStatus();
        if(root!=null&&startupPermissions)
            root.postDelayed(this::askStartupPermissions,550L);
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode==CAPTURE_REQUEST && resultCode==RESULT_OK && data!=null) {
            Intent svc=new Intent(this,VisionService.class);
            svc.setAction(VisionService.ACTION_START);
            svc.putExtra("resultCode",resultCode);
            svc.putExtra("captureData",data);
            try{startForegroundService(svc);msg("Captura autorizada. Abra a Hezilex na conta DEMO.");}
            catch(Exception e){msg("Falha ao iniciar captura: "+e.getMessage());}
        } else if(requestCode==CAPTURE_REQUEST)msg("Captura não autorizada.");
        if(requestCode==CAPTURE_REQUEST)startupPermissions=false;
    }
}
