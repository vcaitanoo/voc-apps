package pt.vcaitano.tradervision;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Execução sempre falha-fechada. Só aceita Chrome, rótulo Conta Demo no
 * conteúdo acessível e campos numéricos confirmados antes de tocar no botão.
 * Se o Chrome não expõe esses textos, NÃO opera (não tenta às cegas).
 */
public final class TapService extends AccessibilityService {
    public static volatile TapService INSTANCE;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final AtomicBoolean busy=new AtomicBoolean(false);
    private static final class Entry{
        final String text; final Rect bounds;
        Entry(String t,Rect r){text=t;bounds=r;}
    }
    @Override protected void onServiceConnected(){super.onServiceConnected();INSTANCE=this;}
    @Override public void onAccessibilityEvent(AccessibilityEvent e){}
    @Override public void onInterrupt(){}
    @Override public void onDestroy(){INSTANCE=null;super.onDestroy();}
    private void collect(AccessibilityNodeInfo node,List<Entry> found,int depth){
        if(node==null||depth>25||found.size()>2000)return;
        CharSequence cs=node.getText();
        if(cs==null||cs.length()==0)cs=node.getContentDescription();
        if(cs!=null&&cs.length()>0){
            Rect r=new Rect();node.getBoundsInScreen(r);
            found.add(new Entry(cs.toString().trim(),r));
        }
        for(int i=0;i<node.getChildCount();i++)collect(node.getChild(i),found,depth+1);
    }
    private List<Entry> read(){
        List<Entry> vals=new ArrayList<>();
        AccessibilityNodeInfo n=getRootInActiveWindow();
        if(n!=null)collect(n,vals,0);
        return vals;
    }
    private boolean demo(List<Entry> vals){
        boolean demo=false,button=false,real=false;
        for(Entry e:vals){
            String s=e.text.toLowerCase(Locale.ROOT);
            if(s.contains("conta demo")||s.contains("demo account"))demo=true;
            if(s.contains("conta real")||s.contains("real account"))real=true;
            if(s.equals("comprar")||s.equals("vender")||s.equals("buy")||s.equals("sell"))button=true;
        }
        return demo&&button&&!real;
    }
    private boolean isChrome(){
        AccessibilityNodeInfo node=getRootInActiveWindow();
        return node!=null&&"com.android.chrome".contentEquals(node.getPackageName());
    }
    private boolean haveStake(List<Entry> vals,int w,int h,double expected){
        for(Entry e:vals){
            double x=e.bounds.exactCenterX()/Math.max(1,w);
            double y=e.bounds.exactCenterY()/Math.max(1,h);
            if(x<.06||x>.49||y<.74||y>.97)continue;
            String text=e.text.replace("€","").replace(" ","").replace(',','.');
            try{if(Math.abs(Double.parseDouble(text)-expected)<.001)return true;}
            catch(Exception ignored){}
        }
        return false;
    }
    private boolean haveExpiry(List<Entry> vals,int w,int h,int expected){
        for(Entry e:vals){
            double x=e.bounds.exactCenterX()/Math.max(1,w);
            double y=e.bounds.exactCenterY()/Math.max(1,h);
            if(x<.52||x>.96||y<.74||y>.97)continue;
            String txt=e.text.toLowerCase(Locale.ROOT).trim();
            if(txt.matches("^"+expected+"\\s*(min|minutos|minute|minutes|m)$"))return true;
        }
        return false;
    }
    /**
     * Esta primeira candidata não modifica os valores por tentativa cega:
     * se o valor/tempo no Chrome não corresponderem ao esperado, aborta.
     */
    public void placeDemoTrade(boolean buy,int w,int h,int buyX,int buyY,int sellX,int sellY,
                               double stake,int expiry,Runnable onDone,java.util.function.Consumer<String> onFailure){
        if(!busy.compareAndSet(false,true)){onFailure.accept("Já existe gesto pendente");return;}
        main.post(()->{
            try{
                if(!isChrome()){fail("A Hezilex deve estar aberta no Chrome",onFailure);return;}
                List<Entry> vals=read();
                if(!demo(vals)){fail("Não foi possível validar CONTA DEMO e botões via acessibilidade",onFailure);return;}
                if(!haveStake(vals,w,h,stake)){fail("Valor da operação não confirmado. Defina manualmente "+stake+" e volte a observar",onFailure);return;}
                if(!haveExpiry(vals,w,h,expiry)){fail("Expiração não confirmada. Defina manualmente "+expiry+" min",onFailure);return;}
                final int x=buy?buyX:sellX,y=buy?buyY:sellY;
                if(x<0||x>=w||y<0||y>=h){fail("Coordenada fora da tela",onFailure);return;}
                Path path=new Path();path.moveTo(x,y);
                GestureDescription.Builder builder=new GestureDescription.Builder();
                builder.addStroke(new GestureDescription.StrokeDescription(path,0,80));
                boolean scheduled=dispatchGesture(builder.build(),new GestureResultCallback(){
                    @Override public void onCompleted(GestureDescription g){
                        busy.set(false);
                        // Isso confirma a conclusão do gesto, NÃO a aceitação da ordem.
                        onDone.run();
                    }
                    @Override public void onCancelled(GestureDescription g){
                        fail("Gesto cancelado pelo Android",onFailure);
                    }
                },main);
                if(!scheduled)fail("Android recusou o gesto",onFailure);
            }catch(Exception ex){fail("Erro ao analisar campos: "+ex.getMessage(),onFailure);}
        });
    }
    private void fail(String reason,java.util.function.Consumer<String> cb){
        busy.set(false);cb.accept(reason);
    }
}
