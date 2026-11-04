package pt.vcaitano.tradervision;

/**
 * Gatilho de entrada de DEMO: não depende do relógio civil ou de assumir
 * que o servidor da corretora forma velas exatamente no minuto local.
 * Confirma 3 análises iguais e limita a frequência pela vela/expiração.
 * A fonte de velas é visual: esse sinal NÃO prova fechamento de candle.
 */
public final class EntryTiming {
    private EntryTiming(){}
    public static final class Decision {
        public final boolean allowed;
        public final String message;
        private Decision(boolean allowed,String message) {
            this.allowed=allowed;this.message=message;
        }
    }
    /**
     * stableRepeats conta repetições posteriores à primeira captura:
     * 0 = 1 captura, 1 = 2 capturas, 2 = 3 capturas.
     * elapsedSinceLastAttemptMs = -1 significa nunca tentou.
     */
    public static Decision evaluate(int stableRepeats,long elapsedSinceLastAttemptMs,
                                    int timeframeMinutes,int expiryMinutes) {
        if(timeframeMinutes<1||timeframeMinutes>60)
            return new Decision(false,"BLOQUEADO: timeframe fora de 1–60 minutos");
        if(expiryMinutes<1||expiryMinutes>120)
            return new Decision(false,"BLOQUEADO: expiração fora de 1–120 minutos");
        if(stableRepeats<2)
            return new Decision(false,"Confirmando sinal visual ("+
                Math.max(1,stableRepeats+1)+"/3 capturas)");
        long interval=Math.max(timeframeMinutes,expiryMinutes)*60000L;
        if(elapsedSinceLastAttemptMs>=0 && elapsedSinceLastAttemptMs<interval) {
            long sec=(interval-elapsedSinceLastAttemptMs+999L)/1000L;
            return new Decision(false,"Intervalo entre tentativas: "+sec+
                "s restantes (vela/expiração)");
        }
        return new Decision(true,"Sinal confirmado: elegível para validação dos campos DEMO");
    }
}
