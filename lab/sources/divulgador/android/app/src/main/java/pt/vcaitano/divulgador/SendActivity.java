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
        TextView contactsTitle=text("Destinatários autorizados",20);
        contactsTitle.setTypeface(null,1);p.addView(contactsTitle);
        button(p,"IMPORTAR CSV COM CONSENTIMENTO",v->pickCsv());
        TextView help=text("CSV obrigatório: Nome,Email,Consentimento\nConsentimento = sim / yes / true / 1. Os e-mails fictícios gerados pelo Gerador de CSV não servem como lista de envio.",13);
        help.setTextColor(0xff655D52);p.addView(help);
        recipient=text("",16);p.addView(recipient);
        stats=text("",14);p.addView(stats);
        button(p,"✉ ABRIR E-MAIL PARA ENVIO",v->compose());
        button(p,"✓ MARCAR ENVIO CONFIRMADO",v->confirm());
        button(p,"PRÓXIMO DESTINATÁRIO",v->next());
        button(p,"BLOQUEAR / DESCADASTRAR",v->block());
        restore();refresh();
    }
    private void pickCsv(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        startActivityForResult(i,PICK_CSV);
    }
    private static ArrayList<String[]> parseCsv(String data){
        ArrayList<String[]> rows=new ArrayList<>();
        ArrayList<String> row=new ArrayList<>();
        StringBuilder cell=new StringBuilder();boolean inQuote=false;
        for(int i=0;i<data.length();i++){
            char ch=data.charAt(i);
            if(ch=='"'){
                if(inQuote&&i+1<data.length()&&data.charAt(i+1)=='"'){cell.append('"');i++;}
                else inQuote=!inQuote;
            }else if(ch==','&&!inQuote){row.add(cell.toString());cell.setLength(0);}
            else if((ch=='\n'||ch=='\r')&&!inQuote){
                if(ch=='\r'&&i+1<data.length()&&data.charAt(i+1)=='\n')i++;
                row.add(cell.toString());cell.setLength(0);
                if(row.size()>1||!row.get(0).isEmpty())rows.add(row.toArray(new String[0]));
                row=new ArrayList<>();
            }else cell.append(ch);
        }
        if(inQuote)throw new IllegalArgumentException("Aspas incompletas no CSV");
        if(cell.length()>0||!row.isEmpty()){
            row.add(cell.toString());rows.add(row.toArray(new String[0]));
        }
        return rows;
    }
    private static String normalizeHeader(String text){
        return Normalizer.normalize(text,Normalizer.Form.NFD)
            .replaceAll("\\p{M}+","").replace("\uFEFF","")
            .trim().toLowerCase(Locale.ROOT).replace(" ","_");
    }
    @Override protected void onActivityResult(int code,int status,Intent data){
        super.onActivityResult(code,status,data);
        if(code!=PICK_CSV||status!=RESULT_OK||data==null||data.getData()==null)return;
        try{
            StringBuilder csv=new StringBuilder();
            try(BufferedReader in=new BufferedReader(new InputStreamReader(getContentResolver().openInputStream(data.getData()),StandardCharsets.UTF_8))){
                String line;
                while((line=in.readLine())!=null){
                    csv.append(line).append('\n');
                    if(csv.length()>4_000_000)throw new IllegalArgumentException("CSV maior que 4MB");
                }
            }
            ArrayList<String[]> rows=parseCsv(csv.toString());
            if(rows.isEmpty())throw new IllegalArgumentException("CSV vazio");
            int e=-1,n=-1,c=-1;
            for(int i=0;i<rows.get(0).length;i++){
                String key=normalizeHeader(rows.get(0)[i]);
                if(key.equals("email")||key.equals("e-mail"))e=i;
                if(key.equals("nome")||key.equals("name"))n=i;
                if(key.equals("consentimento")||key.equals("consent")||key.equals("opt_in")||key.equals("permissao"))c=i;
            }
            if(e<0||c<0)throw new IllegalArgumentException("É necessário ter as colunas Email e Consentimento");
            HashSet<String> seen=new HashSet<>();
            for(JSONObject x:contacts)seen.add(x.optString("email"));
            int added=0,skipped=0;
            for(int i=1;i<rows.size();i++){
                String[] fields=rows.get(i);
                if(e>=fields.length||c>=fields.length){skipped++;continue;}
                String email=fields[e].trim().toLowerCase(Locale.ROOT);
                String yes=fields[c].trim().toLowerCase(Locale.ROOT);
                boolean allowed=yes.equals("sim")||yes.equals("yes")||yes.equals("true")||
                    yes.equals("1")||yes.equals("consentido")||yes.equals("autorizado");
                if(!allowed||!EMAIL.matcher(email).matches()||blocked.contains(email)||!seen.add(email)){
                    skipped++;continue;
                }
                JSONObject ob=new JSONObject();
                ob.put("email",email);
                ob.put("name",n>=0&&n<fields.length?fields[n].trim():"");
                contacts.add(ob);added++;
            }
            save();refresh();
            Toast.makeText(this,"Importados "+added+" · Ignorados "+skipped,Toast.LENGTH_LONG).show();
        }catch(Exception ex){Toast.makeText(this,"CSV: "+ex.getMessage(),Toast.LENGTH_LONG).show();}
    }
    private JSONObject active(){
        while(current<contacts.size()){
            JSONObject obj=contacts.get(current);
            if(!blocked.contains(obj.optString("email"))&&!confirmed.contains(obj.optString("email")))return obj;
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
        recipient.setText(obj==null?"Nenhum destinatário pendente.":"Destinatário: "+obj.optString("name")+" <"+obj.optString("email")+">");
        stats.setText("Importados: "+contacts.size()+"  · Confirmados: "+confirmed.size()+
            "  · Bloqueados: "+blocked.size()+"  · Pendentes: "+remaining());
    }
    private String fill(String template,JSONObject obj){
        String name=obj.optString("name");
        if(name.isEmpty())name="tudo bem?";
        return template.replace("{nome}",name)
            .replace("{produto}",product.getText().toString())
            .replace("{link}",link.getText().toString());
    }
    private void compose(){
        JSONObject obj=active();
        if(obj==null){Toast.makeText(this,"Importe destinatários autorizados.",Toast.LENGTH_LONG).show();return;}
        String email=obj.optString("email");
        Intent out=new Intent(Intent.ACTION_SENDTO);
        out.setData(Uri.fromParts("mailto",email,null));
        out.putExtra(Intent.EXTRA_EMAIL,new String[]{email});
        out.putExtra(Intent.EXTRA_SUBJECT,fill(subject.getText().toString(),obj));
        out.putExtra(Intent.EXTRA_TEXT,fill(body.getText().toString(),obj));
        try{startActivity(Intent.createChooser(out,"Escolha o aplicativo de e-mail"));}
        catch(Exception ex){Toast.makeText(this,"Nenhum aplicativo de e-mail encontrado.",Toast.LENGTH_LONG).show();}
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
            for(int i=0;i<c.length();i++)contacts.add(c.getJSONObject(i));
            JSONArray yes=new JSONArray(pref.getString("confirmed","[]"));
            for(int i=0;i<yes.length();i++)confirmed.add(yes.getString(i));
            JSONArray deny=new JSONArray(pref.getString("blocked","[]"));
            for(int i=0;i<deny.length();i++)blocked.add(deny.getString(i));
        }catch(Exception ignored){}
    }
}
