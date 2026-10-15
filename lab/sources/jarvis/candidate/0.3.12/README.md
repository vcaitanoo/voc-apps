# Jarvis VC37 — 0.3.12

Candidata para corrigir dois problemas reportados: o Jarvis deixar de ouvir e a seleção cair numa voz feminina.

- `versionCode`: 37
- `versionName`: 0.3.12
- A voz masculina em português é obrigatória; se não existir uma voz compatível instalada, o app deve informar o erro em vez de falar com voz feminina.
- A captura deve continuar baseada em `AudioRecord`/microfone, sem `SpeechRecognizer.startListening()` e sem bipes de reconhecimento.
- A versão estável não deve ser substituída antes de compilação, validação e teste no dispositivo.

O patch de aplicação está em `apply_vc37.py`. O build de distribuição é orquestrado pelo VOC Lab; o APK só pode ser promovido depois da validação do artefato e teste real.
