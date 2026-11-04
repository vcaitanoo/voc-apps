package pt.vcaitano.tradervision;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** Gestão em moeda, independente do reconhecimento visual. */
public final class RiskManager {
    public static final double MIN_STAKE=1.00;
    private RiskManager(){}
    public static final class Plan {
        public final boolean valid;
        public final double stake, effectiveRiskPercent;
        public final boolean aboveTarget;
        private Plan(boolean ok,double v,double effective,boolean over){
            valid=ok;stake=v;effectiveRiskPercent=effective;aboveTarget=over;
        }
    }
    public static Plan calculate(double balance,double targetPercent){
        if(!Double.isFinite(balance)||!Double.isFinite(targetPercent)
            ||balance<MIN_STAKE||targetPercent<=0||targetPercent>20)
            return new Plan(false,0,0,false);
        BigDecimal b=BigDecimal.valueOf(balance);
        BigDecimal pct=BigDecimal.valueOf(targetPercent);
        BigDecimal target=b.multiply(pct).divide(BigDecimal.valueOf(100),2,RoundingMode.DOWN);
        BigDecimal stake=target.max(BigDecimal.valueOf(MIN_STAKE));
        if(stake.compareTo(b)>0)return new Plan(false,0,0,false);
        double amount=stake.doubleValue(), effective=amount*100.0/balance;
        return new Plan(true,amount,effective,effective>targetPercent+0.0001);
    }
}
