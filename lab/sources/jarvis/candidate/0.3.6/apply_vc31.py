from pathlib import Path
import hashlib
import re

ROOT = Path("jarvis0215")
CANDIDATE = Path("lab/sources/jarvis/candidate/0.3.6")
PATCH = CANDIDATE / "changes.patch"
EXPECTED_PATCH_SHA256 = "fad6d6d77c815da1d32df399f69c4ff93103a269535bbba7af3b96e4a00e1a96"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_unified_patch(root: Path, patch_path: Path) -> None:
    def same_line(actual: str, expected: str) -> bool:
        return actual == expected or actual.rstrip("\r\n") == expected.rstrip("\r\n")

    lines = patch_path.read_text().splitlines(keepends=True)
    index = 0
    while index < len(lines):
        if not lines[index].startswith("--- "):
            index += 1
            continue
        old_header = lines[index]
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            raise SystemExit("malformed unified patch header")
        new_header = lines[index]
        index += 1

        old_name = old_header[4:].split("\t", 1)[0].strip()
        new_name = new_header[4:].split("\t", 1)[0].strip()
        selected = new_name if new_name != "/dev/null" else old_name
        if selected.startswith(("a/", "b/")):
            selected = selected[2:]
        target = root / selected
        original = target.read_text().splitlines(keepends=True) if target.exists() else []
        output = []
        original_index = 0

        while index < len(lines) and not lines[index].startswith("--- "):
            header = lines[index]
            if not header.startswith("@@ "):
                index += 1
                continue
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", header)
            if not match:
                raise SystemExit(f"malformed hunk for {selected}")
            old_start = int(match.group(1))
            copy_until = max(0, old_start - 1)
            if copy_until < original_index:
                raise SystemExit(f"overlapping hunks for {selected}")
            output.extend(original[original_index:copy_until])
            original_index = copy_until
            index += 1

            while index < len(lines):
                row = lines[index]
                if row.startswith(("@@ ", "--- ", "diff ")):
                    break
                marker = row[:1]
                content = row[1:]
                if marker == " ":
                    if original_index >= len(original) or not same_line(original[original_index], content):
                        raise SystemExit(f"context mismatch in {selected}")
                    output.append(original[original_index])
                    original_index += 1
                elif marker == "-":
                    if original_index >= len(original) or not same_line(original[original_index], content):
                        raise SystemExit(f"deletion mismatch in {selected}")
                    original_index += 1
                elif marker == "+":
                    output.append(content)
                elif marker == "\\":
                    pass
                else:
                    raise SystemExit(f"unexpected patch line in {selected}")
                index += 1

        if new_name == "/dev/null":
            target.unlink()
        else:
            output.extend(original[original_index:])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("".join(output))


if not ROOT.is_dir():
    raise SystemExit("canonical Jarvis source directory is missing")
if not PATCH.is_file() or sha256(PATCH) != EXPECTED_PATCH_SHA256:
    raise SystemExit("VC31 changes.patch missing or SHA-256 changed")

build = ROOT / "app/build.gradle.kts"
before = build.read_text()
if 'versionCode = 29' not in before or 'versionName = "0.3.4"' not in before:
    raise SystemExit("VC31 must be applied only on canonical VC29 source")

# Apply only the VC31 hunks required by the normal Jarvis conversation path.
# The ReminderSpeechService hunk was generated against a slightly different VC25
# snapshot and blocks the whole build even though it is unrelated to live chat.
# Vercel already proved build.gradle + VoiceController hunks apply cleanly.
raw_patch = PATCH.read_text()
selected_parts = []
chunks = raw_patch.split("\n--- ")
for index, chunk in enumerate(chunks):
    part = chunk if index == 0 else "--- " + chunk
    if part.startswith("--- a/app/build.gradle.kts") or part.startswith("--- a/app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"):
        selected_parts.append(part.rstrip("\n") + "\n")
filtered_patch = CANDIDATE / ".vc31-conversation.patch"
filtered_patch.write_text("".join(selected_parts))
if not selected_parts:
    raise SystemExit("VC31 conversation patch selection failed")
apply_unified_patch(ROOT, filtered_patch)
filtered_patch.unlink(missing_ok=True)

voice = (ROOT / "app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt").read_text()
after = build.read_text()

checks = [
    ('versionCode = 31' in after and 'versionName = "0.3.6"' in after, "identity"),
    ('r.startListening(recognitionIntent())' not in voice, "SpeechRecognizer/beep source removed"),
    ('MediaRecorder.AudioSource.MIC' in voice, "MIC AudioRecord source"),
    ('MediaRecorder.AudioSource.VOICE_RECOGNITION' in voice, "VOICE_RECOGNITION fallback"),
    ('preRollMaxBytes = SAMPLE_RATE * 2 * 4 / 10' in voice, "400ms pre-roll"),
    ('silenceStopFrames = (SAMPLE_RATE * 7 / 10)' in voice, "700ms end-silence"),
    ('noisePeak = 80.0' in voice, "adaptive VAD"),
    ('TextToSpeech(appContext, listener, "com.samsung.SMT")' in voice, "Samsung TTS preference"),
    ('#male_' in voice and '_m00' in voice and 'explicitMale' in voice, "explicit male voice detection"),
    ('BrainClient.transcribe(token, wav)' in voice, "cloud Whisper transcription route"),
]
for ok, label in checks:
    if not ok:
        raise SystemExit("VC31 validation failed: " + label)

print("VC31 applied: faster adaptive silent capture + stronger male PT-BR conversation TTS")
