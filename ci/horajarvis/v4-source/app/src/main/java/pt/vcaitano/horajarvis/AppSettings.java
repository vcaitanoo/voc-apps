package pt.vcaitano.horajarvis;

import android.content.Context;
import android.content.SharedPreferences;

/** Configuração local; segunda-feira corresponde ao bit zero do campo dias. */
public final class AppSettings {
    public boolean enabled = false; // O utilizador escolhe explicitamente ativar.
    public int daysMask = 127;       // Sete dias da semana.
    public int startMinute = 8 * 60;
    public int endMinute = 22 * 60;
    public int intervalMinute = 60;
    // Modos novos: mantemos o intervalo original por defeito (migração sem perder dados).
    public boolean customMode = false;
    public String customTimes = "13:00, 15:00, 16:50, 17:00";
    public boolean vibrate = true;
    public boolean fullScreen = true;
    /** false = frases variadas da v1.1.0; true = apenas a hora, sem saudações. */
    public boolean conciseSpeech = false;
    /** Frases livres: texto geral ou linhas HH:MM | mensagem. */
    public boolean customSpeech = false;
    public String customSpeechLines = "";

    public static AppSettings load(Context context) {
        SharedPreferences prefs = context.getSharedPreferences("horajarvis", Context.MODE_PRIVATE);
        AppSettings result = new AppSettings();
        result.enabled = prefs.getBoolean("enabled", result.enabled);
        result.daysMask = prefs.getInt("days", result.daysMask);
        result.startMinute = prefs.getInt("start", result.startMinute);
        result.endMinute = prefs.getInt("end", result.endMinute);
        result.intervalMinute = prefs.getInt("interval", result.intervalMinute);
        result.customMode = prefs.getBoolean("customMode", result.customMode);
        result.customTimes = prefs.getString("customTimes", result.customTimes);
        result.vibrate = prefs.getBoolean("vibrate", result.vibrate);
        result.fullScreen = prefs.getBoolean("fullScreen", result.fullScreen);
        result.conciseSpeech = prefs.getBoolean("conciseSpeech", result.conciseSpeech);
        result.customSpeech = prefs.getBoolean("customSpeech", result.customSpeech);
        result.customSpeechLines = prefs.getString("customSpeechLines", result.customSpeechLines);
        result.daysMask &= 127;
        result.startMinute = clamp(result.startMinute, 0, 1439);
        result.endMinute = clamp(result.endMinute, 0, 1439);
        result.intervalMinute = clamp(result.intervalMinute, 15, 720);
        return result;
    }

    public void save(Context context) {
        context.getSharedPreferences("horajarvis", Context.MODE_PRIVATE).edit()
            .putBoolean("enabled", enabled)
            .putInt("days", daysMask)
            .putInt("start", startMinute)
            .putInt("end", endMinute)
            .putInt("interval", intervalMinute)
            .putBoolean("customMode", customMode)
            .putString("customTimes", customTimes)
            .putBoolean("vibrate", vibrate)
            .putBoolean("fullScreen", fullScreen)
            .putBoolean("conciseSpeech", conciseSpeech)
            .putBoolean("customSpeech", customSpeech)
            .putString("customSpeechLines", customSpeechLines)
            .apply();
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }
}
