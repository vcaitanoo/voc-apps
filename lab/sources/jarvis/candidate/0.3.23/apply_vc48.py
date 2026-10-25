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
# Keep any existing optional args rather than assuming VC9's method signature.
import re
chat_signature = re.compile(r"fun\s+chat\s*\(([^)]*)\)\s*:\s*ChatResponse\?\s*\{")
matches = list(chat_signature.finditer(brain))
if len(matches) != 1:
    candidates = [line.strip() for line in brain.splitlines() if "fun chat" in line]
    raise SystemExit("VC48: unexpected chat declaration " + repr(candidates[:8]))
existing_params = matches[0].group(1)
if "accessToken:" not in existing_params or "message:" not in existing_params:
    raise SystemExit("VC48: chat parameters changed: " + existing_params)
signature = matches[0].group(0)
replacement = signature.replace(existing_params, existing_params.rstrip() + ", conversation: List<Pair<String, String>> = emptyList()")
brain = brain.replace(signature, replacement, 1)
# Add prior turns immediately before the actual network call, without assuming
# the exact JSON body-building layout in this newer version of BrainClient.
network_anchor = 'val (status, response) = request(baseUrl, "POST", "/v1/chat", accessToken, body.toString())'
if brain.count(network_anchor) != 1:
    candidates=[line.strip() for line in brain.splitlines() if "/v1/chat" in line]
    raise SystemExit("VC48: cannot locate real chat request " + repr(candidates[:8]))
brain = brain.replace(network_anchor, '''val previousTurns = JSONArray()
            val earlier = conversation
                .filter { (role, text) ->
                    (role == "user" || role == "assistant") && text.isNotBlank()
                }.takeLast(14).toMutableList()
            if (earlier.lastOrNull()?.first == "user" &&
                earlier.lastOrNull()?.second?.trim() == cleanMessage) {
                earlier.removeAt(earlier.lastIndex)
            }
            earlier.takeLast(12).forEach { (role, turn) ->
                previousTurns.put(JSONObject()
                    .put("role", role)
                    .put("content", turn.trim().take(1_800)))
            }
            val pendingTurns = body.optJSONArray("messages") ?: JSONArray()
            for (index in 0 until pendingTurns.length()) {
                previousTurns.put(pendingTurns.get(index))
            }
            body.put("messages", previousTurns)
            ''' + network_anchor, 1)
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
# Published VC47 routes requests via JarvisAgent (NOT directly to BrainClient).
oldCall="agent.handle(token, text)"
if main.count(oldCall)!=1:raise SystemExit("VC48 missing real MainActivity agent.handle dispatcher")
main=main.replace(oldCall,"agent.handle(token, text, conversationForBrain)",1)
main=main.replace(".map {\n                (if (it.role == \"jarvis\") \"assistant\" else \"user\") to it.text\n            }", ".map {\n                (if (it.role == \"jarvis\") \"assistant\" else \"user\") to it.text\n            }")
if "agent.handle(token, text, conversationForBrain)" not in main:
    raise SystemExit("VC48 failed to wire UI history to real agent")
MAIN.write_text(main,encoding="utf-8")


# Preserve tools and reminder routing: recent conversation is forwarded only
# when the orchestrator chooses the AI provider, never used to score tool intent.
agents=list(APP.glob("src/main/java/**/JarvisAgent.kt"))
providers=list(APP.glob("src/main/java/**/AiProvider.kt"))
if len(agents)!=1 or len(providers)!=1:
    raise SystemExit("VC48 agent/provider paths not unique")
AGENT=agents[0]; PROVIDER=providers[0]
agent=AGENT.read_text(encoding="utf-8")
agent=replace_once(agent,
    "fun handle(accessToken: String?, rawMessage: String): AgentResponse? {",
    "fun handle(accessToken: String?, rawMessage: String, conversation: List<Pair<String, String>> = emptyList()): AgentResponse? {",
    "agent history parameter")
agent=replace_once(agent,
    "requiresInternet = InternetNeedDetector.requiresInternet(message)",
    "requiresInternet = InternetNeedDetector.requiresInternet(message),\n                conversation = conversation",
    "agent history forwarded to AI request")
AGENT.write_text(agent,encoding="utf-8")

provider=PROVIDER.read_text(encoding="utf-8")
provider=replace_once(provider,
    "val requiresInternet: Boolean = false\n)",
    "val requiresInternet: Boolean = false,\n    val conversation: List<Pair<String, String>> = emptyList()\n)",
    "AiRequest schema compatible with all existing callers")
provider=replace_once(provider,
    "webSearch = request.requiresInternet",
    "webSearch = request.requiresInternet,\n            conversation = request.conversation",
    "full history reaches BrainClient via GatewayAiProvider")
PROVIDER.write_text(provider,encoding="utf-8")

check=[
    ('versionCode = 48' in build and 'versionName = "0.3.23"' in build,"version"),
    ('conversation: List<Pair<String, String>>' in brain,"nonbreaking chat signature"),
    ('earlier.takeLast(12).forEach' in brain,"history forwarding"),
    ('conversationForBrain' in main,"snapshot"),
    ('conversation = request.conversation' in provider,"AI provider forwards turns"),
    ('agent.handle(token, text, conversationForBrain)' in main,"real UI route"),
    ('VoiceController' in main and 'voiceController.deliverResponse(response.text)' in main,"male voice output untouched"),
    ('JarvisListeningService' in main and 'override fun onPause()' in main,"background listening still intact"),
]
for good,what in check:
    if not good:raise SystemExit("VC48 failed invariant: "+what)
print("VC48_SOURCE_OK — recent turns sent to real AI; no TTS, reminders or microphone changes")
