# Jarvis VC48 — resultado real da compilação
Consultado: 2026-10-25T14:36:47.992794+00:00
Execução: https://github.com/vcaitanoo/voc-apps/actions/runs/40202916304

## Build, verify and publish Jarvis 0.3.23 / VC48: failure
- Set up job: success
- Check out GitHub source of truth: success
- Set up Java 17: success
- Set up Gradle 9.5.1: success
- Prepare canonical source: success
- Build, sign, verify and publish the APK: failure
- Register VC48 in the GitHub/VOC Lab source catalog: skipped
- Sync the live VOC Lab catalog in Supabase: skipped
- Save build evidence: success
- Post Set up Gradle 9.5.1: success
- Post Set up Java 17: success
- Post Check out GitHub source of truth: success
- Complete job: success

### Erros observados
```text
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:15.1307833Z   dependency-graph-continue-on-failure: true
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:29.3541139Z ^[[36;1mexpected = {^[[0m
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:29.3543639Z ^[[36;1mfor key, value in expected.items():^[[0m
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:30.2351214Z VC38 source patch validated: male TTS fallback, VoicePrint gate and error recovery
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:30.2863680Z VC42 validated: explicit male PT-BR only; Google TTS first; female/default fallback removed; no voice-failure notices
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:30.4349831Z VC48 expected exactly 1 BrainClient.chat signature, found 0
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:30.4404953Z ##[error]Process completed with exit code 1.
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:30.9725477Z (node:2271) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
Build, verify and publish Jarvis 0.3.23 / VC48	UNKNOWN STEP	2026-10-25T14:35:33.0925637Z Starting process 'Gradle build daemon'. Working directory: /home/runner/.gradle/daemon/9.5.1 Command: /usr/lib/jvm/temurin-17-jdk-amd64/bin/java --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base
```
