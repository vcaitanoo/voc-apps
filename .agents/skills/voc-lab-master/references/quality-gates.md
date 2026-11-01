# Portões de qualidade por tipo de tarefa

## Diagnóstico / mudança pontual
- Garantir origem correta, escopo pequeno, arquivos alterados exatos e diff limpo.
- Reproduzir o bug antes da correção quando viável; definir um teste específico de regressão e executar onde há ambiente.
- Se um teste não puder ser executado, reportar a ausência sem declarar “corrigido”.

## Projeto Android
- Confirmar identidade da app: applicationId/package, versionCode, versionName, minSdk/targetSdk, assinatura e compatibilidade da versão de Android.
- Build com Gradle a partir do fonte validado, sem reempacotar APK nem modificar classes.dex/smali.
- Verificar `aapt2`/`apkanalyzer`/`bundletool`/`apksigner` conforme ferramenta disponível; calcular SHA-256 de todos os artefatos e confrontar certificado histórico.
- Diferenciar: código revisado; testes unitários; build compilada; análise estrutural; instalação em emulador; **teste físico pelo usuário**. Nenhum nível implica o seguinte.

## Navegação GPS 3D
Preservar, quando não solicitada alteração, GPS real, rotas/recalculo, posição e rumo, suavidade, zoom, giro 2 dedos, pinça, arrasto, legibilidade das ruas, câmera 2D/3D, árvores, casas/postos/mercados/igrejas 3D, tela ligada, modo noturno, AdMob/consentimento e ações de cancelar/terminar rota. Para mudança em gesto ou câmera, conferir principalmente regressões de toque e desempenho. Não alegar que teste em navegador prova fluidez no Samsung.

## Jarvis
Não tocar em voz masculina escolhida, VoicePrint, escuta, notificações faladas, lembretes, memória de conversa ou função backend de IA fora de escopo. Não trocar o provedor ou a identidade de voz “para melhorar” sem pedido.

## Damas
Não afetar regras, tabuleiro, IA, multiplayer em dois aparelhos, turnos, pareamento, anúncios e persistência sem solicitação. Um teste de tela local não comprova partida entre dois Androids.

## Tela Sempre Ativa
Não afetar relógio, bloqueio/proximidade, anti burn-in, segmentação, brilho, toque, notificações, permissões, anúncios ou comportamento em diferentes modelos Samsung fora de escopo.
