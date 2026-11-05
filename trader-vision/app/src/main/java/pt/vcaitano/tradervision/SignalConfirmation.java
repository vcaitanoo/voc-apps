package pt.vcaitano.tradervision;

/**
 * Confirmações das últimas cinco capturas visuais.
 *
 * Um setup pode alternar de nome de estratégia sem alterar a direção.
 * Não zeramos a confirmação só porque UMA captura perdeu pontuação.
 * Nunca arma no frame atual sem sinal. Sinais opostos conflitantes
 * não geram toque (no máximo um voto oposto na janela).
 *
 * É uma heurística de DEMO, não estimativa de chance de vitória.
 */
public final class SignalConfirmation {
    private static final int WINDOW=5;
    private final int[] votes=new int[WINDOW];
    private int next=0;
    private int samples=0;

    public static final class State {
        public final int progress;
        public final boolean ready;
        public final String direction;
        private State(int progress,boolean ready,String direction) {
            this.progress=progress;this.ready=ready;this.direction=direction;
        }
    }

    public State observe(String direction,int score,int minimumScore) {
        final int current;
        if("COMPRAR".equals(direction)&&score>=minimumScore)current=1;
        else if("VENDER".equals(direction)&&score>=minimumScore)current=-1;
        else current=0;

        votes[next]=current;
        next=(next+1)%WINDOW;
        if(samples<WINDOW)samples++;

        if(current==0)return new State(0,false,"AGUARDAR");

        int agreement=0,contradictions=0;
        for(int i=0;i<samples;i++){
            if(votes[i]==current)agreement++;
            else if(votes[i]==-current)contradictions++;
        }
        int progress=Math.min(3,agreement);
        return new State(progress,agreement>=3&&contradictions<=1,
            current==1?"COMPRAR":"VENDER");
    }

    public void reset() {
        java.util.Arrays.fill(votes,0);
        next=0;samples=0;
    }
}
