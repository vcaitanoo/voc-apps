package pt.vcaitano.divulgador;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;

/** Configure multiple Gmail accounts using local encrypted App Passwords. */
public final class GmailAccountsActivity extends Activity {
    private final int COLOR=0xff19347A;
    private LinearLayout list;
    private EditText email,password,limit;

    private int dp(int v){
        return (int)(v*getResources().getDisplayMetrics().density+0.5f);
    }
    private TextView text(String s,int size){
        TextView t=new TextView(this);
        t.setText(s);t.setTextColor(0xff18243B);t.setTextSize(size);
        t.setPadding(0,dp(12),0,dp(5));return t;
    }
    private EditText input(LinearLayout p,String label,String hint,boolean secret){
        p.addView(text(label,15));
        EditText e=new EditText(this);e.setTextSize(16);e.setHint(hint);
        e.setSingleLine(true);
        if(secret)e.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        else if(label.toLowerCase().contains("limite"))e.setInputType(InputType.TYPE_CLASS_NUMBER);
        else e.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        p.addView(e,new LinearLayout.LayoutParams(-1,dp(52)));
        return e;
    }
    private void button(LinearLayout p,String title,View.OnClickListener callback){
        Button b=new Button(this);b.setText(title);b.setAllCaps(false);b.setOnClickListener(callback);
        p.addView(b,new LinearLayout.LayoutParams(-1,dp(50)));
    }

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setStatusBarColor(COLOR);
        ScrollView scroll=new ScrollView(this);
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(16),dp(18),dp(32));
        root.setBackgroundColor(0xfff5f7fb);
        scroll.addView(root);setContentView(scroll);

        TextView title=text("Contas Gmail para envio automático",24);
        title.setTypeface(null,1);root.addView(title);
        root.addView(text("Adicione as suas contas Gmail autorizadas. Cada conta usa uma senha DE APP do Google com verificação em duas etapas. Não coloque a senha normal da conta.",14));
        button(root,"COMO GERAR SENHA DE APP GOOGLE",v->{
            Intent link=new Intent(Intent.ACTION_VIEW,Uri.parse("https://myaccount.google.com/apppasswords"));
            startActivity(link);
        });
        email=input(root,"Endereço Gmail","exemplo@gmail.com",false);
        password=input(root,"Senha de app (16 caracteres)","Não é a senha principal",true);
        limit=input(root,"Limite diário desta conta (1 a 100)","40",false);
        limit.setText("40");
        button(root,"ADICIONAR / ATUALIZAR CONTA",v->add());
        root.addView(text("Contas cadastradas (senhas criptografadas no Android)",19));
        list=new LinearLayout(this);list.setOrientation(LinearLayout.VERTICAL);
        root.addView(list);
        root.addView(text("Envio começa apenas quando você preparar a fila e clicar em INICIAR. A campanha pausa diante de limite/bloqueio do Gmail. O uso de várias contas não autoriza ultrapassar limites do Google nem enviar mensagens sem consentimento.",13));
        refresh();
    }

    private void add(){
        try{
            String addr=email.getText().toString().trim();
            String secret=password.getText().toString();
            int daily=Integer.parseInt(limit.getText().toString().trim());
            new GmailAccounts(this).add(addr,secret,daily);
            email.setText("");password.setText("");
            Toast.makeText(this,"Conta Gmail guardada com criptografia.",Toast.LENGTH_LONG).show();
            refresh();
        }catch(Exception error){
            Toast.makeText(this,error.getMessage(),Toast.LENGTH_LONG).show();
        }
    }

    private void refresh(){
        list.removeAllViews();
        try{
            ArrayList<GmailAccounts.Account> accounts=new GmailAccounts(this).list();
            if(accounts.isEmpty()){
                list.addView(text("Nenhuma conta cadastrada.",14));
                return;
            }
            for(GmailAccounts.Account account:accounts){
                LinearLayout panel=new LinearLayout(this);
                panel.setOrientation(LinearLayout.VERTICAL);
                panel.setPadding(dp(10),dp(8),dp(10),dp(8));
                panel.setBackgroundColor(Color.WHITE);
                LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);
                p.bottomMargin=dp(9);
                list.addView(panel,p);
                panel.addView(text(account.email,17));
                AutoMailQueue queue=new AutoMailQueue(this);
                panel.addView(text("Limite: "+account.dailyCap+"/dia · Usado hoje: "+
                    queue.accountUsed(account.email),13));
                queue.close();

                CheckBox enabled=new CheckBox(this);
                enabled.setText("Habilitada para envios da fila");
                enabled.setChecked(account.enabled);
                enabled.setOnCheckedChangeListener((btn,on)->{
                    try{new GmailAccounts(this).setEnabled(account.email,on);}
                    catch(Exception ex){Toast.makeText(this,"Falha ao alterar conta.",Toast.LENGTH_SHORT).show();}
                });
                panel.addView(enabled);
                button(panel,"TESTAR CONEXÃO (SEM ENVIAR)",v->new Thread(()->{
                    try{
                        SmtpMailSender.test(account);
                        runOnUiThread(()->Toast.makeText(this,
                            "Conexão Gmail confirmada: "+account.email,Toast.LENGTH_LONG).show());
                    }catch(Exception ex){
                        runOnUiThread(()->Toast.makeText(this,
                            "Gmail recusou a conexão. Confira senha de app, autenticação e internet.",
                            Toast.LENGTH_LONG).show());
                    }
                }).start());
                button(panel,"ENVIAR TESTE PARA ESTA PRÓPRIA CONTA",v->{
                    new AlertDialog.Builder(this)
                        .setTitle("Enviar e-mail de teste?")
                        .setMessage("Será enviada uma mensagem real de "+account.email+
                            " para esta mesma conta, apenas para validar o SMTP.")
                        .setNegativeButton("Cancelar",null)
                        .setPositiveButton("Enviar teste",(d,w)->new Thread(()->{
                            try{
                                AutoMailQueue.Job example=new AutoMailQueue.Job(-1L,
                                    account.email,"Teste","Teste do Divulgador Mobile",
                                    "Esta mensagem confirma que sua conta Gmail está preparada para envios autorizados.",
                                    "Divulgador Mobile","","");
                                SmtpMailSender.send(this,account,example);
                                runOnUiThread(()->Toast.makeText(this,
                                    "Teste enviado para "+account.email,Toast.LENGTH_LONG).show());
                            }catch(Exception e){
                                runOnUiThread(()->Toast.makeText(this,
                                    "Falha no envio de teste. Confira o Gmail e a senha de app.",
                                    Toast.LENGTH_LONG).show());
                            }
                        }).start()).show();
                });
                button(panel,"REMOVER CONTA",v->
                    new AlertDialog.Builder(this)
                        .setTitle("Remover "+account.email+"?")
                        .setMessage("A senha de app guardada será removida deste celular. A fila de destinatários permanece.")
                        .setNegativeButton("Cancelar",null)
                        .setPositiveButton("Remover",(d,w)->{
                            try{
                                new GmailAccounts(this).remove(account.email);
                                refresh();
                            }catch(Exception ex){
                                Toast.makeText(this,"Erro ao remover conta.",Toast.LENGTH_SHORT).show();
                            }
                        }).show());
            }
        }catch(Exception ex){
            list.addView(text("Não foi possível ler as contas criptografadas. "+ex.getClass().getSimpleName(),14));
        }
    }
}
