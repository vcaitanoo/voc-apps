package pt.vcaitano.divulgador;

import java.io.StringWriter;
import java.util.Arrays;
import java.util.ArrayList;

public final class CsvFormatTest {
    private static void check(boolean condition,String message) {
        if(!condition)throw new AssertionError(message);
    }
    private static void generatedAndReimport() throws Exception {
        StringWriter out=new StringWriter();
        CsvFormat.writeGenerated(out,Arrays.asList(
            new String[]{"Rui Costa","ptruicosta@gmail.com","Porto","32"},
            new String[]{"Sara; Fragoso","pt.sarafragoso@gmail.com","Lisboa","28"}
        ));
        String text=out.toString();
        check(text.startsWith("\uFEFFEmail;Nome;Cidade;Idade;Consentimento\r\n"),"Cabeçalho Excel Portugal");
        ArrayList<String[]> rows=CsvFormat.parse(text);
        check(rows.size()==3,"Header + 2 registros");
        check(rows.get(0).length==5,"5 colunas reais");
        check(rows.get(0)[0].equals("Email"),"Email primeira coluna");
        check(rows.get(0)[4].equals("Consentimento"),"Consentimento declarado");
        check(rows.get(1)[0].equals("ptruicosta@gmail.com"),"Email integra lista");
        check(rows.get(1)[1].equals("Rui Costa"),"Nome não mudou");
        check(rows.get(1)[4].equals("nao"),"Não inventa consentimento");
        check(rows.get(2)[1].equals("Sara; Fragoso"),"Campo escapado com ponto e vírgula");
    }
    private static void commaAndMultiline() {
        ArrayList<String[]> r=CsvFormat.parse("\uFEFFNome,Email,Consentimento\r\n\"Costa, Rui\",pt.ruicosta@gmail.com,sim\r\n");
        check(r.size()==2,"Cabeçalho e registro CSV com vírgulas");
        check(r.get(1)[0].equals("Costa, Rui"),"Aspas CSV");
        check(r.get(1)[1].equals("pt.ruicosta@gmail.com"),"Email normal");
        ArrayList<String[]> multiline=CsvFormat.parse("Email;Nome\r\nx@example.test;\"Nome\nCom quebra\"\r\n");
        check(multiline.get(1)[1].equals("Nome\nCom quebra"),"Campo multilinha");
    }
    private static void tabsAndNoConsent() {
        ArrayList<String[]> r=CsvFormat.parse("Email\tNome\nx@example.test\tJoão\n");
        check(r.size()==2 && r.get(0).length==2,"TSV e consentimento opcional");
        check(r.get(1)[0].equals("x@example.test"),"Email TSV");
    }
    public static void main(String[] args) throws Exception {
        generatedAndReimport();
        commaAndMultiline();
        tabsAndNoConsent();
        System.out.println("OK: CSV Email/Consentimento, Portugal, parser reversível, CSV comma/semicolon/tab.");
    }
}
