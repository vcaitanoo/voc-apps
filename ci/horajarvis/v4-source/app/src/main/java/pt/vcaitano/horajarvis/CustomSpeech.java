package pt.vcaitano.horajarvis;

import java.util.Calendar;
import java.util.Locale;
import java.util.regex.Pattern;

/** Aplica o texto personalizado uma unica vez, sem duplicar a hora dita pelo usuario. */
public final class CustomSpeech {
    private CustomSpeech() { }

    public static String format(String phrase, Calendar when, String humanTime, String shortTime) {
        if (phrase.contains("{hora}")) {
            return phrase.replace("{hora}", humanTime);
        }
        if (mentionsCurrentTime(phrase, when, humanTime, shortTime)) {
            return phrase;
        }
        return shortTime + ". " + phrase;
    }

    private static boolean mentionsCurrentTime(String phrase, Calendar when, String humanTime, String shortTime) {
        String normalized = phrase.toLowerCase(Locale.ROOT);
        if (normalized.contains(humanTime.toLowerCase(Locale.ROOT))
                || normalized.contains(shortTime.toLowerCase(Locale.ROOT))) {
            return true;
        }

        int hour = when.get(Calendar.HOUR_OF_DAY);
        int minute = when.get(Calendar.MINUTE);

        // "12h40", "12:40", "12 h 40", "12h4", "12:04", com zero opcional.
        String fullTime = "(?<!\\d)0?" + hour + "\\s*(?:h|:)\\s*0?" + minute + "(?!\\d)";
        if (Pattern.compile(fullTime, Pattern.CASE_INSENSITIVE).matcher(phrase).find()) {
            return true;
        }

        // "sao 12 e 40", quando a pessoa ja diz o horario por extenso parcial.
        String spokenNumber = "(?iu)\\b(?:são|sao|é|e|deu|deram|dão|dao)\\s+0?"
                + hour + "\\s+e\\s+0?" + minute + "\\b";
        if (Pattern.compile(spokenNumber).matcher(phrase).find()) {
            return true;
        }

        // "ja sao 12h" e "ja sao 12 horas": hora ja mencionada no anuncio.
        String statedHour = "(?iu)\\b(?:são|sao|é|e|deu|deram|dão|dao|marcou)\\s+0?"
                + hour + "\\s*(?:h\\b|horas?\\b)";
        if (Pattern.compile(statedHour).matcher(phrase).find()) {
            return true;
        }

        if (minute == 0) {
            if (hour == 0 && normalized.contains("meia-noite")) return true;
            if (hour == 12 && normalized.contains("meio-dia")) return true;
        }
        return false;
    }
}
