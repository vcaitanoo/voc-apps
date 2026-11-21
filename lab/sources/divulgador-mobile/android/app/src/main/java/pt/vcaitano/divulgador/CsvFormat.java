package pt.vcaitano.divulgador;

import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

/**
 * CSV RFC-4180 simples, compartilhado pelo gerador e pelo importador.
 * Detecta ; , ou TAB no cabeçalho e preserva aspas, BOM e campos multilinha.
 * O gerador produz dados sintéticos: consentimento NÃO é inventado.
 */
public final class CsvFormat {
    public static final String GENERATED_HEADER="Email;Nome;Cidade;Idade;Consentimento";
    private CsvFormat() {}

    public static String cell(String value, char delimiter) {
        String s = value == null ? "" : value;
        if (s.indexOf(delimiter) >= 0 || s.indexOf('"') >= 0 ||
            s.indexOf('\r') >= 0 || s.indexOf('\n') >= 0) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }

    public static void writeGenerated(Writer writer, List<String[]> rows) throws IOException {
        writer.write('\uFEFF');
        writer.write(GENERATED_HEADER);
        writer.write("\r\n");
        for (String[] row : rows) {
            if (row.length < 4) throw new IOException("Registro incompleto");
            // Ordem interna dos dados: Nome, Email, Cidade, Idade.
            writer.write(cell(row[1], ';'));
            writer.write(';');
            writer.write(cell(row[0], ';'));
            writer.write(';');
            writer.write(cell(row[2], ';'));
            writer.write(';');
            writer.write(cell(row[3], ';'));
            writer.write(";nao\r\n");  // "nao" = SEM autorização de envio
        }
        writer.flush();
    }

    private static char delimiter(String raw) {
        int comma=0, semicolon=0, tab=0;
        boolean quoted=false;
        for (int i=0;i<raw.length();i++) {
            char ch=raw.charAt(i);
            if (ch=='"') {
                if(quoted && i+1<raw.length() && raw.charAt(i+1)=='"') i++;
                else quoted=!quoted;
            } else if (!quoted && (ch=='\r'||ch=='\n')) break;
            else if (!quoted && ch==',') comma++;
            else if (!quoted && ch==';') semicolon++;
            else if (!quoted && ch=='\t') tab++;
        }
        if (tab>comma && tab>semicolon) return '\t';
        return semicolon>comma ? ';' : ',';
    }

    public static ArrayList<String[]> parse(String content) {
        if (content==null) throw new IllegalArgumentException("CSV vazio");
        String raw=content.replace("\uFEFF","");
        char separator=delimiter(raw);
        ArrayList<String[]> rows=new ArrayList<>();
        ArrayList<String> row=new ArrayList<>();
        StringBuilder cell=new StringBuilder();
        boolean quote=false;
        for (int i=0;i<raw.length();i++) {
            char ch=raw.charAt(i);
            if (ch=='"') {
                if (quote && i+1<raw.length() && raw.charAt(i+1)=='"') {
                    cell.append('"'); i++;
                } else quote=!quote;
            } else if (ch==separator && !quote) {
                row.add(cell.toString()); cell.setLength(0);
            } else if ((ch=='\r'||ch=='\n') && !quote) {
                if (ch=='\r' && i+1<raw.length() && raw.charAt(i+1)=='\n') i++;
                row.add(cell.toString()); cell.setLength(0);
                if (row.size()>1 || !row.get(0).isEmpty()) {
                    rows.add(row.toArray(new String[0]));
                }
                row=new ArrayList<>();
            } else cell.append(ch);
        }
        if(quote) throw new IllegalArgumentException("Aspas incompletas no CSV");
        if(cell.length()>0 || !row.isEmpty()) {
            row.add(cell.toString());
            rows.add(row.toArray(new String[0]));
        }
        return rows;
    }
}
