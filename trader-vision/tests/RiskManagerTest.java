package pt.vcaitano.tradervision;

public final class RiskManagerTest {
    private static void expect(boolean value,String msg){if(!value)throw new AssertionError(msg);}
    private static void stake(double balance,double pct,double value,boolean over){
        RiskManager.Plan p=RiskManager.calculate(balance,pct);
        expect(p.valid,"Expected valid plan: "+balance);
        expect(Math.abs(p.stake-value)<0.00001,"Wrong stake for "+balance+": "+p.stake+" != "+value);
        expect(p.aboveTarget==over,"Risk flag wrong for "+balance);
    }
    public static void main(String[]a){
        stake(29.48,1.0,1.0,true);
        stake(99.99,1.0,1.0,true);
        stake(100.0,1.0,1.0,false);
        stake(150.0,1.0,1.5,false);
        stake(250.0,1.0,2.5,false);
        stake(1000.0,1.0,10.0,false);
        stake(101.13,1.0,1.01,false);
        stake(15.0,2.0,1.0,true);
        RiskManager.Plan p=RiskManager.calculate(29.48,1.0);
        expect(Math.abs(p.effectiveRiskPercent-3.3921302578)<0.0001,"effective risk");
        for(double b:new double[]{0,0.99,-1,Double.NaN,Double.POSITIVE_INFINITY})
            expect(!RiskManager.calculate(b,1.0).valid,"invalid balance "+b);
        for(double r:new double[]{0,-2,21,Double.NaN,Double.POSITIVE_INFINITY})
            expect(!RiskManager.calculate(100,r).valid,"invalid risk "+r);
        System.out.println("RiskManager tests passed");
    }
}
