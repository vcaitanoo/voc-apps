package pt.vcaitano.divulgador;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.work.Constraints;
import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.ExistingWorkPolicy;
import androidx.work.NetworkType;
import androidx.work.OneTimeWorkRequest;
import androidx.work.PeriodicWorkRequest;
import androidx.work.Worker;
import androidx.work.WorkerParameters;
import androidx.work.WorkManager;

import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

/**
 * Fully automatic scheduling when authorized by user. No compose UI per email.
 * WorkManager is OS-managed and may delay work on battery saver / Android Doze.
 * Hard floor of 30 seconds between consecutive messages. Provider quota blocks
 * pause the entire batch, never automatically hop to another Gmail account.
 */
public final class AutoMailWorker extends Worker {
    private static final Object GLOBAL_LOCK=new Object();
    private static final String PERIODIC="divulgador_gmail_15min";
    private static final String IMMEDIATE="divulgador_gmail_first";
    private static final int BATCH_MAX=8;
    private static final int MIN_INTERVAL_MS=30000;
    public AutoMailWorker(@NonNull Context context,@NonNull WorkerParameters params){
        super(context,params);
    }

    private static Constraints network(){
        return new Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build();
    }

    public static void start(Context context){
        AutoMailQueue queue=new AutoMailQueue(context);
        queue.setRunning(true);
        queue.setError("");
        WorkManager manager=WorkManager.getInstance(context);
        PeriodicWorkRequest recurring=new PeriodicWorkRequest.Builder(
            AutoMailWorker.class,15,TimeUnit.MINUTES).setConstraints(network()).build();
        manager.enqueueUniquePeriodicWork(PERIODIC,ExistingPeriodicWorkPolicy.KEEP,recurring);
        OneTimeWorkRequest initial=new OneTimeWorkRequest.Builder(AutoMailWorker.class)
            .setConstraints(network()).build();
        manager.enqueueUniqueWork(IMMEDIATE,ExistingWorkPolicy.KEEP,initial);
    }

    public static void pause(Context context){
        new AutoMailQueue(context).setRunning(false);
        WorkManager manager=WorkManager.getInstance(context);
        manager.cancelUniqueWork(PERIODIC);
        manager.cancelUniqueWork(IMMEDIATE);
    }

    @NonNull
    @Override public Result doWork(){
        synchronized(GLOBAL_LOCK){
            Context context=getApplicationContext();
            AutoMailQueue queue=new AutoMailQueue(context);
            if(!queue.isRunning())return Result.success();
            // Old 'processing' row could have been delivered just before process death.
            queue.recoverInterrupted();
            try{
                ArrayList<GmailAccounts.Account> accounts=new GmailAccounts(context).list();
                ArrayList<GmailAccounts.Account> enabled=new ArrayList<>();
                for(GmailAccounts.Account account:accounts)if(account.enabled)enabled.add(account);
                if(enabled.isEmpty()){
                    queue.setError("Adicione uma conta Gmail com senha de app para ativar o envio.");
                    queue.setRunning(false);
                    return Result.success();
                }

                for(int i=0;i<BATCH_MAX && !isStopped();i++){
                    if(!queue.isRunning())break;
                    AutoMailQueue.Status state=queue.status();
                    if(state.waiting==0) {
                        queue.setRunning(false);
                        break;
                    }
                    GmailAccounts.Account sender=selectAccount(queue,enabled);
                    if(sender==null){
                        queue.setError("Limite diário configurado para todas as contas: aguardando próximo dia UTC.");
                        // No sending beyond cap. Periodic scheduler will try next cycle.
                        break;
                    }
                    long remaining=MIN_INTERVAL_MS-(System.currentTimeMillis()-queue.lastSentMillis());
                    if(remaining>0){
                        try{Thread.sleep(Math.min(remaining,MIN_INTERVAL_MS));}
                        catch(InterruptedException interrupted){
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                    if(isStopped() || !queue.isRunning())break;
                    AutoMailQueue.Job job=queue.claim();
                    if(job==null)break;
                    try{
                        SmtpMailSender.send(context,sender,job);
                        queue.markSent(job,sender.email);
                        queue.recordAccountUse(sender.email);
                        queue.setAccountCursor(queue.accountCursor()+1);
                        queue.setError("");
                    }catch(Exception error){
                        String reason=SmtpMailSender.safeError(error);
                        // Be conservative: unknown SMTP results must not be resent automatically.
                        boolean uncertain=!SmtpMailSender.providerBlocked(error);
                        queue.markPendingOrUncertain(job,reason,uncertain);
                        queue.setError(reason);
                        if(SmtpMailSender.providerBlocked(error)){
                            queue.setRunning(false);
                        }
                        break;
                    }
                }
            }catch(Exception error){
                queue.setError("Fila pausada devido a erro interno. Confira contas e mensagens.");
                queue.setRunning(false);
            }finally{queue.close();}
            return Result.success();
        }
    }

    private static GmailAccounts.Account selectAccount(AutoMailQueue queue,
                    ArrayList<GmailAccounts.Account> accounts){
        if(accounts.isEmpty())return null;
        int start=Math.floorMod(queue.accountCursor(),accounts.size());
        for(int i=0;i<accounts.size();i++){
            GmailAccounts.Account a=accounts.get((start+i)%accounts.size());
            if(queue.accountUsed(a.email)<a.dailyCap)return a;
        }
        return null;
    }
}
