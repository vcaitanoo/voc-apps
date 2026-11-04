package pt.vcaitano.tradervision;

public final class PanelPositionTest {
    private static void equal(int a,int b,String message){
        if(a!=b)throw new AssertionError(message+" ("+a+" != "+b+")");
    }
    private static void close(float a,float b,String message){
        if(Math.abs(a-b)>.00001)throw new AssertionError(message+" ("+a+" != "+b+")");
    }
    public static void main(String[]args){
        equal(PanelPosition.move(20,36f,250),56,"drag down or right");
        equal(PanelPosition.move(20,-100f,250),0,"no negative edge");
        equal(PanelPosition.move(20,800f,250),250,"no screen overflow");
        equal(PanelPosition.move(50,0f,0),0,"full screen panel");
        close(PanelPosition.fraction(125,250),.5f,"middle ratio");
        close(PanelPosition.fraction(400,250),1f,"ratio clamped upper");
        close(PanelPosition.fraction(-30,250),0f,"ratio clamped lower");
        close(PanelPosition.fraction(22,0),0f,"zero span");
        equal(PanelPosition.restore(.5f,900,5),450,"restore different display size");
        equal(PanelPosition.restore(-1f,900,42),42,"legacy start");
        equal(PanelPosition.restore(2f,900,42),900,"saved ratio out of range");
        equal(PanelPosition.restore(Float.NaN,900,42),42,"corrupted saved state");
        equal(PanelPosition.restore(.5f,0,42),0,"too small display");
        System.out.println("PanelPosition tests passed");
    }
}
