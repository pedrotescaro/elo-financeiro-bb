# Dossiê de apresentação: estrutura de slides

Estrutura para uma apresentação de oito a dez minutos ao avaliador ou à banca. Cada seção abaixo é um slide ou um bloco de slides. A ordem segue a sequência: problema → stakeholder → solução → Bob → watsonx → arquitetura → evidências → métricas → limites → próximos passos.

---

## Slide 1: Título e equipe

**Título:** Elo Financeiro: análise de fluxo de caixa assistida por agente para o atendimento do Banco do Brasil

**Conteúdo:**
- Nome da equipe: Fatec Ferraz Heal
- Trilha 1: Serviços Financeiros Digitais Inteligentes com Banco do Brasil
- IBM SkillsBuild AI Experiential Learning Lab Brasil, Finalização 17

---

## Slide 2: O problema

**Título:** Preparar um atendimento financeiro consome mais tempo do que o próprio atendimento

**Conteúdo:**
- O gerente de relacionamento do BB atende clientes com problemas de fluxo de caixa: saldo zerou antes do recebimento, parcelamento comprometeu a margem, PIX suspeito.
- Para preparar esse atendimento, o gerente reconstrói o cenário financeiro manualmente: consulta saldo e histórico, monta o calendário de contas, identifica gastos flexíveis, calcula qual ajuste é viável.
- Estimativa de tempo para essa preparação: 15 a 20 minutos por atendimento de perfil complexo. [SUPOSIÇÃO A VALIDAR]
- Quando a projeção não está pronta, a conversa começa pelo diagnóstico e não pela solução.

**Nota para apresentação:** destacar que a estimativa de tempo é uma suposição que precisa de validação. Não apresentar como resultado medido.

---

## Slide 3: Stakeholder

**Título:** Marcos, gerente de relacionamento

**Conteúdo:**
- Dez anos de banco, agência de médio porte.
- Atende de oito a doze clientes por dia; dois a três apresentam situações de caixa que exigem análise antes de propor qualquer produto. [SUPOSIÇÃO A VALIDAR]
- Ferramentas disponíveis hoje: sistema do banco para consulta de saldo e histórico. Sem ferramenta para projetar calendário de saídas e entradas.
- O que Marcos precisa: chegar ao atendimento com o cenário mapeado, as alternativas calculadas e os limites declarados.
- Esta persona é hipotética. Não foi validada em entrevistas com gerentes do BB.

---

## Slide 4: A solução

**Título:** O gerente abre a análise já calculada em dois a três minutos

**Conteúdo:**
- Marcos autoriza a leitura do cenário sintético do cliente. O agente apresenta:
  1. Calendário de saldo diário com o menor saldo destacado.
  2. Data do risco e os eventos que contribuem para o problema.
  3. Proposta de ajuste com efeito calculado e hipóteses visíveis.
  4. Trilha de consultas, aprovações e revogações da sessão.
- Marcos confere, aprova ou ajusta. Nenhum dinheiro é movimentado sem aprovação.
- Uma nova despesa atualiza a projeção; o plano anterior não reautoriza uma nova ação.

**Nota para apresentação:** mostrar a tela do protótipo ao vivo ou em captura durante este slide.

---

## Slide 5: Onde entra o IBM Bob

**Título:** O IBM Bob é a ferramenta com que a equipe construiu e testou o agente

**Conteúdo:**
- Cinco sessões reais em modo Agent, de dois integrantes, entre 2026-10-28 e 2026-11-11.
- Projeção de todas as parcelas de uma compra no calendário, com 22 testes (Guilherme, PR #3).
- Redução personalizada de gastos com prévia no servidor e 37 testes em três camadas (Pedro).
- Cinco problemas corrigidos no fluxo de propostas e 30 casos de validação IBM (Pedro).
- Diagnóstico do feedback e documentos de resposta, com 8 de 8 tarefas concluídas (Pedro).
- Cada sessão tem registro, captura do painel e commits que o avaliador pode abrir.
- O Bob não aparece na tela do gerente: ele é a ferramenta de desenvolvimento, não o agente financeiro.

**Nota para apresentação:** mostrar a tabela de sessões de `docs/USO_DO_BOB.md` e uma captura do painel. Não atribuir ao Bob o selo do planejador nem o script de prova do watsonx, que foram feitos fora dele.

---

## Slide 6: Onde entra o IBM watsonx.ai

**Título:** O IBM watsonx.ai escolhe as ferramentas; o código calcula

**Conteúdo:**
- `elo/watsonx.py` autentica no IBM Cloud IAM e envia o cenário sintético a um modelo Granite da conta.
- O modelo devolve só a lista de ferramentas: `cashflow`, `purchase`, `safety`, `guidance`.
- Saldos, parcelas, permissões e aprovações ficam no código Python. O modelo não calcula nem executa operações.
- O selo no topo da análise diz quem planejou: watsonx.ai, contingência por regras ou regras locais.
- `python -m elo.prova_watsonx` grava a evidência da chamada real com o modelo informado pela própria API.
- Estado: testado com respostas simuladas; chamada real na conta do programa ainda não executada.
- IBM watsonx Orchestrate: não utilizado.

**Nota para apresentação:** se a chamada real já tiver sido feita, mostrar o JSON em `docs/evidencias/watsonx/`. Se não, dizer "modo por regras" e mostrar o selo correspondente.

---

## Slide 7: Arquitetura

**Título:** Ferramentas separadas, política no código, modelo como seletor

**Conteúdo:**
- `elo/core.py`: coordenador, ferramentas financeiras (cashflow, purchase, safety, guidance), política de aprovação.
- `elo/watsonx.py`: adaptador REST para IBM watsonx.ai; contingência por regras se falhar.
- `elo/prova_watsonx.py`: gera a evidência da chamada real, sem chave nem token.
- `elo/retrieval.py`: recuperação local de orientações por conceitos curados e TF-IDF.
- `elo/server.py`: servidor HTTP com sessões em memória, expiração e limites de recursos.
- `web/`: interface em HTML, CSS e JavaScript sem dependências externas.
- `data/`: cenários sintéticos e base de orientações curadas.
- `tests/`: 233 testes automatizados em Python e 36 de interface em JavaScript.

**Diagrama:** ver `docs/ARQUITETURA.md` para o diagrama Mermaid completo.

---

## Slide 8: Evidências técnicas

**Título:** O que está comprovado e o que ainda precisa de execução

**Conteúdo:**

| Evidência | Estado |
| --- | --- |
| 233 testes Python e 36 de interface passando, Ruff limpo | Comprovado localmente em 2026-11-11; CI no GitHub Actions |
| Três jornadas verificadas em servidor local | Comprovado |
| Cinco sessões do Bob com registros, capturas e commits | Comprovado; falta o parágrafo de revisão de cada integrante |
| 30 casos de validação IBM com respostas simuladas | Comprovado |
| Chamada real ao watsonx.ai e 30 casos com o modelo | Pendente; script de prova pronto |
| Publicação para os avaliadores | Pendente; guia em `docs/DEPLOY.md` |

---

## Slide 9: Métricas

**Título:** O que medimos, o que estimamos e o que ainda precisa ser verificado

**Conteúdo:**

| Dimensão | Resultado ou estimativa | Fonte ou método |
| --- | --- | --- |
| Aprovação exigida antes de qualquer ação | 100%, zero ações sem consentimento | Testes automatizados (RF01, RF05) |
| Ferramentas selecionadas corretamente (respostas simuladas) | 30/30 casos; mede o contrato, não o modelo | `test_ibm_validation.py` |
| Tempo de preparação atual (gerente) | 15 a 20 min | [SUPOSIÇÃO A VALIDAR] |
| Tempo com o agente | 2 a 3 min | [SUPOSIÇÃO A VALIDAR] |
| Compreensão da análise pelo gerente | Não medido | Pesquisa exploratória descrita em VALIDACAO.md |

**Nota para apresentação:** ser explícito sobre quais são suposições. O avaliador valorizará a honestidade mais do que números não comprovados.

---

## Slide 10: Limites

**Título:** O que este protótipo não faz

**Conteúdo:**
- Não conecta contas bancárias, não realiza transferências, não contrata crédito.
- Não confirma fraude: os sinais de PIX são ilustrativos e baseados em regras.
- A chamada IBM real ainda não foi executada na conta do programa (até lá, a demonstração roda por regras).
- O deploy público ainda não foi realizado.
- A persona do gerente não foi validada em entrevistas reais.
- As métricas de tempo são estimativas, não resultados medidos.
- Não é um produto oficial do Banco do Brasil nem uma entrega IBM finalizada.

---

## Slide 11: Próximos passos

**Título:** O que a equipe precisa fazer antes da submissão final

**Conteúdo:**

| Prioridade | Tarefa |
| --- | --- |
| Hoje | Escrever o parágrafo de revisão nos cinco registros do Bob |
| Hoje | Rodar `python -m elo.prova_watsonx` e `test_ibm_validation.py` com credenciais reais, de preferência dentro de uma sessão do Bob (Prompt 7) |
| Hoje/amanhã | Gravar o vídeo seguindo o roteiro em DEMO.md |
| Amanhã | Publicar no Render e registrar URL em VERIFICACAO.md |
| Amanhã | Preencher e enviar o formulário de submissão |

**Documentos de referência:** `docs/ENTREGA.md` para a lista completa de pendências.

---

## Notas de apresentação

- Manter o tom honesto sobre o que está pronto e o que não está. O avaliador lê os documentos.
- Não usar logotipos oficiais do BB ou da IBM.
- Não declarar uso de IBM watsonx Orchestrate.
- Não apresentar métricas com [SUPOSIÇÃO A VALIDAR] como resultados obtidos.
- Se mostrar o protótipo ao vivo, identificar o modo (regras ou watsonx) antes de começar a navegar.
