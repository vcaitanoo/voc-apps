from pathlib import Path

ROOT = Path("jarvis0215")
APP = ROOT / "app"
BUILD = APP / "build.gradle.kts"
VOICE = APP / "src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f"VC26 expected block missing ({label}) in {path}")
    path.write_text(text.replace(old, new, 1))


# VC26 is an incremental successor of the published VC25 source only.
replace_once(BUILD, 'versionCode = 25', 'versionCode = 26', 'versionCode')
replace_once(BUILD, 'versionName = "0.3.0"', 'versionName = "0.3.1"', 'versionName')

voice = VOICE.read_text()

# -----------------------------------------------------------------------------
# 1) RESTORE THE HISTORICAL MALE-ONLY VOICE BEHAVIOUR
# VC24/VC25 allowed fallback to an unspecified PT-BR/PT/default voice when the
# Android engine did not label the selected voice as male. On the user's device
# that fallback resolves to a female voice. The older working Jarvis used the
# explicitly detected PT-BR male voice. Restore that exact selection policy and
# never intentionally choose the unspecified/female fallback.
# -----------------------------------------------------------------------------
old_selected = '        val selected = male ?: anyPtBr ?: anyPortuguese ?: engine.defaultVoice ?: voices.firstOrNull()\n'
new_selected = '        val selected = male\n'
if old_selected not in voice:
    # VC24 form before VC25 added defaultVoice fallback.
    old_selected = '        val selected = male ?: anyPtBr ?: anyPortuguese\n'
if old_selected not in voice:
    raise SystemExit('VC26 male voice selector anchor missing')
voice = voice.replace(old_selected, new_selected, 1)

old_assignment = '''        if (selected != null) {
            runCatching { engine.voice = selected }
        } else {
            runCatching { engine.setLanguage(Locale.getDefault()) }
        }
        return true
'''
new_assignment = '''        if (selected != null) {
            runCatching { engine.voice = selected }
            return true
        }
        return false
'''
if old_assignment in voice:
    voice = voice.replace(old_assignment, new_assignment, 1)
else:
    old_assignment = '''        if (selected != null) runCatching { engine.voice = selected }
        return true
'''
    new_assignment = '''        if (selected != null) {
            runCatching { engine.voice = selected }
            return true
        }
        return false
'''
    if old_assignment not in voice:
        raise SystemExit('VC26 male voice assignment anchor missing')
    voice = voice.replace(old_assignment, new_assignment, 1)

# -----------------------------------------------------------------------------
# 2) ZERO BEEP IN FOREGROUND *AND* BACKGROUND CONTINUOUS LISTENING
# The canonical VC25 lineage contains two guards that exclude the background
# JarvisListeningService from the tone-suppression code:
#   - silenceRecognitionTones() returns immediately when managed by the service;
#   - startRecognitionNow() only calls it when NOT managed by the service.
# Remove only those exclusions and preserve the recognition lifecycle itself.
# -----------------------------------------------------------------------------
# Canonical VC22/VC25 helper (fully-qualified AudioManager form).
voice = voice.replace(
    '        if (managedByListeningService || recognitionSystemVolumeBefore != null) return\n',
    '        if (recognitionSystemVolumeBefore != null) return\n'
)

# Older mute-window helper, retained for compatibility if present in the rebuilt
# lineage. These replacements are no-ops when those historical blocks are absent.
voice = voice.replace(
    '        if (managedByListeningService) return\n        val audio = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager ?: return\n',
    '        val audio = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager ?: return\n'
)
voice = voice.replace(
    '        if (managedByListeningService) return\n        val previous = recognitionVolumeBeforeMute ?: return\n',
    '        val previous = recognitionVolumeBeforeMute ?: return\n'
)
voice = voice.replace(
    '                if (!managedByListeningService) muteRecognitionToneWindow(950L)\n',
    '                muteRecognitionToneWindow(950L)\n'
)

# VC25 startRecognitionNow service guard.
voice = voice.replace(
    '            if (!managedByListeningService) silenceRecognitionTones()\n',
    '            silenceRecognitionTones()\n'
)

# Structural invariants: if either service exclusion survived, stop instead of
# producing an APK that can still beep in the waiting/background state.
if 'managedByListeningService || recognitionSystemVolumeBefore != null' in voice:
    raise SystemExit('VC26 failed to remove service exclusion inside silenceRecognitionTones')
if 'if (!managedByListeningService) silenceRecognitionTones()' in voice:
    raise SystemExit('VC26 failed to remove background startRecognition tone guard')

VOICE.write_text(voice)

# Final source invariants. No UI, IA, memory, agent, reminder, networking or app
# action code is touched by VC26.
final_build = BUILD.read_text()
final_voice = VOICE.read_text()
if 'versionCode = 26' not in final_build or 'versionName = "0.3.1"' not in final_build:
    raise SystemExit('VC26 identity validation failed')
if 'val selected = male' not in final_voice:
    raise SystemExit('VC26 strict male voice validation failed')
if 'if (recognitionSystemVolumeBefore != null) return' not in final_voice:
    raise SystemExit('VC26 background tone suppression helper validation failed')
if '            silenceRecognitionTones()\n            r.startListening(recognitionIntent())' not in final_voice:
    raise SystemExit('VC26 startRecognition tone suppression validation failed')

print('VC26 applied: historical male-only PT-BR voice + tone suppression during background listening')
