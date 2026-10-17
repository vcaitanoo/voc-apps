from pathlib import Path

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
BRAIN = ROOT / "app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"
OVERRIDE = Path("lab/sources/jarvis/candidate/0.2.16/overrides/BrainClient.kt")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"VC39 expected block missing ({label})")
    return text.replace(old, new, 1)


build = BUILD.read_text(encoding="utf-8")
build = replace_once(build, "versionCode = 38", "versionCode = 39", "versionCode")
build = replace_once(build, 'versionName = "0.3.13"', 'versionName = "0.3.14"', "versionName")
BUILD.write_text(build, encoding="utf-8")

brain = BRAIN.read_text(encoding="utf-8")
override = OVERRIDE.read_text(encoding="utf-8")

# Keep the canonical BrainClient produced by the full patch chain. The override
# is an older full-file snapshot, so transplant only the reminder-management
# functions to avoid reverting the current wake-word/persona fixes.
if "private fun reminderManagementResponse(" not in brain:
    source_start = override.find("    private fun reminderManagementResponse(")
    source_end = override.find("    private fun reminderCancellationResponse(", source_start)
    if source_start < 0 or source_end < 0:
        raise SystemExit("VC39 reminder methods not found in override source")
    methods = override[source_start:source_end]

    cancel_start = brain.find("    private fun reminderCancellationResponse(")
    if cancel_start < 0:
        raise SystemExit("VC39 target reminder cancellation method missing in canonical source")
    brain = brain[:cancel_start] + methods + brain[cancel_start:]

    clean = "        val cleanMessage = message.trim()"
    if "reminderManagementResponse(accessToken, cleanMessage)?.let { return it }" not in brain:
        brain = replace_once(
            brain,
            clean + "\n",
            clean + "\n\n        reminderManagementResponse(accessToken, cleanMessage)?.let { return it }\n",
            "insert reminder-management dispatch",
        )

# Add confirmation before the existing delete-all action. Keep the canonical
# cancellation implementation and insert only the explicit confirmation gate.
if "Isso vai apagar todos os" not in brain:
    cancel_start = brain.find("    private fun reminderCancellationResponse(")
    if cancel_start < 0:
        raise SystemExit("VC39 reminder cancellation function missing")
    line_start = brain.find("        val cancelAll = Regex(", cancel_start)
    if line_start < 0:
        raise SystemExit("VC39 cancel-all detection missing")
    line_end = brain.find("\n", line_start)
    if line_end < 0:
        raise SystemExit("VC39 cancel-all detection line is incomplete")
    confirmation = r'''
        if (cancelAll && reminders.size > 1) {
            val confirmed = Regex("\\b(confirmo|confirmar|confirmado|confirmada|sim apague|pode apagar|pode excluir)\\b")
                .containsMatchIn(normalizedMessage)
            if (!confirmed) {
                return localActionResponse(
                    "Isso vai apagar todos os ${reminders.size} lembretes ativos. Para confirmar, diga: confirmo apagar todos os lembretes.",
                    health
                )
            }
        }'''
    brain = brain[:line_end] + "\n" + confirmation + brain[line_end:]

required_imports = [
    "import java.time.LocalDate",
    "import java.time.LocalDateTime",
    "import java.time.LocalTime",
    "import java.time.ZoneId",
    "import java.time.format.DateTimeFormatter",
]
for item in required_imports:
    if item not in brain:
        package_end = brain.find("\n", brain.find("package "))
        if package_end < 0:
            raise SystemExit("VC39 package declaration missing")
        brain = brain[:package_end + 1] + item + "\n" + brain[package_end + 1:]

BRAIN.write_text(brain, encoding="utf-8")

required = [
    "looksLikeReminderListing",
    "looksLikeReminderEdit",
    "updateReminderTime",
    "reminderManagementResponse",
    "confirmo apagar todos os lembretes",
    "jarvis_update_reminder_time",
    "O dono chamou-te pelo nome",
]
missing = [item for item in required if item not in brain]
if missing:
    raise SystemExit("VC39 reminder/persona invariants missing: " + ", ".join(missing))
if "O usuário apenas chamou você dizendo" in brain:
    raise SystemExit("VC39 canonical wake-word prompt regressed to the old text")
print("VC39 reminder management merged into canonical BrainClient; persona preserved")
