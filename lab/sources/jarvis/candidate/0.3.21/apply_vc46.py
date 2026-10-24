#!/usr/bin/env python3
"""VC46: restore the historical cloud-first male voice, with verified MP3 decode.

Exact successor of the published VC45; preserves its TTS voice lock, listening
pipeline, VoicePrint, interface, saved reminders and release signing. No fallback
to a female/default local voice.
"""
from pathlib import Path
import re

ROOT=Path("jarvis0215")
BUILD=ROOT/"app/build.gradle.kts"
VOICE=ROOT/"app/src/main/java/pt/vcaitano/jarvis/voice/VoiceController.kt"
BRAIN=ROOT/"app/src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"

def once(s,old,new,label):
    n=s.count(old)
    if n!=1: raise SystemExit(f"VC46 expected exactly 1 {label}, got {n}")
    return s.replace(old,new,1)

build=BUILD.read_text(encoding="utf-8")
build=once(build,"versionCode = 45","versionCode = 46","versionCode")
build=once(build,'versionName = "0.3.20"','versionName = "0.3.21"',"versionName")
BUILD.write_text(build,encoding="utf-8")

# The existing historic speech gateway remains unchanged for old APKs. Only
# VC46 requests MP3 from a new authenticated server endpoint.
brain=BRAIN.read_text(encoding="utf-8")
brain=once(
    brain,
    'val (status, response) = request(voiceBaseUrl, "POST", "/speak", accessToken, body.toString())',
    '''val maleSpeechMp3Gateway = voiceBaseUrl.removeSuffix("/jarvis-voice") + "/jarvis-voice-mp3"
            val (status, response) = request(maleSpeechMp3Gateway, "POST", "/speak", accessToken, body.toString())''',
    "cloud speech endpoint",
)
BRAIN.write_text(brain,encoding="utf-8")

voice=VOICE.read_text(encoding="utf-8")
dispatch=re.compile(r'        handler\.post \{ (speakWith(?:MaleOnlyLocalFallback|LocalFallback))\(text\) \}')
matches=list(dispatch.finditer(voice))
if len(matches)!=1: raise SystemExit(f"VC46 expected one local speech dispatch, found {len(matches)}")
local_fn=matches[0].group(1)
old=matches[0].group(0)
new='''        // Original Jarvis: male cloud speech is primary; Android's positively
        // identified male TTS is the offline fallback. MP3 is decoded by
        // Android MediaPlayer, NEVER passed to raw PCM AudioTrack.
        Thread {
            val token = AuthSessionStore.validAccessToken(appContext)
            val cloudAudio = runCatching {
                BrainClient.synthesizeSpeech(token, text)
            }.getOrNull()
            val played = cloudAudio != null && playVerifiedMaleMp3(cloudAudio.pcm)
            handler.post {
                if (destroyed || !voiceOutputEnabled) {
                    finishSpeaking()
                } else if (played) {
                    finishSpeaking()
                } else {
                    %s(text)
                }
            }
        }.apply {
            name = "jarvis-original-male-cloud-voice"
            isDaemon = true
            start()
        }''' % local_fn
voice=once(voice,old,new,"restore cloud-first response speech")

helper=r'''    private fun playVerifiedMaleMp3(bytes: ByteArray): Boolean {
        // Reject raw PCM, WAV and malformed/JSON data: all can sound like
        // distorted phonemes if treated as raw 16-bit PCM.
        if (bytes.size < 200 || bytes.size > 8_000_000) return false
        val id3 = bytes.size >= 3 &&
            bytes[0] == 'I'.code.toByte() &&
            bytes[1] == 'D'.code.toByte() &&
            bytes[2] == '3'.code.toByte()
        val frame = bytes.size >= 2 &&
            (bytes[0].toInt() and 255) == 255 &&
            (bytes[1].toInt() and 224) == 224
        if (!id3 && !frame) return false

        var cacheFile: java.io.File? = null
        var player: android.media.MediaPlayer? = null
        try {
            cacheFile = java.io.File.createTempFile(
                "jarvis-original-male-", ".mp3", appContext.cacheDir
            )
            cacheFile.writeBytes(bytes)
            val media = android.media.MediaPlayer()
            player = media
            media.setAudioAttributes(
                android.media.AudioAttributes.Builder()
                    .setUsage(android.media.AudioAttributes.USAGE_MEDIA)
                    .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            media.setDataSource(cacheFile.absolutePath)
            media.prepare()
            if (!voiceOutputEnabled || destroyed) return false
            media.start()
            val duration = media.duration.toLong().coerceIn(500L, 90_000L)
            val deadline = System.currentTimeMillis() + duration + 4_000L
            var heard = false
            while (!destroyed && voiceOutputEnabled && System.currentTimeMillis() < deadline) {
                if (!media.isPlaying) break
                heard = true
                Thread.sleep(45L)
            }
            return heard && !media.isPlaying && !destroyed && voiceOutputEnabled
        } catch (_: Throwable) {
            return false
        } finally {
            runCatching { player?.stop() }
            runCatching { player?.release() }
            runCatching { cacheFile?.delete() }
        }
    }

'''
anchor='    private fun playPcm(pcm: ByteArray, sampleRate: Int): Boolean {'
voice=once(voice,anchor,helper+anchor,"verified MP3 playback helper")
if 'startListening(' in voice:
    raise SystemExit("VC46 regressed silent AudioRecord listening")
for token in (
    'playVerifiedMaleMp3(cloudAudio.pcm)',
    'jarvis-original-male-cloud-voice','jarvis_original_male_voice_lock',
    'readyEngine.setSpeechRate(0.98f)','readyEngine.setPitch(0.76f)',
    'VoicePrint.matches(appContext','MediaRecorder.AudioSource.MIC','explicitMale',
):
    if token not in voice:
        raise SystemExit("VC46 missing voice/listening invariant: "+token)
VOICE.write_text(voice,encoding="utf-8")
print("VC46_SOURCE_OK: existing VC45 preserved; original male cloud-first restored; MP3 validated and decoded; no female fallback")
