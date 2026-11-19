package pt.vcaitano.geradoremail;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Random;
import java.util.Set;

public class MainActivity extends Activity {
    private static final int REQUEST_CSV = 205;
    private static final String[] MODES = {
        "Gmail — Brasil", "Gmail — Portugal", "Apple — iCloud / Me / Mac",
        "Misturar todos", "Domínio personalizado"
    };
    private static final String[] BR_NAMES = {
        "Gabriel", "Lucas", "Mateus", "Pedro", "Enzo", "João", "Arthur", "Bernardo",
        "Davi", "Miguel", "Rafael", "Gustavo", "Felipe", "Bruno", "Caio", "Daniel",
        "Henrique", "Leonardo", "Marcos", "Thiago", "Júlia", "Alice", "Sophia",
        "Helena", "Manuela", "Laura", "Beatriz", "Giovanna", "Valentina", "Isabella",
        "Mariana", "Camila", "Larissa", "Amanda", "Bianca", "Carolina", "Letícia",
        "Natália", "Vitória", "Yasmin"
    };
    private static final String[] BR_SURNAMES = {
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
        "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
        "Almeida", "Lopes", "Soares", "Vieira", "Barbosa", "Melo", "Rocha", "Dias",
        "Teixeira", "Correia", "Monteiro", "Cardoso", "Mendes", "Nunes", "Moreira",
        "Araújo"
    };
    private static final String[] BR_CITIES = {
        "São Paulo", "Rio de Janeiro", "Curitiba", "Belo Horizonte", "Salvador",
        "Fortaleza", "Brasília", "Recife", "Porto Alegre", "Goiânia", "Campinas",
        "Florianópolis", "Manaus", "Belém", "Vitória"
    };
    private static final String[] PT_NAMES = {
        "João", "Miguel", "Tiago", "Diogo", "André", "Francisco", "Gonçalo",
        "Afonso", "Pedro", "Rui", "Ricardo", "Carlos", "António", "Manuel",
        "Mariana", "Inês", "Sofia", "Beatriz", "Leonor", "Matilde", "Ana",
        "Carolina", "Margarida", "Catarina", "Rita", "Teresa", "Filipa", "Sara"
    };
    private static final String[] PT_SURNAMES = {
        "Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa",
        "Rodrigues", "Martins", "Sousa", "Fernandes", "Gonçalves",
        "Gomes", "Lopes", "Marques", "Almeida", "Ribeiro", "Pinto",
        "Carvalho", "Teixeira", "Moreira", "Correia", "Monteiro", "Rocha"
    };
    private static final String[] PT_CITIES = {
        "Lisboa", "Porto", "Braga", "Coimbra", "Aveiro", "Guimarães",
        "Lousada", "Penafiel", "Paredes", "Amarante", "Vila Real",
        "Viana do Castelo", "Leiria", "Faro", "Setúbal", "Évora",
        "Bragança", "Viseu", "Funchal", "Ponta Delgada"
    };
    private static final String[] APPLE = {"icloud.com", "me.com", "mac.com"};
    private static final int INK = Color.rgb(26, 36, 61);
    private static final int PRIMARY = Color.rgb(49, 73, 177);
    private final List<String[]> records = new ArrayList<>();
    private Spinner mode;
    private EditText quantity, minAge, maxAge, seed, domain;
    private TextView preview, result;
    private Button generate, save;
    private boolean busy = false;

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private TextView label(String text, int size) {
        TextView view = new TextView(this);
        view.setText(text);
        view.setTextColor(INK);
        view.setTextSize(size);
        view.setPadding(0, dp(12), 0, dp(5));
        return view;
    }

    private EditText input(String text, boolean number) {
        EditText field = new EditText(this);
        field.setSingleLine(true);
        field.setText(text);
        field.setTextSize(17);
        field.setPadding(dp(10), dp(8), dp(10), dp(8));
        field.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PRIMARY));
        if (number) field.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        return field;
    }

    private void addField(LinearLayout parent, String title, EditText field) {
        parent.addView(label(title, 15));
        parent.addView(field, new LinearLayout.LayoutParams(-1, dp(52)));
    }

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(24, 40, 100));
        getWindow().setNavigationBarColor(Color.rgb(245, 247, 252));
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(245, 247, 252));
        LinearLayout all = new LinearLayout(this);
        all.setOrientation(LinearLayout.VERTICAL);
        all.setPadding(dp(20), dp(18), dp(20), dp(28));
        scroll.addView(all);
        setContentView(scroll);

        TextView heading = label("Gerador de E-mails", 26);
        heading.setTypeface(null, 1);
        heading.setPadding(0, dp(8), 0, dp(3));
        all.addView(heading);
        TextView description = label("Gere dados sintéticos e exporte um CSV no celular. Funciona sem internet.", 14);
        description.setTextColor(Color.rgb(80, 88, 108));
        description.setPadding(0, 0, 0, dp(17));
        all.addView(description);

        all.addView(label("Tipo de e-mail", 15));
        mode = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
            android.R.layout.simple_spinner_item, MODES);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        mode.setAdapter(adapter);
        all.addView(mode, new LinearLayout.LayoutParams(-1, dp(54)));

        quantity = input("1000", true);
        minAge = input("18", true);
        maxAge = input("45", true);
        seed = input("", false);
        seed.setHint("Opcional: 12345");
        domain = input("example.test", false);
        addField(all, "Quantidade de registros", quantity);
        addField(all, "Idade mínima", minAge);
        addField(all, "Idade máxima", maxAge);
        addField(all, "Seed (repetir uma geração)", seed);
        addField(all, "Domínio personalizado (somente no último modo)", domain);
        mode.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            public void onItemSelected(android.widget.AdapterView<?> p, View v, int pos, long id) {
                domain.setEnabled(pos == 4);
                domain.setAlpha(pos == 4 ? 1.0f : 0.45f);
            }
            public void onNothingSelected(android.widget.AdapterView<?> p) {}
        });

        generate = new Button(this);
        generate.setText("GERAR LISTA");
        generate.setAllCaps(false);
        generate.setTextSize(17);
        generate.setTextColor(Color.WHITE);
        generate.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PRIMARY));
        LinearLayout.LayoutParams buttons = new LinearLayout.LayoutParams(-1, dp(54));
        buttons.topMargin = dp(24);
        all.addView(generate, buttons);
        generate.setOnClickListener(v -> generateRecords());

        save = new Button(this);
        save.setText("SALVAR CSV NO CELULAR");
        save.setAllCaps(false);
        save.setTextSize(16);
        save.setEnabled(false);
        LinearLayout.LayoutParams second = new LinearLayout.LayoutParams(-1, dp(54));
        second.topMargin = dp(8);
        all.addView(save, second);
        save.setOnClickListener(v -> chooseFile());

        result = label("Nenhum registro gerado ainda.", 15);
        result.setPadding(0, dp(20), 0, dp(6));
        all.addView(result);
        preview = label("", 13);
        preview.setTypeface(android.graphics.Typeface.MONOSPACE);
        preview.setTextIsSelectable(true);
        preview.setPadding(dp(12), dp(8), dp(12), dp(14));
        preview.setBackgroundColor(Color.WHITE);
        all.addView(preview, new LinearLayout.LayoutParams(-1, -2));

        TextView warning = label("Atenção: os endereços são fictícios. Não são contas criadas, ativas ou verificadas e podem coincidir com endereços reais.", 12);
        warning.setTextColor(Color.rgb(107, 90, 66));
        all.addView(warning);
    }

    private static String pick(String[] options, Random random) {
        return options[random.nextInt(options.length)];
    }

    private static String normalize(String value) {
        String normalized = Normalizer.normalize(value, Normalizer.Form.NFD)
            .replaceAll("\\p{M}+", "");
        return normalized.toLowerCase(Locale.ROOT)
            .replaceAll("[^a-z0-9]+", ".").replaceAll("^\\.+|\\.+$", "");
    }

    private void generateRecords() {
        if (busy) return;
        final int count, minimum, maximum, modeIndex;
        final String ownDomain;
        final Long randomSeed;
        try {
            count = Integer.parseInt(quantity.getText().toString().trim());
            minimum = Integer.parseInt(minAge.getText().toString().trim());
            maximum = Integer.parseInt(maxAge.getText().toString().trim());
            if (count < 1 || count > 100000) throw new IllegalArgumentException("Quantidade: de 1 a 100.000.");
            if (minimum < 0 || minimum > maximum || maximum > 120)
                throw new IllegalArgumentException("Informe idades válidas de 0 a 120.");
            modeIndex = mode.getSelectedItemPosition();
            ownDomain = domain.getText().toString().trim().toLowerCase(Locale.ROOT);
            if (modeIndex == 4 &&
                (!ownDomain.matches("[a-z0-9][a-z0-9.-]*\\.[a-z]{2,}") || ownDomain.contains("..")))
                throw new IllegalArgumentException("Domínio inválido. Exemplo: example.test");
            String seedText = seed.getText().toString().trim();
            randomSeed = seedText.isEmpty() ? null : Long.parseLong(seedText);
        } catch (Exception error) {
            Toast.makeText(this, "Verifique os campos: " + error.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        busy = true;
        generate.setEnabled(false);
        save.setEnabled(false);
        result.setText("Gerando " + count + " registros...");
        new Thread(() -> {
            try {
                Random random = randomSeed == null ? new Random() : new Random(randomSeed);
                Set<String> used = new HashSet<>();
                List<String[]> created = new ArrayList<>(count);
                for (int i = 0; i < count; i++) {
                    int kind = modeIndex == 3 ? random.nextInt(3) : modeIndex;
                    boolean portugal = kind == 1 || (kind == 2 && random.nextBoolean());
                    String first = pick(portugal ? PT_NAMES : BR_NAMES, random);
                    String last = pick(portugal ? PT_SURNAMES : BR_SURNAMES, random);
                    String city = pick(portugal ? PT_CITIES : BR_CITIES, random);
                    String mailDomain = kind == 2 ? pick(APPLE, random) :
                        kind == 4 ? ownDomain : "gmail.com";
                    String base = normalize(first) + "." + normalize(last);
                    String email = base + "@" + mailDomain;
                    if (!used.add(email)) {
                        int start = random.nextInt(99) + 1;
                        boolean found = false;
                        for (int j = 0; j < 99; j++) {
                            int suffix = 1 + (start + j - 1) % 99;
                            email = base + suffix + "@" + mailDomain;
                            if (used.add(email)) { found = true; break; }
                        }
                        if (!found) {
                            int suffix = 100 + random.nextInt(900000);
                            do { email = base + suffix++ + "@" + mailDomain; }
                            while (!used.add(email));
                        }
                    }
                    created.add(new String[]{first + " " + last, email, city,
                        String.valueOf(minimum + random.nextInt(maximum - minimum + 1))});
                }
                StringBuilder sample = new StringBuilder();
                int shown = Math.min(10, created.size());
                for (int i = 0; i < shown; i++) {
                    String[] row = created.get(i);
                    sample.append(i + 1).append(". ").append(row[0]).append("\n")
                          .append(row[1]).append("\n")
                          .append(row[2]).append(" · ").append(row[3]).append(" anos\n\n");
                }
                runOnUiThread(() -> {
                    records.clear();
                    records.addAll(created);
                    result.setText(records.size() + " registros gerados. Prontos para exportar.");
                    preview.setText(sample.toString());
                    busy = false;
                    generate.setEnabled(true);
                    save.setEnabled(true);
                });
            } catch (Exception ex) {
                runOnUiThread(() -> {
                    result.setText("Falha na geração: " + ex.getMessage());
                    busy = false;
                    generate.setEnabled(true);
                    save.setEnabled(!records.isEmpty());
                });
            }
        }).start();
    }

    private void chooseFile() {
        if (busy || records.isEmpty()) return;
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("text/csv");
        intent.putExtra(Intent.EXTRA_TITLE, "usuarios_fake_" +
            new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.ROOT).format(new java.util.Date()) + ".csv");
        startActivityForResult(intent, REQUEST_CSV);
    }

    private static String csvCell(String text) {
        if (text.contains(",") || text.contains("\"") ||
            text.contains("\r") || text.contains("\n"))
            return "\"" + text.replace("\"", "\"\"") + "\"";
        return text;
    }

    @Override
    protected void onActivityResult(int code, int status, Intent data) {
        super.onActivityResult(code, status, data);
        if (code != REQUEST_CSV || status != RESULT_OK || data == null || data.getData() == null)
            return;
        if (busy || records.isEmpty()) return;
        final android.net.Uri uri = data.getData();
        final List<String[]> snapshot = new ArrayList<>(records);
        busy = true;
        generate.setEnabled(false);
        save.setEnabled(false);
        result.setText("Salvando CSV...");
        new Thread(() -> {
            try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                if (out == null) throw new java.io.IOException("Não foi possível abrir o arquivo.");
                try (Writer writer = new OutputStreamWriter(out, StandardCharsets.UTF_8)) {
                    writer.write('\uFEFF');
                    writer.write("Nome,Email,Cidade,Idade\r\n");
                    for (String[] row : snapshot) {
                        for (int i = 0; i < row.length; i++) {
                            if (i > 0) writer.write(',');
                            writer.write(csvCell(row[i]));
                        }
                        writer.write("\r\n");
                    }
                    writer.flush();
                }
                runOnUiThread(() -> {
                    busy = false;
                    generate.setEnabled(true);
                    save.setEnabled(true);
                    result.setText("CSV salvo com sucesso: " + snapshot.size() + " registros.");
                    Toast.makeText(this, "Arquivo CSV salvo no celular.", Toast.LENGTH_LONG).show();
                });
            } catch (Exception error) {
                runOnUiThread(() -> {
                    busy = false;
                    generate.setEnabled(true);
                    save.setEnabled(true);
                    result.setText("Erro ao salvar: " + error.getMessage());
                });
            }
        }).start();
    }
}
