from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text()
old = '''        Thread {
            val token = AuthSessionStore.validAccessToken(appContext)
            val cloudAudio = BrainClient.synthesizeSpeech(token, text)
            if (cloudAudio != null && voiceOutputEnabled && !destroyed) {
                val played = playPcm(cloudAudio.pcm, cloudAudio.sampleRate)
                handler.post {
                    if (played) finishSpeaking() else speakWithMaleOnlyLocalFallback(text)
                }
            } else {
                handler.post { speakWithMaleOnlyLocalFallback(text) }
            }
        }.apply {'''
new = '''        Thread {
            val token = AuthSessionStore.validAccessToken(appContext)
            val chunks = splitForSpeech(text)
            val cloudAudio = if (token.isNullOrBlank()) {
                emptyList()
            } else {
                chunks.map { chunk -> BrainClient.synthesizeSpeech(token, chunk) }
            }
            val cloudReady = cloudAudio.size == chunks.size && cloudAudio.all { it != null }
            if (cloudReady && voiceOutputEnabled && !destroyed) {
                val played = cloudAudio.filterNotNull().all { audio ->
                    voiceOutputEnabled && !destroyed && playPcm(audio.pcm, audio.sampleRate)
                }
                handler.post {
                    if (played) finishSpeaking() else speakWithMaleOnlyLocalFallback(text)
                }
            } else {
                handler.post { speakWithMaleOnlyLocalFallback(text) }
            }
        }.apply {'''
if old not in s:
    raise SystemExit('voice delivery block not found')
s = s.replace(old, new, 1)
needle = '    private fun speakWithMaleOnlyLocalFallback(text: String) {'
helper = r'''    private fun splitForSpeech(text: String, maxChars: Int = 650): List<String> {
        val clean = text.trim()
        if (clean.length <= maxChars) return listOf(clean)
        val sentences = clean.split(Regex("(?<=[.!?])\\s+"))
        val chunks = mutableListOf<String>()
        val current = StringBuilder()
        for (sentence in sentences) {
            if (sentence.length > maxChars) {
                if (current.isNotEmpty()) {
                    chunks += current.toString().trim()
                    current.clear()
                }
                sentence.chunked(maxChars).forEach { chunks += it.trim() }
                continue
            }
            if (current.isNotEmpty() && current.length + 1 + sentence.length > maxChars) {
                chunks += current.toString().trim()
                current.clear()
            }
            if (current.isNotEmpty()) current.append(' ')
            current.append(sentence)
        }
        if (current.isNotEmpty()) chunks += current.toString().trim()
        return chunks.filter { it.isNotBlank() }
    }

''' + needle
if needle not in s:
    raise SystemExit('voice fallback block not found')
p.write_text(s.replace(needle, helper, 1))
