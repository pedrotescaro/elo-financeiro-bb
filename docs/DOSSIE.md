# Dossiê de apresentação em slides

Estrutura para uma apresentação de oito a dez minutos. A ordem segue a pedida pela equipe: problema, stakeholder, solução, IBM Bob, IBM watsonx, arquitetura, evidências, métricas, limites e próximos passos. Não usar logotipos oficiais do BB ou da IBM.

---

## Slide 1: Título e equipe

**Título:** Elo Financeiro: a carteira da agência numa conversa, e o contato com o cliente antes do aperto

**Conteúdo:**
- Equipe Fatec Ferraz Heal, Finalização #17
- Trilha 1: Serviços Financeiros Digitais Inteligentes com Banco do Brasil
- IBM SkillsBuild AI Experiential Learning Lab Brasil

---

## Slide 2: O problema

**Título:** O banco descobre que o cliente ficou sem dinheiro depois que ele já ficou

**Conteúdo:**
- Contas vencem antes do salário. O saldo de hoje parece suficiente, mas o calendário leva o cliente ao negativo.
- Para agir antes, alguém na agência precisaria olhar o saldo futuro de cada cliente da carteira.
- Feita à mão, essa triagem leva horas por semana e acaba ficando para depois [SUPOSIÇÃO A VALIDAR].
- Resultado: o contato acontece quando o cliente já está no cheque especial ou pedindo renegociação.

---

## Slide 3: Stakeholder

**Título:** Carla, analista de negócios, e Marcos, gerente de relacionamento

**Conteúdo:**
- **Carla (principal):** analista de negócios da agência. Toda semana define quais clientes de pessoa física os gerentes devem procurar.
- **Marcos (secundário):** gerente de relacionamento. Liga para o cliente e precisa chegar com o cenário pronto.
- Dor da Carla: não existe uma visão de saldo futuro da carteira inteira.
- Dor do Marcos: refazer o calendário de cada cliente antes de ligar.
- As duas personas são hipotéticas e ainda não foram validadas com funcionários do BB.

---

## Slide 4: A solução

**Título:** Perguntar em português, receber a lista, abrir o caso

**Conteúdo:**
- **Visão do analista:** Carla pergunta "quem fica no vermelho nos próximos 7 dias?" ou "quem resolve com ajuste de gastos?" e recebe a lista, a falta somada para a margem e o próximo passo de cada cliente.
- **Lista de contatos da semana:** Carla manda os clientes escolhidos para uma lista com gerente e situação, exportada em CSV. O desfecho do atendimento volta para a lista.
- **Visão do atendimento:** Marcos abre o cliente com um clique e vê calendário diário, pior dia, hipóteses e uma proposta de ajuste com efeito calculado.
- Só entram clientes com consentimento de compartilhamento, no modelo do Open Finance.
- Nada é movimentado e nenhum crédito é oferecido. O cliente aprova cada ajuste; uma despesa nova invalida a aprovação antiga.

**Nota para apresentação:** demonstrar ao vivo, começando pela visão do analista.

---

## Slide 5: Onde entra o IBM Bob

**Título:** O IBM Bob é a ferramenta com que a equipe construiu e testa o agente

**Conteúdo:**
- Cinco sessões reais em modo Agent, de dois integrantes, entre 28/10 e 11/11/2026, todas com registro, captura e commits em `bob_sessions/`.
- O que ele fez: projeção das parcelas de uma compra (22 testes), redução personalizada com prévia no servidor (37 testes), cinco correções no fluxo de propostas e 30 casos de validação IBM, e o diagnóstico do feedback (8 de 8 tarefas).
- Modo Agent em uso: leitura de vários arquivos antes de alterar código, tarefas encadeadas com verificação, plano com tarefas acompanhadas.
- Próximas sessões, sobre a visão do analista: gabarito de 30 perguntas (ingestão de documentos), testes por segmento em paralelo e concordância do watsonx.ai.
- O Bob não aparece na tela do analista: é ferramenta de desenvolvimento, não o agente financeiro.

**Nota para apresentação:** mostrar a tabela de sessões de `docs/USO_DO_BOB.md` e um trecho gravado de uma sessão real. Não atribuir ao Bob a visão do analista, que foi feita fora dele.

---

## Slide 6: Onde entra o IBM watsonx

**Título:** O IBM watsonx.ai entende a pergunta; o código calcula a resposta

**Conteúdo:**
- **Interpretação:** a pergunta do analista vai ao modelo Granite da conta, que devolve só uma consulta estruturada (intenção, segmento, prazo, cliente). A consulta é validada contra uma lista fechada.
- **Seleção de ferramentas:** na tela de atendimento, o modelo escolhe quais ferramentas rodam (`cashflow`, `purchase`, `safety`, `guidance`).
- Autenticação pelo IBM Cloud IAM, com token só em memória.
- Se o modelo falhar ou sair do contrato, as regras assumem e a tela avisa.
- Estado: testado com respostas simuladas. A chamada real é comprovada com `python -m elo.prova_watsonx`, que grava `model_id` e horário devolvidos pela API.
- IBM watsonx Orchestrate e IBM Consulting Advantage: não utilizados nesta versão.

---

## Slide 7: Arquitetura

**Título:** Duas visões, um só cálculo

**Conteúdo:**
- `elo/carteira.py`: carteira sintética, análise em lote e perguntas do analista.
- `elo/core.py`: ferramentas de caixa, compra, segurança e orientação; política de aprovação.
- `elo/watsonx.py`: interpretação de perguntas e seleção de ferramentas pelo IBM watsonx.ai, com contingência.
- `elo/server.py`: sessões, consentimento, limites, lista de contatos e as rotas `/api/carteira`, `/api/analista`, `/api/contatos` e do atendimento.
- `web/`: visão do analista (`analista.html`) e visão do atendimento (`index.html`), sem dependências.
- `data/`: carteira de 40 clientes sintéticos e cenários de demonstração.
- O analista e o gerente veem o mesmo número para o mesmo cliente; um teste confere isso cliente a cliente.

---

## Slide 8: Evidências técnicas

**Título:** O que está comprovado e o que ainda falta

**Conteúdo:**

| Evidência | Estado |
| --- | --- |
| 264 testes Python e 43 de interface, Ruff limpo | Comprovado localmente em 2026-11-11; CI no GitHub Actions |
| Visão do analista ligada ao atendimento, testada no navegador | Comprovado localmente |
| Cinco sessões do Bob com registros, capturas e commits | Comprovado; falta o parágrafo de revisão de cada integrante |
| Chamada real ao watsonx.ai | Pendente; script de prova pronto |
| Sessão do Bob sobre a visão do analista | Pendente; Prompts 11 a 13 prontos |
| Publicação para os avaliadores | Pendente; guia em `docs/DEPLOY.md` |

---

## Slide 9: Métricas

**Título:** O que medimos e o que ainda é estimativa

**Conteúdo:**

| Dimensão | Valor | Fonte |
| --- | --- | --- |
| Clientes em risco na carteira sintética | 15 de 37 (11 negativos, 4 abaixo da margem); 6 resolvíveis por ajuste | Medido |
| Antecedência do aviso | Mediana de 7 dias antes do primeiro negativo | Medido na carteira sintética |
| Tempo de análise da carteira | Cerca de 3 ms para 37 clientes; cerca de 4 ms por pergunta | Medido e exibido na tela |
| Coerência analista x atendimento | 100% dos clientes | Teste automatizado |
| Ações sem aprovação | Zero | Testes automatizados |
| Tempo da triagem manual | 2 a 3 h por semana | [SUPOSIÇÃO A VALIDAR] |
| Acerto do watsonx.ai na interpretação | A medir em 30 perguntas | Prompt 13 de `docs/USO_DO_BOB.md` |

**Nota para apresentação:** separar em voz alta o que é medido do que é estimativa.

---

## Slide 10: Limites

**Título:** O que este protótipo não faz

**Conteúdo:**
- Não usa dados reais: carteira e clientes são sintéticos.
- Não conecta contas, não transfere dinheiro, não oferece crédito e não confirma fraude.
- A projeção usa só eventos conhecidos; recebimentos podem atrasar.
- A chamada real ao watsonx.ai ainda não foi executada na conta do programa.
- As personas e os tempos manuais não foram validados com funcionários do BB.
- Não é produto oficial do Banco do Brasil nem da IBM.

---

## Slide 11: Próximos passos

**Título:** O que falta, em ordem

**Conteúdo:**

| Prioridade | Tarefa |
| --- | --- |
| 1 | Sessões do Bob com os Prompts 11 a 13 e chamada real ao watsonx.ai |
| 2 | Parágrafo de revisão nos cinco registros do Bob |
| 3 | Gravar o vídeo com `docs/DEMO.md` e publicar o protótipo |
| 4 | Cronometrar a triagem com analistas voluntários |
| 5 | Levar a orquestração para o IBM watsonx Orchestrate |

---

## Notas de apresentação

- Começar pela pergunta da analista, não pela tecnologia.
- Ler o selo da tela como ele está (watsonx.ai ou regras).
- Não apresentar [SUPOSIÇÃO A VALIDAR] como resultado.
- Não declarar uso de Orchestrate ou Consulting Advantage.
