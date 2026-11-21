package pt.vcaitano.divulgador;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;

/**
 * Simulação OFFLINE do processamento da lista importada/gerada.
 * Não acessa SMTP, rede ou fila de envio real; nunca confirma entregas.
 */
public final class CampaignSimulation {
    private CampaignSimulation() {}
    private static int dp(Activity a,int n){
        return Math.round(a.getResources().getDisplayMetrics().density*n);
    }

    public static void show(Activity activity,List<JSONObject> contacts){
        if(contacts==null || contacts.isEmpty()){
            new AlertDialog.Builder(activity).setTitle("Simulação")
                .setMessage("Importe ou gere um CSV antes de simular.")
                .setPositiveButton("OK",null).show();
            return;
        }

        ArrayList<String> recipients=new ArrayList<>();
        HashSet<String> seen=new HashSet<>();
        int skipped=0;
        for(JSONObject item:contacts){
            String email=item.optString("email","").trim().toLowerCase(Locale.ROOT);
            if(!email.matches("^[A-Za-z0-9_+.%'-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
                || !seen.add(email))skipped++;
            else recipients.add(email);
        }
        final int invalidOrRepeated=skipped;
        final int total=recipients.size();

        LinearLayout layout=new LinearLayout(activity);
        layout.setPadding(dp(activity,18),dp(activity,10),dp(activity,18),dp(activity,6));
        layout.setOrientation(LinearLayout.VERTICAL);
        TextView info=new TextView(activity);
        info.setText("SIMULAÇÃO — NENHUM E-MAIL SERÁ ENVIADO.\n"+
            "Percorre a lista fictícia no celular para testar importação, contagem e progresso, sem Gmail ou destinatários externos.");
        info.setTextColor(0xff815013);info.setTextSize(14);
        layout.addView(info);

        TextView pct=new TextView(activity);
        pct.setText("0% simulado");pct.setTextSize(27);pct.setTypeface(null,1);
        pct.setTextColor(0xff087F8C);pct.setGravity(Gravity.CENTER);
        pct.setPadding(0,dp(activity,12),0,dp(activity,6));
        layout.addView(pct);

        ProgressBar bar=new ProgressBar(activity,null,android.R.attr.progressBarStyleHorizontal);
        bar.setMax(100);
        layout.addView(bar,new LinearLayout.LayoutParams(-1,dp(activity,9)));

        TextView stats=new TextView(activity);
        stats.setTextSize(16);stats.setTextColor(0xff18243B);
        stats.setPadding(0,dp(activity,12),0,dp(activity,12));
        layout.addView(stats);

        Button pause=new Button(activity);pause.setText("PAUSAR SIMULAÇÃO");
        layout.addView(pause,new LinearLayout.LayoutParams(-1,dp(activity,50)));

        AlertDialog dialog=new AlertDialog.Builder(activity)
            .setTitle("Teste de campanha (não envia)")
            .setView(layout).setNegativeButton("FECHAR",null).create();
        Handler handler=new Handler(Looper.getMainLooper());
        final int[] processed={0};
        final boolean[] paused={false},closed={false};
        Runnable[] tick=new Runnable[1];
        tick[0]=()->{
            if(closed[0]||!dialog.isShowing()||paused[0])return;
            processed[0]=Math.min(total,processed[0]+25);
            int progress=total==0?100:(int)Math.round(100d*processed[0]/total);
            pct.setText(progress+"% simulado");
            bar.setProgress(progress);
            stats.setText("Registros válidos: "+total+
                "\nProcessados na simulação: "+processed[0]+
                "\nPendentes na simulação: "+(total-processed[0])+
                "\nInválidos ou repetidos: "+invalidOrRepeated+
                "\nE-mails realmente enviados: 0");
            if(processed[0]<total)handler.postDelayed(tick[0],100);
            else {pause.setEnabled(false);pause.setText("SIMULAÇÃO CONCLUÍDA");}
        };
        pause.setOnClickListener(v->{
            paused[0]=!paused[0];
            if(paused[0]){pause.setText("CONTINUAR SIMULAÇÃO");handler.removeCallbacks(tick[0]);}
            else {pause.setText("PAUSAR SIMULAÇÃO");handler.post(tick[0]);}
        });
        dialog.setOnDismissListener(d->{closed[0]=true;handler.removeCallbacks(tick[0]);});
        dialog.show();handler.post(tick[0]);
    }
}
