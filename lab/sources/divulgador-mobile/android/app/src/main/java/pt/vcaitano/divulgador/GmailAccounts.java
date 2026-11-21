package pt.vcaitano.divulgador;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Locale;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/**
 * Gmail SMTP accounts kept encrypted with AndroidKeyStore AES-GCM.
 * Only Gmail app passwords, NEVER the regular Google account password.
 * Removing the Android app destroys this local secret store.
 */
public final class GmailAccounts {
    private static final String ALIAS="pt.vcaitano.divulgadormobile.smtp.v1";
    private static final String FILE="gmail_accounts_secure_v1";
    private static final String FIELD="accounts";
    private static final String EMAIL_RE="[A-Za-z0-9._%+\\-]+@(?:gmail\\.com|googlemail\\.com)";
    private final Context context;

    public static final class Account {
        public final String email;
        public final String appPassword;
        public final boolean enabled;
        public final int dailyCap;
        Account(String email,String appPassword,boolean enabled,int dailyCap){
            this.email=email;this.appPassword=appPassword;this.enabled=enabled;this.dailyCap=dailyCap;
        }
    }

    public GmailAccounts(Context context){this.context=context.getApplicationContext();}

    private static String normalEmail(String text) {
        String email=text==null?"":text.trim().toLowerCase(Locale.ROOT);
        if(!email.matches(EMAIL_RE))throw new IllegalArgumentException("Insira uma conta @gmail.com válida.");
        return email;
    }

    private SecretKey key() throws Exception {
        KeyStore store=KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        KeyStore.Entry e=store.getEntry(ALIAS,null);
        if(e instanceof KeyStore.SecretKeyEntry)return ((KeyStore.SecretKeyEntry)e).getSecretKey();
        KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(ALIAS,
            KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256).build());
        return generator.generateKey();
    }

    private synchronized JSONArray read() throws Exception {
        SharedPreferences prefs=context.getSharedPreferences(FILE,Context.MODE_PRIVATE);
        String value=prefs.getString(FIELD,"");
        if(value.isEmpty())return new JSONArray();
        byte[] packed=Base64.decode(value,Base64.NO_WRAP);
        if(packed.length<28)throw new IllegalStateException("Dados de contas inválidos.");
        byte[] iv=new byte[12],ciphertext=new byte[packed.length-12];
        System.arraycopy(packed,0,iv,0,iv.length);
        System.arraycopy(packed,iv.length,ciphertext,0,ciphertext.length);
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE,key(),new GCMParameterSpec(128,iv));
        return new JSONArray(new String(cipher.doFinal(ciphertext),StandardCharsets.UTF_8));
    }

    private synchronized void write(JSONArray list) throws Exception {
        Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE,key());
        byte[] iv=cipher.getIV();
        byte[] secret=cipher.doFinal(list.toString().getBytes(StandardCharsets.UTF_8));
        byte[] packed=new byte[iv.length+secret.length];
        System.arraycopy(iv,0,packed,0,iv.length);
        System.arraycopy(secret,0,packed,iv.length,secret.length);
        String encoded=Base64.encodeToString(packed,Base64.NO_WRAP);
        if(!context.getSharedPreferences(FILE,Context.MODE_PRIVATE)
           .edit().putString(FIELD,encoded).commit()) {
            throw new IllegalStateException("Falha ao guardar conta criptografada.");
        }
    }

    public synchronized ArrayList<Account> list() throws Exception {
        JSONArray arr=read();
        ArrayList<Account> out=new ArrayList<>();
        for(int i=0;i<arr.length();i++){
            JSONObject entry=arr.getJSONObject(i);
            out.add(new Account(
                entry.getString("email"),entry.getString("password"),
                entry.optBoolean("enabled",true),entry.optInt("dailyCap",40)));
        }
        return out;
    }

    public synchronized void add(String email,String appPassword,int dailyCap) throws Exception {
        email=normalEmail(email);
        String password=appPassword==null?"":appPassword.replaceAll("\\s+","");
        if(password.length()!=16)throw new IllegalArgumentException(
            "Use uma senha de app Google de 16 caracteres; não use sua senha Gmail normal.");
        if(dailyCap<1||dailyCap>100)throw new IllegalArgumentException("Limite de 1 a 100 mensagens por dia.");
        JSONArray list=read(), next=new JSONArray();
        for(int i=0;i<list.length();i++){
            JSONObject e=list.getJSONObject(i);
            if(!email.equals(e.optString("email")))next.put(e);
        }
        next.put(new JSONObject().put("email",email).put("password",password)
            .put("enabled",true).put("dailyCap",dailyCap));
        write(next);
    }

    public synchronized void remove(String email) throws Exception {
        JSONArray list=read(), next=new JSONArray();
        for(int i=0;i<list.length();i++){
            JSONObject e=list.getJSONObject(i);
            if(!e.optString("email").equalsIgnoreCase(email))next.put(e);
        }
        write(next);
    }

    public synchronized void setEnabled(String email,boolean enabled) throws Exception {
        JSONArray list=read();
        for(int i=0;i<list.length();i++){
            JSONObject e=list.getJSONObject(i);
            if(e.optString("email").equalsIgnoreCase(email))e.put("enabled",enabled);
        }
        write(list);
    }
}
