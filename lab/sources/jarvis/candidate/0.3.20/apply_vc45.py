#!/usr/bin/env python3
"""VC45 — recover original male pt-BR TTS identity, deriving *only* from VC44.

Do not touch microphones, reminders, UI, backend or voiceprint. Stop rather than
publishing a new APK when the canonical VC44 anchors no longer match.
"""
from pathlib import Path

ROOT = Path("jarvis0215")
BUILD = ROOT / "app/build.gradle.kts"
VOICE = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
REMINDER = ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/ReminderSpeechService.kt"

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"VC45: expected 1 {label}, found {count}")
    return source.replace(old, new, 1)

build = BUILD.read_text(encoding="utf-8")
build = replace_once(build, "versionCode = 44", "versionCode = 45", "versionCode")
build = replace_once(build, 'versionName = "0.3.19"', 'versionName = "0.3.20"', "versionName")
BUILD.write_text(build, encoding="utf-8")

voice = VOICE.read_text(encoding="utf-8")

# The original working Jarvis used the device's configured Android engine;
# forcing Samsung as the first engine was documented as selecting a female
# default on this Samsung. Try the previously pinned engine (if any), else
# Android default, before the Samsung/Google male-only fallbacks.
old_engine = '''        val requestedEngine = when (engineStep) {
            0 -> "com.samsung.SMT"
            1 -> "com.google.android.tts"
            else -> null
        }'''
new_engine = '''        val originalVoicePrefs = appContext.getSharedPreferences("jarvis_original_male_voice_lock", Context.MODE_PRIVATE)
        val pinnedEngine = originalVoicePrefs.getString("engine", null)
        val requestedEngine = when (engineStep) {
            0 -> pinnedEngine // null means original Android default engine
            1 -> "com.samsung.SMT"
            else -> "com.google.android.tts"
        }'''
voice = replace_once(voice,old_engine,new_engine,"restored default-first engine order")

# Preserve the original acoustic settings found in the historical VC7 source.
voice = replace_once(voice,"readyEngine.setSpeechRate(0.96f)","readyEngine.setSpeechRate(0.98f)","initial speech speed")
voice = replace_once(voice,"readyEngine.setPitch(0.90f)","readyEngine.setPitch(0.76f)","initial pitch")
voice = replace_once(voice,"tts?.setSpeechRate(0.96f)","tts?.setSpeechRate(0.98f)","reply speech speed")
voice = replace_once(voice,"tts?.setPitch(0.90f)","tts?.setPitch(0.76f)","reply pitch")

# Once a verified male pt-BR voice has been selected, pin its Android Voice
# identifier and provider in persistent app preferences. Never silently switch
# to a different voice when a provider or its voice list changes.
# Keep VC44's existing explicit-male selector intact. Only enforce an
# existing pinned voice at the *confirmed voice application* boundary.
# A previous patch hard-coded "val selected = male" as an exact anchor and
# aborted CI #38 before Kotlin compilation when VC44 formatted it differently.
voice = replace_once(
    voice,
    "            if (applied) return true\n",
    '''            if (applied) {
                val originalLock = appContext.getSharedPreferences(
                    "jarvis_original_male_voice_lock", Context.MODE_PRIVATE
                )
                val lockedVoiceName = originalLock.getString("voice_name", null)
                val confirmed = engine.voice
                val ptBrConfirmed = confirmed != null &&
                    confirmed.name == selected.name &&
                    confirmed.locale.language.equals("pt", ignoreCase = true) &&
                    confirmed.locale.country.equals("BR", ignoreCase = true)
                if (!ptBrConfirmed) return false
                // Never replace a previously accepted male voice by a
                // different male/female TTS provider voice without consent.
                if (!lockedVoiceName.isNullOrBlank() && selected.name != lockedVoiceName) return false
                if (lockedVoiceName.isNullOrBlank()) {
                    val engineId = when (activeTtsEngineStep) {
                        0 -> engine.defaultEngine
                        1 -> "com.samsung.SMT"
                        else -> "com.google.android.tts"
                    }
                    originalLock.edit()
                        .putString("voice_name", selected.name)
                        .putString("engine", engineId)
                        .apply()
                }
                return true
            }
''',
    "persist positively identified male pt-BR voice",
)
VOICE.write_text(voice, encoding="utf-8")

# Scheduled reminder speech must preserve the *same* original male timbre.
reminder = REMINDER.read_text(encoding="utf-8")
reminder = replace_once(reminder,"engine.setSpeechRate(0.96f)","engine.setSpeechRate(0.98f)","reminder rate")
reminder = replace_once(reminder,"engine.setPitch(0.90f)","engine.setPitch(0.76f)","reminder pitch")
reminder = replace_once(
    reminder,
    "        val selected = candidates.firstOrNull() ?: return false\n",
    '''        val lockedName = getSharedPreferences("jarvis_original_male_voice_lock", 0)
            .getString("voice_name", null)
        val selected = if (lockedName.isNullOrBlank()) {
            candidates.firstOrNull()
        } else {
            candidates.firstOrNull { it.name == lockedName }
        } ?: return false
''',
    "reminders use same pinned male identity",
)
REMINDER.write_text(reminder, encoding="utf-8")

assert 'versionCode = 45' in BUILD.read_text()
assert 'versionName = "0.3.20"' in BUILD.read_text()
for key in (
    'jarvis_original_male_voice_lock', 'lockedVoiceName',
    'readyEngine.setSpeechRate(0.98f)','readyEngine.setPitch(0.76f)',
    'tts?.setSpeechRate(0.98f)','tts?.setPitch(0.76f)',
    'MediaRecorder.AudioSource.MIC','explicitMale','VoicePrint.matches',
):
    if key not in voice:
        raise SystemExit("VC45: invariant missing: " + key)
if 'startListening(' in voice:
    raise SystemExit("VC45: prohibited beep-prone SpeechRecognizer")
print("VC45_SOURCE_OK: VC44 preserved; original pt-BR male voice locked; rate/pitch restored; no unverified voices")
