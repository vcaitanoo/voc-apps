package pt.vcaitano.tradervision;

/**
 * Geometria do painel flutuante independente de Android.
 * A janela nunca ultrapassa a área utilizável do ecrã e a posição
 * persiste como fração, não como coordenada fixa em pixels.
 */
public final class PanelPosition {
    private PanelPosition() {}

    public static int move(int startPx,float deltaPx,int maxPx) {
        int value=Math.round(startPx+deltaPx);
        return Math.max(0,Math.min(Math.max(0,maxPx),value));
    }
    public static float fraction(int currentPx,int maxPx) {
        if(maxPx<=0)return 0f;
        return Math.max(0f,Math.min(1f,currentPx/(float)maxPx));
    }
    public static int restore(float normalized,int maxPx,int fallbackPx) {
        int cap=Math.max(0,maxPx);
        if(!Float.isFinite(normalized)||normalized<0)
            return Math.max(0,Math.min(cap,fallbackPx));
        return Math.round(Math.max(0f,Math.min(1f,normalized))*cap);
    }
}
