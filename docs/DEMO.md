# Roteiro de apresentação — até três minutos

Objetivo: mostrar um problema reconhecível, uma decisão com consequência calculada e o controle da pessoa sobre cada ação. O roteiro reserva aproximadamente 125 segundos para o programa funcionando, entre 20 e 145 segundos. Ensaiar e ajustar as pausas para manter o vídeo em até 180 segundos; a gravação e sua publicação continuam pendentes.

## Preparação

1. Executar `python -m elo.server` na raiz do projeto e abrir `http://127.0.0.1:8000`.
2. Selecionar **Chegar ao próximo recebimento** (`scenario-month`). Se a leitura estiver ativa, clicar em **Reiniciar cenário** (`demo-reset`) para restaurar os valores e depois em **Desativar leitura e limpar planos** (`consent-toggle`). O reinício dos dados preserva o consentimento; a revogação é uma escolha separada.
3. Fechar os detalhes que não serão usados, conferir fonte e enquadramento, ocultar notificações e manter somente dados sintéticos na tela. As datas de outubro pertencem ao cenário fictício.
4. Abrir **Apresentar a ideia** para os quadros iniciais de problema e proposta. Ao chegar ao quadro de demonstração, voltar à interface interativa para realizar os cliques reais. Usar o quadro de tecnologias no encerramento.
5. Deixar o checkpoint `docs/BOB_STATUS.md` e o repositório preparados em abas separadas. Mostrar capturas ou relatórios do Bob somente quando forem arquivos originais da sessão; o checkpoint é um registro da equipe, não uma captura do Bob.

O roteiro usa a aprovação padrão de R$ 300 para preservar a sequência **menos R$ 100 → R$ 200 → R$ 50**. A redução personalizada pode ser demonstrada em um ensaio separado, abrindo **Ajustar o valor da redução** (`reduction-options`), sem alongar o vídeo principal.

## Cenas e narração

| Tempo | Tela e ação | Narração sugerida |
| --- | --- | --- |
| 0–10 s | Em **Apresentar a ideia**, mostrar o quadro do problema. | “Mil e quinhentos reais na conta. Parece suficiente. Mas e se as contas vencerem antes de receber? O saldo de hoje não conta toda a história.” |
| 10–20 s | Avançar para o quadro da proposta e depois para a demonstração real. | “O Elo Financeiro propõe antecipar esse aperto, explicar as alternativas e acompanhar a escolha. Vamos ver isso funcionando com um cenário fictício.” |
| 20–30 s | Na interface, clicar em **Autorizar dados da demonstração** (`start`). | “A análise começa com a minha autorização. Estes dados são sintéticos: nenhuma conta bancária está conectada.” |
| 30–48 s | Mostrar **Menor saldo previsto** (`minimum`) e o gráfico. Abrir **Ver os valores de cada dia** se necessário para apontar 13/10; fechar em seguida. | “Começamos com mil e quinhentos reais, mas o calendário leva o saldo a menos cem antes de receber. O saldo final positivo esconde esse intervalo. Aqui, o menor saldo é o que merece atenção.” |
| 48–67 s | Mostrar o efeito da proposta e clicar em **Ativar plano de gastos** (`approve-budget-plan`). Apontar o novo valor de R$ 200. | “A proposta reduz trezentos reais de lazer previsto, preservando as despesas essenciais. Eu confiro o impacto e aprovo. O menor saldo passa a duzentos reais. É um ajuste de orçamento futuro; nenhum dinheiro foi movimentado.” |
| 67–85 s | Clicar em **Simular nova despesa** (`monitor`). Mostrar R$ 50, o novo estado da margem e o botão desativado. | “Agora surge uma despesa de cento e cinquenta reais. A projeção é recalculada e a margem cai para cinquenta. A escolha anterior não autoriza uma nova ação: o Elo precisa considerar o novo contexto.” |
| 85–103 s | Abrir **Por que o Elo sugeriu isso** e uma explicação; mostrar brevemente **Ferramentas e orientações consultadas**. | “Eu posso conferir os valores, as hipóteses e os limites. As ferramentas fazem os cálculos; as orientações vêm de uma pequena base local. A trilha mostra consultas e autorizações realizadas nesta sessão.” |
| 103–120 s | Selecionar **Decidir sobre uma compra** (`scenario-purchase`). Mostrar comparação à vista, parcelamento e meta, sem aprovar outra ação. | “Na compra, o Elo compara um celular de três mil e quinhentos reais com as contas do período. Ele mostra o que cabe no horizonte e permite registrar uma meta para planejar antes de comprar.” |
| 120–135 s | Selecionar **Verificar sinais de risco** (`scenario-pix`). Apontar urgência, destinatário novo e valor atípico. | “No PIX, sinais fictícios de urgência, destinatário novo e valor atípico sugerem uma pausa para conferir. São regras ilustrativas: o protótipo não confirma fraude nem realiza ou bloqueia o pagamento.” |
| 135–145 s | Clicar em **Desativar leitura e limpar planos**. Abrir **O que aconteceu nesta sessão** para mostrar a revogação. | “A pessoa continua no controle. Ao revogar, a análise fica oculta e os planos são limpos. O registro dessa escolha permanece somente nesta sessão temporária.” |
| 145–168 s | Retomar **Apresentar a ideia**, no quadro de tecnologias; se necessário, apontar o checkpoint de desenvolvimento. | “O checkpoint da equipe registra apoio do IBM Bob no desenvolvimento e nos testes; os anexos originais de sessão ainda precisam ser reunidos. Esta demonstração usa regras em Python. Há um adaptador opcional para watsonx.ai selecionar ferramentas, ainda sem chamada real comprovada. A versão atual não utiliza watsonx Orchestrate.” |
| 168–180 s | Mostrar o repositório público e encerrar no quadro da proposta ou na interface. | “Clareza antes da decisão: antecipar, explicar e acompanhar, com autorização. O código é público. Os próximos passos são validar com usuários e concluir as evidências IBM.” |

## Como apresentar com precisão

- Dizer **“menor saldo previsto”**, não “dinheiro economizado”: os valores são resultados do cenário sintético.
- Na compra, explicar que somente parcelas com vencimento dentro do horizonte entram na projeção. O cenário padrão considera a primeira parcela; as demais não desaparecem da obrigação futura.
- Manter o modo por regras e a indicação de dados sintéticos identificáveis. A apresentação não deve sugerir que uma chamada IBM está ocorrendo quando o programa usa a contingência local.
- Atribuir ao Bob apenas o trabalho registrado e revisado pela equipe. A interface desta apresentação e um checkpoint em Markdown não substituem capturas e relatórios originais do Bob.
- Não anunciar integração Orchestrate, conexão oficial com Banco do Brasil, hospedagem publicada, eficácia contra fraude ou resultados com usuários sem evidência correspondente.

Depois de gravar, conferir duração, legibilidade dos três valores principais e áudio. Publicar o vídeo, testar a permissão de acesso sem login do autor e preencher [INSCRICAO.md](INSCRICAO.md). O endereço local do programa não serve como URL pública de entrega.
