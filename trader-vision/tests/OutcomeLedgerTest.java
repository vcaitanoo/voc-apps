package pt.vcaitano.tradervision;
public final class OutcomeLedgerTest {
 static void eq(OutcomeLedger.Result actual,OutcomeLedger.Result expected){
  if(actual!=expected)throw new AssertionError(actual+" != "+expected);
 }
 public static void main(String[]args){
  long expiry=300000;
  eq(OutcomeLedger.reconcile(30.30,31.17,1,30000,expiry),OutcomeLedger.Result.PENDING);
  eq(OutcomeLedger.reconcile(30.30,31.17,1,310000,expiry),OutcomeLedger.Result.WIN);
  eq(OutcomeLedger.reconcile(30.30,29.30,1,310000,expiry),OutcomeLedger.Result.LOSS);
  eq(OutcomeLedger.reconcile(30.30,30.30,1,310000,expiry),OutcomeLedger.Result.UNKNOWN);
  eq(OutcomeLedger.reconcile(30.30,35.30,1,310000,expiry),OutcomeLedger.Result.UNKNOWN);
  eq(OutcomeLedger.reconcile(30.30,null,1,310000,expiry),OutcomeLedger.Result.UNKNOWN);
  eq(OutcomeLedger.reconcile(30.30,29.30,1,300000,expiry),OutcomeLedger.Result.PENDING);
  System.out.println("OutcomeLedger tests passed");
 }
}
