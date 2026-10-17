# Jarvis 0.3.16 / VC41 candidate

Voice-only correction:
- Prefer the Samsung TTS engine, which provided Jarvis's historic male voice.
- Accept only an explicitly identified male voice in Brazilian Portuguese (pt-BR).
- Do not fall back to unspecified Portuguese voices or use pitch lowering as a substitute for a male voice.
- Do not show TTS startup or playback failure notices; return to the idle/listening UI quietly.
- Preserve the existing signed package identity and unrelated app functionality.

Build and physical-device validation are required before this candidate can be marked stable.
