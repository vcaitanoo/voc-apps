package pt.vcaitano.tradervision;

/** Timing is based on the visible Hezilex candle countdown, NOT Android time. */
public final class CandleClock {
    private CandleClock(){}
    public static final class Decision{
        public final boolean allowed; public final String reason;
        private Decision(boolean allowed,String reason){this.allowed=allowed;this.reason=reason;}
    }
    public static Decision check(Integer remaining,int timeframe){
        if(timeframe<1||timeframe>60)
            return new Decision(false,"Período de vela inválido");
        if(remaining==null)
            return new Decision(false,"Aguardando cronómetro da vela na Hezilex (OCR)");
        int total=timeframe*60;
        if(remaining<0||remaining>total)
            return new Decision(false,"Cronómetro não corresponde ao período configurado");
        // Between 1 and 15 seconds after a fresh candle begins on the broker.
        if(remaining>=total-15&&remaining<=total-1)
            return new Decision(true,"Início de vela confirmado no gráfico");
        return new Decision(false,"Aguardando nova vela (restam "+remaining+"s na Hezilex)");
    }
}
