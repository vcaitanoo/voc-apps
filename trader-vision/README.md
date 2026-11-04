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

