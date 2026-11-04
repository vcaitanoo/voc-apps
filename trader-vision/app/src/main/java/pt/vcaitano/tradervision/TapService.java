package pt.vcaitano.tradervision;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.graphics.Rect;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * DEMO-only gesture executor. ML Kit verifies the *current screenshot* first,
 * because Hezilex renders part of its UI in a canvas that accessibility cannot read.
 * No text inferred from the image means NO TOUCH. Chrome must be active.
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
    private boolean isChrome(){
        AccessibilityNodeInfo node=getRootInActiveWindow();
        return node!=null&&node.getPackageName()!=null
          &&"com.android.chrome".contentEquals(node.getPackageName());
    }
    private boolean explicitRealAccountSelected(int w,int h){
        List<Entry> values=new ArrayList<>();
        AccessibilityNodeInfo root=getRootInActiveWindow();
        if(root!=null)collect(root,values,0);
        for(Entry item:values){
            String lower=item.text.toLowerCase(Locale.ROOT);
            double x=item.bounds.exactCenterX()/Math.max(1,w);
            double y=item.bounds.exactCenterY()/Math.max(1,h);
            if(x<.50&&y>.13&&y<.31
                &&(lower.contains("conta real")||lower.contains("real account")))return true;
        }
        return false;
    }
    public void placeDemoTrade(boolean buy,int w,int h,int buyX,int buyY,int sellX,int sellY,
                               VisualTradeVerifier.Check evidence,Runnable onGestureCompleted,
                               java.util.function.Consumer<String> onFailure){
        if(evidence==null||!evidence.allowed()){
            onFailure.accept(evidence==null?"OCR DEMO indisponível":evidence.reason);
            return;
        }
        if(!busy.compareAndSet(false,true)){
            onFailure.accept("Gesto anterior ainda em andamento");
            return;
        }
        main.post(()->{
            try {
                if(!isChrome()){
                    fail("O Chrome deve estar na frente para operar na Hezilex",onFailure);
                    return;
                }
                if(explicitRealAccountSelected(w,h)){
                    fail("CONTA REAL encontrada no Chrome. Entrada bloqueada.",onFailure);
                    return;
                }
                final int x=buy?buyX:sellX;
                final int y=buy?buyY:sellY;
                if(x<0||x>=w||y<(int)(h*.65)||y>=(int)(h*.88)){
                    fail("Botão fora da área esperada; não tocar",onFailure);
                    return;
                }
                Path path=new Path();path.moveTo(x,y);
                GestureDescription.Builder builder=new GestureDescription.Builder();
                builder.addStroke(new GestureDescription.StrokeDescription(path,0,90));
                boolean scheduled=dispatchGesture(builder.build(),new GestureResultCallback(){
                    @Override public void onCompleted(GestureDescription g){
                        busy.set(false);
                        // A callback confirma o gesto Android, NÃO a aceitação da ordem.
                        onGestureCompleted.run();
                    }
                    @Override public void onCancelled(GestureDescription g){
                        fail("Android cancelou o toque",onFailure);
                    }
                },main);
                if(!scheduled)fail("Android recusou enviar o toque",onFailure);
            }catch(Exception ex){
                fail("Falha na validação do gesto: "+ex.getClass().getSimpleName(),onFailure);
            }
        });
    }
    private void fail(String reason,java.util.function.Consumer<String> cb){
        busy.set(false);cb.accept(reason);
    }
}
