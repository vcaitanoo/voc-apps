# Exact VC46 source inspection

Recovered from verified canonical VC18–VC46 patch chain. Contains only targeted unmodified code excerpts.

## MainActivity.kt
File lines: 1467
### override fun onPause — matches=0
### override fun onStop — matches=1
```kotlin
220:         refreshState()
221:     }
222: 
223:     override fun onStop() {
224:         if (listeningEnabled) voiceController.handoffToBackground()
225:         super.onStop()
226:     }
227: 
228:     override fun onDestroy() {
229:         uiHandler.removeCallbacksAndMessages(null)
230:         voiceController.destroy()
231:         super.onDestroy()
232:     }
233: 
234:     private fun refreshState() {
235:         notificationAccess = NotificationManagerCompat
236:             .getEnabledListenerPackages(this)
237:             .contains(packageName)
238:         bufferedEvents = DeviceEventBuffer.count(this)
239: 
240:         val session = AuthSessionStore.load(this)
241:         authenticated = session != null
242:         authStatus = if (session != null) "Sessão ativa" else "Sem sessão"
243: 
244:         if (session != null) {
245:             EventSyncScheduler.enqueue(this)
246:         }
247: 
248:         if (session?.needsRefresh() == true && !authBusy) {
249:             authBusy = true
250:             Thread {
251:                 val result = runCatching {
252:                     SupabaseAuthClient.refresh(session.refreshToken)
253:                 }.getOrElse {
254:                     SupabaseAuthClient.AuthResult(null, "Falha ao renovar sessão")
255:                 }
256: 
257:                 runOnUiThread {
258:                     result.session?.let {
259:                         AuthSessionStore.save(this, it)
260:                         authenticated = true
261:                         authStatus = "Sessão ativa"
262:                         EventSyncScheduler.enqueue(this)
263:                     } ?: run {
264:                         AuthSessionStore.clear(this)
265:                         authenticated = false
266:                         authStatus = result.message
267:                     }
268:                     authBusy = false
269:                 }
270:             }.start()
271:         }
272: 
273:         if (!BrainClient.isConfigured) {
274:             brainStatus = "Não configurado"
275:             return
276:         }
277: 
278:         brainStatus = "A verificar..."
279:         Thread {
280:             val health = BrainClient.healthStatus()
281:             runOnUiThread {
282:                 brainStatus = if (health.online) "Online" else "Sem resposta"
283:                 chatMode = health.chatMode
284:                 providersConfigured = health.providersConfigured
285:                 providersAvailable = health.providersAvailable
286:             }
287:         }.start()
288:     }
289: 
290:     private fun toggleListening(enabled: Boolean) {
291:         lastError = null
292: 
293:         if (!enabled) {
294:             listeningEnabled = false
```
### override fun onResume — matches=1
```kotlin
213:         setContent { JarvisApp() }
214:     }
215: 
216:     override fun onResume() {
217:         super.onResume()
218:         JarvisListeningService.stop(this)
219:         voiceController.resumeForegroundListening()
220:         refreshState()
221:     }
222: 
223:     override fun onStop() {
224:         if (listeningEnabled) voiceController.handoffToBackground()
225:         super.onStop()
226:     }
227: 
228:     override fun onDestroy() {
229:         uiHandler.removeCallbacksAndMessages(null)
230:         voiceController.destroy()
231:         super.onDestroy()
232:     }
233: 
234:     private fun refreshState() {
235:         notificationAccess = NotificationManagerCompat
236:             .getEnabledListenerPackages(this)
237:             .contains(packageName)
238:         bufferedEvents = DeviceEventBuffer.count(this)
239: 
240:         val session = AuthSessionStore.load(this)
241:         authenticated = session != null
242:         authStatus = if (session != null) "Sessão ativa" else "Sem sessão"
243: 
244:         if (session != null) {
245:             EventSyncScheduler.enqueue(this)
246:         }
247: 
248:         if (session?.needsRefresh() == true && !authBusy) {
249:             authBusy = true
250:             Thread {
251:                 val result = runCatching {
252:                     SupabaseAuthClient.refresh(session.refreshToken)
253:                 }.getOrElse {
254:                     SupabaseAuthClient.AuthResult(null, "Falha ao renovar sessão")
255:                 }
256: 
257:                 runOnUiThread {
258:                     result.session?.let {
259:                         AuthSessionStore.save(this, it)
260:                         authenticated = true
261:                         authStatus = "Sessão ativa"
262:                         EventSyncScheduler.enqueue(this)
263:                     } ?: run {
264:                         AuthSessionStore.clear(this)
265:                         authenticated = false
266:                         authStatus = result.message
267:                     }
268:                     authBusy = false
269:                 }
270:             }.start()
271:         }
272: 
273:         if (!BrainClient.isConfigured) {
274:             brainStatus = "Não configurado"
275:             return
276:         }
277: 
278:         brainStatus = "A verificar..."
279:         Thread {
280:             val health = BrainClient.healthStatus()
281:             runOnUiThread {
282:                 brainStatus = if (health.online) "Online" else "Sem resposta"
283:                 chatMode = health.chatMode
284:                 providersConfigured = health.providersConfigured
285:                 providersAvailable = health.providersAvailable
286:             }
287:         }.start()
```
### override fun onDestroy — matches=1
```kotlin
225:         super.onStop()
226:     }
227: 
228:     override fun onDestroy() {
229:         uiHandler.removeCallbacksAndMessages(null)
230:         voiceController.destroy()
231:         super.onDestroy()
232:     }
233: 
234:     private fun refreshState() {
235:         notificationAccess = NotificationManagerCompat
236:             .getEnabledListenerPackages(this)
237:             .contains(packageName)
238:         bufferedEvents = DeviceEventBuffer.count(this)
239: 
240:         val session = AuthSessionStore.load(this)
241:         authenticated = session != null
242:         authStatus = if (session != null) "Sessão ativa" else "Sem sessão"
243: 
244:         if (session != null) {
245:             EventSyncScheduler.enqueue(this)
246:         }
247: 
248:         if (session?.needsRefresh() == true && !authBusy) {
249:             authBusy = true
250:             Thread {
251:                 val result = runCatching {
252:                     SupabaseAuthClient.refresh(session.refreshToken)
253:                 }.getOrElse {
254:                     SupabaseAuthClient.AuthResult(null, "Falha ao renovar sessão")
255:                 }
256: 
257:                 runOnUiThread {
258:                     result.session?.let {
259:                         AuthSessionStore.save(this, it)
260:                         authenticated = true
261:                         authStatus = "Sessão ativa"
262:                         EventSyncScheduler.enqueue(this)
263:                     } ?: run {
264:                         AuthSessionStore.clear(this)
265:                         authenticated = false
266:                         authStatus = result.message
267:                     }
268:                     authBusy = false
269:                 }
270:             }.start()
271:         }
272: 
273:         if (!BrainClient.isConfigured) {
274:             brainStatus = "Não configurado"
275:             return
276:         }
277: 
278:         brainStatus = "A verificar..."
279:         Thread {
280:             val health = BrainClient.healthStatus()
281:             runOnUiThread {
282:                 brainStatus = if (health.online) "Online" else "Sem resposta"
283:                 chatMode = health.chatMode
284:                 providersConfigured = health.providersConfigured
285:                 providersAvailable = health.providersAvailable
286:             }
287:         }.start()
288:     }
289: 
290:     private fun toggleListening(enabled: Boolean) {
291:         lastError = null
292: 
293:         if (!enabled) {
294:             listeningEnabled = false
295:             voiceController.stopContinuousListening()
296:             return
297:         }
298: 
299:         if (!voiceController.isRecognitionAvailable()) {
```
### private fun SystemScreen — matches=1
```kotlin
937:     }
938: 
939:     @Composable
940:     private fun SystemScreen(modifier: Modifier = Modifier) {
941:         var email by remember { mutableStateOf("") }
942:         var password by remember { mutableStateOf("") }
943:         var memoryExpanded by remember { mutableStateOf(false) }
944:         val savedMemories = remember(messages.size, memoryExpanded, personalMemoryEnabled) {
945:             runCatching { agent.memories.active(1_000) }.getOrDefault(emptyList())
946:         }
947: 
948:         LazyColumn(
949:             modifier = modifier
950:                 .fillMaxWidth()
951:                 .padding(14.dp),
952:             verticalArrangement = Arrangement.spacedBy(12.dp)
953:         ) {
954:             item {
955:                 Text(
956:                     "Sistema",
957:                     style = MaterialTheme.typography.headlineSmall,
958:                     fontWeight = FontWeight.Bold
959:                 )
960:             }
961: 
962:             item { SystemCard("Cérebro", brainStatus) }
963:             item { SystemCard("IAs", "$providersConfigured configuradas de $providersAvailable preparadas") }
964:             item { SystemCard("Memória", "${savedMemories.size} itens locais cifrados") }
965:             item {
966:                 SystemCard(
967:                     "Notificações",
968:                     if (notificationAccess) "Acesso ativo" else "Acesso desativado"
969:                 )
970:             }
971:             item { SystemCard("Eventos locais pendentes", bufferedEvents.toString()) }
972:             item {
973:                 Card(
974:                     modifier = Modifier.fillMaxWidth(),
975:                     colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
976:                 ) {
977:                     Column(
978:                         modifier = Modifier.padding(14.dp),
979:                         verticalArrangement = Arrangement.spacedBy(8.dp)
980:                     ) {
981:                         Text(
982:                             "Lembretes salvos",
983:                             style = MaterialTheme.typography.titleMedium,
984:                             fontWeight = FontWeight.SemiBold
985:                         )
986:                         Text(
987:                             "Cada item tem um número. Você pode apagar pelo botão ou dizer: “apague o lembrete número 5”.",
988:                             style = MaterialTheme.typography.bodySmall,
989:                             color = MaterialTheme.colorScheme.onSurfaceVariant
990:                         )
991:                         Row(
992:                             modifier = Modifier.fillMaxWidth(),
993:                             horizontalArrangement = Arrangement.SpaceBetween,
994:                             verticalAlignment = Alignment.CenterVertically
995:                         ) {
996:                             Text(
997:                                 reminderStatus,
998:                                 modifier = Modifier.weight(1f),
999:                                 style = MaterialTheme.typography.bodySmall,
1000:                                 color = MaterialTheme.colorScheme.onSurfaceVariant
1001:                             )
1002:                             TextButton(
1003:                                 enabled = !remindersLoading,
1004:                                 onClick = { refreshSavedReminders() }
1005:                             ) {
1006:                                 Text("Atualizar")
1007:                             }
1008:                         }
1009:                         if (remindersLoading) {
1010:                             CircularProgressIndicator(
1011:                                 modifier = Modifier.size(20.dp),
```
## VoiceController.kt
File lines: 1250
### fun handoffToBackground — matches=1
```kotlin
130:         }
131:     }
132: 
133:     fun handoffToBackground() {
134:         if (managedByListeningService || destroyed) return
135:         cancelRecognition()
136:         restoreRecognitionTones(force = true)
137:         if (continuousEnabled) JarvisListeningService.start(appContext)
138:     }
139: 
140:     fun setVoiceOutputEnabled(enabled: Boolean) {
141:         voiceOutputEnabled = enabled
142:         settings.readResponses = enabled
143:         if (!enabled) {
144:             runCatching { currentTrack?.pause() }
145:             runCatching { currentTrack?.flush() }
146:             runCatching { currentTrack?.release() }
147:             currentTrack = null
148:             tts?.stop()
149:             SpeechCoordinator.release(speechOwnerId)
150:             speaking = false
151:             waitingForReply = false
152:             publishIdleOrListening()
153:         }
154:     }
155: 
156:     fun startContinuousListening() {
157:         if (destroyed) return
158:         if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
159:             emit(State.ERROR)
160:             onErrorMessage("Permissão de microfone não concedida.")
161:             return
162:         }
163:         continuousEnabled = true
164:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, true).apply()
165:         waitingForReply = false
166:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
167:         startRecognitionSoon(if (managedByListeningService) 0L else 350L)
168:     }
169: 
170:     fun stopContinuousListening() {
171:         continuousEnabled = false
172:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, false).apply()
173:         waitingForReply = false
174:         listening = false
175:         wakeConversationUntilMs = 0L
176:         restartScheduled = false
177:         handler.removeCallbacksAndMessages(null)
178:         onPartialText("")
179:         cancelRecognition()
180:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
181:         if (!speaking) emit(State.IDLE)
182:     }
183: 
184:     fun pauseForResponse() {
185:         waitingForReply = true
186:         listening = false
187:         onPartialText("")
188:         cancelRecognition()
189:     }
190: 
191:     fun deliverResponse(text: String) {
192:         waitingForReply = true
193:         listening = false
194:         onPartialText("")
195:         cancelRecognition()
196: 
197:         if (!voiceOutputEnabled || text.isBlank()) {
198:             waitingForReply = false
199:             publishIdleOrListening()
200:             return
201:         }
202: 
203:         speaking = true
204:         emit(State.SPEAKING)
```
### fun resumeForegroundListening — matches=1
```kotlin
122: 
123:     fun isContinuousEnabled(): Boolean = continuousEnabled
124: 
125:     fun resumeForegroundListening() {
126:         if (managedByListeningService || destroyed) return
127:         JarvisListeningService.stop(appContext)
128:         if (continuousEnabled && !waitingForReply && !speaking) {
129:             startRecognitionSoon(650L)
130:         }
131:     }
132: 
133:     fun handoffToBackground() {
134:         if (managedByListeningService || destroyed) return
135:         cancelRecognition()
136:         restoreRecognitionTones(force = true)
137:         if (continuousEnabled) JarvisListeningService.start(appContext)
138:     }
139: 
140:     fun setVoiceOutputEnabled(enabled: Boolean) {
141:         voiceOutputEnabled = enabled
142:         settings.readResponses = enabled
143:         if (!enabled) {
144:             runCatching { currentTrack?.pause() }
145:             runCatching { currentTrack?.flush() }
146:             runCatching { currentTrack?.release() }
147:             currentTrack = null
148:             tts?.stop()
149:             SpeechCoordinator.release(speechOwnerId)
150:             speaking = false
151:             waitingForReply = false
152:             publishIdleOrListening()
153:         }
154:     }
155: 
156:     fun startContinuousListening() {
157:         if (destroyed) return
158:         if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
159:             emit(State.ERROR)
160:             onErrorMessage("Permissão de microfone não concedida.")
161:             return
162:         }
163:         continuousEnabled = true
164:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, true).apply()
165:         waitingForReply = false
166:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
167:         startRecognitionSoon(if (managedByListeningService) 0L else 350L)
168:     }
169: 
170:     fun stopContinuousListening() {
171:         continuousEnabled = false
172:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, false).apply()
173:         waitingForReply = false
174:         listening = false
175:         wakeConversationUntilMs = 0L
176:         restartScheduled = false
177:         handler.removeCallbacksAndMessages(null)
178:         onPartialText("")
179:         cancelRecognition()
180:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
181:         if (!speaking) emit(State.IDLE)
182:     }
183: 
184:     fun pauseForResponse() {
185:         waitingForReply = true
186:         listening = false
187:         onPartialText("")
188:         cancelRecognition()
189:     }
190: 
191:     fun deliverResponse(text: String) {
192:         waitingForReply = true
193:         listening = false
194:         onPartialText("")
195:         cancelRecognition()
196: 
```
### fun startContinuousListening — matches=1
```kotlin
153:         }
154:     }
155: 
156:     fun startContinuousListening() {
157:         if (destroyed) return
158:         if (ContextCompat.checkSelfPermission(appContext, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
159:             emit(State.ERROR)
160:             onErrorMessage("Permissão de microfone não concedida.")
161:             return
162:         }
163:         continuousEnabled = true
164:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, true).apply()
165:         waitingForReply = false
166:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
167:         startRecognitionSoon(if (managedByListeningService) 0L else 350L)
168:     }
169: 
170:     fun stopContinuousListening() {
171:         continuousEnabled = false
172:         prefs.edit().putBoolean(KEY_LISTENING_ALLOWED, false).apply()
173:         waitingForReply = false
174:         listening = false
175:         wakeConversationUntilMs = 0L
176:         restartScheduled = false
177:         handler.removeCallbacksAndMessages(null)
178:         onPartialText("")
179:         cancelRecognition()
180:         if (!managedByListeningService) JarvisListeningService.stop(appContext)
181:         if (!speaking) emit(State.IDLE)
182:     }
183: 
184:     fun pauseForResponse() {
185:         waitingForReply = true
186:         listening = false
187:         onPartialText("")
188:         cancelRecognition()
189:     }
190: 
191:     fun deliverResponse(text: String) {
192:         waitingForReply = true
193:         listening = false
194:         onPartialText("")
195:         cancelRecognition()
196: 
197:         if (!voiceOutputEnabled || text.isBlank()) {
198:             waitingForReply = false
199:             publishIdleOrListening()
200:             return
201:         }
202: 
203:         speaking = true
204:         emit(State.SPEAKING)
205:         SpeechCoordinator.claim(speechOwnerId) {
206:             handler.post {
207:                 runCatching { currentTrack?.stop() }
208:                 runCatching { tts?.stop() }
209:                 speaking = false
210:                 waitingForReply = false
211:                 publishIdleOrListening()
212:             }
213:         }
214: 
215:         // VC23: local TTS only. The cloud voice occasionally produced phonemes
216:         // not present in the displayed answer; local TTS reads the exact text.
217:         // Original Jarvis: male cloud speech is primary; Android's positively
218:         // identified male TTS is the offline fallback. MP3 is decoded by
219:         // Android MediaPlayer, NEVER passed to raw PCM AudioTrack.
220:         Thread {
221:             val token = AuthSessionStore.validAccessToken(appContext)
222:             val cloudAudio = runCatching {
223:                 BrainClient.synthesizeSpeech(token, text)
224:             }.getOrNull()
225:             val played = cloudAudio != null && playVerifiedMaleMp3(cloudAudio.pcm)
226:             handler.post {
227:                 if (destroyed || !voiceOutputEnabled) {
```
### fun destroy — matches=2
```kotlin
733:         listening = false
734:     }
735: 
736:     private fun destroyRecognizerOnly() {
737:         val r = recognizer
738:         recognizer = null
739:         runCatching { r?.cancel() }
740:         runCatching { r?.destroy() }
741:     }
742: 
743:     private fun initializeTextToSpeech(engineStep: Int = 0) {
744:         if (destroyed) return
745: 
746:         val attemptId = ++ttsInitializationGeneration
747:         activeTtsEngineStep = engineStep
748:         ttsInitializationInProgress = true
749:         ttsReady = false
750:         val previous = tts
751:         tts = null
752:         runCatching { previous?.stop() }
753:         runCatching { previous?.shutdown() }
754: 
755:         val originalVoicePrefs = appContext.getSharedPreferences("jarvis_original_male_voice_lock", Context.MODE_PRIVATE)
756:         val pinnedEngine = originalVoicePrefs.getString("engine", null)
757:         val requestedEngine = when (engineStep) {
758:             0 -> pinnedEngine // null means original Android default engine
759:             1 -> "com.samsung.SMT"
760:             else -> "com.google.android.tts"
761:         }
762: 
763:         var candidate: TextToSpeech? = null
764:         var attemptFinished = false
765: 
766:         fun failAttempt() {
767:             handler.post {
768:                 if (attemptId != ttsInitializationGeneration || destroyed || attemptFinished) return@post
769:                 attemptFinished = true
770:                 runCatching { candidate?.stop() }
771:                 runCatching { candidate?.shutdown() }
772:                 if (tts === candidate) tts = null
773:                 ttsReady = false
774: 
775:                 if (engineStep < 2) {
776:                     handler.post { initializeTextToSpeech(engineStep + 1) }
777:                 } else {
778:                     ttsInitializationInProgress = false
779:                     publishIdleOrListening()
780:                 }
781:             }
782:         }
783: 
784:         val listener = TextToSpeech.OnInitListener { status ->
785:             handler.post {
786:                 if (attemptId != ttsInitializationGeneration || destroyed) {
787:                     runCatching { candidate?.shutdown() }
788:                     return@post
789:                 }
790:                 if (attemptFinished) return@post
791: 
792:                 val readyEngine = candidate
793:                 if (status != TextToSpeech.SUCCESS || readyEngine == null) {
794:                     failAttempt()
795:                     return@post
796:                 }
797: 
798:                 tts = readyEngine
799:                 if (!configurePortugueseVoice()) {
800:                     failAttempt()
801:                     return@post
802:                 }
803: 
804:                 attemptFinished = true
805:                 ttsInitializationInProgress = false
806:                 ttsReady = true
807:                 readyEngine.setSpeechRate(0.98f)
```
```kotlin
1231:         }
1232:     }
1233: 
1234:     fun destroy() {
1235:         destroyed = true
1236:         continuousEnabled = false
1237:         waitingForReply = false
1238:         restartScheduled = false
1239:         handler.removeCallbacksAndMessages(null)
1240:         destroyRecognizerOnly()
1241:         runCatching { currentTrack?.stop() }
1242:         runCatching { currentTrack?.release() }
1243:         currentTrack = null
1244:         tts?.stop()
1245:         tts?.shutdown()
1246:         tts = null
1247:         SpeechCoordinator.release(speechOwnerId)
1248:         SpeechCoordinator.release(listeningOwnerId)
1249:     }
1250: }
```
### fun deliverResponse — matches=1
```kotlin
188:         cancelRecognition()
189:     }
190: 
191:     fun deliverResponse(text: String) {
192:         waitingForReply = true
193:         listening = false
194:         onPartialText("")
195:         cancelRecognition()
196: 
197:         if (!voiceOutputEnabled || text.isBlank()) {
198:             waitingForReply = false
199:             publishIdleOrListening()
200:             return
201:         }
202: 
203:         speaking = true
204:         emit(State.SPEAKING)
205:         SpeechCoordinator.claim(speechOwnerId) {
206:             handler.post {
207:                 runCatching { currentTrack?.stop() }
208:                 runCatching { tts?.stop() }
209:                 speaking = false
210:                 waitingForReply = false
211:                 publishIdleOrListening()
212:             }
213:         }
214: 
215:         // VC23: local TTS only. The cloud voice occasionally produced phonemes
216:         // not present in the displayed answer; local TTS reads the exact text.
217:         // Original Jarvis: male cloud speech is primary; Android's positively
218:         // identified male TTS is the offline fallback. MP3 is decoded by
219:         // Android MediaPlayer, NEVER passed to raw PCM AudioTrack.
220:         Thread {
221:             val token = AuthSessionStore.validAccessToken(appContext)
222:             val cloudAudio = runCatching {
223:                 BrainClient.synthesizeSpeech(token, text)
224:             }.getOrNull()
225:             val played = cloudAudio != null && playVerifiedMaleMp3(cloudAudio.pcm)
226:             handler.post {
227:                 if (destroyed || !voiceOutputEnabled) {
228:                     finishSpeaking()
229:                 } else if (played) {
230:                     finishSpeaking()
231:                 } else {
232:                     speakWithLocalFallback(text)
233:                 }
234:             }
235:         }.apply {
236:             name = "jarvis-original-male-cloud-voice"
237:             isDaemon = true
238:             start()
239:         }
240:     }
241: 
242:     fun resumeAfterFailedResponse() {
243:         waitingForReply = false
244:         publishIdleOrListening()
245:     }
246: 
247:     private fun createRecognizer(): SpeechRecognizer? {
248:         recognizerIsOnDevice = false
249:         return runCatching { SpeechRecognizer.createSpeechRecognizer(appContext) }.getOrNull()
250:     }
251: 
252:     private fun ensureRecognizer(): SpeechRecognizer? {
253:         recognizer?.let { return it }
254:         val created = createRecognizer() ?: return null
255:         created.setRecognitionListener(object : RecognitionListener {
256:             override fun onReadyForSpeech(params: Bundle?) {
257:                 listening = true
258:                 emit(State.LISTENING)
259:             }
260: 
261:             override fun onBeginningOfSpeech() {
262:                 listening = true
```
### private fun initializeTextToSpeech — matches=1
```kotlin
740:         runCatching { r?.destroy() }
741:     }
742: 
743:     private fun initializeTextToSpeech(engineStep: Int = 0) {
744:         if (destroyed) return
745: 
746:         val attemptId = ++ttsInitializationGeneration
747:         activeTtsEngineStep = engineStep
748:         ttsInitializationInProgress = true
749:         ttsReady = false
750:         val previous = tts
751:         tts = null
752:         runCatching { previous?.stop() }
753:         runCatching { previous?.shutdown() }
754: 
755:         val originalVoicePrefs = appContext.getSharedPreferences("jarvis_original_male_voice_lock", Context.MODE_PRIVATE)
756:         val pinnedEngine = originalVoicePrefs.getString("engine", null)
757:         val requestedEngine = when (engineStep) {
758:             0 -> pinnedEngine // null means original Android default engine
759:             1 -> "com.samsung.SMT"
760:             else -> "com.google.android.tts"
761:         }
762: 
763:         var candidate: TextToSpeech? = null
764:         var attemptFinished = false
765: 
766:         fun failAttempt() {
767:             handler.post {
768:                 if (attemptId != ttsInitializationGeneration || destroyed || attemptFinished) return@post
769:                 attemptFinished = true
770:                 runCatching { candidate?.stop() }
771:                 runCatching { candidate?.shutdown() }
772:                 if (tts === candidate) tts = null
773:                 ttsReady = false
774: 
775:                 if (engineStep < 2) {
776:                     handler.post { initializeTextToSpeech(engineStep + 1) }
777:                 } else {
778:                     ttsInitializationInProgress = false
779:                     publishIdleOrListening()
780:                 }
781:             }
782:         }
783: 
784:         val listener = TextToSpeech.OnInitListener { status ->
785:             handler.post {
786:                 if (attemptId != ttsInitializationGeneration || destroyed) {
787:                     runCatching { candidate?.shutdown() }
788:                     return@post
789:                 }
790:                 if (attemptFinished) return@post
791: 
792:                 val readyEngine = candidate
793:                 if (status != TextToSpeech.SUCCESS || readyEngine == null) {
794:                     failAttempt()
795:                     return@post
796:                 }
797: 
798:                 tts = readyEngine
799:                 if (!configurePortugueseVoice()) {
800:                     failAttempt()
801:                     return@post
802:                 }
803: 
804:                 attemptFinished = true
805:                 ttsInitializationInProgress = false
806:                 ttsReady = true
807:                 readyEngine.setSpeechRate(0.98f)
808:                 readyEngine.setPitch(0.76f)
809:                 readyEngine.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
810:                     override fun onStart(utteranceId: String?) {
811:                         handler.post {
812:                             speaking = true
813:                             emit(State.SPEAKING)
814:                         }
```
### private fun configurePortugueseVoice — matches=1
```kotlin
873:         }
874:     }
875: 
876:     private fun configurePortugueseVoice(): Boolean {
877:         val engine = tts ?: return false
878:         // Jarvis speech output must remain Brazilian Portuguese.
879:         runCatching { engine.setLanguage(brazilianPortuguese) }
880: 
881:         fun explicitMale(name: String): Boolean {
882:             val n = name.lowercase(Locale.ROOT)
883:             if (listOf("female", "feminina", "mulher", "woman", "_f00", "-f00", "#female_").any(n::contains)) return false
884:             return listOf(
885:                 "male", "masculino", "homem", "#male_", "_m00", "-m00",
886:                 "_m01", "-m01", "_m02", "-m02", "_m03", "-m03"
887:             ).any(n::contains) || Regex("(?:^|[_#-])m\\d{1,2}(?:$|[_#-])").containsMatchIn(n)
888:         }
889: 
890:         fun score(voice: android.speech.tts.Voice): Int {
891:             if (!explicitMale(voice.name)) return Int.MIN_VALUE
892:             val language = voice.locale.language.lowercase(Locale.ROOT)
893:             val country = voice.locale.country.uppercase(Locale.ROOT)
894:             var value = 0
895:             // Only a positively identified Brazilian Portuguese male voice is valid.
896:             if (language == "pt" && country == "BR") value += 12_000
897:             else return Int.MIN_VALUE
898:             if (voice.name.contains("#male_", ignoreCase = true)) value += 1_000
899:             if (voice.name.contains("m00", ignoreCase = true)) value += 900
900:             if (!voice.isNetworkConnectionRequired) value += 250
901:             value += voice.quality
902:             return value
903:         }
904: 
905:         val voices = runCatching { engine.voices?.toList().orEmpty() }.getOrDefault(emptyList())
906:         val selected = voices.maxByOrNull(::score)?.takeIf { score(it) > Int.MIN_VALUE }
907:         if (selected != null) {
908:             val applied = runCatching {
909:                 engine.voice = selected
910:                 engine.voice?.name == selected.name
911:             }.getOrDefault(false)
912:             if (applied) {
913:                 val originalLock = appContext.getSharedPreferences(
914:                     "jarvis_original_male_voice_lock", Context.MODE_PRIVATE
915:                 )
916:                 val lockedVoiceName = originalLock.getString("voice_name", null)
917:                 val confirmed = engine.voice
918:                 val ptBrConfirmed = confirmed != null &&
919:                     confirmed.name == selected.name &&
920:                     confirmed.locale.language.equals("pt", ignoreCase = true) &&
921:                     confirmed.locale.country.equals("BR", ignoreCase = true)
922:                 if (!ptBrConfirmed) return false
923:                 // Never replace a previously accepted male voice by a
924:                 // different male/female TTS provider voice without consent.
925:                 if (!lockedVoiceName.isNullOrBlank() && selected.name != lockedVoiceName) return false
926:                 if (lockedVoiceName.isNullOrBlank()) {
927:                     val engineId = when (activeTtsEngineStep) {
928:                         0 -> engine.defaultEngine
929:                         1 -> "com.samsung.SMT"
930:                         else -> "com.google.android.tts"
931:                     }
932:                     originalLock.edit()
933:                         .putString("voice_name", selected.name)
934:                         .putString("engine", engineId)
935:                         .apply()
936:                 }
937:                 return true
938:             }
939:         }
940:         return false
941:     }
942: 
943:     private fun splitForSpeech(text: String, maxChars: Int = 650): List<String> {
944:         val clean = text.trim()
945:         if (clean.length <= maxChars) return listOf(clean)
946:         val sentences = clean.split(Regex("(?<=[.!?])\\s+"))
947:         val chunks = mutableListOf<String>()
948:         val current = StringBuilder()
949:         for (sentence in sentences) {
950:             if (sentence.length > maxChars) {
951:                 if (current.isNotEmpty()) {
952:                     chunks += current.toString().trim()
953:                     current.clear()
954:                 }
955:                 sentence.chunked(maxChars).forEach { chunks += it.trim() }
956:                 continue
957:             }
958:             if (current.isNotEmpty() && current.length + 1 + sentence.length > maxChars) {
959:                 chunks += current.toString().trim()
960:                 current.clear()
961:             }
962:             if (current.isNotEmpty()) current.append(' ')
963:             current.append(sentence)
964:         }
965:         if (current.isNotEmpty()) chunks += current.toString().trim()
966:         return chunks.filter { it.isNotBlank() }
967:     }
968: 
969:     private fun speakWithLocalFallback(text: String, attempt: Int = 0) {
970:         lastSpeechText = text
971:         if (!voiceOutputEnabled || destroyed || !SpeechCoordinator.isOwner(speechOwnerId)) {
972:             finishSpeaking()
973:             return
974:         }
975:         if (tts == null || !ttsReady) {
976:             if (!ttsInitializationInProgress && attempt == 0) initializeTextToSpeech()
977:             if (attempt < 80) {
978:                 handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 250L)
979:             } else {
980:                 speaking = false
981:                 waitingForReply = false
982:                 onErrorMessage("Não encontrei uma voz masculina em português do Brasil. Ative a voz masculina do Samsung TTS ou do Google TTS nas definições de texto para voz.")
983:                 publishIdleOrListening()
984:             }
985:             return
986:         }
987: 
988:         if (!configurePortugueseVoice()) {
989:             if (activeTtsEngineStep < 2) {
990:                 ttsReady = false
```
### private fun speakWithLocalFallback — matches=1
```kotlin
966:         return chunks.filter { it.isNotBlank() }
967:     }
968: 
969:     private fun speakWithLocalFallback(text: String, attempt: Int = 0) {
970:         lastSpeechText = text
971:         if (!voiceOutputEnabled || destroyed || !SpeechCoordinator.isOwner(speechOwnerId)) {
972:             finishSpeaking()
973:             return
974:         }
975:         if (tts == null || !ttsReady) {
976:             if (!ttsInitializationInProgress && attempt == 0) initializeTextToSpeech()
977:             if (attempt < 80) {
978:                 handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 250L)
979:             } else {
980:                 speaking = false
981:                 waitingForReply = false
982:                 onErrorMessage("Não encontrei uma voz masculina em português do Brasil. Ative a voz masculina do Samsung TTS ou do Google TTS nas definições de texto para voz.")
983:                 publishIdleOrListening()
984:             }
985:             return
986:         }
987: 
988:         if (!configurePortugueseVoice()) {
989:             if (activeTtsEngineStep < 2) {
990:                 ttsReady = false
991:                 initializeTextToSpeech(activeTtsEngineStep + 1)
992:                 handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 350L)
993:             } else {
994:                 speaking = false
995:                 waitingForReply = false
996:                 onErrorMessage("Não encontrei uma voz masculina em português do Brasil. Ative a voz masculina do Samsung TTS ou do Google TTS nas definições de texto para voz.")
997:                 publishIdleOrListening()
998:             }
999:             return
1000:         }
1001:         tts?.setPitch(0.76f)
1002:         tts?.setSpeechRate(0.98f)
1003:         val chunks = splitForSpeech(text)
1004:         if (chunks.isEmpty()) {
1005:             finishSpeaking()
1006:             return
1007:         }
1008:         val utteranceBase = "jarvis-response-${System.currentTimeMillis()}"
1009:         finalUtteranceId = "$utteranceBase-${chunks.lastIndex}"
1010:         var failed = false
1011:         chunks.forEachIndexed { index, chunk ->
1012:             val result = tts?.speak(
1013:                 chunk,
1014:                 if (index == 0) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD,
1015:                 null,
1016:                 "$utteranceBase-$index"
1017:             )
1018:             if (result == null || result == TextToSpeech.ERROR) failed = true
1019:         }
1020:         if (failed) {
1021:             if (attempt < 2) {
1022:                 handler.postDelayed({ speakWithLocalFallback(text, attempt + 1) }, 300L)
1023:             } else {
1024:                 handleTtsPlaybackError(activeTtsEngineStep)
1025:             }
1026:         }
1027:     }
1028: 
1029:     private fun finishSpeaking() {
1030:         SpeechCoordinator.release(speechOwnerId)
1031:         finalUtteranceId = null
1032:         speaking = false
1033:         waitingForReply = false
1034:         currentTrack = null
1035:         if (continuousEnabled) wakeConversationUntilMs = System.currentTimeMillis() + WAKE_WINDOW_MS
1036:         publishIdleOrListening()
1037:     }
1038: 
1039:     private fun emit(state: State) {
1040:         onStateChanged(state)
```
### private fun playVerifiedMaleMp3 — matches=1
```kotlin
1040:         onStateChanged(state)
1041:     }
1042: 
1043:     private fun playVerifiedMaleMp3(bytes: ByteArray): Boolean {
1044:         // Reject raw PCM, WAV and malformed/JSON data: all can sound like
1045:         // distorted phonemes if treated as raw 16-bit PCM.
1046:         if (bytes.size < 200 || bytes.size > 8_000_000) return false
1047:         val id3 = bytes.size >= 3 &&
1048:             bytes[0] == 'I'.code.toByte() &&
1049:             bytes[1] == 'D'.code.toByte() &&
1050:             bytes[2] == '3'.code.toByte()
1051:         val frame = bytes.size >= 2 &&
1052:             (bytes[0].toInt() and 255) == 255 &&
1053:             (bytes[1].toInt() and 224) == 224
1054:         if (!id3 && !frame) return false
1055: 
1056:         var cacheFile: java.io.File? = null
1057:         var player: android.media.MediaPlayer? = null
1058:         try {
1059:             cacheFile = java.io.File.createTempFile(
1060:                 "jarvis-original-male-", ".mp3", appContext.cacheDir
1061:             )
1062:             cacheFile.writeBytes(bytes)
1063:             val media = android.media.MediaPlayer()
1064:             player = media
1065:             media.setAudioAttributes(
1066:                 android.media.AudioAttributes.Builder()
1067:                     .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
1068:                     .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
1069:                     .build()
1070:             )
1071:             media.setDataSource(cacheFile.absolutePath)
1072:             media.prepare()
1073:             if (!voiceOutputEnabled || destroyed) return false
1074:             media.start()
1075:             val duration = media.duration.toLong().coerceIn(500L, 90_000L)
1076:             val deadline = System.currentTimeMillis() + duration + 4_000L
1077:             var heard = false
1078:             while (!destroyed && voiceOutputEnabled && System.currentTimeMillis() < deadline) {
1079:                 if (!media.isPlaying) break
1080:                 heard = true
1081:                 Thread.sleep(45L)
1082:             }
1083:             return heard && !media.isPlaying && !destroyed && voiceOutputEnabled
1084:         } catch (_: Throwable) {
1085:             return false
1086:         } finally {
1087:             runCatching { player?.stop() }
1088:             runCatching { player?.release() }
1089:             runCatching { cacheFile?.delete() }
1090:         }
1091:     }
1092: 
1093:     private fun playPcm(pcm: ByteArray, sampleRate: Int): Boolean {
1094:         if (pcm.isEmpty()) return false
1095:         val minBuffer = AudioTrack.getMinBufferSize(
1096:             sampleRate,
1097:             AudioFormat.CHANNEL_OUT_MONO,
1098:             AudioFormat.ENCODING_PCM_16BIT
1099:         )
1100:         if (minBuffer <= 0) return false
1101: 
1102:         val track = try {
1103:             AudioTrack.Builder()
1104:                 .setAudioAttributes(
1105:                     AudioAttributes.Builder()
1106:                         .setUsage(AudioAttributes.USAGE_ASSISTANCE_ACCESSIBILITY)
1107:                         .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
1108:                         .build()
1109:                 )
1110:                 .setAudioFormat(
1111:                     AudioFormat.Builder()
1112:                         .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
1113:                         .setSampleRate(sampleRate)
1114:                         .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
```
## JarvisListeningService.kt
File lines: 62
### fun start(context: — matches=1
```kotlin
29:         private const val ACTION_START="pt.vcaitano.jarvis.voice.action.START"; private const val ACTION_STOP="pt.vcaitano.jarvis.voice.action.STOP"; private const val TAKEOVER_DELAY_MS=1500L
30:         @Volatile private var backgroundControllerActive=false
31:         fun isBackgroundControllerActive():Boolean=backgroundControllerActive
32:         fun start(context:Context){if(ContextCompat.checkSelfPermission(context,Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)return;ContextCompat.startForegroundService(context,Intent(context,JarvisListeningService::class.java).setAction(ACTION_START))}
33:         fun stop(context:Context){val intent=Intent(context,JarvisListeningService::class.java).setAction(ACTION_STOP);runCatching{context.startService(intent)}.onFailure{runCatching{context.stopService(Intent(context,JarvisListeningService::class.java))}}}
34:     }
35:     private val handler=Handler(Looper.getMainLooper()); private var wakeLock:PowerManager.WakeLock?=null; private var backgroundController:VoiceController?=null
36:     override fun onCreate(){super.onCreate();createChannel()}
37:     override fun onStartCommand(intent:Intent?,flags:Int,startId:Int):Int{
38:         if(intent?.action==ACTION_STOP){handler.removeCallbacksAndMessages(null);stopBackgroundController();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf();return START_NOT_STICKY}
39:         startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY
40:     }
41:     override fun onTaskRemoved(rootIntent:Intent?){handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);super.onTaskRemoved(rootIntent)}
42:     override fun onDestroy(){handler.removeCallbacksAndMessages(null);stopBackgroundController();wakeLock?.let{if(it.isHeld)runCatching{it.release()}};wakeLock=null;super.onDestroy()}
43:     override fun onBind(intent:Intent?):IBinder?=null
44:     private fun startBackgroundController(){
45:         if(backgroundController!=null)return;backgroundControllerActive=true
46:         backgroundController=VoiceController(this,true,{state->val detail=when(state){VoiceController.State.LISTENING->"Atento em segundo plano • diga “Jarvis” para chamar";VoiceController.State.SPEAKING->"Jarvis está respondendo";VoiceController.State.ERROR->"Escuta precisa de atenção";VoiceController.State.IDLE->"Jarvis ativo"};runOnMain{startForegroundNow(detail)}},{},{command->handleBackgroundCommand(command)},{message->runOnMain{startForegroundNow(message.take(90))}}).also{it.startContinuousListening()}
47:     }
48:     private fun stopBackgroundController(){backgroundControllerActive=false;backgroundController?.destroy();backgroundController=null}
49:     private fun handleBackgroundCommand(command:String){
50:         val clean=command.trim();if(clean.isBlank()){backgroundController?.resumeAfterFailedResponse();return}
51:         Thread{
52:             val token=AuthSessionStore.validAccessToken(this)
53:             val response=runCatching{(application as JarvisApplication).agent.handle(token,clean)}.getOrNull();if(response==null){backgroundController?.deliverResponse("Meu cérebro não respondeu agora. Tente me chamar novamente em instantes.");return@Thread}
54:             synchronized(ConversationStore){val conversation=ConversationStore.load(this).toMutableList();conversation+=ChatMessage("user",clean);conversation+=ChatMessage("jarvis",response.text);ConversationStore.save(this,conversation)};backgroundController?.deliverResponse(response.text)
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
### override fun onStartCommand — matches=1
```kotlin
34:     }
35:     private val handler=Handler(Looper.getMainLooper()); private var wakeLock:PowerManager.WakeLock?=null; private var backgroundController:VoiceController?=null
36:     override fun onCreate(){super.onCreate();createChannel()}
37:     override fun onStartCommand(intent:Intent?,flags:Int,startId:Int):Int{
38:         if(intent?.action==ACTION_STOP){handler.removeCallbacksAndMessages(null);stopBackgroundController();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf();return START_NOT_STICKY}
39:         startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY
40:     }
41:     override fun onTaskRemoved(rootIntent:Intent?){handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);super.onTaskRemoved(rootIntent)}
42:     override fun onDestroy(){handler.removeCallbacksAndMessages(null);stopBackgroundController();wakeLock?.let{if(it.isHeld)runCatching{it.release()}};wakeLock=null;super.onDestroy()}
43:     override fun onBind(intent:Intent?):IBinder?=null
44:     private fun startBackgroundController(){
45:         if(backgroundController!=null)return;backgroundControllerActive=true
46:         backgroundController=VoiceController(this,true,{state->val detail=when(state){VoiceController.State.LISTENING->"Atento em segundo plano • diga “Jarvis” para chamar";VoiceController.State.SPEAKING->"Jarvis está respondendo";VoiceController.State.ERROR->"Escuta precisa de atenção";VoiceController.State.IDLE->"Jarvis ativo"};runOnMain{startForegroundNow(detail)}},{},{command->handleBackgroundCommand(command)},{message->runOnMain{startForegroundNow(message.take(90))}}).also{it.startContinuousListening()}
47:     }
48:     private fun stopBackgroundController(){backgroundControllerActive=false;backgroundController?.destroy();backgroundController=null}
49:     private fun handleBackgroundCommand(command:String){
50:         val clean=command.trim();if(clean.isBlank()){backgroundController?.resumeAfterFailedResponse();return}
51:         Thread{
52:             val token=AuthSessionStore.validAccessToken(this)
53:             val response=runCatching{(application as JarvisApplication).agent.handle(token,clean)}.getOrNull();if(response==null){backgroundController?.deliverResponse("Meu cérebro não respondeu agora. Tente me chamar novamente em instantes.");return@Thread}
54:             synchronized(ConversationStore){val conversation=ConversationStore.load(this).toMutableList();conversation+=ChatMessage("user",clean);conversation+=ChatMessage("jarvis",response.text);ConversationStore.save(this,conversation)};backgroundController?.deliverResponse(response.text)
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
### override fun onTaskRemoved — matches=1
```kotlin
38:         if(intent?.action==ACTION_STOP){handler.removeCallbacksAndMessages(null);stopBackgroundController();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf();return START_NOT_STICKY}
39:         startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY
40:     }
41:     override fun onTaskRemoved(rootIntent:Intent?){handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);super.onTaskRemoved(rootIntent)}
42:     override fun onDestroy(){handler.removeCallbacksAndMessages(null);stopBackgroundController();wakeLock?.let{if(it.isHeld)runCatching{it.release()}};wakeLock=null;super.onDestroy()}
43:     override fun onBind(intent:Intent?):IBinder?=null
44:     private fun startBackgroundController(){
45:         if(backgroundController!=null)return;backgroundControllerActive=true
46:         backgroundController=VoiceController(this,true,{state->val detail=when(state){VoiceController.State.LISTENING->"Atento em segundo plano • diga “Jarvis” para chamar";VoiceController.State.SPEAKING->"Jarvis está respondendo";VoiceController.State.ERROR->"Escuta precisa de atenção";VoiceController.State.IDLE->"Jarvis ativo"};runOnMain{startForegroundNow(detail)}},{},{command->handleBackgroundCommand(command)},{message->runOnMain{startForegroundNow(message.take(90))}}).also{it.startContinuousListening()}
47:     }
48:     private fun stopBackgroundController(){backgroundControllerActive=false;backgroundController?.destroy();backgroundController=null}
49:     private fun handleBackgroundCommand(command:String){
50:         val clean=command.trim();if(clean.isBlank()){backgroundController?.resumeAfterFailedResponse();return}
51:         Thread{
52:             val token=AuthSessionStore.validAccessToken(this)
53:             val response=runCatching{(application as JarvisApplication).agent.handle(token,clean)}.getOrNull();if(response==null){backgroundController?.deliverResponse("Meu cérebro não respondeu agora. Tente me chamar novamente em instantes.");return@Thread}
54:             synchronized(ConversationStore){val conversation=ConversationStore.load(this).toMutableList();conversation+=ChatMessage("user",clean);conversation+=ChatMessage("jarvis",response.text);ConversationStore.save(this,conversation)};backgroundController?.deliverResponse(response.text)
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
### override fun onDestroy — matches=1
```kotlin
39:         startForegroundNow("Escuta contínua ativa • diga “Jarvis” para chamar");acquireWakeLock();handler.removeCallbacksAndMessages(null);handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);return START_STICKY
40:     }
41:     override fun onTaskRemoved(rootIntent:Intent?){handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);super.onTaskRemoved(rootIntent)}
42:     override fun onDestroy(){handler.removeCallbacksAndMessages(null);stopBackgroundController();wakeLock?.let{if(it.isHeld)runCatching{it.release()}};wakeLock=null;super.onDestroy()}
43:     override fun onBind(intent:Intent?):IBinder?=null
44:     private fun startBackgroundController(){
45:         if(backgroundController!=null)return;backgroundControllerActive=true
46:         backgroundController=VoiceController(this,true,{state->val detail=when(state){VoiceController.State.LISTENING->"Atento em segundo plano • diga “Jarvis” para chamar";VoiceController.State.SPEAKING->"Jarvis está respondendo";VoiceController.State.ERROR->"Escuta precisa de atenção";VoiceController.State.IDLE->"Jarvis ativo"};runOnMain{startForegroundNow(detail)}},{},{command->handleBackgroundCommand(command)},{message->runOnMain{startForegroundNow(message.take(90))}}).also{it.startContinuousListening()}
47:     }
48:     private fun stopBackgroundController(){backgroundControllerActive=false;backgroundController?.destroy();backgroundController=null}
49:     private fun handleBackgroundCommand(command:String){
50:         val clean=command.trim();if(clean.isBlank()){backgroundController?.resumeAfterFailedResponse();return}
51:         Thread{
52:             val token=AuthSessionStore.validAccessToken(this)
53:             val response=runCatching{(application as JarvisApplication).agent.handle(token,clean)}.getOrNull();if(response==null){backgroundController?.deliverResponse("Meu cérebro não respondeu agora. Tente me chamar novamente em instantes.");return@Thread}
54:             synchronized(ConversationStore){val conversation=ConversationStore.load(this).toMutableList();conversation+=ChatMessage("user",clean);conversation+=ChatMessage("jarvis",response.text);ConversationStore.save(this,conversation)};backgroundController?.deliverResponse(response.text)
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
### private fun startBackgroundController — matches=1
```kotlin
41:     override fun onTaskRemoved(rootIntent:Intent?){handler.postDelayed({startBackgroundController()},TAKEOVER_DELAY_MS);super.onTaskRemoved(rootIntent)}
42:     override fun onDestroy(){handler.removeCallbacksAndMessages(null);stopBackgroundController();wakeLock?.let{if(it.isHeld)runCatching{it.release()}};wakeLock=null;super.onDestroy()}
43:     override fun onBind(intent:Intent?):IBinder?=null
44:     private fun startBackgroundController(){
45:         if(backgroundController!=null)return;backgroundControllerActive=true
46:         backgroundController=VoiceController(this,true,{state->val detail=when(state){VoiceController.State.LISTENING->"Atento em segundo plano • diga “Jarvis” para chamar";VoiceController.State.SPEAKING->"Jarvis está respondendo";VoiceController.State.ERROR->"Escuta precisa de atenção";VoiceController.State.IDLE->"Jarvis ativo"};runOnMain{startForegroundNow(detail)}},{},{command->handleBackgroundCommand(command)},{message->runOnMain{startForegroundNow(message.take(90))}}).also{it.startContinuousListening()}
47:     }
48:     private fun stopBackgroundController(){backgroundControllerActive=false;backgroundController?.destroy();backgroundController=null}
49:     private fun handleBackgroundCommand(command:String){
50:         val clean=command.trim();if(clean.isBlank()){backgroundController?.resumeAfterFailedResponse();return}
51:         Thread{
52:             val token=AuthSessionStore.validAccessToken(this)
53:             val response=runCatching{(application as JarvisApplication).agent.handle(token,clean)}.getOrNull();if(response==null){backgroundController?.deliverResponse("Meu cérebro não respondeu agora. Tente me chamar novamente em instantes.");return@Thread}
54:             synchronized(ConversationStore){val conversation=ConversationStore.load(this).toMutableList();conversation+=ChatMessage("user",clean);conversation+=ChatMessage("jarvis",response.text);ConversationStore.save(this,conversation)};backgroundController?.deliverResponse(response.text)
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
### private fun startForegroundNow — matches=1
```kotlin
55:         }.apply{name="jarvis-background-chat";isDaemon=true;start()}
56:     }
57:     private fun createChannel(){if(Build.VERSION.SDK_INT<Build.VERSION_CODES.O)return;getSystemService(NotificationManager::class.java).createNotificationChannel(NotificationChannel(CHANNEL_ID,"Jarvis ativo",NotificationManager.IMPORTANCE_LOW).apply{description="Mantém o Jarvis atento enquanto você permitir";setShowBadge(false)})}
58:     private fun startForegroundNow(detail:String){val notification=buildNotification(detail);if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.Q)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE)else startForeground(NOTIFICATION_ID,notification)}
59:     private fun buildNotification(detail:String):Notification{val pi=PendingIntent.getActivity(this,0,Intent(this,MainActivity::class.java).apply{flags=Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP},PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);return NotificationCompat.Builder(this,CHANNEL_ID).setSmallIcon(android.R.drawable.ic_btn_speak_now).setContentTitle("Jarvis está atento").setContentText(detail).setContentIntent(pi).setOngoing(true).setSilent(true).setCategory(NotificationCompat.CATEGORY_SERVICE).setPriority(NotificationCompat.PRIORITY_LOW).build()}
60:     private fun acquireWakeLock(){if(wakeLock?.isHeld==true)return;val manager=getSystemService(Context.POWER_SERVICE) as PowerManager;wakeLock=manager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"Jarvis:AlwaysListening").apply{setReferenceCounted(false);acquire()}}
61:     private fun runOnMain(block:()->Unit){if(Looper.myLooper()==Looper.getMainLooper())block()else handler.post(block)}
62: }
```
## BrainClient.kt
File lines: 584
### fun synthesizeSpeech — matches=1
```kotlin
485:         }.getOrNull()
486:     }
487: 
488:     fun synthesizeSpeech(accessToken: String?, text: String): SpeechAudio? {
489:         if (accessToken.isNullOrBlank() || text.isBlank()) return null
490:         val body = JSONObject().put("text", text.trim())
491:         repeat(2) { attempt ->
492:             val audio = runCatching {
493:                 val maleSpeechMp3Gateway = voiceBaseUrl.removeSuffix("/jarvis-voice") + "/jarvis-voice-mp3"
494:             val (status, response) = request(maleSpeechMp3Gateway, "POST", "/speak", accessToken, body.toString())
495:                 if (status !in 200..299) return@runCatching null
496:                 val json = JSONObject(response)
497:                 val encoded = json.optString("audioBase64")
498:                 if (encoded.isBlank()) return@runCatching null
499:                 SpeechAudio(
500:                     pcm = Base64.decode(encoded, Base64.DEFAULT),
501:                     sampleRate = json.optInt("sampleRate", 24_000).coerceAtLeast(8_000)
502:                 )
503:             }.getOrNull()
504:             if (audio != null) return audio
505:             if (attempt == 0) Thread.sleep(350L)
506:         }
507:         return null
508:     }
509: 
510:     fun activeReminders(accessToken: String): List<Reminder> {
511:         if (accessToken.isBlank()) return emptyList()
512:         return runCatching {
513:             val (status, response) = request(baseUrl, "GET", "/v1/reminders/active", accessToken, null)
514:             if (status !in 200..299) return@runCatching emptyList()
515:             val rows = JSONObject(response).optJSONArray("reminders") ?: JSONArray()
516:             buildList {
517:                 for (index in 0 until rows.length()) {
518:                     val row = rows.optJSONObject(index) ?: continue
519:                     val id = row.optString("id").trim()
520:                     val title = row.optString("title").trim()
521:                     val nextFireAt = row.optString("next_fire_at").trim()
522:                     if (id.isBlank() || title.isBlank() || nextFireAt.isBlank()) continue
523:                     val millis = runCatching {
524:                         OffsetDateTime.parse(nextFireAt).toInstant().toEpochMilli()
525:                     }.recoverCatching {
526:                         Instant.parse(nextFireAt).toEpochMilli()
527:                     }.getOrNull() ?: continue
528:                     add(
529:                         Reminder(
530:                             id = id,
531:                             title = title,
532:                             details = row.optString("details").takeIf { it.isNotBlank() },
533:                             intervalMinutes = if (row.isNull("interval_minutes")) null else row.optInt("interval_minutes").takeIf { it > 0 },
534:                             nextFireAtMillis = millis
535:                         )
536:                     )
537:                 }
538:             }
539:         }.getOrDefault(emptyList())
540:     }
541: 
542:     fun cancelReminder(accessToken: String, id: String): Boolean {
543:         if (accessToken.isBlank() || id.isBlank()) return false
544:         return deactivateReminder(accessToken, id)
545:     }
546: 
547:     fun markReminderFired(accessToken: String, id: String): Boolean {
548:         if (accessToken.isBlank() || id.isBlank()) return false
549:         val body = JSONObject().put("id", id)
550:         return runCatching {
551:             request(baseUrl, "POST", "/v1/reminders/fired", accessToken, body.toString()).first in 200..299
552:         }.getOrDefault(false)
553:     }
554: 
555:     private fun request(
556:         rootUrl: String,
557:         method: String,
558:         path: String,
559:         accessToken: String?,
```
### private val voiceBaseUrl — matches=1
```kotlin
58:     private val baseUrl: String
59:         get() = BuildConfig.BRAIN_BASE_URL.trim().trimEnd('/')
60: 
61:     private val voiceBaseUrl: String
62:         get() = baseUrl.substringBeforeLast('/') + "/jarvis-voice"
63: 
64:     val isConfigured: Boolean
65:         get() = baseUrl.startsWith("https://")
66: 
67:     fun healthStatus(): HealthStatus {
68:         if (!isConfigured) return HealthStatus(online = false)
69:         return runCatching {
70:             val (status, body) = request(baseUrl, "GET", "/health", null, null)
71:             if (status !in 200..299) return@runCatching HealthStatus(online = false)
72:             val json = JSONObject(body)
73:             HealthStatus(
74:                 online = json.optString("status") == "ok",
75:                 chatMode = json.optString("chatMode", "unknown"),
76:                 providersConfigured = json.optInt("providersConfigured", 0),
77:                 providersAvailable = json.optInt("providersAvailable", 4)
78:             )
79:         }.getOrElse { HealthStatus(online = false) }
80:     }
81: 
82:     fun health(): Boolean = healthStatus().online
83: 
84:     fun postEvent(accessToken: String, event: JSONObject): Boolean {
85:         if (!isConfigured || accessToken.isBlank()) return false
86:         return runCatching {
87:             request(baseUrl, "POST", "/v1/events", accessToken, event.toString()).first in 200..299
88:         }.getOrDefault(false)
89:     }
90: 
91:     fun chat(accessToken: String?, message: String, webSearch: Boolean = false): ChatResponse? {
92:         if (!isConfigured || message.isBlank()) return null
93:         val cleanMessage = message.trim()
94: 
95:         reminderManagementResponse(accessToken, cleanMessage)?.let { return it }
96: 
97:         reminderCancellationResponse(accessToken, cleanMessage)?.let { return it }
98: 
99:         val outboundMessage = if (cleanMessage.equals("Jarvis", ignoreCase = true)) {
100:             """
101:             O dono chamou-te pelo nome, sem dizer mais nada. Nao respondas ao nome como se fosse uma pergunta: confirma que estas atento e pronto para ouvir o que vem a seguir.
102:             Regras desta resposta:
103:             - UMA frase. Curta. Oral. Nada de listas, nada de markdown, nada de aspas.
104:             - Nao digas "estou aqui" nem "podes falar" nem "em que posso ajudar". Usa outras palavras.
105:             - Cada vez uma formula diferente. Nao tenhas um bordao fixo.
106:             - Se souberes algo concreto e recente do dono (um lembrete proximo, algo em atraso), podes menciona-lo em meia frase. Uma so. Nunca despejares a agenda.
107:             - Nao anuncies o que estas a fazer nem menciones infraestrutura, audio ou modelos.
108:             - Portugues de Portugal.
109:             """.trimIndent()
110:         } else {
111:             cleanMessage
112:         }
113: 
114:         val messages = JSONArray().put(
115:             JSONObject().put("role", "user").put("content", outboundMessage)
116:         )
117:         val body = JSONObject()
118:             .put("messages", messages)
119:             .put("webSearch", webSearch)
120: 
121:         return runCatching {
122:             val (status, response) = request(baseUrl, "POST", "/v1/chat", accessToken, body.toString())
123:             if (status !in 200..299) {
124:                 val serverMessage = runCatching {
125:                     JSONObject(response).optString("message").takeIf { it.isNotBlank() }
126:                 }.getOrNull() ?: response.take(180).ifBlank { null }
127:                 throw ChatException(status, serverMessage)
128:             }
129:             val json = JSONObject(response)
130:             val rawText = json.optString("text").takeIf { it.isNotBlank() } ?: return@runCatching null
131:             val text = sanitizeAssistantText(rawText)
132:             if (text.isBlank()) {
```
