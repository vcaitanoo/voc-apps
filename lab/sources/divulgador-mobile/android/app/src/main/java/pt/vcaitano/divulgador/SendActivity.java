package pt.vcaitano.divulgador;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
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
    private TextView recipient, stats;
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
        button(p,"VER PRÉVIA DO E-MAIL",v->previewEmail());
        button(p,"✉ ABRIR E-MAIL PARA ENVIO",v->compose());
        button(p,"✓ MARCAR ENVIO CONFIRMADO",v->confirm());
        button(p,"PRÓXIMO DESTINATÁRIO",v->next());
        button(p,"BLOQUEAR / DESCADASTRAR",v->block());
        restore();refresh();
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
                confirmed.add(obj.optString("email"));current++;save();refresh();
            }).show();
    }
    private void next(){if(active()!=null)current++;refresh();}
    private void block(){
        JSONObject obj=active();if(obj==null)return;
        blocked.add(obj.optString("email"));current++;save();refresh();
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
