package pt.vcaitano.divulgador;

import android.content.ContentValues;
import android.content.Context;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.UUID;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

/**
 * Persistent opt-in-only queue. Keeps original recipient and message state across
 * app restarts. A process crash while an SMTP operation is in flight becomes
 * "uncertain" instead of automatically resending a possible duplicate.
 */
public final class AutoMailQueue extends SQLiteOpenHelper {
    private static final String DATABASE="divulgador_mail_queue_v1.sqlite";
    private static final int VERSION=1;
    private static final String PREFS="divulgador_auto_mail_state_v1";
    private final Context context;

    public static final class Job {
        public final long id;
        public final String email,name,subject,body,product,link,photosDirectory;
        Job(long id,String email,String name,String subject,String body,String product,String link,String photosDirectory) {
            this.id=id;this.email=email;this.name=name;this.subject=subject;
            this.body=body;this.product=product;this.link=link;this.photosDirectory=photosDirectory;
        }
    }
    public static final class Status {
        public final int waiting,sent,failed,uncertain,blocked,total;
        public final boolean running;
        public final String error;
        Status(int waiting,int sent,int failed,int uncertain,int blocked,
               boolean running,String error) {
            this.waiting=waiting;this.sent=sent;this.failed=failed;this.uncertain=uncertain;
            this.blocked=blocked;this.total=waiting+sent+failed+uncertain+blocked;
            this.running=running;this.error=error;
        }
    }

    public AutoMailQueue(Context ctx){super(ctx,DATABASE,null,VERSION);context=ctx.getApplicationContext();}

    @Override public void onCreate(SQLiteDatabase db){
        db.execSQL("CREATE TABLE delivery("+
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"+
            "email TEXT NOT NULL UNIQUE COLLATE NOCASE,name TEXT NOT NULL,"+
            "subject TEXT NOT NULL, body TEXT NOT NULL,product TEXT NOT NULL,"+
            "link TEXT NOT NULL,photo_dir TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'queued',"+
            "sender TEXT, sent_at INTEGER, error TEXT, created_at INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE sender_days(email TEXT NOT NULL, day TEXT NOT NULL,"+
                   "used INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(email,day))");
        db.execSQL("CREATE TABLE blacklist(email TEXT PRIMARY KEY COLLATE NOCASE)");
        db.execSQL("CREATE INDEX idx_delivery_state ON delivery(status,id)");
    }

    @Override public void onUpgrade(SQLiteDatabase db,int old,int now){
        throw new IllegalStateException("Migração de banco não definida, base preservada.");
    }

    private SharedPreferences prefs(){
        return context.getSharedPreferences(PREFS,Context.MODE_PRIVATE);
    }

    public boolean isRunning(){return prefs().getBoolean("running",false);}
    public void setRunning(boolean running) {
        prefs().edit().putBoolean("running",running).apply();
    }
    public void setError(String message){
        prefs().edit().putString("last_error",message==null?"":message).apply();
    }
    public long lastSentMillis(){return prefs().getLong("last_sent_ms",0);}
    public void setLastSentMillis(long millis) {
        prefs().edit().putLong("last_sent_ms",millis).apply();
    }
    public int accountCursor(){return prefs().getInt("account_cursor",0);}
    public void setAccountCursor(int cursor) {
        prefs().edit().putInt("account_cursor",cursor).apply();
    }

    private static String safe(String text,int max){
        String s=text==null?"":text.trim();
        return s.length()<=max?s:s.substring(0,max);
    }

    private String snapshotPhotos() throws IOException {
        File source=new File(context.getFilesDir(),"mail_photos");
        File[] items=source.listFiles();
        if(items==null||items.length==0)return "";
        File base=new File(context.getFilesDir(),"auto_mail_attachments");
        if(!base.isDirectory()&&!base.mkdirs())throw new IOException("Falha ao criar pasta de anexos");
        String name="batch_"+UUID.randomUUID().toString().replace("-","");
        File folder=new File(base,name);
        if(!folder.mkdirs())throw new IOException("Falha ao preparar anexos da campanha");
        long total=0;
        int count=0;
        for(File file:items) {
            if(!file.isFile() || !file.getName().matches("foto_[a-f0-9]{32}\\.(jpg|png|webp|heic|gif)"))continue;
            if(count>=6)break;
            total+=file.length();
            if(total>20L*1024*1024)throw new IOException("Anexos excedem 20 MB");
            try(FileInputStream input=new FileInputStream(file);
                FileOutputStream output=new FileOutputStream(new File(folder,file.getName()))){
                byte[] buffer=new byte[16384];int n;
                while((n=input.read(buffer))!=-1)output.write(buffer,0,n);
            }
            count++;
        }
        if(count==0){folder.delete();return "";}
        return name;
    }

    public synchronized int enqueueAuthorized(List<JSONObject> contacts,
                String subject,String body,String product,String link) throws IOException {
        String s=safe(subject,200),m=safe(body,10000);
        if(s.isEmpty()||m.isEmpty())throw new IllegalArgumentException("Preencha assunto e mensagem.");
        SQLiteDatabase db=getWritableDatabase();
        String photos=snapshotPhotos();  // Photos frozen for this batch.
        int added=0;
        db.beginTransaction();
        try{
            for(JSONObject obj:contacts) {
                if(!obj.optBoolean("consented",false) ||
                    obj.optBoolean("synthetic",false)) continue;
                String email=obj.optString("email","").trim().toLowerCase(Locale.ROOT);
                if(!email.matches("^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"))
                    continue;
                try(Cursor blocked=db.rawQuery("SELECT 1 FROM blacklist WHERE email=?",new String[]{email})){
                    if(blocked.moveToFirst())continue;
                }
                ContentValues row=new ContentValues();
                row.put("email",email);
                row.put("name",safe(obj.optString("name"),150));
                row.put("subject",s);
                row.put("body",m);
                row.put("product",safe(product,150));
                row.put("link",safe(link,2000));
                row.put("photo_dir",photos);
                row.put("status","queued");
                row.put("created_at",System.currentTimeMillis());
                if(db.insertWithOnConflict("delivery",null,row,SQLiteDatabase.CONFLICT_IGNORE)!=-1)added++;
            }
            db.setTransactionSuccessful();
        } finally {db.endTransaction();}
        return added;
    }

    private static Job fromCursor(Cursor c){
        return new Job(c.getLong(0),c.getString(1),c.getString(2),
            c.getString(3),c.getString(4),c.getString(5),c.getString(6),c.getString(7));
    }
    public synchronized Job claim(){
        SQLiteDatabase db=getWritableDatabase();
        db.beginTransaction();
        try{
            Job job=null;
            try(Cursor c=db.rawQuery(
                 "SELECT id,email,name,subject,body,product,link,photo_dir FROM delivery "+
                 "WHERE status='queued' AND email NOT IN (SELECT email FROM blacklist) "+
                 "ORDER BY id LIMIT 1",null)){
                if(c.moveToFirst())job=fromCursor(c);
            }
            if(job!=null){
                ContentValues data=new ContentValues();data.put("status","processing");
                int count=db.update("delivery",data,"id=? AND status='queued'",
                    new String[]{String.valueOf(job.id)});
                if(count!=1)job=null;
            }
            db.setTransactionSuccessful();
            return job;
        }finally{db.endTransaction();}
    }

    public synchronized void markSent(Job job,String account){
        SQLiteDatabase db=getWritableDatabase();
        ContentValues row=new ContentValues();
        row.put("status","sent");row.put("sender",account);
        row.put("sent_at",System.currentTimeMillis());
        row.putNull("error");
        db.update("delivery",row,"id=? AND status='processing'",new String[]{String.valueOf(job.id)});
        setLastSentMillis(System.currentTimeMillis());
    }

    public synchronized void markFailure(Job job,String error){
        ContentValues row=new ContentValues();row.put("status","failed");
        row.put("error",safe(error,350));
        getWritableDatabase().update("delivery",row,"id=? AND status='processing'",
            new String[]{String.valueOf(job.id)});
    }

    public synchronized void markPendingOrUncertain(Job job,String error,boolean uncertain){
        ContentValues row=new ContentValues();
        row.put("status",uncertain?"uncertain":"queued");
        row.put("error",safe(error,350));
        getWritableDatabase().update("delivery",row,"id=? AND status='processing'",
            new String[]{String.valueOf(job.id)});
    }

    public synchronized void recoverInterrupted(){
        // Never automatically resend emails that may have reached Gmail before process death.
        ContentValues update=new ContentValues();update.put("status","uncertain");
        update.put("error","Envio interrompido. Conferir na caixa Enviados antes de reenviar.");
        getWritableDatabase().update("delivery",update,"status='processing'",null);
    }

    public synchronized void block(String email){
        String normalized=email.trim().toLowerCase(Locale.ROOT);
        SQLiteDatabase db=getWritableDatabase();
        ContentValues black=new ContentValues();black.put("email",normalized);
        db.insertWithOnConflict("blacklist",null,black,SQLiteDatabase.CONFLICT_IGNORE);
        ContentValues changed=new ContentValues();changed.put("status","blocked");
        db.update("delivery",changed,"email=? AND status IN ('queued','failed')",
                  new String[]{normalized});
    }

    public synchronized void manualSent(String email){
        ContentValues row=new ContentValues();row.put("status","sent");
        row.put("sent_at",System.currentTimeMillis());row.put("sender","manual");
        getWritableDatabase().update("delivery",row,"email=? AND status='queued'",
            new String[]{email.toLowerCase(Locale.ROOT)});
    }

    private static String utcDay(){
        SimpleDateFormat fmt=new SimpleDateFormat("yyyy-MM-dd",Locale.ROOT);
        fmt.setTimeZone(TimeZone.getTimeZone("UTC"));
        return fmt.format(new Date());
    }

    public synchronized int accountUsed(String email){
        try(Cursor c=getReadableDatabase().rawQuery(
            "SELECT used FROM sender_days WHERE email=? AND day=?",
            new String[]{email,utcDay()})){
            return c.moveToFirst()?c.getInt(0):0;
        }
    }

    public synchronized void recordAccountUse(String email){
        SQLiteDatabase db=getWritableDatabase();
        db.beginTransaction();
        try{
            ContentValues values=new ContentValues();
            values.put("email",email);values.put("day",utcDay());values.put("used",0);
            db.insertWithOnConflict("sender_days",null,values,SQLiteDatabase.CONFLICT_IGNORE);
            db.execSQL("UPDATE sender_days SET used=used+1 WHERE email=? AND day=?",
                       new Object[]{email,utcDay()});
            db.setTransactionSuccessful();
        }finally{db.endTransaction();}
    }

    public synchronized Status status(){
        int waiting=0,sent=0,failed=0,uncertain=0,blocked=0;
        try(Cursor c=getReadableDatabase().rawQuery(
            "SELECT status,COUNT(*) FROM delivery GROUP BY status",null)){
            while(c.moveToNext()) {
                String state=c.getString(0);int count=c.getInt(1);
                if(state.equals("queued")||state.equals("processing"))waiting+=count;
                else if(state.equals("sent"))sent+=count;
                else if(state.equals("failed"))failed+=count;
                else if(state.equals("uncertain"))uncertain+=count;
                else if(state.equals("blocked"))blocked+=count;
            }
        }
        return new Status(waiting,sent,failed,uncertain,blocked,isRunning(),
            prefs().getString("last_error",""));
    }
}
