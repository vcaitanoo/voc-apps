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
