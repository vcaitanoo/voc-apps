from pathlib import Path
import hashlib
import shutil
import struct
import re


ROOT = Path("jarvis0215")
CANDIDATE = Path("lab/sources/jarvis/candidate/0.3.0")
PATCH = CANDIDATE / "changes.patch"
OVERRIDES = CANDIDATE / "overrides"

EXPECTED = {
    PATCH: "616f673a09921e0ea14c24f023139981e8819e1c77c381476275a891d1dd6749",
    OVERRIDES / "jarvis_logo.png": "b111bf2c5d317c8fd49f464ecfc7f035775ac7049c6535a980ddd795c4c2b6aa",
    OVERRIDES / "drawable-nodpi/jarvis_launcher_logo.png": "245cd0f0b1abd53f792334d52c794c218efd81277fdda7c0dc9b5cc4c1ca49a0",
    OVERRIDES / "mipmap-mdpi/ic_launcher.png": "c86bfee184441262521802eabab46f23d6d6b19f1ee889533ffa0161f231762b",
    OVERRIDES / "mipmap-hdpi/ic_launcher.png": "aa0278647be678f56ff61a2385ec5b920f97d59c6d10f657496ee7fcda73164a",
    OVERRIDES / "mipmap-xhdpi/ic_launcher.png": "4eaf1111880c8155b65909b08ed0d0e6d3c14da0aadf04ffdc56f712833f4a1a",
    OVERRIDES / "mipmap-xxhdpi/ic_launcher.png": "081d144023cfd1a1a4f9416341dbc246c0f8deb964ad66e533e729d524ba670e",
    OVERRIDES / "mipmap-xxxhdpi/ic_launcher.png": "98cdb82294dcb83c1284c2e425cd1c4ac9e8630132454885b56221c81ab72b02",
}
EXPECTED_DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise SystemExit(f"invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def apply_unified_patch(root: Path, patch_path: Path) -> None:
    """Aplica o diff determinístico sem depender do binário `patch`."""
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
        output: list[str] = []
        original_index = 0

        while index < len(lines) and not lines[index].startswith("--- "):
            header = lines[index]
            if not header.startswith("@@ "):
                index += 1
                continue
            match = re.match(
                r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@",
                header,
            )
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
                    if original_index >= len(original) or original[original_index] != content:
                        raise SystemExit(f"context mismatch in {selected}")
                    output.append(content)
                    original_index += 1
                elif marker == "-":
                    if original_index >= len(original) or original[original_index] != content:
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

build_file = ROOT / "app/build.gradle.kts"
before = build_file.read_text()
if 'versionCode = 24' not in before or 'versionName = "0.2.22"' not in before:
    raise SystemExit("VC25 must be applied only on the canonical VC24 source")

for path, expected_hash in EXPECTED.items():
    if not path.is_file() or sha256(path) != expected_hash:
        raise SystemExit(f"candidate input missing or changed: {path}")

apply_unified_patch(ROOT, PATCH)

res = ROOT / "app/src/main/res"
foreground = OVERRIDES / "drawable-nodpi/jarvis_launcher_logo.png"
if png_size(foreground) != (432, 432):
    raise SystemExit("adaptive launcher foreground has an unexpected size")
target_foreground = res / "drawable-nodpi/jarvis_launcher_logo.png"
target_foreground.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(foreground, target_foreground)

for density, expected_size in EXPECTED_DENSITIES.items():
    source = OVERRIDES / f"mipmap-{density}/ic_launcher.png"
    if png_size(source) != (expected_size, expected_size):
        raise SystemExit(f"launcher size mismatch for {density}")
    target = res / f"mipmap-{density}"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target / "ic_launcher.png")
    shutil.copyfile(source, target / "ic_launcher_round.png")

after = build_file.read_text()
manifest = (ROOT / "app/src/main/AndroidManifest.xml").read_text()
required = (
    'versionCode = 25',
    'versionName = "0.3.0"',
    'applicationId = "pt.vcaitano.jarvis"',
)
if any(value not in after for value in required):
    raise SystemExit("VC25 identity validation failed")
if 'android:icon="@mipmap/ic_launcher"' not in manifest:
    raise SystemExit("launcher icon is not configured")
if 'android:roundIcon="@mipmap/ic_launcher_round"' not in manifest:
    raise SystemExit("round launcher icon is not configured")

print("VC25 applied: agent architecture, secure memory, spoken reminders, web grounding, wake-word tolerance and approved launcher assets")
