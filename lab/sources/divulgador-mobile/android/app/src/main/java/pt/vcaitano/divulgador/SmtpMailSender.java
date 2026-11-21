package pt.vcaitano.divulgador;

import android.content.Context;
import android.net.Uri;

import java.io.File;
import java.util.ArrayList;
import java.util.Date;
import java.util.Properties;

import javax.mail.AuthenticationFailedException;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeBodyPart;
import javax.mail.internet.MimeMessage;
import javax.mail.internet.MimeMultipart;

/**
 * Gmail SMTP over TLS/SSL (465). Needs a Google 16-character App Password
 * associated with the account, not the regular password.
 * No bypass of Gmail quotas; provider errors pause the whole queue.
 */
public final class SmtpMailSender {
    private SmtpMailSender(){}

    private static Session session() {
        Properties properties=new Properties();
        properties.put("mail.smtp.host","smtp.gmail.com");
        properties.put("mail.smtp.port","465");
        properties.put("mail.smtp.auth","true");
        properties.put("mail.smtp.ssl.enable","true");
        properties.put("mail.smtp.ssl.checkserveridentity","true");
        properties.put("mail.smtp.connectiontimeout","20000");
        properties.put("mail.smtp.timeout","30000");
        properties.put("mail.smtp.writetimeout","30000");
        return Session.getInstance(properties);
    }

    public static void test(GmailAccounts.Account sender) throws MessagingException {
        Transport transport=session().getTransport("smtp");
        try {
            transport.connect("smtp.gmail.com",465,sender.email,sender.appPassword);
        } finally {
            try{transport.close();}catch(Exception ignored){}
        }
    }

    private static String fill(String template,AutoMailQueue.Job job){
        String name=job.name==null||job.name.isEmpty()?"tudo bem?":job.name;
        return template.replace("{nome}",name)
            .replace("{produto}",job.product==null?"":job.product)
            .replace("{link}",job.link==null?"":job.link);
    }

    public static void send(Context context,GmailAccounts.Account sender,
                            AutoMailQueue.Job job) throws Exception {
        if(job.email==null || !job.email.matches("^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"))
            throw new IllegalArgumentException("Email de destino inválido");
        MimeMessage mail=new MimeMessage(session());
        mail.setFrom(new InternetAddress(sender.email));
        mail.setRecipient(Message.RecipientType.TO,new InternetAddress(job.email));
        mail.setReplyTo(new InternetAddress[]{new InternetAddress(sender.email)});
        mail.setSubject(fill(job.subject,job),"UTF-8");
        mail.setSentDate(new Date());
        String content=fill(job.body,job);
        if(!content.contains("REMOVER")&&!content.toLowerCase().contains("descadastr")){
            content+="\n\nPara não receber outras mensagens, responda REMOVER.";
        }
        // Also allow the recipient to send an unsubscribe request using their mail client.
        mail.setHeader("List-Unsubscribe","<mailto:"+sender.email+"?subject=REMOVER>");

        File folder=new File(context.getFilesDir(),"mail_photos");
        File[] stored=folder.listFiles();
        ArrayList<File> files=new ArrayList<>();
        long total=0;
        if(stored!=null)for(File file:stored){
            if(!file.isFile()||!file.getName().matches("foto_[a-f0-9]{32}\\.(jpg|png|webp|heic|gif)"))
                continue;
            if(files.size()==6)break;
            total+=file.length();
            if(total>20L*1024*1024)throw new IllegalArgumentException("Anexos excedem 20 MB");
            files.add(file);
        }

        if(files.isEmpty()) {
            mail.setText(content,"UTF-8");
        }else{
            MimeMultipart multipart=new MimeMultipart("mixed");
            MimeBodyPart text=new MimeBodyPart();
            text.setText(content,"UTF-8");
            multipart.addBodyPart(text);
            for(File file:files) {
                MimeBodyPart attachment=new MimeBodyPart();
                attachment.attachFile(file);
                multipart.addBodyPart(attachment);
            }
            mail.setContent(multipart);
        }
        mail.saveChanges();

        Transport smtp=session().getTransport("smtp");
        try{
            smtp.connect("smtp.gmail.com",465,sender.email,sender.appPassword);
            smtp.sendMessage(mail,mail.getAllRecipients());
        } finally{
            try{smtp.close();}catch(Exception ignored){}
        }
    }

    /** Provider limit and auth errors must pause the entire queue, not rotate. */
    public static boolean providerBlocked(Exception error){
        if(error instanceof AuthenticationFailedException)return true;
        String message=String.valueOf(error.getMessage()).toLowerCase(java.util.Locale.ROOT);
        return message.contains("quota")||message.contains("rate limit")||
            message.contains("too many")||message.contains("daily")||
            message.contains("authentication")||message.contains("app password")||
            message.contains("535")||message.contains("421")||
            message.contains("454")||message.contains("temporarily blocked")||
            message.contains("unsolicited")||message.contains("spam");
    }

    public static String safeError(Exception error){
        if(error instanceof AuthenticationFailedException)
            return "Gmail recusou a autenticação; confira a senha de app.";
        if(providerBlocked(error))
            return "Gmail limitou ou bloqueou o envio. Campanha pausada.";
        if(error instanceof MessagingException)
            return "Falha de comunicação SMTP. Confirme na caixa Enviados.";
        return "Erro de envio: "+error.getClass().getSimpleName();
    }
}
