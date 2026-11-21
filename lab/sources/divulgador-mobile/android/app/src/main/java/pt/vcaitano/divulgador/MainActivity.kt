package pt.vcaitano.divulgador

import android.content.Context
import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { Root(applicationContext) } }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Root(ctx: Context) {
    val api = remember { Api(DIVULGADOR_BASE_URL) }
    val scope = rememberCoroutineScope()

    var campaigns by remember { mutableStateOf<List<Campaign>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    var serverOnline by remember { mutableStateOf(false) }
    var dryRun by remember { mutableStateOf(true) }
    var showNew by remember { mutableStateOf(false) }

    suspend fun refresh() {
        try {
            val health = api.health()
            serverOnline = health.status == "ok"
            dryRun = health.dryRun
            campaigns = api.list()
            error = null
        } catch (e: Exception) {
            serverOnline = false
            error = "Sem ligacao ao servidor"
        }
    }

    LaunchedEffect(Unit) {
        while (true) {
            refresh()
            delay(30_000)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Divulgador") },
                actions = {
                    Text(
                        if (serverOnline) "Servidor online" else "A ligar...",
                        color = if (serverOnline) {
                            MaterialTheme.colorScheme.primary
                        } else {
                            MaterialTheme.colorScheme.error
                        },
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.padding(end = 16.dp)
                    )
                }
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                text = { Text("Nova campanha") },
                icon = {},
                onClick = { showNew = true },
                expanded = true
            )
        }
    ) { pad ->
        Column(
            Modifier
                .padding(pad)
                .padding(horizontal = 16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(onClick = { ctx.startActivity(Intent(ctx, SendActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }, modifier = Modifier.weight(1f)) { Text("Enviar e-mails", fontSize = 12.sp) }
                OutlinedButton(onClick = { ctx.startActivity(Intent(ctx, GeneratorActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }, modifier = Modifier.weight(1f)) { Text("Gerador CSV", fontSize = 12.sp) }
            }
            OutlinedButton(
                modifier = Modifier.fillMaxWidth(),
                onClick = {
                    ctx.startActivity(
                        Intent(ctx, SendActivity::class.java)
                            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                            .putExtra("pick_csv_on_start", true)
                    )
                }
            ) { Text("IMPORTAR CSV E CONFIGURAR") }
            Text("Envio automático depende de servidor autenticado. Envio manual usa seu app de e-mail.", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            if (serverOnline) {
                Text(
                    if (dryRun) {
                        "Servidor ligado • modo seguro de teste"
                    } else {
                        "Servidor ligado • envios reais ativos"
                    },
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }

            error?.let {
                Text(
                    it,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }

            if (campaigns.isEmpty() && error == null) {
                Box(
                    Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        if (serverOnline) {
                            "Servidor ligado. Ainda nao ha campanhas."
                        } else {
                            "A ligar ao servidor..."
                        }
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    contentPadding = PaddingValues(bottom = 96.dp)
                ) {
                    items(campaigns, key = { it.id }) { c ->
                        CampaignCard(
                            c = c,
                            onSend = {
                                ctx.startActivity(Intent(ctx, SendActivity::class.java)
                                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                                    .putExtra("campaign_name", c.name)
                                    .putExtra("campaign_link", c.link)
                                    .putExtra("campaign_desc", c.description))
                            },
                            onToggle = {
                                scope.launch {
                                    try {
                                        api.setState(
                                            c.id,
                                            if (c.state == "active") "paused" else "active"
                                        )
                                        refresh()
                                    } catch (_: Exception) {
                                        error = "Falhou a atualizar a campanha"
                                    }
                                }
                            },
                            onDelete = {
                                scope.launch {
                                    try {
                                        api.delete(c.id)
                                        refresh()
                                    } catch (_: Exception) {
                                        error = "Falhou a apagar a campanha"
                                    }
                                }
                            }
                        )
                    }
                }
            }
        }
    }

    if (showNew) {
        NewCampaignDialog(
            onDismiss = { showNew = false },
            onCreate = { n, l, d, a, cap ->
                scope.launch {
                    try {
                        api.create(n, l, d, a, cap)
                        refresh()
                    } catch (_: Exception) {
                        error = "Falhou a criar campanha"
                    }
                }
                showNew = false
            }
        )
    }
}

@Composable
fun CampaignCard(c: Campaign, onSend: () -> Unit, onToggle: () -> Unit, onDelete: () -> Unit) {
    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    c.name,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 18.sp,
                    modifier = Modifier.weight(1f)
                )
                AssistChip(
                    onClick = {},
                    label = { Text(if (c.state == "active") "ativa" else "pausada") }
                )
            }
            Spacer(Modifier.height(4.dp))
            Text(c.description, fontSize = 13.sp, maxLines = 2)
            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(20.dp)) {
                Metric("enviados", c.stats.sent)
                Metric("fila", c.stats.queued)
                Metric("descartados", c.stats.skipped)
                Metric("falhas", c.stats.failed)
            }
            Spacer(Modifier.height(8.dp))
            Row {
                TextButton(onClick = onSend) { Text("Preparar e-mail") }
                TextButton(onClick = onToggle) {
                    Text(if (c.state == "active") "Pausar" else "Ativar")
                }
                TextButton(onClick = onDelete) {
                    Text("Apagar")
                }
            }
        }
    }
}

@Composable
fun Metric(label: String, value: Int) {
    Column {
        Text("$value", fontWeight = FontWeight.Bold, fontSize = 20.sp)
        Text(label, fontSize = 11.sp)
    }
}

@Composable
fun NewCampaignDialog(
    onDismiss: () -> Unit,
    onCreate: (String, String, String, String, Int) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var link by remember { mutableStateOf("") }
    var desc by remember { mutableStateOf("") }
    var aud by remember { mutableStateOf("") }
    var cap by remember { mutableStateOf("40") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Nova campanha") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    name,
                    { name = it },
                    label = { Text("Nome") },
                    singleLine = true
                )
                OutlinedTextField(
                    link,
                    { link = it },
                    label = { Text("Link") },
                    singleLine = true
                )
                OutlinedTextField(
                    desc,
                    { desc = it },
                    label = { Text("O que e e para que serve") }
                )
                OutlinedTextField(
                    aud,
                    { aud = it },
                    label = { Text("Publico-alvo") }
                )
                OutlinedTextField(
                    cap,
                    { cap = it.filter(Char::isDigit) },
                    label = { Text("Envios por dia") },
                    singleLine = true
                )
            }
        },
        confirmButton = {
            TextButton(
                enabled = name.isNotBlank() && link.isNotBlank() && desc.isNotBlank(),
                onClick = {
                    onCreate(
                        name,
                        link,
                        desc,
                        aud,
                        cap.toIntOrNull() ?: 40
                    )
                }
            ) {
                Text("Criar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}
