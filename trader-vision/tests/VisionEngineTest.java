package pt.vcaitano.tradervision;
public final class VisionEngineTest {
 static final int W=1000,H=1400;
 static final int GREEN=0xff00c48b,RED=0xfff34d5e,DARK=0xff111625;
 static void fill(int[] a,int x1,int y1,int x2,int y2,int color) {
  for(int y=Math.max(0,y1);y<=Math.min(H-1,y2);y++)
   for(int x=Math.max(0,x1);x<=Math.min(W-1,x2);x++)a[y*W+x]=color;
 }
 static int[] frame(){
  int[] pixels=new int[W*H];java.util.Arrays.fill(pixels,DARK);
  fill(pixels,20,1010,480,1080,GREEN);
  fill(pixels,520,1010,980,1080,RED);
  // 38 narrow candlesticks with 2-pixel gaps
  for(int i=0;i<38;i++){
    int x=80+i*19;
    int y=700+(i%7-3)*12;
    int c=i%3==0?RED:GREEN;
    fill(pixels,x+6,y-17,x+6,y+38,c);
    fill(pixels,x,y,x+13,y+19,c);
  }
  // Price stripe that previously merged candles into a giant bar
  fill(pixels,76,835,879,835,RED);
  // A bright red moving overlay must not be interpreted as candles
  fill(pixels,240,500,560,580,RED);
  return pixels;
 }
 static void check(boolean b,String msg){if(!b)throw new AssertionError(msg);}
 public static void main(String[]args){
  int[] pixels=frame();
  VisionEngine.Result r=VisionEngine.analyze(pixels,W,H,22,new int[]{235,495,565,585});
  check(r.buttons,"expected buy/sell buttons");
  check(r.buyY>=1010&&r.buyY<=1080,
      "tap must be calibrated INSIDE the colored button: "+r.buyY);
  check(r.bars>=34,"missed narrow candles: "+r.bars);
  check(r.bars<=42,"false positives: "+r.bars);
  check(!r.regime.equals("SEM DADOS"),"should analyze enough candles");

  // Regressão relatada em 41100.jpg: o usuário arrastou o painel sobre
  // o botão VENDER. VC5 retornava do motor com ZERO velas e SEM DADOS.
  int[] covered=frame();
  fill(covered,575,930,980,1320,DARK);
  int[] movingPanel={570,925,985,1325};
  VisionEngine.Result blocked=VisionEngine.analyze(covered,W,H,22,movingPanel);
  check(!blocked.buttons,"masked SELL must never be eligible for a click");
  check(blocked.bars>=34,"masked SELL must not erase visible candles: "+blocked.bars);
  check(!blocked.regime.equals("SEM DADOS"),"chart still analyzed despite hidden SELL");
  check(blocked.detail.contains("BOTÕES PARCIALMENTE OCULTOS"),
      "explain why touches are disabled");

  // Even if controls cannot be calibrated, candle recognition remains
  // independent. A hidden button must never authorize a blind tap.
  int[] hidden=frame();
  fill(hidden,0,940,999,1320,DARK);
  VisionEngine.Result chartOnly=VisionEngine.analyze(hidden,W,H,22,new int[]{0,936,999,1325});
  check(!chartOnly.buttons,"hidden controls cannot authorize automatic touch");
  check(chartOnly.bars>=34,"should still count chart candles: "+chartOnly.bars);

  System.out.println("VisionEngineTest passed: "+r.bars+
      " normal, "+blocked.bars+" with draggable overlay, "+
      chartOnly.bars+" with buttons covered");
 }
}
