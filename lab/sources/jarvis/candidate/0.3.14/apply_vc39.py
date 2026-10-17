from pathlib import Path

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
BRAIN = ROOT / "app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"VC39 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(BUILD, "versionCode = 38", "versionCode = 39", "versionCode")
replace_once(BUILD, 'versionName = "0.3.13"', 'versionName = "0.3.14"', "versionName")

brain = BRAIN.read_text(encoding="utf-8")
required = ["looksLikeReminderListing", "updateReminderTime", "reminderManagementResponse", "confirmo apagar todos os lembretes", "jarvis_update_reminder_time"]
missing = [item for item in required if item not in brain]
if missing:
    raise SystemExit("VC39 reminder management implementation missing: " + ", ".join(missing))
if 'jarvis_update_reminder_time' not in brain:
    raise SystemExit("VC39 reminder editing RPC path missing")
print("VC39 reminder management invariants validated")
