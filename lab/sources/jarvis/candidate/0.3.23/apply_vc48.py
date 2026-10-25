#!/usr/bin/env python3
"""VC48: actual multi-turn AI interaction instead of one isolated message.

Derive EXCLUSIVELY from published VC47. This patch does not touch voice output,
TTS selection, audio, wake word, reminders, VoicePrint, or foreground services.
"""
from pathlib import Path

APP=Path("jarvis0215/app")
BUILD=APP/"build.gradle.kts"
MAIN=APP/"src/main/java/pt/vcaitano/jarvis/MainActivity.kt"
BRAIN=APP/"src/main/java/pt/vcaitano/jarvis/network/BrainClient.kt"

def replace_once(s,old,new,what):
    n=s.count(old)
    if n!=1:raise SystemExit(f"VC48 expected exactly 1 {what}, found {n}")
    return s.replace(old,new,1)

build=BUILD.read_text(encoding="utf-8")
build=replace_once(build,"versionCode = 47","versionCode = 48","versionCode")
build=replace_once(build,'versionName = "0.3.22"','versionName = "0.3.23"',"versionName")
BUILD.write_text(build,encoding="utf-8")

brain=BRAIN.read_text(encoding="utf-8")
brain=replace_once(
    brain,
    "fun chat(accessToken: String?, message: String): ChatResponse? {",
    "fun chat(accessToken: String?, message: String, conversation: List<Pair<String, String>> = emptyList()): ChatResponse? {",
    "BrainClient.chat signature",
)
brain=replace_once(brain,
    '''        val messages = JSONArray().put(
            JSONObject().put("role", "user").put("content", outboundMessage)
        )
        val body = JSONObject().put("messages", messages)''',
    '''        // Include recent chat turns so phrases like "então hoje é o segundo
        // turno?" or "e o resultado?" have a referent. This is still local,
        // user-owned history; never share another user's conversation.
        val messages = JSONArray()
        val earlier = conversation
            .filter { (role, text) ->
                (role == "user" || role == "assistant") && text.isNotBlank()
            }.takeLast(14).toMutableList()
        // MainActivity already appended the current user turn to its UI store.
        if (earlier.lastOrNull()?.first == "user" &&
            earlier.lastOrNull()?.second?.trim() == cleanMessage) {
            earlier.removeAt(earlier.lastIndex)
        }
        earlier.takeLast(12).forEach { (role, turn) ->
            messages.put(JSONObject()
                .put("role", role)
                .put("content", turn.trim().take(1_800)))
        }
        messages.put(JSONObject().put("role", "user").put("content", outboundMessage))
        val body = JSONObject().put("messages", messages)''',
    "multi-turn conversation body",
)
BRAIN.write_text(brain,encoding="utf-8")

main=MAIN.read_text(encoding="utf-8")
main=replace_once(
    main,
    '''        messages += ChatMessage(role = "user", text = text)
        persistConversation()

        chatBusy = true''',
    '''        messages += ChatMessage(role = "user", text = text)
        persistConversation()

        // Snapshot before starting the background request. The server receives
        // recent user/Jarvis turns, not an isolated sentence without context.
        val conversationForBrain = messages.toList().takeLast(16)
            .filter { it.role == "user" || it.role == "jarvis" }
            .map {
                (if (it.role == "jarvis") "assistant" else "user") to it.text
            }

        chatBusy = true''',
    "capture UI conversation",
)
oldCall="BrainClient.chat(token, text)"
oldRenew="BrainClient.chat(renewed, text)"
if oldCall not in main and oldRenew not in main:
    raise SystemExit("VC48 cannot find MainActivity BrainClient.chat sites")
main=main.replace(oldCall,"BrainClient.chat(token, text, conversationForBrain)")
main=main.replace(oldRenew,"BrainClient.chat(renewed, text, conversationForBrain)")
if "BrainClient.chat(" not in main:
    raise SystemExit("VC48 conversation dispatcher lost")
if "conversationForBrain" not in main:
    raise SystemExit("VC48 conversation capture missing")
MAIN.write_text(main,encoding="utf-8")

check=[
    ('versionCode = 48' in build and 'versionName = "0.3.23"' in build,"version"),
    ('conversation: List<Pair<String, String>>' in brain,"nonbreaking chat signature"),
    ('earlier.takeLast(12).forEach' in brain,"history forwarding"),
    ('conversationForBrain' in main,"snapshot"),
    ('VoiceController' in main and 'voiceController.deliverResponse(response.text)' in main,"male voice output untouched"),
    ('JarvisListeningService' in main and 'override fun onPause()' in main,"background listening still intact"),
]
for good,what in check:
    if not good:raise SystemExit("VC48 failed invariant: "+what)
print("VC48_SOURCE_OK — recent turns sent to real AI; no TTS, reminders or microphone changes")
