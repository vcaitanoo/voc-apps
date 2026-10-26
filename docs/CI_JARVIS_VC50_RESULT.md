# Jarvis VC50 — resultado real da compilação
Consultado: 2026-10-26T20:46:41.582336+00:00
Execução: https://github.com/vcaitanoo/voc-apps/actions/runs/40398528641

## Build, verify and publish Jarvis 0.3.25 / VC50: failure
- Set up job: success
- Check out GitHub source of truth: success
- Set up Java 17: success
- Set up Gradle 9.5.1: success
- Prepare canonical source: success
- Build, sign, verify and publish the APK: failure
- Register VC50 in the GitHub/VOC Lab source catalog: skipped
- Sync the live VOC Lab catalog in Supabase: skipped
- Save build evidence: success
- Post Set up Gradle 9.5.1: success
- Post Set up Java 17: success
- Post Check out GitHub source of truth: success
- Complete job: success

### Erros observados
```text
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:01.6652150Z   dependency-graph-continue-on-failure: true
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:15.2627386Z ^[[36;1mexpected = {^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:15.2630127Z ^[[36;1mfor key, value in expected.items():^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:16.1509564Z VC38 source patch validated: male TTS fallback, VoicePrint gate and error recovery
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:16.2066462Z VC42 validated: explicit male PT-BR only; Google TTS first; female/default fallback removed; no voice-failure notices
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:16.4209354Z VC50 expected onDestroy cleanup once, got 2
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:16.4267854Z ##[error]Process completed with exit code 1.
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:16.9220552Z (node:2488) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:46:19.4477797Z Starting process 'Gradle build daemon'. Working directory: /home/runner/.gradle/daemon/9.5.1 Command: /usr/lib/jvm/temurin-17-jdk-amd64/bin/java --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base
```
