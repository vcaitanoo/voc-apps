package pt.vcaitano.horajarvis;

import java.util.Calendar;

public final class CustomSpeechRegression {
    private static Calendar at(int h, int m) {
        Calendar c = Calendar.getInstance();
        c.set(Calendar.HOUR_OF_DAY, h);
        c.set(Calendar.MINUTE, m);
        return c;
    }
    private static void eq(String expected, String actual, String caseName) {
        if (!expected.equals(actual))
            throw new AssertionError(caseName + ": esperado [" + expected + "], recebido [" + actual + "]");
    }
    public static void main(String[] args) {
        Calendar noon40 = at(12,40);
        String human = "são 12 horas e 40 minutos";
        String shortTime = "São 12 horas e 40 minutos";
        eq("Olá, são 12h40. Tirar a parenteral da geladeira.",
           CustomSpeech.format("Olá, são 12h40. Tirar a parenteral da geladeira.",noon40,human,shortTime),
           "expressao 12h40");
        eq("Olá, são 12:40. Lembrete de hoje.",
           CustomSpeech.format("Olá, são 12:40. Lembrete de hoje.",noon40,human,shortTime),
           "expressao 12:40");
        eq("Olha, já são 12 horas e 40 minutos. Aviso importante.",
           CustomSpeech.format("Olha, já são 12 horas e 40 minutos. Aviso importante.",noon40,human,shortTime),
           "expressao hora completa");
        eq("Agora são 12 e 40. Aviso importante.",
           CustomSpeech.format("Agora são 12 e 40. Aviso importante.",noon40,human,shortTime),
           "expressao numeros falados");
        eq("São 12 horas e 40 minutos. Tirar da geladeira.",
           CustomSpeech.format("Tirar da geladeira.",noon40,human,shortTime),
           "sem horario adiciona hora");
        eq("São 12 horas e 40 minutos. Buscar o filho às 17h.",
           CustomSpeech.format("Buscar o filho às 17h.",noon40,human,shortTime),
           "horario diferente nao suprime hora atual");
        eq("Olá, são 12 horas e 40 minutos. Tirar da geladeira.",
           CustomSpeech.format("Olá, {hora}. Tirar da geladeira.",noon40,human,shortTime),
           "marcador em local escolhido");
        Calendar five = at(17,0);
        eq("Olha, já dão 17h. Melhor buscar seu filho.",
           CustomSpeech.format("Olha, já dão 17h. Melhor buscar seu filho.",five,"são 17 horas em ponto","São 17 horas"),
           "17h sem minuto");
        eq("São 17 horas. Buscar criança.",
           CustomSpeech.format("Buscar criança.",five,"são 17 horas em ponto","São 17 horas"),
           "hora curta");
        eq("Já é meio-dia! Preparar almoço.",
           CustomSpeech.format("Já é meio-dia! Preparar almoço.",at(12,0),"é meio-dia em ponto","São 12 horas"),
           "meio-dia");
        System.out.println("REGRESSAO_FALA_PERSONALIZADA_OK 10 testes");
    }
}
