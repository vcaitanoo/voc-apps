# Jarvis v17 — teste real do servidor em produção

UTC: 2026-10-25T15:13:02.935844+00:00
GitHub Action: 40205869986

Health: PASS; automatic web=True; session required=False
## Conversa comum: PASS
Mode: ai-direct; model provider: openrouter; sources=0; text-length=159; attempt=False

## Tesla carro voador / pesquisa automatica sem login: PASS
Mode: ai-web-sources; model provider: openrouter; sources=4; text-length=568; attempt=True
- source host: www.youtube.com
- source host: forbes.com.br
- source host: www.youtube.com
- source host: coinmarketcap.com

## Tesla pergunta sobre noticias sem login: PASS
Mode: ai-web-sources; model provider: openrouter; sources=4; text-length=397; attempt=True
- source host: www.facebook.com
- source host: ncnews.com.br
- source host: motorwatt.com
- source host: g1.globo.com

Overall: PASS; failures=0
