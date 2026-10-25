# Jarvis v21 — teste real do servidor em produção

UTC: 2026-10-25T22:17:08.358597+00:00
GitHub Action: 40239456032

Health: PASS; automatic web=True; session required=False
## Conversa comum: PASS
Mode: ai-direct; model provider: openrouter; sources=0; text-length=135; attempt=False

## Tesla carro voador / pesquisa automatica sem login: PASS
Mode: ai-web-sources; model provider: openrouter; sources=3; text-length=689; attempt=True
- source host: pasqualepillitteri.it
- source host: roadsterflyingcar.com
- source host: www.tradingkey.com

## Tesla pergunta sobre noticias sem login: PASS
Mode: ai-web-sources; model provider: openrouter; sources=4; text-length=767; attempt=True
- source host: www.greendrive-accessories.com
- source host: ncnews.com.br
- source host: motorwatt.com
- source host: g1.globo.com

## Apuracao do segundo turno: FAIL
Mode: web-unavailable; model provider: jarvis-web; sources=0; text-length=113; attempt=False

Overall: FAIL; failures=1
