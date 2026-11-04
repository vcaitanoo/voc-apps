package pt.vcaitano.horajarvis;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.TreeSet;

/** Cada hora é um minuto do dia (0...1439), sem restrição de intervalo. */
public final class CustomTimes {
    private CustomTimes() { }

    public static List<Integer> parse(String raw) {
        TreeSet<Integer> minutes = new TreeSet<>();
        if (raw == null || raw.trim().isEmpty()) return new ArrayList<>();
        for (String token : raw.split("[,;\\n\\r]+")) {
            String item = token.trim().toLowerCase(Locale.ROOT).replace('h', ':');
            if (item.isEmpty()) continue;
            String[] parts = item.split(":", -1);
            if (parts.length > 2 || parts.length < 1) throw new IllegalArgumentException("Hora inválida: " + token.trim());
            int hour, minute = 0;
            try {
                hour = Integer.parseInt(parts[0].trim());
                if (parts.length == 2 && !parts[1].trim().isEmpty()) minute = Integer.parseInt(parts[1].trim());
            } catch (NumberFormatException ex) { throw new IllegalArgumentException("Hora inválida: " + token.trim()); }
            if (hour < 0 || hour > 23 || minute < 0 || minute > 59)
                throw new IllegalArgumentException("Escolha uma hora entre 00:00 e 23:59: " + token.trim());
            minutes.add(hour * 60 + minute);
        }
        return new ArrayList<>(minutes);
    }

    public static String normalize(String input) {
        StringBuilder result = new StringBuilder();
        for (int minute : parse(input)) {
            if (result.length() > 0) result.append(", ");
            result.append(String.format(Locale.ROOT, "%02d:%02d", minute / 60, minute % 60));
        }
        return result.toString();
    }
}
