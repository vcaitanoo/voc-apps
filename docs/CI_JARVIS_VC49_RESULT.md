# Jarvis VC49 — resultado real da compilação
Consultado: 2026-10-26T20:10:58.403933+00:00
Execução: https://github.com/vcaitanoo/voc-apps/actions/runs/40393041754

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
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:09:08.0085343Z   dependency-graph-continue-on-failure: true
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:09:25.2625270Z ^[[36;1mexpected = {^[[0m
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:09:25.2627842Z ^[[36;1mfor key, value in expected.items():^[[0m
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:09:26.2860495Z VC38 source patch validated: male TTS fallback, VoicePrint gate and error recovery
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:09:26.3413308Z VC42 validated: explicit male PT-BR only; Google TTS first; female/default fallback removed; no voice-failure notices
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:08.0501470Z > Task :app:checkKotlinGradlePluginConfigurationErrors SKIPPED
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.1411798Z e: file:///home/runner/work/voc-apps/voc-apps/gl/.jarvis-build-vc49/source/app/src/main/java/pt/vcaitano/jarvis/voice/ReminderSpeechService.kt:153:43 Only safe (?.) or non-null asserted (!!.) calls are allowed on a nullable receiver of type 'Voice?'.
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2450295Z FAILURE: Build failed with an exception.
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2503043Z > A failure occurred while executing org.jetbrains.kotlin.compilerRunner.btapi.BuildToolsApiCompilationWork
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2509311Z    > Compilation error. See log for more details
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2517077Z 	at org.gradle.internal.Try$Failure.ifSuccessfulOrElse(Try.java:288)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2594738Z 	at org.gradle.internal.concurrent.ExecutorPolicy$CatchAndRecordFailures.onExecute(ExecutorPolicy.java:64)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2598156Z Caused by: org.gradle.workers.internal.DefaultWorkerExecutor$WorkExecutionException: A failure occurred while executing org.jetbrains.kotlin.compilerRunner.btapi.BuildToolsApiCompilationWork
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2602261Z 	at org.gradle.internal.work.DefaultAsyncWorkTracker.lambda$waitForItemsAndGatherFailures$2(DefaultAsyncWorkTracker.java:132)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2613071Z 	at org.gradle.internal.work.DefaultAsyncWorkTracker.lambda$waitForItemsAndGatherFailures$3(DefaultAsyncWorkTracker.java:128)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2619572Z 	at org.gradle.internal.work.DefaultAsyncWorkTracker.waitForItemsAndGatherFailures(DefaultAsyncWorkTracker.java:127)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2621554Z 	at org.gradle.internal.work.DefaultAsyncWorkTracker.waitForItemsAndGatherFailures(DefaultAsyncWorkTracker.java:93)
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.2775209Z Caused by: org.jetbrains.kotlin.gradle.tasks.CompilationErrorException: Compilation error. See log for more details
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:32.7564651Z ##[error]Process completed with exit code 1.
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:33.3549842Z (node:3266) [DEP0169] DeprecationWarning: `url.parse()` behavior is not standardized and prone to errors that have security implications. Use the WHATWG URL API instead. CVEs are not issued for `url.parse()` vulnerabilities.
Build, verify and publish Jarvis 0.3.24 / VC49	UNKNOWN STEP	2026-10-26T20:10:35.0861649Z Not performing cache-cleanup due to build failure
```
