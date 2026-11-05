package pt.vcaitano.tradervision;
import java.util.ArrayList;
import java.util.List;

public final class VisualTradeVerifierTest {
    static void assertTrue(boolean b,String m){if(!b)throw new AssertionError(m);}
    static List<VisualTradeVerifier.Area> screen(String account,String stake,String expiry){
        List<VisualTradeVerifier.Area> a=new ArrayList<>();
        a.add(new VisualTradeVerifier.Area(account,15,215,168,240));
        a.add(new VisualTradeVerifier.Area(stake,274,1121,350,1155));
        a.add(new VisualTradeVerifier.Area(expiry,803,1121,880,1155));
        return a;
    }
    public static void main(String[] args){
        var yes=VisualTradeVerifier.evaluate(screen("Conta Demo","1,00","5 min"),1152,1320,1,5);
        assertTrue(yes.allowed(),"Full screenshot DEMO should pass");
        assertTrue(!VisualTradeVerifier.evaluate(screen("Conta Real","1,00","5 min"),1152,1320,1,5).allowed(),"Real account blocked");
        assertTrue(!VisualTradeVerifier.evaluate(screen("Conta Demo","3,00","5 min"),1152,1320,1,5).allowed(),"Wrong stake blocked");
        assertTrue(!VisualTradeVerifier.evaluate(screen("Conta Demo","1,00","2 min"),1152,1320,1,5).allowed(),"Wrong expiry blocked");
        assertTrue(!VisualTradeVerifier.evaluate(screen("","1,00","5 min"),1152,1320,1,5).allowed(),"Unknown account blocked");
        assertTrue(VisualTradeVerifier.amountEquals("Valor 1,00 €",1),"Decimal with label");
        assertTrue(!VisualTradeVerifier.amountEquals("Valor 10,00",1),"Avoid partial matches");
        assertTrue(VisualTradeVerifier.expiryEquals("5 minutos",5),"Minutes Portuguese");
        assertTrue(!VisualTradeVerifier.expiryEquals("15 min",5),"Avoid partial expiry match");
        var moved=screen("Conta Demo","1,00","5 min");
        moved.set(0,new VisualTradeVerifier.Area("Conta Demo",600,40,800,80));
        assertTrue(!VisualTradeVerifier.evaluate(moved,1152,1320,1,5).allowed(),"Text out of active account region is not enough");
        
        var account=screen("Conta Demo","1,00","5 min");
        account.add(new VisualTradeVerifier.Area("€ 32,05",20,245,175,280));
        account.add(new VisualTradeVerifier.Area("04:58",1040,520,1145,570));
        Double b=VisualTradeVerifier.demoBalance(account,1152,1320);
        assertTrue(b!=null&&Math.abs(b-32.05)<.0001,"read balance");
        Integer countdown=VisualTradeVerifier.candleRemainingSeconds(account,1152,1320);
        assertTrue(countdown!=null&&countdown==298,"read server candle countdown");
        account.set(0,new VisualTradeVerifier.Area("Conta Real",15,215,168,240));
        assertTrue(VisualTradeVerifier.demoBalance(account,1152,1320)==null,"reject real balance");
        System.out.println("VisualTradeVerifier tests passed");
    }
}
