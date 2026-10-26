# Jarvis VC50 — resultado real da compilação
Consultado: 2026-10-26T20:49:54.229571+00:00
Execução: https://github.com/vcaitanoo/voc-apps/actions/runs/40398740106

## Build, verify and publish Jarvis 0.3.25 / VC50: failure
- Set up job: success
- Check out GitHub source of truth: success
- Set up Java 17: success
- Set up Gradle 9.5.1: success
- Prepare canonical source: success
- Build, sign, verify and publish the APK: success
- Register VC50 in the GitHub/VOC Lab source catalog: failure
- Sync the live VOC Lab catalog in Supabase: skipped
- Save build evidence: success
- Post Set up Gradle 9.5.1: success
- Post Set up Java 17: success
- Post Check out GitHub source of truth: success
- Complete job: success

### Erros observados
```text
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:47:32.3694511Z   dependency-graph-continue-on-failure: true
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:47:41.1201036Z ^[[36;1mexpected = {^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:47:41.1203105Z ^[[36;1mfor key, value in expected.items():^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:47:42.8232861Z VC38 source patch validated: male TTS fallback, VoicePrint gate and error recovery
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:47:42.8728253Z VC42 validated: explicit male PT-BR only; Google TTS first; female/default fallback removed; no voice-failure notices
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:48:23.5460418Z > Task :app:checkKotlinGradlePluginConfigurationErrors SKIPPED
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:26.0051274Z ^[[36;1m    raise SystemExit("Unexpected VC50 publish metadata")^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:26.0053025Z ^[[36;1m    raise SystemExit("Jarvis app not found in lab/catalog.json")^[[0m
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:28.0314145Z  ! [remote rejected] HEAD -> main (cannot lock ref 'refs/heads/main': is at 52fa9cabf4ed1a4b99c576af13a20e8548755525 but expected fa6033becb05690c36eb58c83ccb9b2e91926e51)
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:28.0315240Z error: failed to push some refs to 'https://github.com/vcaitanoo/voc-apps'
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:28.0334917Z ##[error]Process completed with exit code 1.
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:28.7523400Z (node:2954) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:31.6041047Z Starting process 'Gradle build daemon'. Working directory: /home/runner/.gradle/daemon/9.5.1 Command: /usr/lib/jvm/temurin-17-jdk-amd64/bin/java --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base
Build, verify and publish Jarvis 0.3.25 / VC50	UNKNOWN STEP	2026-10-26T20:49:37.1490726Z Failed to save cache entry with path '/home/runner/.gradle/caches/modules-*/files-*/*/*/*/*' and key: gradle-dependencies-v1-77853267de53cceee2b716ea8a6d3ad9: ReserveCacheError: Unable to reserve cache with key gradle-dependencies-v1-77853267de53cceee2b716ea8a6
```
