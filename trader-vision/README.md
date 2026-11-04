# VOC Trader Vision 0.1.0-demo
Novo projeto Android independente, criado para captura visual do gráfico Hezilex em Chrome, análise local e **teste em conta DEMO**. O código-fonte original do MT5 não foi copiado; apenas famílias de estratégias foram adaptadas. Não há trailing nas opções com expiração fixa.

**Nunca opere contas reais nesta versão.** A imagem não fornece necessariamente OHLC/preço exato, histórico oculto, payout, retorno ou probabilidade real de lucro. A nota 0–100 é técnica, não taxa de acerto. O bot bloqueia operações se não identificar botões, velas suficientes, campos e condições de risco. Para testar cliques, configure/autorize conta demo, acessibilidade e captura, veja o painel.

- Package: pt.vcaitano.tradervision
- versionCode: 1; versionName: 0.1.0-demo
- Captura: Android MediaProjection com consentimento a cada sessão
- Toque: AccessibilityService ativado manualmente
- Tela ligada: FLAG_KEEP_SCREEN_ON e WakeLock enquanto captura
- Análises: EMA 9/21/50, RSI, MACD proxy, Bollinger, ATR, DX proxy de tendência, suporte/resistência, 11 famílias de setups.
- Barras agregadas de outros timeframes NÃO disponíveis somente por imagem. Período do gráfico escolhido manualmente.
- Sem API não se pode verificar por completo os resultados executados na corretora. Os WIN/LOSS são apontamentos manuais.
- A compra/venda somente é permitida após validação de screenshot + confirmação de campos + janela de horário e risco definido pelo utilizador.
- Não inclui OCR nem modelo ML externo. Detecta botões por cores e pixels das velas, e textos de campos usando acessibilidade do Chrome quando expostos.

Build: Gradle 8.13 + Android SDK 36 + JDK 17: `gradle -p trader-vision :app:assembleDebug`.
Debug APK é assinado com certificado de teste (não usar para produção; builds de runners distintos exigem assinatura persistente para atualizar sem reinstalar).

**Estado:** fonte candidata; build Android em CI e teste em aparelho requerem confirmação independente.
