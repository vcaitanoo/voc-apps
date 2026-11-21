package pt.vcaitano.divulgador;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.content.res.ColorStateList;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.widget.*;
import android.graphics.Color;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.Pattern;

/** Envio apenas pelo aplicativo de e-mail autorizado pelo usuário. */
public class SendActivity extends Activity {
    private static final int PICK_CSV=106;
    private static final int INK=0xff18243B;
    private static final Pattern EMAIL=Pattern.compile("^[A-Za-z0-9_+.%'-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    private EditText subject, body, product, link;
    private PhotoAttachments photoAttachments;
    private TextView recipient, stats, automaticStatus;
    private TextView dashboardPercent, dashboardWarning, dashboardState;
    private ProgressBar dashboardProgress;
    private final TextView[] dashboardValues=new TextView[6];
    private final Handler dashboardHandler=new Handler(Looper.getMainLooper());
    private boolean dashboardVisible=false;
    private final Runnable dashboardTick=new Runnable(){
        @Override public void run(){
            if(!dashboardVisible)return;
            updateAutomaticStatus();
            dashboardHandler.postDelayed(this,5000);
        }
    };
    private final ArrayList<JSONObject> contacts=new ArrayList<>();
    private final HashSet<String> confirmed=new HashSet<>(), blocked=new HashSet<>();
    private int current=0;
    private int dp(int v){return (int)(getResources().getDisplayMetrics().density*v+0.5f);}
    private TextView text(String s,int size){
        TextView t=new TextView(this);t.setText(s);t.setTextColor(INK);t.setTextSize(size);
        t.setPadding(0,dp(10),0,dp(6));return t;
    }
    private EditText field(LinearLayout p,String label,String value,boolean multi){
        p.addView(text(label,15));
        EditText e=new EditText(this);e.setText(value);e.setTextSize(16);
        if(multi){e.setMinLines(4);e.setGravity(android.view.Gravity.TOP);}
        else e.setSingleLine(true);
        p.addView(e,new LinearLayout.LayoutParams(-1,-2));return e;
    }
    private void button(LinearLayout p,String name,android.view.View.OnClickListener action){
        Button b=new Button(this);b.setText(name);b.setTextSize(15);b.setAllCaps(false);
        b.setOnClickListener(action);p.addView(b,new LinearLayout.LayoutParams(-1,dp(53)));
    }
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setStatusBarColor(0xff19347A);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        LinearLayout p=new LinearLayout(this);p.setOrientation(LinearLayout.VERTICAL);
        p.setPadding(dp(19),dp(16),dp(19),dp(40));p.setBackgroundColor(0xffF5F7FB);
        scroll.addView(p);setContentView(scroll);
        createDashboard(p);
        TextView title=text("Divulgação por e-mail",25);title.setTypeface(null,1);p.addView(title);
        p.addView(text("Importe contatos autorizados, edite a mensagem e confirme o envio no Gmail ou outro app de e-mail.",14));
        String name=getIntent().getStringExtra("campaign_name");
        String url=getIntent().getStringExtra("campaign_link");
        String desc=getIntent().getStringExtra("campaign_desc");
        product=field(p,"Produto / serviço",name==null?"":name,false);
        link=field(p,"Link público",url==null?"":url,false);
        subject=field(p,"Assunto",name==null?"Conheça o nosso projeto":"Conheça "+name,false);
        body=field(p,"Mensagem (use {nome}, {produto}, {link})",
            "Olá {nome},\n\n"+(desc==null?"Quero apresentar {produto}.":desc)+
            "\n\nSaiba mais em {link}\n\nCaso não deseje receber outras mensagens, responda REMOVER.",true);
        // As fotos pertencem à campanha configurada, e não à lista de contatos.
        photoAttachments=new PhotoAttachments(this,p);
        TextView contactsTitle=text("Destinatários autorizados",20);
        contactsTitle.setTypeface(null,1);p.addView(contactsTitle);
        button(p,"IMPORTAR CSV",v->pickCsv());
        TextView help=text("Aceita CSV com vírgula ou ponto e vírgula. A coluna Email é obrigatória; Consentimento é opcional na importação. Listas sem consentimento são carregadas para configurar e visualizar, mas não podem ser enviadas sem autorização. Endereços gerados são fictícios.",13);
        help.setTextColor(0xff655D52);p.addView(help);
        recipient=text("",16);p.addView(recipient);
        stats=text("",14);p.addView(stats);
        TextView autoTitle=text("Envio automático Gmail",21);
        autoTitle.setTypeface(null,1);p.addView(autoTitle);
        p.addView(text("Configure várias contas Gmail, prepare a fila e toque uma única vez em INICIAR. Os envios autorizados são processados automaticamente, sem abrir o Gmail para cada contato.",14));
        button(p,"GERENCIAR CONTAS GMAIL",v->startActivity(
            new Intent(this,GmailAccountsActivity.class)));
        button(p,"PREPARAR FILA COM CONTATOS AUTORIZADOS",v->prepareAutoQueue(false));
        button(p,"▶ INICIAR ENVIO AUTOMÁTICO",v->confirmAutoStart());
        button(p,"⏸ PAUSAR ENVIO AUTOMÁTICO",v->{
            AutoMailWorker.pause(this);
            updateAutomaticStatus();
            Toast.makeText(this,"Fila automática pausada.",Toast.LENGTH_LONG).show();
        });
        button(p,"ATUALIZAR ESTATÍSTICAS DA FILA",v->updateAutomaticStatus());
        automaticStatus=text("",14);p.addView(automaticStatus);
        button(p,"VER PRÉVIA DO E-MAIL",v->previewEmail());
        button(p,"✉ ABRIR E-MAIL PARA ENVIO",v->compose());
        button(p,"✓ MARCAR ENVIO CONFIRMADO",v->confirm());
        button(p,"PRÓXIMO DESTINATÁRIO",v->next());
        button(p,"BLOQUEAR / DESCADASTRAR",v->block());
        restore();refresh();
        updateAutomaticStatus();
        // O gerador passa apenas o nome do arquivo no cache privado (evita limite do Intent).
        String generated=getIntent().getStringExtra("import_generated_file");
        if(generated!=null){
            if(!generated.matches("divulgador-gerado-[0-9]+\\.csv")){
                Toast.makeText(this,"Origem de importação inválida.",Toast.LENGTH_LONG).show();
            }else{
                File source=new File(getCacheDir(),generated);
                stats.setText("Carregando CSV criado no Gerador...");
                readGeneratedFile(source);
            }
        }else if(getIntent().getBooleanExtra("pick_csv_on_start",false)){
            // Atalho da tela inicial: escolher lista e voltar ao editor já preenchido.
            pickCsv();
        }
    }
    private GradientDrawable dashboardBackground(int fillColor){
        GradientDrawable background=new GradientDrawable();
        background.setColor(fillColor);
        background.setCornerRadius(dp(16));
        background.setStroke(dp(1),0xffDEE5F2);
        return background;
    }

    private TextView metricValue(LinearLayout parent,String caption){
        LinearLayout metric=new LinearLayout(this);
        metric.setOrientation(LinearLayout.VERTICAL);
        metric.setGravity(Gravity.CENTER);
        metric.setPadding(dp(2),dp(8),dp(2),dp(8));
        LinearLayout.LayoutParams slot=new LinearLayout.LayoutParams(0,-2,1f);
        slot.setMargins(dp(2),0,dp(2),0);
        parent.addView(metric,slot);

        TextView value=new TextView(this);
        value.setText("0");
        value.setTextColor(0xff19347A);
        value.setTextSize(23);
        value.setTypeface(null,1);
        value.setGravity(Gravity.CENTER);
        metric.addView(value,new LinearLayout.LayoutParams(-1,-2));

        TextView label=new TextView(this);
        label.setText(caption);
        label.setTextColor(0xff596478);
        label.setTextSize(12);
        label.setGravity(Gravity.CENTER);
        metric.addView(label,new LinearLayout.LayoutParams(-1,-2));
        return value;
    }

    private void createDashboard(LinearLayout root){
        LinearLayout panel=new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(13),dp(12),dp(13),dp(12));
        panel.setBackground(dashboardBackground(0xffFFFFFF));
        LinearLayout.LayoutParams outside=new LinearLayout.LayoutParams(-1,-2);
        outside.bottomMargin=dp(16);
        root.addView(panel,outside);

        LinearLayout head=new LinearLayout(this);
        head.setOrientation(LinearLayout.HORIZONTAL);
        head.setGravity(Gravity.CENTER_VERTICAL);
        panel.addView(head,new LinearLayout.LayoutParams(-1,-2));
        TextView title=text("PAINEL DE ENVIOS",16);
        title.setTypeface(null,1);title.setTextColor(0xff19347A);
        head.addView(title,new LinearLayout.LayoutParams(0,-2,1f));
        dashboardPercent=text("0%",22);
        dashboardPercent.setTypeface(null,1);
        dashboardPercent.setTextColor(0xff087F8C);
        head.addView(dashboardPercent);

        dashboardProgress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);
        dashboardProgress.setMax(100);dashboardProgress.setProgress(0);
        dashboardProgress.setProgressTintList(ColorStateList.valueOf(0xff087F8C));
        LinearLayout.LayoutParams progressSize=new LinearLayout.LayoutParams(-1,dp(9));
        progressSize.topMargin=dp(6);progressSize.bottomMargin=dp(5);
        panel.addView(dashboardProgress,progressSize);

        dashboardState=text("Aguardando dados de envio.",12);
        dashboardState.setTextColor(0xff526078);
        panel.addView(dashboardState);
        String[] labels={"Importados","Autorizados","Sem consent.","Na fila","Enviados","Falhas"};
        for(int rowIndex=0;rowIndex<2;rowIndex++){
            LinearLayout row=new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER);
            panel.addView(row,new LinearLayout.LayoutParams(-1,-2));
            for(int col=0;col<3;col++){
                int i=rowIndex*3+col;
                dashboardValues[i]=metricValue(row,labels[i]);
            }
        }
        dashboardWarning=text("",13);
        dashboardWarning.setTextColor(0xff88531A);
        dashboardWarning.setPadding(dp(8),dp(7),dp(8),dp(7));
        dashboardWarning.setBackground(dashboardBackground(0xffFFF5E5));
        panel.addView(dashboardWarning,new LinearLayout.LayoutParams(-1,-2));
    }

    private void renderDashboard(AutoMailQueue.Status status){
        if(dashboardPercent==null)return;
        int authorized=0,withoutConsent=0;
        for(JSONObject row:contacts){
            String email=row.optString("email");
            if(!row.optBoolean("consented",false) || row.optBoolean("synthetic",false)){
                withoutConsent++;
            }else if(!blocked.contains(email)&&!confirmed.contains(email)){
                authorized++;
            }
        }
        // Percentual de mensagens realmente enfileiradas; exclui sem consentimento.
        int total=status.total;
        int percent=total==0?0:(int)Math.round(100.0*status.sent/total);
        dashboardPercent.setText(percent+"% enviado");
        dashboardProgress.setProgress(percent);
        dashboardValues[0].setText(String.format(Locale.getDefault(),"%,d",contacts.size()));
        dashboardValues[1].setText(String.format(Locale.getDefault(),"%,d",authorized));
        dashboardValues[2].setText(String.format(Locale.getDefault(),"%,d",withoutConsent));
        dashboardValues[3].setText(String.format(Locale.getDefault(),"%,d",status.waiting));
        dashboardValues[4].setText(String.format(Locale.getDefault(),"%,d",status.sent));
        dashboardValues[5].setText(String.format(Locale.getDefault(),"%,d",status.failed));
        dashboardState.setText((status.running?"● Automático ativo":"○ Automático pausado")+
            " · Total na fila: "+total+" · Incertos: "+status.uncertain+
            " · Bloqueados: "+status.blocked);
        if(!status.error.isEmpty()){
            dashboardWarning.setText("Atenção: "+status.error);
        }else if(status.waiting==0 && authorized==0 && !contacts.isEmpty()){
            dashboardWarning.setText("Nenhum destinatário autorizado. Contatos sem consentimento"+
                " ou gerados ficticiamente não entram na fila. Importe uma lista real autorizada.");
        }else if(status.waiting==0 && authorized>0){
            dashboardWarning.setText("Há contatos autorizados. Toque PREPARAR FILA e depois INICIAR ENVIO AUTOMÁTICO.");
        }else if(status.total==0){
            dashboardWarning.setText("Importe contatos autorizados para preparar a primeira campanha.");
        }else{
            dashboardWarning.setText("Atualização a cada 5 segundos enquanto esta tela estiver aberta.");
        }
    }

    @Override protected void onResume(){
        super.onResume();
        dashboardVisible=true;
        dashboardHandler.removeCallbacks(dashboardTick);
        dashboardHandler.post(dashboardTick);
    }
    @Override protected void onPause(){
        dashboardVisible=false;
        dashboardHandler.removeCallbacks(dashboardTick);
        super.onPause();
    }

    private void updateAutomaticStatus(){
        if(automaticStatus==null)return;
        AutoMailQueue q=new AutoMailQueue(this);
        try{
            AutoMailQueue.Status status=q.status();
            renderDashboard(status);
            automaticStatus.setText(
                (status.running?"● ENVIO AUTOMÁTICO ATIVO":"○ ENVIO PAUSADO")+
                "\nNa fila: "+status.waiting+" · Enviados: "+status.sent+
                " · Falhas: "+status.failed+" · Incertos: "+status.uncertain+
                " · Bloqueados: "+status.blocked+
                (status.error.isEmpty()?"":"\nAviso: "+status.error)+
                "\nO Android pode atrasar tarefas em segundo plano para poupar bateria.");
        }finally{q.close();}
    }

    private int eligibleCount(){
        int total=0;
        for(JSONObject obj:contacts)
            if(obj.optBoolean("consented",false) && !obj.optBoolean("synthetic",false) &&
               !blocked.contains(obj.optString("email")) &&
               !confirmed.contains(obj.optString("email")))total++;
        return total;
    }

    private void prepareAutoQueue(boolean startAfter){
        final ArrayList<JSONObject> snapshot=new ArrayList<>();
        for(JSONObject obj:contacts){
            if(obj.optBoolean("consented",false) && !obj.optBoolean("synthetic",false) &&
               !blocked.contains(obj.optString("email")) &&
               !confirmed.contains(obj.optString("email")))snapshot.add(obj);
        }
        if(snapshot.isEmpty() && !startAfter){
            Toast.makeText(this,"Sem destinatários autorizados para envio. E-mails gerados fictícios não entram na fila.",Toast.LENGTH_LONG).show();
            return;
        }
        final String title=subject.getText().toString();
        final String message=body.getText().toString();
        final String campaign=product.getText().toString();
        final String address=link.getText().toString();
        new Thread(()->{
            AutoMailQueue queue=new AutoMailQueue(this);
            try{
                int inserted=queue.enqueueAuthorized(snapshot,title,message,campaign,address);
                if(startAfter && queue.status().waiting>0){
                    AutoMailWorker.start(this);
                }
                runOnUiThread(()->{
                    updateAutomaticStatus();
                    Toast.makeText(this,inserted+" novo(s) destinatário(s) incluído(s) na fila.",
                        Toast.LENGTH_LONG).show();
                });
            }catch(Exception error){
                runOnUiThread(()->Toast.makeText(this,
                    "Falha ao preparar fila: "+error.getMessage(),Toast.LENGTH_LONG).show());
            }finally{queue.close();}
        }).start();
    }

    private void confirmAutoStart(){
        int eligible=eligibleCount();
        AutoMailQueue queue=new AutoMailQueue(this);
        AutoMailQueue.Status before=queue.status();
        queue.close();
        try{
            int configured=0;
            for(GmailAccounts.Account item:new GmailAccounts(this).list())
                if(item.enabled)configured++;
            if(configured==0){
                Toast.makeText(this,"Adicione e ative pelo menos uma conta Gmail.",Toast.LENGTH_LONG).show();
                startActivity(new Intent(this,GmailAccountsActivity.class));
                return;
            }
        }catch(Exception error){
            Toast.makeText(this,"Erro ao consultar contas Gmail.",Toast.LENGTH_LONG).show();
            return;
        }
        if(eligible==0 && before.waiting==0){
            Toast.makeText(this,"Não há contatos autorizados. Importe lista com consentimento.",Toast.LENGTH_LONG).show();
            return;
        }
        new AlertDialog.Builder(this)
            .setTitle("Iniciar envio automático?")
            .setMessage("A campanha enviará os e-mails da fila sem confirmação individual.\n"+
                "Autorizados nesta tela: "+eligible+"\n"+
                "Pendentes na fila: "+before.waiting+"\n\n"+
                "Intervalo mínimo: 30 segundos entre e-mails. "+
                "Só serão enviados contatos autorizados. "+
                "O serviço pausa em bloqueios do Gmail. "+
                "Você pode PAUSAR a qualquer momento.")
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("INICIAR",(d,w)->prepareAutoQueue(true)).show();
    }

    private void pickCsv(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        startActivityForResult(i,PICK_CSV);
    }
    private static String normalizeHeader(String text){
        return Normalizer.normalize(text,Normalizer.Form.NFD)
            .replaceAll("\\p{M}+","").replace("\uFEFF","")
            .trim().toLowerCase(Locale.ROOT).replace(" ","_");
    }
    private static String readCsv(InputStream stream) throws Exception {
        if(stream==null) throw new IllegalArgumentException("Arquivo não acessível");
        try(BufferedReader in=new BufferedReader(new InputStreamReader(stream,StandardCharsets.UTF_8))){
            StringBuilder csv=new StringBuilder();
            char[] buffer=new char[8192];int count;
            while((count=in.read(buffer))!=-1){
                csv.append(buffer,0,count);
                if(csv.length()>18_000_000)throw new IllegalArgumentException("CSV maior que 18 MB");
            }
            return csv.toString();
        }
    }
    private void readGeneratedFile(File source){
        new Thread(()->{
            try{
                if(!source.isFile() || source.length()>18_000_000)
                    throw new IllegalArgumentException("Arquivo gerado ausente ou muito grande");
                String csv=readCsv(new FileInputStream(source));
                source.delete();
                importCsvText(csv,true);
            }catch(Exception ex){
                runOnUiThread(()->Toast.makeText(this,"Importação direta: "+ex.getMessage(),Toast.LENGTH_LONG).show());
            }
        }).start();
    }
    @Override protected void onActivityResult(int code,int status,Intent data){
        super.onActivityResult(code,status,data);
        if(code==PhotoAttachments.PICK_IMAGE_REQUEST){
            if(status==RESULT_OK && photoAttachments!=null)photoAttachments.handleResult(data);
            return;
        }
        if(code!=PICK_CSV||status!=RESULT_OK||data==null||data.getData()==null)return;
        Uri uri=data.getData();
        stats.setText("Lendo lista CSV...");
        new Thread(()->{
            try{importCsvText(readCsv(getContentResolver().openInputStream(uri)),false);}
            catch(Exception ex){runOnUiThread(()->Toast.makeText(this,"CSV: "+ex.getMessage(),Toast.LENGTH_LONG).show());}
        }).start();
    }
    private static boolean isApproved(String text){
        String value=text.trim().toLowerCase(Locale.ROOT);
        return value.equals("sim")||value.equals("yes")||value.equals("true")||
               value.equals("1")||value.equals("consentido")||value.equals("autorizado");
    }
    private void importCsvText(String csv,boolean generated){
        // Processa fora da thread visual, inclusive listas maiores.
        try{
            ArrayList<String[]> rows=CsvFormat.parse(csv);
            if(rows.isEmpty())throw new IllegalArgumentException("CSV vazio");
            int e=-1,n=-1,c=-1;
            for(int i=0;i<rows.get(0).length;i++){
                String key=normalizeHeader(rows.get(0)[i]);
                if(key.equals("email")||key.equals("e-mail"))e=i;
                if(key.equals("nome")||key.equals("name"))n=i;
                if(key.equals("consentimento")||key.equals("consent")||
                   key.equals("opt_in")||key.equals("permissao"))c=i;
            }
            if(e<0)throw new IllegalArgumentException("Coluna Email não encontrada. Use Email;Nome;Cidade;Idade;Consentimento");
            ArrayList<JSONObject> incoming=new ArrayList<>();
            HashSet<String> seen=new HashSet<>();
            int invalid=0,approved=0,pending=0;
            for(int i=1;i<rows.size();i++){
                String[] fields=rows.get(i);
                if(e>=fields.length){invalid++;continue;}
                String email=fields[e].trim().toLowerCase(Locale.ROOT);
                if(!EMAIL.matcher(email).matches() || !seen.add(email)){invalid++;continue;}
                boolean consent=!generated && c>=0 && c<fields.length && isApproved(fields[c]);
                JSONObject ob=new JSONObject();
                ob.put("email",email);
                ob.put("name",n>=0 && n<fields.length?fields[n].trim():"");
                ob.put("consented",consent);
                ob.put("synthetic",generated);
                incoming.add(ob);
                if(consent)approved++; else pending++;
            }
            final int malformed=invalid,valid=approved,waiting=pending;
            runOnUiThread(()->{
                HashMap<String,JSONObject> present=new HashMap<>();
                for(JSONObject obj:contacts)present.put(obj.optString("email"),obj);
                int imported=0,updated=0;
                for(JSONObject obj:incoming){
                    String email=obj.optString("email");
                    if(blocked.contains(email))continue;
                    JSONObject existing=present.get(email);
                    if(existing!=null){
                        if(!existing.optBoolean("consented",false) && obj.optBoolean("consented",false)){
                            try{existing.put("consented",true);existing.put("synthetic",false);}catch(Exception ignored){}
                            updated++;
                        }
                    }else{
                        contacts.add(obj);present.put(email,obj);imported++;
                    }
                }
                // Se a fila antiga terminou, localiza os contatos importados.
                if(current>=contacts.size())current=0;
                save();refresh();
                Toast.makeText(this,"Carregados: "+imported+" · Autorizados: "+valid+
                    " · Pendentes: "+waiting+" · Inválidos: "+malformed+
                    (updated>0?" · Autorizações atualizadas: "+updated:""),Toast.LENGTH_LONG).show();
            });
        }catch(Exception ex){
            runOnUiThread(()->Toast.makeText(this,"CSV: "+ex.getMessage(),Toast.LENGTH_LONG).show());
        }
    }
    private JSONObject active(){
        while(current<contacts.size()){
            JSONObject obj=contacts.get(current);
            if(!blocked.contains(obj.optString("email")) &&
               !confirmed.contains(obj.optString("email")) &&
               obj.optBoolean("consented",false))return obj;
            current++;
        }
        return null;
    }
    private int remaining(){
        int count=0;
        for(JSONObject obj:contacts)if(!confirmed.contains(obj.optString("email"))&&!blocked.contains(obj.optString("email")))count++;
        return count;
    }
    private void refresh(){
        JSONObject obj=active();
        if(obj==null && !contacts.isEmpty()){
            JSONObject sample=contacts.get(0);
            recipient.setText("Lista carregada para configurar. Exemplo: "+sample.optString("name")+
                " <"+sample.optString("email")+">");
        }else{
            recipient.setText(obj==null?"Importe uma lista CSV.":"Próximo autorizado: "+obj.optString("name")+" <"+obj.optString("email")+">");
        }
        int authorized=0,pending=0;
        for(JSONObject row:contacts){
            if(!row.optBoolean("consented",false))pending++;
            else if(!confirmed.contains(row.optString("email"))&&!blocked.contains(row.optString("email")))authorized++;
        }
        stats.setText("Importados: "+contacts.size()+" · Autorizados a enviar: "+authorized+
            " · Sem consentimento: "+pending+" · Envio confirmado: "+confirmed.size()+
            " · Bloqueados: "+blocked.size());
        updateAutomaticStatus();
    }
    private String fill(String template,JSONObject obj){
        String name=obj.optString("name");
        if(name.isEmpty())name="tudo bem?";
        return template.replace("{nome}",name)
            .replace("{produto}",product.getText().toString())
            .replace("{link}",link.getText().toString());
    }
    private void previewEmail(){
        JSONObject sample=active();
        if(sample==null && !contacts.isEmpty())sample=contacts.get(0);
        if(sample==null){Toast.makeText(this,"Importe ou gere uma lista primeiro.",Toast.LENGTH_LONG).show();return;}
        new AlertDialog.Builder(this)
            .setTitle(fill(subject.getText().toString(),sample))
            .setMessage("Para: "+sample.optString("email")+"\n\n"+
                fill(body.getText().toString(),sample)+
                "\n\nFotos anexadas: "+(photoAttachments==null?0:photoAttachments.size()))
            .setPositiveButton("Fechar",null).show();
    }
    private void compose(){
        JSONObject obj=active();
        if(obj==null){Toast.makeText(this,"Lista pronta para configurar, mas nenhum destinatário possui consentimento de envio. Importe uma lista autorizada.",Toast.LENGTH_LONG).show();return;}
        String email=obj.optString("email");
        String title=fill(subject.getText().toString(),obj);
        String message=fill(body.getText().toString(),obj);
        ArrayList<Uri> images=new ArrayList<>();
        try {
            if(photoAttachments!=null)images=photoAttachments.uris();
        } catch(Exception error) {
            Toast.makeText(this,"Erro ao preparar fotos: "+error.getMessage(),Toast.LENGTH_LONG).show();
            return;
        }
        Intent out;
        if(images.isEmpty()){
            // Sem fotos: mantém exatamente o caminho existente de envio por e-mail.
            out=new Intent(Intent.ACTION_SENDTO);
            out.setData(Uri.fromParts("mailto",email,null));
        } else if(images.size()==1) {
            out=new Intent(Intent.ACTION_SEND);
            out.setType("image/*");
            out.putExtra(Intent.EXTRA_STREAM,images.get(0));
            PhotoAttachments.grant(out,images,this);
        } else {
            out=new Intent(Intent.ACTION_SEND_MULTIPLE);
            out.setType("image/*");
            out.putParcelableArrayListExtra(Intent.EXTRA_STREAM,images);
            PhotoAttachments.grant(out,images,this);
        }
        out.putExtra(Intent.EXTRA_EMAIL,new String[]{email});
        out.putExtra(Intent.EXTRA_SUBJECT,title);
        out.putExtra(Intent.EXTRA_TEXT,message);
        try {
            startActivity(Intent.createChooser(out,"Escolha o aplicativo de e-mail para enviar"));
        }catch(Exception error){
            Toast.makeText(this,"Nenhum aplicativo compatível para enviar e-mail com os anexos.",Toast.LENGTH_LONG).show();
        }
    }
    private void confirm(){
        JSONObject obj=active();if(obj==null)return;
        new AlertDialog.Builder(this).setTitle("Confirmar envio")
            .setMessage("Você confirmou que o aplicativo de e-mail realmente enviou esta mensagem?")
            .setNegativeButton("Não",null)
            .setPositiveButton("Sim, enviada",(d,w)->{
                confirmed.add(obj.optString("email"));
                AutoMailQueue queue=new AutoMailQueue(this);
                queue.manualSent(obj.optString("email"));queue.close();
                current++;save();refresh();updateAutomaticStatus();
            }).show();
    }
    private void next(){if(active()!=null)current++;refresh();}
    private void block(){
        JSONObject obj=active();if(obj==null)return;
        blocked.add(obj.optString("email"));
        AutoMailQueue queue=new AutoMailQueue(this);
        queue.block(obj.optString("email"));queue.close();
        current++;save();refresh();updateAutomaticStatus();
    }
    private void save(){
        JSONArray c=new JSONArray();for(JSONObject x:contacts)c.put(x);
        getPreferences(MODE_PRIVATE).edit()
            .putString("contacts",c.toString())
            .putString("confirmed",new JSONArray(confirmed).toString())
            .putString("blocked",new JSONArray(blocked).toString()).apply();
    }
    private void restore(){
        try{
            android.content.SharedPreferences pref=getPreferences(MODE_PRIVATE);
            JSONArray c=new JSONArray(pref.getString("contacts","[]"));
            for(int i=0;i<c.length();i++){
                JSONObject entry=c.getJSONObject(i);
                // Compatibilidade com CSVs autorizados importados na VC4:
                // o importador anterior só aceitava linhas com consentimento positivo.
                if(!entry.has("consented"))entry.put("consented",true);
                if(!entry.has("synthetic"))entry.put("synthetic",false);
                contacts.add(entry);
            }
            JSONArray yes=new JSONArray(pref.getString("confirmed","[]"));
            for(int i=0;i<yes.length();i++)confirmed.add(yes.getString(i));
            JSONArray deny=new JSONArray(pref.getString("blocked","[]"));
            for(int i=0;i<deny.length();i++)blocked.add(deny.getString(i));
        }catch(Exception ignored){}
    }
}
