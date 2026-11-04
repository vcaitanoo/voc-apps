package pt.vcaitano.tradervision;

public final class EntryTimingTest {
    private static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args){
        check(!EntryTiming.evaluate(0,-1,5,5).allowed,"1 captura não basta");
        check(!EntryTiming.evaluate(1,-1,5,5).allowed,"2 capturas não bastam");
        check(EntryTiming.evaluate(2,-1,5,5).allowed,"sinal estável não deve aguardar minuto do relógio");
        check(!EntryTiming.evaluate(3,0,5,5).allowed,"não repetir entrada");
        check(!EntryTiming.evaluate(3,299999,5,5).allowed,"ainda em cooldown");
        check(EntryTiming.evaluate(3,300000,5,5).allowed,"liberar após candle de 5min");
        check(!EntryTiming.evaluate(3,300000,5,7).allowed,"respeitar expiração maior");
        check(EntryTiming.evaluate(3,420000,5,7).allowed,"liberar após expiração maior");
        check(!EntryTiming.evaluate(3,-1,0,5).allowed,"timeframe inválido");
        check(!EntryTiming.evaluate(3,-1,5,0).allowed,"expiração inválida");
        check(!EntryTiming.evaluate(3,-1,61,5).allowed,"timeframe acima da faixa");
        check(!EntryTiming.evaluate(3,-1,5,121).allowed,"expiração acima da faixa");
        System.out.println("EntryTiming tests passed");
    }
}
