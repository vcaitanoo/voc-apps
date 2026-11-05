package pt.vcaitano.tradervision;

/**
 * Conservative account-balance reconciliation for ONE DEMO trade at a time.
 * Gesture completion is not order acceptance; unresolved cases are UNKNOWN.
 * No settlement is invented from chart direction or predicted payouts.
 */
public final class OutcomeLedger {
    private OutcomeLedger(){}
    public enum Result { PENDING, WIN, LOSS, UNKNOWN }
    public static Result reconcile(double before,Double after,double stake,
                                   long elapsedMs,long expiryMs) {
        if(elapsedMs<expiryMs+3000L)return Result.PENDING;
        if(after==null || !Double.isFinite(before)||!Double.isFinite(after)
           ||stake<1||!Double.isFinite(stake))return Result.UNKNOWN;
        double delta=after-before;
        // DEMO binary-option net gain should be positive but lower than stake;
        // allow slight platform variation, never classify arbitrary deposits.
        if(delta>=Math.max(.08,stake*.15) && delta<=stake*1.05)
            return Result.WIN;
        if(Math.abs(delta+stake)<=Math.max(.04,stake*.04))
            return Result.LOSS;
        return Result.UNKNOWN;
    }
}
