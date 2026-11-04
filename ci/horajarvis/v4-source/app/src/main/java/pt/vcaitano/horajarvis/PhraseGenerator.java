package pt.vcaitano.horajarvis;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Calendar;

/** 32 x 24 x 20 = 15.360 combinações. Permutação evita repetições consecutivas. */
public final class PhraseGenerator {
    private static final String[] GREETINGS = {
        "Senhor,", "Muito bem, senhor.", "Com licença, senhor.", "À sua disposição, senhor.",
        "Uma informação, senhor.", "Senhor, atenção ao horário.", "Conforme solicitado, senhor.",
        "Passando para informar, senhor.", "Registro de horário, senhor.", "Atualização de horário, senhor.",
        "Senhor, aqui está o horário.", "Informação do seu assistente, senhor.",
        "Senhor, espero não interromper.", "Um breve aviso, senhor.", "Hora do relatório, senhor.",
        "Precisamente, senhor.", "Pelo relógio, senhor.", "Senhor, já chegou a hora.",
        "Uma rápida atualização, senhor.", "Senhor, tenho a hora atual.", "Como combinado, senhor.",
        "De acordo com a sua programação, senhor.", "Senhor, aviso programado.",
        "Seu lembrete de horário, senhor.", "Novo aviso, senhor.", "Hora de conferir o relógio, senhor.",
        "Pronto, senhor.", "Estou a acompanhar o tempo, senhor.", "Senhor, pontualmente.",
        "O relógio acaba de marcar o horário, senhor.", "Relatório pontual, senhor.",
        "Senhor, atualização concluída."
    };
    private static final String[] LEADS = {
        "Agora", "Neste momento", "Exatamente agora", "O relógio indica que agora", 
        "Pelo horário atual, agora", "De acordo com o relógio, agora",
        "Neste instante", "Na hora marcada, agora", "O horário deste momento indica que agora",
        "Conferindo a hora, agora", "A informação atual é que agora", "No momento presente, agora",
        "Pela contagem do tempo, agora", "Ao verificar o relógio, agora",
        "A marcação atual indica que agora", "Com precisão, agora",
        "Aqui está o horário: agora", "O horário confirmado é este: agora",
        "Na sua hora local, agora", "O tempo segue: agora", "A marcação neste instante é: agora",
        "Sem atraso, agora", "Conforme programado, agora", "A hora exata indica que agora"
    };
    private static final String[] ENDINGS = {
        "", "Tudo em ordem.", "Aviso concluído.", "Continuo atento ao relógio.",
        "Até ao próximo horário.", "Sigo à disposição.", "Tempo atualizado.",
        "Missão cumprida.", "Seguimos com a programação.", "O tempo não para.",
        "Mais um horário registado.", "Continuo a acompanhar os minutos.",
        "Registo efetuado.", "O próximo aviso virá no horário programado.",
        "Horário confirmado.", "A sua programação continua ativa.",
        "Informação entregue.", "Vou continuar de olho no tempo.",
        "Acompanhamento em curso.", "Tudo devidamente sincronizado."
    };
    public static final int COMBINATIONS = GREETINGS.length * LEADS.length * ENDINGS.length;
    private PhraseGenerator() { }

    public static synchronized String next(Context context, Calendar when) {
        SharedPreferences prefs = context.getSharedPreferences("horajarvis_phrases", Context.MODE_PRIVATE);
        long count = prefs.getLong("sequence", 0L);
        prefs.edit().putLong("sequence", count + 1).apply();
        int index = (int) Math.floorMod(count * 7919L + 157L, COMBINATIONS);
        int greet = index % GREETINGS.length;
        int lead = (index / GREETINGS.length) % LEADS.length;
        int ending = (index / (GREETINGS.length * LEADS.length)) % ENDINGS.length;
        String result = GREETINGS[greet] + " " + LEADS[lead] + " " + humanTime(when) + ".";
        if (!ENDINGS[ending].isEmpty()) result += " " + ENDINGS[ending];
        return result;
    }

    /** A notificação, a tela de aviso e a voz usam a mesma frase gerada. */
    public static String accordingToSettings(Context context, Calendar now) {
        return forSettings(context, now, AppSettings.load(context));
    }

    /** Permite também pré-visualizar as opções ainda não salvas na tela principal. */
    public static String forSettings(Context context, Calendar now, AppSettings config) {
        if (config.customSpeech) {
            String personalized = customAt(config.customSpeechLines, now);
            if (personalized != null) {
                // {hora} insere a hora corrente no local escrito pelo utilizador.
                // Sem marcador, a hora é anunciada antes do texto personalizado.
                if (personalized.contains("{hora}"))
                    return personalized.replace("{hora}", humanTime(now));
                return shortPhrase(now) + ". " + personalized;
            }
        }
        if (config.conciseSpeech) return shortPhrase(now);
        return next(context, now);
    }

    /** Aceita texto geral e linhas opcionais HH:MM | frase. Não cria novos alarmes. */
    public static void validateCustomLines(String raw) {
        if (raw == null || raw.trim().isEmpty())
            throw new IllegalArgumentException("Escreva uma frase ou desative esta opção.");
        if (raw.length() > 3500)
            throw new IllegalArgumentException("Use no máximo 3500 caracteres.");
        boolean found = false;
        for (String line : raw.split("\\r?\\n")) {
            String item = line.trim();
            if (item.isEmpty()) continue;
            found = true;
            int separator = item.indexOf('|');
            if (separator >= 0) {
                String hour = item.substring(0, separator).trim();
                String message = item.substring(separator + 1).trim();
                if (message.isEmpty())
                    throw new IllegalArgumentException("Falta o texto após | no horário " + hour);
                try {
                    if (CustomTimes.parse(hour).size() != 1)
                        throw new IllegalArgumentException("Hora inválida: " + hour);
                } catch (IllegalArgumentException invalid) {
                    throw new IllegalArgumentException("Use HH:MM | frase. Hora inválida: " + hour);
                }
            }
        }
        if (!found) throw new IllegalArgumentException("Escreva ao menos uma frase.");
    }

    private static String customAt(String raw, Calendar when) {
        if (raw == null || raw.trim().isEmpty()) return null;
        int minuteOfDay = when.get(Calendar.HOUR_OF_DAY) * 60 + when.get(Calendar.MINUTE);
        String general = null;
        String exact = null;
        for (String line : raw.split("\\r?\\n")) {
            String item = line.trim();
            if (item.isEmpty()) continue;
            int separator = item.indexOf('|');
            if (separator < 0) {
                general = item;
            } else {
                try {
                    java.util.List<Integer> times = CustomTimes.parse(item.substring(0, separator));
                    String message = item.substring(separator + 1).trim();
                    if (times.size() == 1 && times.get(0) == minuteOfDay && !message.isEmpty())
                        exact = message;
                } catch (IllegalArgumentException ignored) {
                    // Preferência antiga/externa inválida: usa a frase padrão.
                }
            }
        }
        return exact != null ? exact : general;
    }

    /** Sem texto adicional para caber na notificação do relógio. */
    public static String shortPhrase(Calendar when) {
        int h = when.get(Calendar.HOUR_OF_DAY);
        int m = when.get(Calendar.MINUTE);
        String base = h == 1 ? "É uma hora" : "São " + h + " horas";
        if (m == 0) return base;
        return base + " e " + m + (m == 1 ? " minuto" : " minutos");
    }

    public static String humanTime(Calendar now) {
        int h = now.get(Calendar.HOUR_OF_DAY);
        int m = now.get(Calendar.MINUTE);
        String base;
        if (h == 0) base = "é meia-noite";
        else if (h == 12) base = "é meio-dia";
        else if (h == 1) base = "é uma hora";
        else base = "são " + h + " horas";
        if (m == 0) return base + " em ponto";
        return base + " e " + m + (m == 1 ? " minuto" : " minutos");
    }
}
