from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
MAIN = APP / "src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
BRAIN = APP / "src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"VC43 expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


# Version successor of the already published VC42. Never overwrite that base.
build = BUILD.read_text(encoding="utf-8")
build = replace_once(build, "versionCode = 42", "versionCode = 43", "versionCode")
build = replace_once(build, 'versionName = "0.3.17"', 'versionName = "0.3.18"', "versionName")
BUILD.write_text(build, encoding="utf-8")


# Fix numbered cancellation and expose the same secure, user-scoped RPC to the menu.
brain = BRAIN.read_text(encoding="utf-8")
cancellation_marker = r"""        val normalizedMessage = normalizeText(message)
        val cancelAll = Regex("\\b(todos|todas|qualquer|quaisquer)\\b").containsMatchIn(normalizedMessage)
"""
cancellation_replacement = r"""        val normalizedMessage = normalizeText(message)
        val cancelAll = Regex("\\b(todos|todas|qualquer|quaisquer)\\b").containsMatchIn(normalizedMessage)
        val numberedMatch = Regex("\\b(?:lembrete|aviso)\\s+(?:numero\\s*)?(\\d{1,3})\\b|\\b(?:numero|item|n)\\s*(\\d{1,3})\\b|#\\s*(\\d{1,3})").find(normalizedMessage)
        val requestedNumber = numberedMatch?.groupValues?.drop(1)?.firstOrNull { it.isNotBlank() }?.toIntOrNull()
"""
brain = replace_once(brain, cancellation_marker, cancellation_replacement, "numbered cancellation parser")

targets_old = r"""        val targets = when {
            cancelAll -> reminders
            reminders.size == 1 -> reminders
            else -> reminders.filter { reminder ->
                val titleWords = normalizeText(reminder.title)
                    .split(Regex("\\s+"))
                    .filter { it.length >= 4 }
                titleWords.any { word -> normalizedMessage.contains(word) }
            }
        }

        if (targets.isEmpty()) {
"""
targets_new = r"""        val targets = when {
            cancelAll -> reminders
            requestedNumber != null -> reminders.getOrNull(requestedNumber - 1)?.let { listOf(it) } ?: emptyList()
            reminders.size == 1 -> reminders
            else -> reminders.filter { reminder ->
                val titleWords = normalizeText(reminder.title)
                    .split(Regex("\\s+"))
                    .filter { it.length >= 4 }
                titleWords.any { word -> normalizedMessage.contains(word) }
            }
        }

        if (requestedNumber != null && targets.isEmpty()) {
            return localActionResponse(
                "Não existe o lembrete número $requestedNumber. Há ${reminders.size} lembretes ativos. Atualize a lista antes de escolher outro número.",
                health
            )
        }

        if (targets.isEmpty()) {
"""
brain = replace_once(brain, targets_old, targets_new, "numbered cancellation target selection")

old_cancel_match = r"""        return action.containsMatchIn(normalized) && objectWord.containsMatchIn(normalized)
"""
new_cancel_match = r"""        val numberedTarget = Regex("\\b(?:numero|item|n)\\s*\\d{1,3}\\b|#\\s*\\d{1,3}").containsMatchIn(normalized)
        return action.containsMatchIn(normalized) && (objectWord.containsMatchIn(normalized) || numberedTarget)
"""
brain = replace_once(brain, old_cancel_match, new_cancel_match, "numbered cancellation intent")

cancel_api_marker = "    fun markReminderFired(accessToken: String, id: String): Boolean {"
cancel_api = """    fun cancelReminder(accessToken: String, id: String): Boolean {
        if (accessToken.isBlank() || id.isBlank()) return false
        return deactivateReminder(accessToken, id)
    }

"""
brain = replace_once(brain, cancel_api_marker, cancel_api + cancel_api_marker, "public menu cancellation API")

required_brain = [
    "val requestedNumber =",
    "reminders.getOrNull(requestedNumber - 1)",
    "fun cancelReminder(accessToken: String, id: String): Boolean",
    "jarvis_cancel_reminder"
]
missing = [item for item in required_brain if item not in brain]
if missing:
    raise SystemExit("VC43 reminder invariants missing: " + ", ".join(missing))
BRAIN.write_text(brain, encoding="utf-8")


# Add a numbered reminder list and per-item deletion in the existing System menu.
main = MAIN.read_text(encoding="utf-8")
state_marker = '    private var authStatus by mutableStateOf("Sem sessão")\n'
state_addition = """    private var savedReminders by mutableStateOf<List<BrainClient.Reminder>>(emptyList())
    private var remindersLoading by mutableStateOf(false)
    private var reminderStatus by mutableStateOf("Abra Configurações para ver os lembretes.")
"""
if "private var savedReminders by mutableStateOf<List<BrainClient.Reminder>>" not in main:
    main = replace_once(main, state_marker, state_marker + state_addition, "reminder UI state")

methods_marker = "    private fun authenticate("
methods = r"""    private fun refreshSavedReminders() {
        if (remindersLoading) return
        remindersLoading = true
        reminderStatus = "Carregando lembretes…"

        Thread {
            val token = AuthSessionStore.validAccessToken(this@MainActivity)
            val result = if (token == null) emptyList() else BrainClient.activeReminders(token)
            runOnUiThread {
                savedReminders = result
                remindersLoading = false
                reminderStatus = when {
                    token == null -> "Entre na conta Jarvis para consultar seus lembretes."
                    result.isEmpty() -> "Nenhum lembrete ativo."
                    else -> "${result.size} lembretes ativos. Os números seguem a ordem da próxima data."
                }
            }
        }.apply {
            name = "jarvis-reminders-refresh"
            isDaemon = true
            start()
        }
    }

    private fun deleteSavedReminder(index: Int) {
        if (remindersLoading) return
        val selected = savedReminders.getOrNull(index) ?: return
        remindersLoading = true
        reminderStatus = "Apagando o lembrete número ${index + 1}…"

        Thread {
            val token = AuthSessionStore.validAccessToken(this@MainActivity)
            val cancelled = token != null && BrainClient.cancelReminder(token, selected.id)
            val remaining = if (cancelled && token != null) BrainClient.activeReminders(token) else null

            runOnUiThread {
                remindersLoading = false
                when {
                    token == null -> reminderStatus = "Entre na conta Jarvis para apagar lembretes."
                    !cancelled -> reminderStatus = "Não consegui confirmar a exclusão. O lembrete continua na lista."
                    else -> {
                        savedReminders = remaining.orEmpty()
                        val stillActive = remaining?.any { it.id == selected.id } == true
                        reminderStatus = if (stillActive) {
                            "A exclusão não foi confirmada pelo servidor. Atualize e tente novamente."
                        } else {
                            "Lembrete número ${index + 1} apagado e removido da lista ativa."
                        }
                    }
                }
            }
        }.apply {
            name = "jarvis-reminder-delete"
            isDaemon = true
            start()
        }
    }

"""
if methods_marker not in main:
    raise SystemExit("VC43 MainActivity authentication insertion point missing")
main = replace_once(main, methods_marker, methods + methods_marker, "reminder UI methods")

launch_marker = "        MaterialTheme(colorScheme = colors) {\n"
launch_replacement = """        MaterialTheme(colorScheme = colors) {
            LaunchedEffect(selectedTab, authenticated) {
                if (selectedTab == 1) refreshSavedReminders()
            }
"""
main = replace_once(main, launch_marker, launch_replacement, "automatic reminder refresh")

system_anchor = '            item { SystemCard("Eventos locais pendentes", bufferedEvents.toString()) }\n'
system_section = r"""            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            "Lembretes salvos",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            "Cada item tem um número. Você pode apagar pelo botão ou dizer: “apague o lembrete número 5”.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                reminderStatus,
                                modifier = Modifier.weight(1f),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            TextButton(
                                enabled = !remindersLoading,
                                onClick = { refreshSavedReminders() }
                            ) {
                                Text("Atualizar")
                            }
                        }
                        if (remindersLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                strokeWidth = 2.dp
                            )
                        }
                    }
                }
            }

            items(savedReminders.size) { reminderIndex ->
                val reminder = savedReminders[reminderIndex]
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                "${reminderIndex + 1}. ${reminder.title}",
                                fontWeight = FontWeight.SemiBold
                            )
                            Text(
                                "Próximo: ${java.text.SimpleDateFormat("dd/MM/yyyy HH:mm", java.util.Locale("pt", "BR")).format(java.util.Date(reminder.nextFireAtMillis))}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            reminder.details?.takeIf { it.isNotBlank() }?.let { details ->
                                Text(
                                    details,
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                        TextButton(
                            enabled = !remindersLoading,
                            onClick = { deleteSavedReminder(reminderIndex) }
                        ) {
                            Text("Apagar")
                        }
                    }
                }
            }
"""
main = replace_once(main, system_anchor, system_anchor + system_section, "saved reminder menu section")

required_main = [
    "private var savedReminders by mutableStateOf<List<BrainClient.Reminder>>",
    "private fun refreshSavedReminders()",
    "private fun deleteSavedReminder(index: Int)",
    'Text(\n                            "Lembretes salvos"',
    "items(savedReminders.size)",
    "LaunchedEffect(selectedTab, authenticated)"
]
missing = [item for item in required_main if item not in main]
if missing:
    raise SystemExit("VC43 UI invariants missing: " + ", ".join(missing))
MAIN.write_text(main, encoding="utf-8")

print("VC43 patch applied: numbered deletion, saved-reminders menu, and server-confirmed list refresh.")
