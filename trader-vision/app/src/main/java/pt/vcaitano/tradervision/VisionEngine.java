package pt.vcaitano.tradervision;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/**
 * Motor matemático e visual 100% local. O preço é reconstruído em unidades de
 * pixel (invertidas). SEM OCR/DOM ele NÃO conhece preços financeiros exatos,
 * payout, candle timeframe, conta real/demo nem histórico fora do ecrã.
 * Sinais são hipóteses técnicas, não probabilidades de acerto.
 */
public final class VisionEngine {
    public static final class Candle {
        public final int x;
        public final double open, high, low, close;
        public Candle(int x, double open, double high, double low, double close) {
            this.x=x; this.open=open; this.high=high; this.low=low; this.close=close;
        }
        public boolean bull() { return close>open; }
        public double range() { return Math.max(0.01,high-low); }
        public double body() { return Math.abs(close-open); }
    }
    public static final class Result {
        public int bars, buyX, buyY, sellX, sellY, chartLeft, chartRight, chartTop, chartBottom;
        public boolean buttons;
        public String regime="SEM DADOS", strategy="Nenhuma", direction="AGUARDAR", detail="À espera de imagem";
        public int score;
        public int lastX;
        public double trend, rsi, adx, macd, atr;
        public final List<Candle> candles=new ArrayList<>();
        public String panel() {
            return "VOC TRADER VISION · DEMO\n"+
                "Velas visíveis: "+bars+" | Tela: "+(buttons?"OK":"NÃO CALIBRADA")+"\n"+
                "Mercado: "+regime+"\nEstratégia: "+strategy+"\n"+
                "Sinal: "+direction+" | Nota técnica "+score+"/100 (não é probabilidade)\n"+
                "RSI "+fmt(rsi)+"  ADX "+fmt(adx)+"  MACD "+fmt(macd)+"\n"+
                detail;
        }
        private static String fmt(double d) {return String.format(Locale.US,"%.1f",d);}
    }
    private VisionEngine() {}
    static boolean green(int p) {
        int r=(p>>>16)&255, g=(p>>>8)&255, b=p&255;
        return g>90 && g>r*1.40 && g>b*1.18 && r<165;
    }
    static boolean red(int p) {
        int r=(p>>>16)&255, g=(p>>>8)&255, b=p&255;
        return r>115 && r>g*1.36 && r>b*1.11 && g<170;
    }
    static boolean colored(int p) {return green(p)||red(p);}
    private static boolean masked(int x,int y,int[] box) {
        return box!=null&&box.length==4
            &&x>=box[0]&&x<=box[2]&&y>=box[1]&&y<=box[3];
    }
    private static int clamp(int a,int mn,int mx){return Math.max(mn,Math.min(mx,a));}

    public static Result analyze(int[] pixels,int w,int h,int minimumCandles) {
        return analyze(pixels,w,h,minimumCandles,null);
    }
    /**
     * The optional occlusion bounds are the real screen coordinates of our
     * floating overlay. Missing pixels behind that overlay are NEVER inferred.
     */
    public static Result analyze(int[] pixels,int w,int h,int minimumCandles,int[] occlusion) {
        Result out=new Result();
        if(pixels==null||w<250||h<350||pixels.length<w*h) {
            out.detail="Imagem inválida"; return out;
        }
        // Reconhece comprimentos reais dos botões, não memoriza coordenadas
        int bestY=-1,best=-1;
        for(int y=(int)(h*.58);y<(int)(h*.87);y+=3) {
            int ng=0,nr=0;
            for(int x=(int)(w*.04);x<(int)(w*.46);x+=6)if(green(pixels[y*w+x]))ng++;
            for(int x=(int)(w*.54);x<(int)(w*.96);x+=6)if(red(pixels[y*w+x]))nr++;
            int total=ng+nr;
            if(ng>0.42*w/6*.42 && nr>0.42*w/6*.42 && total>best){best=total;bestY=y;}
        }
        out.buttons=bestY>=0;
        out.buyY=out.sellY=bestY+(int)(h*.028);
        out.buyX=(int)(w*.255);out.sellX=(int)(w*.745);
        if(!out.buttons) {
            out.detail="Não achei simultaneamente Comprar e Vender; mantenha a Hezilex visível.";
            return out;
        }
        out.chartLeft=(int)(w*.074);
        out.chartRight=(int)(w*.89); // exclude price labels on the right
        out.chartTop=(int)(h*.34); // include high candles that V4 cropped
        out.chartBottom=clamp(bestY-(int)(h*.043),out.chartTop+40,h-1);
        if(out.chartBottom-out.chartTop<120) {
            out.detail="Área visível do gráfico muito pequena";return out;
        }

        // 1. Ignore our overlay and horizontal price lines. The V4
        // segmentation merged adjacent 5-minute candles across gaps of four
        // pixels, then rejected the merged group as too wide.
        int nX=out.chartRight-out.chartLeft+1;
        boolean[] priceLine=new boolean[h];
        int samples=(nX+1)/2;
        for(int y=out.chartTop;y<out.chartBottom;y++){
            int painted=0;
            for(int x=out.chartLeft;x<=out.chartRight;x+=2){
                if(!masked(x,y,occlusion)&&colored(pixels[y*w+x]))painted++;
            }
            priceLine[y]=painted>samples*.25; // horizontal ticker/price stripe
        }
        boolean[] active=new boolean[nX];
        for(int x=out.chartLeft;x<=out.chartRight;x++){
            int columnPixels=0;
            for(int y=out.chartTop;y<out.chartBottom;y++){
                if(!priceLine[y]&&!masked(x,y,occlusion)&&colored(pixels[y*w+x]))
                    columnPixels++;
            }
            active[x-out.chartLeft]=columnPixels>=3;
        }
        List<int[]> runs=new ArrayList<>();
        int start=-1;
        for(int i=0;i<=nX;i++){
            boolean on=i<nX&&active[i];
            if(on&&start<0)start=i;
            if(!on&&start>=0){
                runs.add(new int[]{start,i-1});
                start=-1;
            }
        }
        int maxBodyWidth=Math.max(24,w/24);
        for(int[] rr:runs){
            int x1=out.chartLeft+rr[0],x2=out.chartLeft+rr[1];
            int width=x2-x1+1;
            if(width>maxBodyWidth)continue; // horizontal stripe, banner, etc.
            int greenCount=0,redCount=0,ymin=out.chartBottom,ymax=out.chartTop;
            for(int x=x1;x<=x2;x++)for(int y=out.chartTop;y<out.chartBottom;y++){
                if(priceLine[y]||masked(x,y,occlusion))continue;
                int pixel=pixels[y*w+x];
                if(green(pixel)){
                    greenCount++;ymin=Math.min(ymin,y);ymax=Math.max(ymax,y);
                }else if(red(pixel)){
                    redCount++;ymin=Math.min(ymin,y);ymax=Math.max(ymax,y);
                }
            }
            if(Math.max(greenCount,redCount)<8||ymax-ymin<2)continue;
            boolean bull=greenCount>=redCount;
            int bodyTop=out.chartBottom,bodyBottom=out.chartTop;
            for(int y=ymin;y<=ymax;y++){
                if(priceLine[y])continue;
                int count=0;
                for(int x=x1;x<=x2;x++){
                    if(masked(x,y,occlusion))continue;
                    int pixel=pixels[y*w+x];
                    if(bull?green(pixel):red(pixel))count++;
                }
                if(count>=Math.max(1,(int)Math.ceil(width*.48))){
                    bodyTop=Math.min(bodyTop,y);
                    bodyBottom=Math.max(bodyBottom,y);
                }
            }
            if(bodyTop>bodyBottom)continue;
            double open=-(bull?bodyBottom:bodyTop);
            double close=-(bull?bodyTop:bodyBottom);
            out.candles.add(new Candle((x1+x2)/2,open,-ymin,-ymax,close));
        }
        out.candles.sort(Comparator.comparingInt(a->a.x));
        out.bars=out.candles.size();
        if(out.bars>0)out.lastX=out.candles.get(out.bars-1).x;
        if(out.bars<minimumCandles){
            out.detail="Detectadas "+out.bars+" velas reais de "+minimumCandles+
                " necessárias. Verifique painel sobre o gráfico e zoom.";
            return out;
        }
        evaluate(out);
        return out;
    }
    private static double ema(double[]a,int n,int end){
        if(a.length==0)return 0;
        end=Math.min(end,a.length-1);
        double e=a[0],k=2.0/(n+1);
        for(int i=1;i<=end;i++)e=e+(a[i]-e)*k;
        return e;
    }
    private static double rsi(double[] c,int end){
        if(end<15)return 50;
        double up=0,down=0;
        for(int i=Math.max(1,end-13);i<=end;i++){
            double d=c[i]-c[i-1];up+=Math.max(0,d);down+=Math.max(0,-d);
        }
        return down==0?100:(100-100/(1+up/down));
    }
    private static double atr(List<Candle> c,int end){
        int n=0; double s=0;
        for(int i=Math.max(1,end-13);i<=end;i++){
            Candle a=c.get(i),p=c.get(i-1);
            s+=Math.max(a.high-a.low,Math.max(Math.abs(a.high-p.close),Math.abs(a.low-p.close)));n++;
        }
        return s/Math.max(1,n);
    }
    private static double adx(List<Candle> c,int end){
        if(end<14)return 0;
        double plus=0,minus=0,tr=0;
        for(int i=Math.max(1,end-13);i<=end;i++){
            Candle a=c.get(i),p=c.get(i-1);
            double up=a.high-p.high,dn=p.low-a.low;
            if(up>dn&&up>0)plus+=up;
            if(dn>up&&dn>0)minus+=dn;
            tr+=Math.max(a.high-a.low,Math.max(Math.abs(a.high-p.close),Math.abs(a.low-p.close)));
        }
        double p=100*plus/Math.max(.01,tr),m=100*minus/Math.max(.01,tr);
        return 100*Math.abs(p-m)/Math.max(.01,p+m); // proxy DX; ADX real requer mais histórico
    }
    private static class Idea{
        final String name;final int dir;final int score;final String why;
        Idea(String n,int d,int s,String w){name=n;dir=d;score=s;why=w;}
    }
    private static void offer(List<Idea> ideas,String n,int d,int score,String why) {
        if(score>=55)ideas.add(new Idea(n,d,Math.min(score,99),why));
    }
    private static void evaluate(Result r){
        List<Candle> cs=r.candles; int end=cs.size()-2; // última vela ainda pode estar aberta
        if(end<18){r.detail="Aguardando velas fechadas";return;}
        Candle c=cs.get(end),p=cs.get(end-1); double[]close=new double[end+1];
        for(int i=0;i<=end;i++)close[i]=cs.get(i).close;
        double e9=ema(close,9,end),e21=ema(close,21,end),e50=ema(close,50,end);
        double e9prev=ema(close,9,end-1),e21prev=ema(close,21,end-1);
        double rsi=rsi(close,end), atr=atr(cs,end), dx=adx(cs,end);
        double macd=(ema(close,12,end)-ema(close,26,end));
        double macdPrev=(ema(close,12,end-1)-ema(close,26,end-1));
        double mean=0,var=0;
        int span=Math.min(20,end+1);
        for(int i=end-span+1;i<=end;i++)mean+=close[i]; mean/=span;
        for(int i=end-span+1;i<=end;i++)var+=Math.pow(close[i]-mean,2);
        double dev=Math.sqrt(var/span), upper=mean+2*dev,lower=mean-2*dev;
        double high=-1e20,low=1e20;int length=Math.min(20,end);
        for(int i=end-length;i<end;i++){high=Math.max(high,cs.get(i).high);low=Math.min(low,cs.get(i).low);}
        double vol=Math.max(1,atr),body=c.body(),range=c.range();
        int trend=(e9>e21 && e21>=e50)?1:((e9<e21 && e21<=e50)?-1:0);
        r.trend=e9-e21;r.rsi=rsi;r.adx=dx;r.macd=macd;r.atr=atr;
        r.regime=(dx>23&&trend!=0)?"TENDÊNCIA "+(trend>0?"ALTA":"BAIXA"):
            ((Math.abs(e9-e21)<vol*.30)?"LATERAL":"TRANSIÇÃO");
        List<Idea> ideas=new ArrayList<>();
        // 11 famílias de setup adaptativas com confluência; scores são NOTAS técnicas,
        // não resultados de backtest nem probabilidade estatística.
        if(trend!=0){
            boolean pull=trend>0? c.low<=e9+vol*.35&&c.close>e9 : c.high>=e9-vol*.35&&c.close<e9;
            if(pull&&dx>18&&rsi>30&&rsi<74)
                offer(ideas,"EMA 9/21 + pullback",trend,64+(dx>25?9:0)+(macd*trend>0?8:0),"Reteste da média rápida com tendência");
            if((e9-e9prev)*trend>0 && (e21-e21prev)*trend>=0 && macd*trend>0)
                offer(ideas,"Momentum + ADX",trend,54+(dx>25?14:0)+(c.body()>vol*.6?9:0),"Inclinação das médias e aceleração");
            if(macd*trend>0 && (macd-macdPrev)*trend>0 && dx>18)
                offer(ideas,"MACD + tendência",trend,62+(dx>26?10:0),"Impulso MACD na direção dominante");
            if(Math.abs(e21-e50)<vol*1.8 && c.close*trend>e50*trend)
                offer(ideas,"EMA 50 de contexto",trend,57+(dx>24?13:0),"Contexto de tendência e posição da EMA50");
            if((trend>0&&c.low<=e21&&c.close>e21)||
               (trend<0&&c.high>=e21&&c.close<e21))
                offer(ideas,"Reteste suporte/resistência EMA",trend,67+(dx>25?10:0),"Reteste e rejeição na média lenta");
        }
        if(c.close>high+vol*.10 && c.bull() && dx>20)
            offer(ideas,"Rompimento de máxima",1,67+(rsi<75?9:0),"Fechamento além da resistência visível");
        if(c.close<low-vol*.10 && !c.bull() && dx>20)
            offer(ideas,"Rompimento de mínima",-1,67+(rsi>25?9:0),"Fechamento além do suporte visível");
        if(c.close>upper && rsi>73 && c.close<c.open)
            offer(ideas,"Bollinger + RSI exaustão",-1,74,"Fora da banda superior + rejeição");
        if(c.close<lower && rsi<27 && c.close>c.open)
            offer(ideas,"Bollinger + RSI exaustão",1,74,"Fora da banda inferior + rejeição");
        if(c.bull()&&!p.bull()&&c.open<=p.close&&c.close>=p.open&&c.body()>vol*.25)
            offer(ideas,"Engolfo de alta",1,60+(rsi<65?11:0)+(trend>=0?9:0),"Corpo anterior engolido");
        if(!c.bull()&&p.bull()&&c.open>=p.close&&c.close<=p.open&&c.body()>vol*.25)
            offer(ideas,"Engolfo de baixa",-1,60+(rsi>35?11:0)+(trend<=0?9:0),"Corpo anterior engolido");
        double lowerWick=Math.min(c.open,c.close)-c.low,upperWick=c.high-Math.max(c.open,c.close);
        if(lowerWick>body*2.2&&lowerWick>upperWick*1.8&&c.low<low+vol*.6)
            offer(ideas,"Pin bar no suporte",1,69+(rsi<45?10:0),"Pavio inferior com rejeição");
        if(upperWick>body*2.2&&upperWick>lowerWick*1.8&&c.high>high-vol*.6)
            offer(ideas,"Pin bar na resistência",-1,69+(rsi>55?10:0),"Pavio superior com rejeição");
        if(dx<21 && span>=20){
            if(c.low<low+vol*.4&&c.bull()&&rsi<43)
                offer(ideas,"Canal lateral: suporte",1,63,"Reversão na parte inferior do canal");
            if(c.high>high-vol*.4&&!c.bull()&&rsi>57)
                offer(ideas,"Canal lateral: resistência",-1,63,"Reversão na parte superior do canal");
        }
        if(c.high>high&&c.close<high-vol*.05&&!c.bull())
            offer(ideas,"Falso rompimento superior",-1,74,"Máxima rejeitada e preço volta ao canal");
        if(c.low<low&&c.close>low+vol*.05&&c.bull())
            offer(ideas,"Falso rompimento inferior",1,74,"Mínima rejeitada e preço volta ao canal");
        // Evita sinais contra fluxo sem evidência forte. Confluência é obrigatória.
        Idea best=null;int votes=0;
        for(Idea a:ideas){
            int score=a.score;
            if(trend!=0&&a.dir==trend)score+=5;
            if(rsi>79&&a.dir==1)score-=12;
            if(rsi<21&&a.dir==-1)score-=12;
            if(score<68)continue;
            int confirm=0;
            for(Idea b:ideas)if(b.dir==a.dir&&b!=a&&b.score>=55)confirm++;
            if(confirm<1)continue;
            score=Math.min(99,score+Math.min(10,confirm*3));
            if(best==null||score>best.score){best=new Idea(a.name,a.dir,score,a.why);votes=confirm;}
        }
        if(best==null){r.detail="Nenhuma configuração com 2 confirmações independentes";return;}
        r.strategy=best.name;r.direction=best.dir==1?"COMPRAR":"VENDER";
        r.score=best.score;
        r.detail=best.why+" · "+(votes+1)+" setups concordantes. Aguardar fecho de vela.";
    }
}
