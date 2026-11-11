# Roteiro de demonstração: até três minutos

Objetivo: mostrar o problema do gerente de relacionamento do BB, a solução funcionando com dados sintéticos, e o IBM Bob operando no fluxo de desenvolvimento. Duração total: 180 segundos.

## Preparação antes de gravar

1. Executar `python -m elo.server` na raiz do projeto e abrir `http://127.0.0.1:8000`.
2. Selecionar **Chegar ao próximo recebimento** (`scenario-month`). Se a leitura estiver ativa, clicar em **Reiniciar cenário** (`demo-reset`) para restaurar os valores e depois em **Desativar leitura e limpar planos** (`consent-toggle`). O reinício dos dados preserva o consentimento; a revogação é uma escolha separada.
3. Fechar outros programas e notificações. Ocultar qualquer dado pessoal ou credencial que possa aparecer na tela.
4. Abrir uma segunda aba com o Bob IDE no repositório Elo Financeiro, deixar pronto para mostrar na cena do Bob (0 s a 20 s).
5. Conferir que o selo do planejador aparece logo abaixo do título da análise depois de autorizar os dados. Sem credenciais IBM ele diz "Planejador: regras locais"; com o watsonx ativo, "Planejador: IBM watsonx.ai escolheu as ferramentas".

## Cenas e narração

| Tempo | Tela e ação | Narração |
| --- | --- | --- |
| 0–15 s | Mostrar o Bob IDE com o repositório carregado. Apontar a lista de tarefas recentes e, em seguida, a tabela de sessões em `docs/USO_DO_BOB.md`. | "Começamos pelo desenvolvimento. Usamos o IBM Bob em modo Agent em cinco sessões: ele implementou a projeção de parcelas e a redução personalizada, corrigiu cinco problemas no fluxo de propostas e criou trinta casos de validação IBM. Cada sessão está registrada com commits no repositório." |
| 15–25 s | Alternar para a interface do protótipo em `http://127.0.0.1:8000`. Mostrar a tela inicial sem dados carregados. | "O problema que o agente resolve: Marcos, gerente de relacionamento do BB, recebe um cliente que precisa de ajuda com o fluxo de caixa. Hoje, Marcos monta esse calendário manualmente. Estimamos quinze a vinte minutos de preparação, isso ainda precisa ser medido com gerentes reais." |
| 25–35 s | Clicar em **Autorizar dados da demonstração** (`start`). Apontar o selo do planejador abaixo do título. | "Com o Elo, Marcos autoriza a leitura. Os dados são sintéticos, nenhuma conta bancária conectada. Este selo mostra quem escolheu as ferramentas: aqui, [regras locais / o IBM watsonx.ai]. Os cálculos são sempre do código." |
| 35–53 s | Mostrar **Menor saldo previsto** (`minimum`) e o gráfico. Abrir **Ver os valores de cada dia** para apontar o pior dia; fechar em seguida. | "O saldo começa em mil e quinhentos reais. Mas o calendário leva o menor saldo a menos cem antes do recebimento. O saldo final positivo esconde esse intervalo, é exatamente o que o Marcos não consegue ver na tela de saldo atual." |
| 53–72 s | Mostrar o efeito da proposta e clicar em **Ativar plano de gastos** (`approve-budget-plan`). Apontar o novo valor de R$ 200. | "O agente propõe reduzir trezentos reais de lazer previsto, preservando as despesas essenciais. Marcos confere o impacto: o menor saldo passa a duzentos reais. Nenhum dinheiro foi movimentado, é um ajuste de orçamento futuro que o gerente aprova explicitamente." |
| 72–90 s | Clicar em **Simular nova despesa** (`monitor`). Mostrar R$ 50 e o novo estado da margem. | "Surge uma despesa de cento e cinquenta reais. A projeção é recalculada: margem cai para cinquenta. O plano anterior não reautoriza uma nova ação, Marcos precisaria revisar e aprovar novamente. Isso evita que uma aprovação antiga cubra um contexto diferente." |
| 90–108 s | Abrir **Por que o Elo sugeriu isso**. Mostrar os números, as hipóteses e os limites. Fechar. | "Marcos pode conferir cada número, cada hipótese e o que não foi considerado. A trilha da sessão mostra todas as consultas e aprovações. Transparência para que o gerente confie na análise antes de apresentar ao cliente." |
| 108–125 s | Selecionar **Decidir sobre uma compra** (`scenario-purchase`). Mostrar comparação à vista, parcelamento e meta. | "Na jornada de compra, o agente compara um celular de três mil e quinhentos reais com o calendário de contas, mostra o impacto da primeira parcela e permite criar uma meta para planejar antes de comprar." |
| 125–140 s | Selecionar **Verificar sinais de risco** (`scenario-pix`). Apontar urgência, destinatário novo e valor atípico. | "Na jornada de PIX, três sinais sintéticos (urgência, destinatário novo e valor atípico) levam o agente a sugerir uma pausa. São regras ilustrativas; o protótipo não confirma fraude nem executa o pagamento." |
| 140–153 s | Clicar em **Desativar leitura e limpar planos**. Mostrar o registro na trilha. | "Marcos encerra a sessão revogando o acesso. Os planos são limpos. O registro da revogação fica na trilha temporária, visível para auditoria, mas descartado com a sessão." |
| 153–172 s | Voltar ao Bob IDE. Mostrar o Prompt 10 sendo digitado: ingestão de documentos em paralelo. | "De volta ao Bob: em modo Agent, ele pode ler múltiplos documentos em paralelo e identificar inconsistências entre eles. Esse é o mesmo modo usado para construir este protótipo, implementação, testes e revisão em uma sessão coordenada." |
| 172–180 s | Mostrar o repositório no GitHub. Encerrar na interface do protótipo. | "O código é público. O próximo passo é validar a chamada real ao IBM watsonx.ai na conta do programa e medir o tempo de preparação com gerentes reais. Clareza antes da decisão, para o gerente chegar ao atendimento com o cenário mapeado." |

## Pontos de precisão

- Dizer **"menor saldo previsto"**, não "dinheiro economizado": os valores são resultados do cenário sintético.
- Dizer **"estimamos quinze a vinte minutos"** com a ressalva **"ainda precisa ser medido"**, nunca apresentar como resultado comprovado.
- Manter o selo do planejador visível e ler o que ele diz. Se estiver em regras locais, dizer "modo por regras"; não fingir que o watsonx está ativo.
- Na cena do Bob, mostrar o Bob operando de verdade (painel real), não uma captura estática.
- Não anunciar hospedagem publicada se ainda não estiver disponível. Dizer "execução local durante esta gravação".
- Atribuir ao Bob apenas o trabalho dos cinco registros em `bob_sessions/`. O selo do planejador e o script de prova do watsonx não foram feitos com o Bob.

## Conferência após gravar

1. Cronometrar: o vídeo deve ter entre 170 e 180 segundos. Ensaiar e ajustar as pausas.
2. Verificar que os três valores principais aparecem legíveis: -R$ 100, R$ 200, R$ 50.
3. Verificar que o selo do planejador aparece legível em pelo menos um momento do vídeo.
4. Verificar que o painel do Bob IDE com as tarefas recentes aparece por pelo menos 5 segundos.
5. Publicar o vídeo, testar o link em janela anônima sem login do autor, e preencher `docs/INSCRICAO.md`.
