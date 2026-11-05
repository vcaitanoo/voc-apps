package pt.vcaitano.tradervision;

public final class SignalConfirmationTest {
    private static void check(boolean test,String why){
        if(!test)throw new AssertionError(why);
    }
    private static SignalConfirmation.State observe(SignalConfirmation s,String d,int score){
        return s.observe(d,score,78);
    }
    public static void main(String[] args){
        SignalConfirmation s=new SignalConfirmation();
        check(!observe(s,"VENDER",92).ready,"one high score not enough");
        check(!observe(s,"VENDER",85).ready,"2/3 not enough");
        check(!observe(s,"AGUARDAR",0).ready,"a gap cannot cause a touch");
        check(observe(s,"VENDER",96).ready,"3 of last 4, one dropout should arm");
        check(!observe(s,"COMPRAR",99).ready,"opposite high must not inherit sell votes");
        check(!observe(s,"AGUARDAR",77).ready,"under threshold never sends a touch");

        s.reset();
        observe(s,"COMPRAR",89);
        observe(s,"VENDER",92);
        observe(s,"COMPRAR",85);
        observe(s,"VENDER",88);
        check(!observe(s,"COMPRAR",92).ready,"3 buys versus 2 sells is conflict");
        check(!observe(s,"VENDER",92).ready,"direction reversal must require reconfirmation");
        s.reset();
        check(observe(s,"COMPRAR",99).progress==1,"first capture 1/3");
        check(observe(s,"COMPRAR",99).progress==2,"second capture 2/3");
        check(observe(s,"COMPRAR",99).progress==3,"third capture 3/3");
        check(observe(s,"COMPRAR",99).ready,"three consecutive high captures pass");
        check(!observe(s,"COMPRAR",65).ready,"current low score blocks touch");
        System.out.println("SignalConfirmationTest passed");
    }
}
