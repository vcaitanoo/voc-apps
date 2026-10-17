# Jarvis 0.3.15 / VC40 candidate

Changes in this candidate:
- Keep the explicitly tagged Portuguese male voice as the first choice.
- Add a fallback to installed Portuguese TTS voices when an Android engine does not identify gender metadata.
- Use a deeper pitch for the fallback path and avoid failing TTS initialization solely because a male tag is missing.
- Preserve the existing reminder-management and owner voice-recognition patch chain.

The workflow must validate the signed APK and confirm the published SHA-256 before registering this candidate in VOC Lab. Device testing is still required before marking it stable.
