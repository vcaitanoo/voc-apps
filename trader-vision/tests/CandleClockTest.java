package pt.vcaitano.tradervision;
public final class CandleClockTest {
 static void ok(boolean b){if(!b)throw new AssertionError("CandleClock");}
 public static void main(String[]args){
  ok(!CandleClock.check(null,5).allowed);
  ok(!CandleClock.check(221,5).allowed);
  ok(!CandleClock.check(120,5).allowed);
  ok(CandleClock.check(299,5).allowed);
  ok(CandleClock.check(290,5).allowed);
  ok(CandleClock.check(285,5).allowed);
  ok(!CandleClock.check(284,5).allowed);
  ok(!CandleClock.check(305,5).allowed);
  ok(!CandleClock.check(59,0).allowed);
  System.out.println("CandleClock tests passed");
 }
}
