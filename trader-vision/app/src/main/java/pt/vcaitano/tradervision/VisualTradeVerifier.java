package pt.vcaitano.tradervision;

import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Checks OCR evidence against screen regions before any automated DEMO order.
 * No confidence score, color or user checkbox can substitute for an active DEMO label.
 */
public final class VisualTradeVerifier {
    private VisualTradeVerifier() {}
    public static final class Area {
        public final String text;
        public final int left, top, right, bottom;
        public Area(String text,int left,int top,int right,int bottom) {
            this.text=text==null?"":text;
            this.left=left;this.top=top;this.right=right;this.bottom=bottom;
        }
    }
    public static final class Check {
        public final boolean demo, real, stake, expiry;
        public final String reason;
        Check(boolean demo,boolean real,boolean stake,boolean expiry,String reason) {
            this.demo=demo;this.real=real;this.stake=stake;this.expiry=expiry;this.reason=reason;
        }
        public boolean allowed() { return demo&&!real&&stake&&expiry; }
    }
    private static final Pattern NUMBER=Pattern.compile("(?<![0-9])([0-9]{1,6}(?:[.,][0-9]{1,2})?)(?![0-9])");
    public static boolean amountEquals(String text,double expected) {
        if(!Double.isFinite(expected)||expected<1)return false;
        Matcher m=NUMBER.matcher(text==null?"":text);
        while(m.find()) {
            try {
                if(Math.abs(Double.parseDouble(m.group(1).replace(',','.'))-expected)<0.005)return true;
            }catch(NumberFormatException ignored){}
        }
        return false;
    }
    public static boolean expiryEquals(String text,int expected) {
        if(expected<1||expected>120||text==null)return false;
        String s=text.toLowerCase(Locale.ROOT).replaceAll("\\s+"," ").trim();
        String regex="(?:^|[^0-9])"+expected+"\\s*(?:min|minutos|mins|minutes|m)(?:$|[^a-z])";
        return Pattern.compile(regex).matcher(s).find();
    }
    private static final Pattern COUNTDOWN=Pattern.compile("(?<![0-9])([0-9]{1,2}):([0-5][0-9])(?![0-9])");
    private static final Pattern EURO=Pattern.compile("(?:€\\s*)([0-9]{1,6}[,.][0-9]{2})(?![0-9])");
    /**
     * Extracts only the active DEMO account balance from top-left of the
     * Hezilex screen. Never use chart price or trade amount as balance.
     * Returns null if the selected account cannot be proved DEMO.
     */
    public static Double demoBalance(List<Area> items,int w,int h) {
        if(items==null||w<=0||h<=0)return null;
        boolean demo=false,real=false;
        Double balance=null;
        for(Area a:items) {
            if(a==null)continue;
            double x=(a.left+a.right)*.5/w,y=(a.top+a.bottom)*.5/h;
            if(x<0||x>.46||y<.13||y>.32)continue;
            String t=a.text.toLowerCase(Locale.ROOT);
            if(t.contains("conta real")||t.contains("real account"))real=true;
            if(t.contains("conta demo")||t.contains("demo account"))demo=true;
            Matcher m=EURO.matcher(t);
            if(m.find()){
                try {
                    double val=Double.parseDouble(m.group(1).replace(',','.'));
                    if(Double.isFinite(val)&&val>=0&&val<1000000)balance=val;
                } catch(NumberFormatException ignored){}
            }
        }
        return demo&&!real?balance:null;
    }
    /** Countdown inside the live chart PRICE badge at right, not expiry selector. */
    public static Integer candleRemainingSeconds(List<Area> items,int w,int h) {
        if(items==null||w<=0||h<=0)return null;
        for(Area a:items) {
            if(a==null)continue;
            double x=(a.left+a.right)*.5/w,y=(a.top+a.bottom)*.5/h;
            if(x<.84||x>.995||y<.30||y>.75)continue;
            Matcher m=COUNTDOWN.matcher(a.text);
            if(m.find()){
                try {return Integer.parseInt(m.group(1))*60+Integer.parseInt(m.group(2));}
                catch(NumberFormatException ignored){}
            }
        }
        return null;
    }
    public static Check evaluate(List<Area> items,int screenW,int screenH,
                                 double expectedStake,int expectedExpiry) {
        if(items==null||screenW<200||screenH<300)
            return new Check(false,false,false,false,"OCR: imagem indisponível");
        boolean demo=false,real=false,stake=false,expiry=false;
        for(Area area:items) {
            if(area==null)continue;
            double x=(area.left+area.right)*.5/screenW;
            double y=(area.top+area.bottom)*.5/screenH;
            String t=area.text.toLowerCase(Locale.ROOT).replaceAll("\\s+"," ").trim();
            // Only the currently selected account label (not inactive account menu entries).
            if(x>=0.00&&x<0.50&&y>0.13&&y<0.31) {
                if(t.contains("conta demo")||t.contains("demo account"))demo=true;
                if(t.contains("conta real")||t.contains("real account"))real=true;
            }
            // Only the stake and expiry controls under Compra/Venda.
            if(x>0.12&&x<0.50&&y>0.81&&y<0.94&&amountEquals(t,expectedStake))stake=true;
            if(x>0.53&&x<0.96&&y>0.81&&y<0.94&&expiryEquals(t,expectedExpiry))expiry=true;
        }
        String reason;
        if(real)reason="BLOQUEADO: CONTA REAL detectada. Somente DEMO.";
        else if(!demo)reason="BLOQUEADO: OCR não confirmou 'Conta Demo' visível.";
        else if(!stake)reason=String.format(Locale.US,
            "BLOQUEADO: valor €%.2f não reconhecido no campo da Hezilex.",expectedStake);
        else if(!expiry)reason="BLOQUEADO: expiração "+expectedExpiry+" min não reconhecida.";
        else reason="OCR: conta DEMO, valor e expiração confirmados";
        return new Check(demo,real,stake,expiry,reason);
    }
}
