# Jarvis VC49 — resultado real da compilação
Consultado: 2026-10-26T20:05:26.017487+00:00
Execução: https://github.com/vcaitanoo/voc-apps/actions/runs/40392343565

## Build, verify and publish Jarvis 0.3.24 / VC49: failure
- Set up job: success
- Check out GitHub source of truth: success
- Set up Java 17: success
- Set up Gradle 9.5.1: success
- Prepare canonical source: success
- Build, sign, verify and publish the APK: failure
- Register VC49 in the GitHub/VOC Lab source catalog: skipped
- Sync the live VOC Lab catalog in Supabase: skipped
- Save build evidence: success
- Post Set up Gradle 9.5.1: success
- Post Set up Java 17: success
- Post Check out GitHub source of truth: success
- Complete job: success

### Erros observados
```text
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:22.1969612Z   dependency-graph-continue-on-failure: true
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:34.8920582Z ^[[36;1mexpected = {^[[0m
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:34.8923201Z ^[[36;1mfor key, value in expected.items():^[[0m
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:35.1513744Z SyntaxError: unterminated string literal (detected at line 25)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:35.1650137Z ##[error]Process completed with exit code 1.
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:04:36.9937618Z Starting process 'Gradle build daemon'. Working directory: /home/runner/.gradle/daemon/9.5.1 Command: /usr/lib/jvm/temurin-17-jdk-amd64/bin/java --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base
```
