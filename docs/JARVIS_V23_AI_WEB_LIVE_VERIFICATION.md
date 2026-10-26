# Jarvis v23 — teste real do servidor em produção

UTC: 2026-10-26T20:14:10.438739+00:00
GitHub Action: 40393802919

Health: PASS; automatic web=True; session required=False
## Conversa comum: PASS
Mode: ai-direct; model provider: openrouter; sources=0; text-length=166; attempt=False

## Tesla carro voador / pesquisa automatica sem login: PASS
Mode: ai-web-sources; model provider: openrouter; sources=3; text-length=361; attempt=True
- source host: roadsterflyingcar.com
- source host: veja.abril.com.br
- source host: g1.globo.com

## Tesla pergunta sobre noticias sem login: FAIL
Mode: ai-web-unavailable; model provider: openrouter; sources=0; text-length=1069; attempt=True

## Apuracao do segundo turno: PASS
Mode: ai-web-sources; model provider: openrouter; sources=1; text-length=279; attempt=True
- source host: www.tse.jus.br

## Serie Meu Nome e Farah: PASS
Mode: ai-web-sources; model provider: openrouter; sources=3; text-length=627; attempt=True
- source host: www.threads.com
- source host: www.estadao.com.br
- source host: www.bnewssaopaulo.com.br

## Continuidade da serie: PASS
Mode: ai-direct; model provider: openrouter; sources=0; text-length=324; attempt=False

Overall: FAIL; failures=1
