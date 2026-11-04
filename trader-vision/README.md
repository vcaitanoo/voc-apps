# VOC Trader Vision – Gestão 0.2.0-demo (teste isolado)

Esta candidata usa EXATAMENTE as fontes visuais/estratégias da V1 instalada, alterando **somente gestão monetária, interface de gestão e identificação do pacote para teste separado**.

O package desta candidata é `pt.vcaitano.tradervision.gestaoteste` (VC2). O V1 (package `pt.vcaitano.tradervision`) e o APK aprovado visualmente NÃO foram sobrescritos. O V1 tinha certificado DEBUG temporário SHA-256 `da17fe1c3ac49d1fcd4c2cc6067f3fad0b1acdcee143129dcc2f1e6a76371f35` cuja chave privada não está disponível; tentar atualizar seu package com outro signer falharia. O novo app instala em paralelo, evitando desinstalar ou afetar a V1. Precisa **parar a V1 antes de iniciar a V2**, pois ambas podem mostrar o painel e capturar a tela.

## Gestão
- Valor mínimo permitido pela Hezilex: €1.
- Valor calculado = `max(€1, truncate_to_cents(saldo_demo × risco% / 100))`.
- Alvo padrão de risco: 1%; continua configurável.
- Saldo de €29,48, risco alvo 1% → entrada €1 e **risco efetivo 3,39%** (o mínimo excede o alvo; informamos isso explicitamente).
- Saldo €100 → €1; saldo €150 → €1,50; saldo €250 → €2,50.
- Saldo inferior a €1, percentual inválido ou entrada acima do saldo: BLOQUEADO.
- O campo de valor do app mostra a gestão calculada e é somente leitura. O campo Valor da Hezilex ainda precisa de ajuste manual para corresponder ao valor calculado; se não coincidir, o robô bloqueia o gesto como na V1.
- Não ler saldo automaticamente da corretora. Atualize-o manualmente no app após mudança de banca. Sem martingale.
- Clique automático somente com os mesmos controles e verificações de conta DEMO da V1.

## Estado
Esta versão é candidata experimental. Compilar/assinar/validar estrutura não comprova abertura no Android nem execução de trade. Testar em DEMO exclusivamente, sem disponibilizar ordem real. V1 mantida e recuperável em `apks/voc-trader-vision/candidate/`.

Para testes matemáticos locais: `javac -d /tmp/tvrisk trader-vision/app/src/main/java/pt/vcaitano/tradervision/RiskManager.java trader-vision/tests/RiskManagerTest.java && java -cp /tmp/tvrisk pt.vcaitano.tradervision.RiskManagerTest`


## Ajuste de gatilho de entrada — V3, código de teste, sem promoção
- O score 0–100 é confluência heurística sobre pixels, **não** probabilidade estatística nem garantia de execução.
- A V2 executava apenas entre o 3º e o 12º segundo após o minuto divisível pelo timeframe, usando relógio local. Isso perdia quase todas as oportunidades depois da condição técnica reconhecida.
- A V3 autoriza a tentativa de entrada em DEMO quando o sinal da penúltima vela (presumida fechada) se mantém por 3 análises consecutivas (score >= mínimo), respeitando validação da conta, payout/expiração configurada, permissões, saldo, stop diário e intervalo mínimo de `max(timeframe, expiração)` minutos entre tentativas.
- Sem dados OHLC oficiais, não se comprova o verdadeiro fechamento nem a sincronização com o broker: nunca usar esta heurística em dinheiro real. Uma rejeição de acessibilidade fica 30s visível no painel, sem tentar toque cego.
- Mesma identidade `pt.vcaitano.tradervision.gestaoteste`, sem novo aplicativo; fonte isolada em branch de fix, versãoCode 3. **Não publicar APK em catálogo** antes de assinar com a MESMA chave privada da V2: certificado SHA-256 `3151054948a50ccb3dde9a97fd1b3bc298f544fe5742aa384d901c3bf1c01632`. A chave debug não está arquivada. Compilar debug com outra chave não oferece atualização por cima. Stable e candidate V2 mantidas.

## Painel móvel — revisão VC3
- A faixa verde **↕ ARRASTE PARA MOVER** no topo e o próprio texto do painel aceitam gestos de arrastar; o botão vermelho PARAR ROBÔ mantém exclusivamente a função de parar.
- O gesto usa coordenadas brutas de toque e `WindowManager.updateViewLayout`, limitadas aos bordos da área disponível para nunca perder o painel fora da tela.
- A localização é guardada em `SharedPreferences` como proporção horizontal/vertical; reaparece no mesmo local relativo após reabrir a captura, inclusive com ecrã redimensionado.
- Não muda a análise visual, o gatilho, os campos da Hezilex, o risco, as permissões nem a identidade Android. Apenas os arquivos `VisionService.java`, `PanelPosition.java` e `PanelPositionTest.java` e este registo documental.
- APK VC3 ainda NÃO distribuído: assinatura de compilação debug do CI é diferente da V2 instalada, cuja chave privada não está recuperada. Não substituir a VC2 no VOC Lab nem afirmar compatibilidade de atualização.
