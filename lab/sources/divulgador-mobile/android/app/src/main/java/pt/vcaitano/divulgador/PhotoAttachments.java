package pt.vcaitano.divulgador;

import android.app.Activity;
import android.content.ClipData;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.core.content.FileProvider;

import org.json.JSONArray;
import org.json.JSONException;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.UUID;

/**
 * Anexos do e-mail no Android. Nunca armazena imagens públicas.
 * Copia imagens selecionadas via seletor SAF para o diretório privado do app,
 * compartilha-as apenas para a app escolhida via FileProvider e URI temporária.
 */
public final class PhotoAttachments {
    public static final int PICK_IMAGE_REQUEST = 307;
    private static final int MAX_PHOTOS = 6;
    private static final long MAX_EACH = 10L * 1024 * 1024;
    private static final long MAX_TOTAL = 20L * 1024 * 1024;
    private static final String PREF_KEY = "email_photo_attachments_v1";

    private final Activity activity;
    private final File directory;
    private final ArrayList<File> photos = new ArrayList<>();
    private final LinearLayout thumbnails;
    private final TextView summary;

    public PhotoAttachments(Activity activity, LinearLayout layout) {
        this.activity = activity;
        this.directory = new File(activity.getFilesDir(), "mail_photos");
        if(!directory.exists() && !directory.mkdirs()) {
            Toast.makeText(activity,"Não foi possível criar pasta para fotos",Toast.LENGTH_LONG).show();
        }

        TextView title=new TextView(activity);
        title.setText("Fotos no e-mail");
        title.setTextSize(19);
        title.setTextColor(0xff18243B);
        title.setPadding(0, dp(18),0,dp(5));
        layout.addView(title);

        TextView explanation=new TextView(activity);
        explanation.setText("Anexe até 6 fotos (máximo 20 MB no total). Elas serão incluídas no Gmail ou outro aplicativo de e-mail. Somente o envio confirmado pelo usuário é registrado.");
        explanation.setTextSize(13);
        explanation.setTextColor(0xff5C6272);
        layout.addView(explanation);

        Button add=new Button(activity);
        add.setText("ADICIONAR FOTOS DA GALERIA");
        add.setAllCaps(false);
        add.setOnClickListener(v->select());
        layout.addView(add,new LinearLayout.LayoutParams(-1,dp(50)));

        Button remove=new Button(activity);
        remove.setText("REMOVER TODAS AS FOTOS");
        remove.setAllCaps(false);
        remove.setOnClickListener(v->clear());
        layout.addView(remove,new LinearLayout.LayoutParams(-1,dp(48)));

        summary=new TextView(activity);
        summary.setTextColor(0xff18243B);
        summary.setTextSize(14);
        summary.setPadding(0,dp(5),0,dp(7));
        layout.addView(summary);

        HorizontalScrollView scrolling=new HorizontalScrollView(activity);
        scrolling.setHorizontalScrollBarEnabled(true);
        thumbnails=new LinearLayout(activity);
        thumbnails.setOrientation(LinearLayout.HORIZONTAL);
        scrolling.addView(thumbnails);
        layout.addView(scrolling,new LinearLayout.LayoutParams(-1,dp(133)));
        restore();
        refresh();
    }

    private int dp(int v) {
        return Math.round(v*activity.getResources().getDisplayMetrics().density);
    }

    private void select() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.setType("image/*");
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try {
            activity.startActivityForResult(intent,PICK_IMAGE_REQUEST);
        } catch (Exception error) {
            Toast.makeText(activity,"Não foi possível abrir a galeria de fotos.",Toast.LENGTH_LONG).show();
        }
    }

    public void handleResult(Intent data) {
        if(data==null)return;
        ArrayList<Uri> uris=new ArrayList<>();
        ClipData picked=data.getClipData();
        if(picked!=null) {
            for(int i=0;i<picked.getItemCount();i++)uris.add(picked.getItemAt(i).getUri());
        } else if(data.getData()!=null) {
            uris.add(data.getData());
        }
        if(uris.isEmpty()){
            Toast.makeText(activity,"Nenhuma foto foi selecionada.",Toast.LENGTH_SHORT).show();
            return;
        }
        int imported=0,ignored=0;
        for(Uri uri:uris) {
            if(photos.size()>=MAX_PHOTOS){ignored++;continue;}
            try {
                importPhoto(uri);
                imported++;
            } catch(Exception ex) {
                ignored++;
            }
        }
        save();
        refresh();
        Toast.makeText(activity,imported+" foto(s) adicionada(s)"+(ignored>0?" · Ignoradas: "+ignored:""),Toast.LENGTH_LONG).show();
    }

    private long sumBytes() {
        long total=0;
        for(File p:photos)total+=p.length();
        return total;
    }

    private void importPhoto(Uri uri) throws Exception {
        if(uri==null || !"content".equalsIgnoreCase(uri.getScheme()))
            throw new IllegalArgumentException("Imagem inválida");
        String mime=activity.getContentResolver().getType(uri);
        if(mime==null || !mime.startsWith("image/"))
            throw new IllegalArgumentException("O arquivo deve ser uma foto");

        String ext=".jpg";
        if("image/png".equals(mime)) ext=".png";
        else if("image/webp".equals(mime)) ext=".webp";
        else if("image/heic".equals(mime)||"image/heif".equals(mime))ext=".heic";
        else if("image/gif".equals(mime)) ext=".gif";
        String name="foto_"+UUID.randomUUID().toString().replace("-","")+ext;
        File output=new File(directory,name);
        long currentTotal=sumBytes(), copied=0;
        try(InputStream input=activity.getContentResolver().openInputStream(uri);
            FileOutputStream dst=new FileOutputStream(output)){
            if(input==null)throw new IllegalArgumentException("Foto indisponível");
            byte[] buffer=new byte[16384];
            int n;
            while((n=input.read(buffer))!=-1) {
                copied+=n;
                if(copied>MAX_EACH || currentTotal+copied>MAX_TOTAL)
                    throw new IllegalArgumentException("Fotos maiores que o limite");
                dst.write(buffer,0,n);
            }
        } catch(Exception e){
            output.delete();
            throw e;
        }
        if(copied==0){output.delete();throw new IllegalArgumentException("Foto vazia");}
        photos.add(output);
    }

    public int size(){return photos.size();}

    public ArrayList<Uri> uris(){
        ArrayList<Uri> result=new ArrayList<>();
        for(File file:photos) {
            if(!file.isFile())continue;
            result.add(FileProvider.getUriForFile(activity,
                activity.getPackageName()+".fileprovider",file));
        }
        return result;
    }

    public static void grant(Intent intent,ArrayList<Uri> uris,Activity activity) {
        if(uris.isEmpty())return;
        ClipData clip=ClipData.newUri(activity.getContentResolver(),"fotos",uris.get(0));
        for(int i=1;i<uris.size();i++)clip.addItem(new ClipData.Item(uris.get(i)));
        intent.setClipData(clip);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
    }

    private void clear() {
        for(File f:photos)f.delete();
        photos.clear();
        save();
        refresh();
    }

    private void remove(File file){
        photos.remove(file);
        file.delete();
        save();
        refresh();
    }

    private void save(){
        JSONArray names=new JSONArray();
        for(File f:photos) names.put(f.getName());
        activity.getPreferences(Activity.MODE_PRIVATE).edit()
            .putString(PREF_KEY,names.toString()).apply();
    }

    private void restore(){
        try {
            JSONArray items=new JSONArray(activity.getPreferences(Activity.MODE_PRIVATE).getString(PREF_KEY,"[]"));
            HashSet<String> found=new HashSet<>();
            for(int i=0;i<items.length() && photos.size()<MAX_PHOTOS;i++){
                String name=items.optString(i,"");
                if(!name.matches("foto_[a-f0-9]{32}\\.(jpg|png|webp|heic|gif)")||!found.add(name))continue;
                File file=new File(directory,name);
                if(file.isFile() && file.length()>0 && file.length()<=MAX_EACH)
                    photos.add(file);
            }
        }catch(Exception ignored){}
    }

    private void refresh() {
        thumbnails.removeAllViews();
        summary.setText(photos.size()+" foto(s) selecionada(s) · "+(sumBytes()/1024)+" KB");
        for(File file:new ArrayList<>(photos)){
            LinearLayout item=new LinearLayout(activity);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setPadding(dp(3),dp(3),dp(8),dp(3));
            ImageView picture=new ImageView(activity);
            picture.setScaleType(ImageView.ScaleType.CENTER_CROP);
            BitmapFactory.Options opt=new BitmapFactory.Options();
            opt.inJustDecodeBounds=true;
            BitmapFactory.decodeFile(file.getAbsolutePath(),opt);
            int larger=Math.max(opt.outWidth,opt.outHeight);
            opt.inSampleSize=Math.max(1,larger/140);
            opt.inJustDecodeBounds=false;
            Bitmap bmp=BitmapFactory.decodeFile(file.getAbsolutePath(),opt);
            if(bmp!=null)picture.setImageBitmap(bmp);
            item.addView(picture,new LinearLayout.LayoutParams(dp(88),dp(88)));

            Button removeOne=new Button(activity);
            removeOne.setAllCaps(false);
            removeOne.setText("Remover");
            removeOne.setTextSize(11);
            removeOne.setPadding(0,0,0,0);
            removeOne.setOnClickListener(v->remove(file));
            item.addView(removeOne,new LinearLayout.LayoutParams(dp(88),dp(35)));
            thumbnails.addView(item);
        }
    }
}
