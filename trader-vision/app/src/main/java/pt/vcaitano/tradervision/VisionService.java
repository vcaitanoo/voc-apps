package pt.vcaitano.tradervision;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.os.SystemClock;
import android.util.DisplayMetrics;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.nio.ByteBuffer;
import java.time.LocalDate;
import java.util.Locale;
import java.util.ArrayList;
import java.util.List;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import java.util.concurrent.atomic.AtomicBoolean;

/** Serviço de captura autorizado por MediaProjection. Nunca executa em conta real. */
public final class VisionService extends Service {
    public static final String ACTION_START="pt.vcaitano.vision.START";
    public static final String ACTION_STOP="pt.vcaitano.vision.STOP";
    public static volatile boolean running=false;
    private static final int NOTIFICATION_ID=909;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private MediaProjection projection;
    private VirtualDisplay display;
    private ImageReader reader;
    private HandlerThread workerThread;
    private Handler worker;
    private WindowManager windows;
    private LinearLayout overlay;
    private WindowManager.LayoutParams overlayParams;
    private TextView text;
    private PowerManager.WakeLock wake;
    private TextRecognizer textRecognizer;
    private final AtomicBoolean visualVerificationPending=new AtomicBoolean(false);
    private long lastVerificationFailureElapsedMs=-1L;
    private int width,height,density;
    private long lastFrame=0,lastAttemptElapsedMs=-1L;
    private volatile String lastGestureMessage="";
    private volatile long lastGestureMessageUntilMs=0L;
    private String previousSignal="";
    private int stability=0;
    private volatile boolean disposing=false;
    private final AtomicBoolean processing=new AtomicBoolean(false);

    @Override public IBinder onBind(Intent i){return null;}
    @Override public int onStartCommand(Intent intent,int flags,int startId){
        if(intent==null)return START_NOT_STICKY;
        if(ACTION_STOP.equals(intent.getAction())){stopSelf();return START_NOT_STICKY;}
        if(!ACTION_START.equals(intent.getAction())||running)return START_NOT_STICKY;
        ensureForeground();
        try{
            int resultCode=intent.getIntExtra("resultCode",0);
            Intent data=Build.VERSION.SDK_INT>=33?
                intent.getParcelableExtra("captureData",Intent.class):
                (Intent)intent.getParcelableExtra("captureData");
            if(resultCode==0||data==null)throw new IllegalStateException("Captura não concedida");
            MediaProjectionManager mgr=(MediaProjectionManager)getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            projection=mgr.getMediaProjection(resultCode,data);
            if(projection==null)throw new IllegalStateException("MediaProjection indisponível");
            projection.registerCallback(new MediaProjection.Callback(){
                @Override public void onStop(){stopSelf();}
            },ui);
            DisplayMetrics dm=new DisplayMetrics();
            ((WindowManager)getSystemService(WINDOW_SERVICE)).getDefaultDisplay().getRealMetrics(dm);
            width=dm.widthPixels;height=dm.heightPixels;density=dm.densityDpi;
            workerThread=new HandlerThread("VisionPixels");workerThread.start();
            worker=new Handler(workerThread.getLooper());
            reader=ImageReader.newInstance(width,height,PixelFormat.RGBA_8888,2);
            reader.setOnImageAvailableListener(this::consume,worker);
            display=projection.createVirtualDisplay("VOC Vision DEMO",width,height,density,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,reader.getSurface(),null,worker);
            textRecognizer=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
            running=true;createOverlay();keepScreenOn();
        }catch(Exception e){
            android.util.Log.e("VOCVision","Captura falhou",e);
            stopSelf();
        }
        return START_NOT_STICKY;
    }
    private void ensureForeground(){
        NotificationManager nm=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        nm.createNotificationChannel(new NotificationChannel("vision","VOC Vision DEMO",NotificationManager.IMPORTANCE_LOW));
        Intent launch=new Intent(this,MainActivity.class);
        PendingIntent open=PendingIntent.getActivity(this,0,launch,PendingIntent.FLAG_IMMUTABLE|PendingIntent.FLAG_UPDATE_CURRENT);
        Notification n=new Notification.Builder(this,"vision")
          .setSmallIcon(R.drawable.ic_launcher)
          .setContentTitle("VOC Trader Vision · DEMO")
          .setContentText("Leitura de tela ativa. Toques apenas com autorização e validação.")
          .setOngoing(true).setContentIntent(open).build();
        if(Build.VERSION.SDK_INT>=29)
            startForeground(NOTIFICATION_ID,n,ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
        else startForeground(NOTIFICATION_ID,n);
    }
    private void keepScreenOn(){
        try{
            PowerManager pm=(PowerManager)getSystemService(POWER_SERVICE);
            wake=pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK,"vocvision:monitor");
            wake.acquire();
        }catch(Exception e){android.util.Log.w("VOCVision","WakeLock não disponível",e);}
    }
    private void createOverlay(){
        windows=(WindowManager)getSystemService(WINDOW_SERVICE);
        overlay=new LinearLayout(this);overlay.setOrientation(LinearLayout.VERTICAL);
        overlay.setPadding(dp(9),dp(8),dp(9),dp(7));
        overlay.setBackgroundColor(0xee172233);
        TextView dragHandle=new TextView(this);
        dragHandle.setText("↕ ARRASTE PARA MOVER");
        dragHandle.setTextColor(0xff70e6bd);
        dragHandle.setTextSize(12);
        dragHandle.setTypeface(null,android.graphics.Typeface.BOLD);
        dragHandle.setPadding(dp(4),dp(3),dp(4),dp(7));
        dragHandle.setContentDescription("Toque e arraste para mover o painel do robô");
        overlay.addView(dragHandle);
        text=new TextView(this);text.setTextColor(Color.WHITE);text.setTextSize(10);
        text.setText("VOC Trader Vision · DEMO\nCaptura iniciada. Abra Hezilex no Chrome.");
        overlay.addView(text);
        Button stop=new Button(this);stop.setText("PARAR ROBÔ");stop.setAllCaps(false);
        stop.setTextColor(Color.WHITE);stop.setTextSize(11);stop.setBackgroundColor(0xffa53b40);
        stop.setOnClickListener(v->stopSelf());overlay.addView(stop);
        WindowManager.LayoutParams lp=new WindowManager.LayoutParams(
          dp(252),WindowManager.LayoutParams.WRAP_CONTENT,
          WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
          WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE|
          WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL|
          WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
          PixelFormat.TRANSLUCENT);
        lp.gravity=Gravity.TOP|Gravity.LEFT;lp.x=dp(4);lp.y=dp(42);
        overlayParams=lp;
        installPanelDrag(dragHandle);
        installPanelDrag(text);
        windows.addView(overlay,lp);
        // A posição é salva como fração da área disponível: mantém-se
        // acessível após mudança da altura do painel ou do tamanho da tela.
        overlay.post(()->{
            if(disposing||overlay==null||windows==null)return;
            SharedPreferences prefs=getSharedPreferences("vision",MODE_PRIVATE);
            float rx=prefs.getFloat("panel_x_ratio",-1f);
            float ry=prefs.getFloat("panel_y_ratio",-1f);
            if(rx>=0f||ry>=0f){
                lp.x=PanelPosition.restore(rx,availableWidth(),dp(4));
                lp.y=PanelPosition.restore(ry,availableHeight(),dp(42));
                windows.updateViewLayout(overlay,lp);
            }
        });
    }
    private int availableWidth(){
        return Math.max(0,width-(overlay==null?dp(252):overlay.getWidth()));
    }
    private int availableHeight(){
        return Math.max(0,height-dp(28)-(overlay==null?0:overlay.getHeight()));
    }
    private void installPanelDrag(View handle){
        final float[] originRaw=new float[2];
        final int[] originXY=new int[2];
        handle.setOnTouchListener((v,event)->{
            if(overlay==null||overlayParams==null||windows==null)return false;
            switch(event.getActionMasked()){
                case MotionEvent.ACTION_DOWN:
                    originRaw[0]=event.getRawX();
                    originRaw[1]=event.getRawY();
                    originXY[0]=overlayParams.x;
                    originXY[1]=overlayParams.y;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    overlayParams.x=PanelPosition.move(originXY[0],
                        event.getRawX()-originRaw[0],availableWidth());
                    overlayParams.y=PanelPosition.move(originXY[1],
                        event.getRawY()-originRaw[1],availableHeight());
                    windows.updateViewLayout(overlay,overlayParams);
                    return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    getSharedPreferences("vision",MODE_PRIVATE).edit()
                        .putFloat("panel_x_ratio",PanelPosition.fraction(
                            overlayParams.x,availableWidth()))
                        .putFloat("panel_y_ratio",PanelPosition.fraction(
                            overlayParams.y,availableHeight()))
                        .apply();
                    return true;
                default:return false;
            }
        });
    }
    private int dp(int v){return (int)(getResources().getDisplayMetrics().density*v+.5f);}
    private void consume(ImageReader ir){
        Image im=null;
        try{
            im=ir.acquireLatestImage();
            if(im==null)return;
            long now=System.currentTimeMillis();
            if(now-lastFrame<1100||!processing.compareAndSet(false,true))return;
            lastFrame=now;
            Image.Plane plane=im.getPlanes()[0];
            ByteBuffer buffer=plane.getBuffer();
            int stride=plane.getRowStride(),pixelStride=plane.getPixelStride();
            if(pixelStride!=4||stride<width*4)return;
            int padded=stride/4;
            Bitmap whole=Bitmap.createBitmap(padded,height,Bitmap.Config.ARGB_8888);
            buffer.rewind();whole.copyPixelsFromBuffer(buffer);
            int[] argb=new int[width*height];
            whole.getPixels(argb,0,width,0,0,width,height);whole.recycle();
            SharedPreferences p=getSharedPreferences("vision",MODE_PRIVATE);
            int minBars=Math.max(18,Math.min(100,MainActivity.getI(p,"candles",22)));
            VisionEngine.Result r=VisionEngine.analyze(argb,width,height,minBars);
            int minScore=Math.max(60,Math.min(99,MainActivity.getI(p,"score",78)));
            evaluateSignal(r,minScore,p,argb);
        }catch(Throwable ex){android.util.Log.w("VOCVision","Falha leitura",ex);}
        finally{
            if(im!=null)im.close();
            processing.set(false);
        }
    }
    private void evaluateSignal(VisionEngine.Result r,int minScore,SharedPreferences p,int[] pixels){
        String reason="";
        double balance=MainActivity.getD(p,"balance",29.48);
        double risk=MainActivity.getD(p,"risk",1);
        RiskManager.Plan plan=RiskManager.calculate(balance,risk);
        double stake=plan.stake;
        boolean auto=p.getBoolean("auto",false),demo=p.getBoolean("demo",false);
        boolean hasSignal=(r.direction.equals("COMPRAR")||r.direction.equals("VENDER"))&&r.score>=minScore;
        String sig=hasSignal?r.direction+"|"+r.strategy:"";
        if(!sig.isEmpty()&&sig.equals(previousSignal))stability++;else stability=0;
        previousSignal=sig;

        if(!auto)reason="OBSERVAÇÃO: cliques desativados";
        else if(!demo)reason="BLOQUEADO: confirme CONTA DEMO";
        else if(!r.buttons)reason="BLOQUEADO: botões não identificados";
        else if(!hasSignal)reason="Aguardando nota mínima "+minScore;
        else {
            int expiry=MainActivity.getI(p,"expiry",5);
            int timeframe=MainActivity.getI(p,"tf",5);
            int max=MainActivity.getI(p,"maxTrades",8);
            String today=LocalDate.now().toString();
            if(!today.equals(p.getString("day",""))){
                p.edit().putString("day",today).putInt("trades",0)
                    .putInt("wins",0).putInt("losses",0).apply();
            }
            int count=p.getInt("trades",0),losses=p.getInt("losses",0);
            long elapsed=lastAttemptElapsedMs<0?-1L:SystemClock.elapsedRealtime()-lastAttemptElapsedMs;
            EntryTiming.Decision timing=EntryTiming.evaluate(stability,elapsed,timeframe,expiry);
            if(!plan.valid)reason="BLOQUEADO: saldo inferior a €1 ou risco configurado inválido";
            else if(count>=max)reason="Limite diário de operações";
            else if(losses>=3)reason="Limite de 3 perdas apontadas hoje";
            else if(!timing.allowed)reason=timing.message;
            else if(TapService.INSTANCE==null)reason="Ative o serviço de acessibilidade";
            else if(visualVerificationPending.get())reason="Verificando conta DEMO e campos no ecrã...";
            else if(lastVerificationFailureElapsedMs>=0
                 &&SystemClock.elapsedRealtime()-lastVerificationFailureElapsedMs<10000L)
                reason="Reverificando em "+((10000L-
                    (SystemClock.elapsedRealtime()-lastVerificationFailureElapsedMs)+999L)/1000L)+
                    "s: "+lastGestureMessage;
            else {
                // Não iniciar cooldown antes da resposta do Android. Capturas,
                // gestos recusados e falhas de OCR não contam como operação.
                verifyAndPlaceDemoTrade(r,p,pixels,stake,expiry);
                reason="Lendo Conta Demo, Valor e Expiração (OCR)...";
            }
        }
        String gestao=plan.valid?String.format(Locale.US,
            "GESTÃO €%.2f | efetivo %.2f%% | alvo %.2f%%%s",
            plan.stake,plan.effectiveRiskPercent,risk,
            plan.aboveTarget?" (mínimo obrigatório)":""):
            "GESTÃO: saldo/risco inválido";
        String display=r.panel()+"\n"+gestao+"\n"+
            "TENTATIVAS "+p.getInt("trades",0)+" · WIN "+p.getInt("wins",0)+
            " · LOSS "+p.getInt("losses",0)+"\n"+reason;
        if(SystemClock.elapsedRealtime()<lastGestureMessageUntilMs&&!lastGestureMessage.isEmpty())
            display+="\n"+lastGestureMessage;
        if(!reason.startsWith("Verificando campos"))setPanel(display);
    }

    private void verifyAndPlaceDemoTrade(VisionEngine.Result result,
                                          SharedPreferences prefs,int[] pixels,
                                          double stake,int expiry){
        if(!visualVerificationPending.compareAndSet(false,true))return;
        final Bitmap screenshot;
        try {
            screenshot=Bitmap.createBitmap(pixels,width,height,Bitmap.Config.ARGB_8888);
        } catch(Exception ex) {
            visualVerificationPending.set(false);
            rejectVerification("Falha ao preparar imagem para OCR");
            return;
        }
        if(textRecognizer==null){
            screenshot.recycle();
            visualVerificationPending.set(false);
            rejectVerification("Leitor visual ainda não iniciado");
            return;
        }
        textRecognizer.process(InputImage.fromBitmap(screenshot,0))
          .addOnSuccessListener(words->{
              if(disposing||!running)return;
              List<VisualTradeVerifier.Area> areas=new ArrayList<>();
              for(Text.TextBlock block:words.getTextBlocks()){
                  Rect br=block.getBoundingBox();
                  if(br!=null)areas.add(new VisualTradeVerifier.Area(
                      block.getText(),br.left,br.top,br.right,br.bottom));
                  for(Text.Line line:block.getLines()){
                      Rect lr=line.getBoundingBox();
                      if(lr!=null)areas.add(new VisualTradeVerifier.Area(
                          line.getText(),lr.left,lr.top,lr.right,lr.bottom));
                  }
              }
              VisualTradeVerifier.Check verified=VisualTradeVerifier.evaluate(
                  areas,width,height,stake,expiry);
              if(!verified.allowed()){
                  rejectVerification(verified.reason);
                  return;
              }
              // A análise pode mudar durante o OCR; só autorizar o sinal
              // que estava estável quando a imagem foi capturada.
              TapService tap=TapService.INSTANCE;
              if(tap==null){rejectVerification("Acessibilidade não está ativa");return;}
              boolean buy=result.direction.equals("COMPRAR");
              tap.placeDemoTrade(buy,width,height,result.buyX,result.buyY,
                result.sellX,result.sellY,verified,
                ()->{
                    lastAttemptElapsedMs=SystemClock.elapsedRealtime();
                    lastVerificationFailureElapsedMs=-1L;
                    int count=prefs.getInt("trades",0);
                    prefs.edit().putInt("trades",count+1).apply();
                    reportGesture("TOQUE "+(buy?"COMPRAR":"VENDER")+
                        " enviado ao Android. Verifique no histórico da Hezilex"+
                        " se a ordem DEMO foi realmente aceite.");
                },
                this::rejectVerification);
          })
          .addOnFailureListener(err->
              rejectVerification("OCR indisponível: "+err.getClass().getSimpleName()))
          .addOnCompleteListener(task->{
              screenshot.recycle();
              visualVerificationPending.set(false);
          });
    }
    private void rejectVerification(String reason){
        lastVerificationFailureElapsedMs=SystemClock.elapsedRealtime();
        reportGesture("SEM ENTRADA: "+reason);
    }
    private void reportGesture(String message){
        lastGestureMessage=message;
        lastGestureMessageUntilMs=SystemClock.elapsedRealtime()+30000L;
        setPanel(message);
    }
    private void setPanel(String s){ui.post(()->{if(!disposing&&text!=null)text.setText(s);});}
    @Override public void onDestroy(){
        disposing=true;running=false;
        if(reader!=null){try{reader.setOnImageAvailableListener(null,null);reader.close();}catch(Exception ignored){}reader=null;}
        if(display!=null){display.release();display=null;}
        if(projection!=null){try{projection.stop();}catch(Exception ignored){}projection=null;}
        if(workerThread!=null){workerThread.quitSafely();workerThread=null;}
        if(overlay!=null&&windows!=null){try{windows.removeViewImmediate(overlay);}catch(Exception ignored){}overlay=null;overlayParams=null;}
        if(wake!=null&&wake.isHeld()){wake.release();wake=null;}
        if(textRecognizer!=null){textRecognizer.close();textRecognizer=null;}
        super.onDestroy();
    }
}
