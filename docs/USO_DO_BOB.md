# Uso do IBM Bob no projeto Elo Financeiro

Este documento mostra o que o Bob fez no projeto, traz prompts prontos para capturar novas evidências e liga cada evidência ao critério de avaliação correspondente.

---

## O que já foi feito e está registrado

Cinco sessões reais, de dois integrantes, em ordem de data. Todas usaram o IBM Bob 2.3.0 em modo Agent. Cada pasta tem o registro e a captura do painel do Bob; os commits podem ser conferidos com `git show --stat <hash>`.

| Data | Integrante | O que o Bob fez | Commits | Registro |
| --- | --- | --- | --- | --- |
| 2026-10-28 | Guilherme | Leu `tests/test_ibm_cache.py` e `elo/watsonx.py`, avaliou cada import sem uso contra a cobertura existente e corrigiu os 12 apontamentos do Ruff sem mudar comportamento | `a6107cb`, PR #2 | [registro](../bob_sessions/2026-11-08-lint-fix-test-ibm-cache/registro.md) |
| 2026-10-28 | Guilherme | Leu dez arquivos antes de alterar qualquer coisa, implementou a projeção de todas as parcelas de uma compra no calendário, a tabela acessível na interface e 22 testes de domínio | `560b59b`, `67bb80a`, PR #3 | [registro](../bob_sessions/2026-11-08-parcelas-fluxo-caixa/registro.md) |
| 2026-11-05 | Pedro | Implementou a redução personalizada de gastos flexíveis com prévia calculada no servidor e aprovação vinculada à versão dos dados, com 37 testes em três camadas | `6d68d07`, `16038dd` | [registro](../bob_sessions/2026-11-05-ajuste-reducao-gastos-flexiveis/registro.md) |
| 2026-11-05 | Pedro | Encontrou cinco problemas no fluxo de propostas (descarte só visual, prévia sem identidade entre abas, recusa que não cancelava a prévia, entre outros), corrigiu e criou os 30 casos de validação IBM | `7c5e853`, `a121388`, `d76f00d` | [registro](../bob_sessions/2026-11-08-mvp-completion/registro.md) |
| 2026-11-11 | Pedro | Leu o repositório, escreveu o diagnóstico do feedback por critério, comparou duas rotas e produziu os documentos de resposta (11 arquivos, sem código) | ainda não commitado | [registro](../bob_sessions/2026-11-11-resposta-ao-feedback/registro.md) |

O que **não** foi feito com o Bob: a visão do analista (`elo/carteira.py`, `web/analista.html`, `web/analista.js`, `data/carteira.json` e o método `interpret` do watsonx), a lista de contatos da semana, a nova apresentação dentro do app, o selo do planejador na interface, `elo/prova_watsonx.py`, o ajuste do modo real em `tests/test_ibm_validation.py` e a ampliação do vocabulário de `elo/retrieval.py`. Esses itens foram feitos em 2026-11-11 fora do Bob e estão separados no registro daquele dia.

### Onde o modo Agent aparece nessas sessões

- **Ingestão de vários arquivos antes de agir:** na sessão de parcelas, o Bob leu `elo/core.py`, `tests/test_core.py`, `data/scenarios.json`, `web/app.js`, `web/index.html`, `README.md`, três documentos e o workflow de CI antes da primeira alteração. Na sessão de 2026-11-11, o painel registra "Explored 6 folders, 13 files".
- **Tarefas encadeadas com verificação:** na sessão de 2026-11-05 (fluxo de propostas), o Bob mapeou os requisitos, corrigiu o servidor, ajustou a interface, escreveu testes nas três camadas e rodou os cinco comandos de verificação antes de reportar.
- **Plano com várias tarefas acompanhadas:** na sessão de 2026-11-11, o painel mostra a lista de tarefas e "All tasks completed! 8/8".
- **Subagentes:** nenhuma das cinco sessões registra delegação a subagentes. Não afirmamos esse uso. O Prompt 10 abaixo pede trabalho paralelo; se a edição do Bob mostrar subtarefas delegadas na tela, grave e registre; se não mostrar, descreva só o que apareceu.

---

## Prompts para capturar evidências adicionais hoje

Cada prompt abaixo pode ser colado diretamente no Bob em modo Agent. Execute um de cada vez, revise o resultado, execute os testes e registre em `bob_sessions/` seguindo o modelo em `bob_sessions/MODELO.md`.

### Prompt 1: Revisar os cálculos financeiros do core

```
No projeto Elo Financeiro, revise elo/core.py com foco nas funções cashflow(), apply_saving() e preview_saving().
Para cada uma:
1. Confirme que todos os valores permanecem em centavos inteiros durante toda a computação.
2. Identifique qualquer caso de borda não coberto pelos testes existentes em tests/test_core.py.
3. Para os casos de borda identificados, escreva os testes ausentes e adicione-os ao arquivo.
Execute python -m unittest tests.test_core -v e confirme que todos passam.
Apresente um resumo do que encontrou, o que escreveu e o resultado dos testes.
```

**Artefato esperado:** novos testes em `tests/test_core.py`, resultado de testes no terminal.
**Critério atendido:** demonstra uso do modo Agent do Bob para revisão e extensão de testes; comprova capacidade de identificar casos não cobertos autonomamente.

---

### Prompt 2: Revisar o adaptador watsonx antes da chamada real

```
No projeto Elo Financeiro, revise elo/watsonx.py com foco em:
1. O prompt enviado ao modelo: ele delimita o contexto adequadamente para reduzir risco de injeção?
2. O tratamento de erros: todos os caminhos de falha ativam o fallback por regras sem expor informação interna?
3. Os testes em tests/test_watsonx.py e tests/test_ibm_cache.py: há casos de falha que não estão cobertos?
Se identificar lacunas nos testes, escreva os casos faltantes.
Execute python -m unittest tests.test_watsonx tests.test_ibm_cache -v e confirme que todos passam.
Apresente um resumo das conclusões e dos testes adicionados, se houver.
```

**Artefato esperado:** análise do prompt de injeção, possíveis testes novos, resultado limpo dos testes.
**Critério atendido:** demonstra uso do Bob para revisão de segurança de integração IBM; suporte para declaração técnica do watsonx.

---

### Prompt 3: Verificar o contrato entre server.py e core.py

```
No projeto Elo Financeiro, trace o caminho completo de uma requisição POST /api/approve desde elo/server.py
até elo/core.py e de volta para a resposta HTTP. Para cada passo:
1. Identifique o que é validado e onde.
2. Verifique se há algum estado compartilhado entre sessões que possa vazar dados entre usuários.
3. Confirme que nenhum dado sensível aparece na resposta ou nos logs.
Execute python -m unittest tests.test_http -v e apresente um resumo do que encontrou.
```

**Artefato esperado:** análise de isolamento de sessão, confirmação de ausência de vazamento, resultado dos testes HTTP.
**Critério atendido:** demonstra uso do Bob para revisão de arquitetura e segurança; relevante para avaliação de robustez.

---

### Prompt 4: Executar a suite completa e verificar o estado do projeto

```
No projeto Elo Financeiro, execute a verificação completa do estado atual:
1. python -m unittest discover -s tests -v
2. python -m ruff check elo tests
3. python -m compileall -q elo tests
4. node --check web/app.js
5. node --test tests/web_behaviors.cjs
Para cada comando, registre exatamente o que foi executado e o resultado.
Se algum teste falhar, identifique a causa e corrija antes de reportar.
Ao final, apresente: contagem de testes, falhas (se houver) e versão do Python usada.
```

**Artefato esperado:** saída de testes capturável para evidência, identificação de eventuais regressões.
**Critério atendido:** demonstra uso do Bob para integração contínua; saída é evidência direta de qualidade do código.

---

### Prompt 5: Revisar a acessibilidade da interface

```
No projeto Elo Financeiro, revise web/index.html com foco em acessibilidade:
1. Todos os botões e campos de formulário têm rótulos legíveis por leitores de tela (aria-label, label, ou texto visível adequado)?
2. Há elementos interativos sem foco de teclado visível?
3. Os estados de carregamento e erro são anunciados para tecnologias assistivas (aria-live, role=alert ou equivalente)?
4. Identifique até três melhorias concretas que podem ser feitas agora sem alterar a funcionalidade.
Para cada melhoria, mostre o trecho original e o trecho corrigido.
```

**Artefato esperado:** lista de melhorias com código, diff aplicável a `web/index.html`.
**Critério atendido:** demonstra uso do Bob para revisão de acessibilidade; documenta cuidado com inclusão digital.

---

### Prompt 6: Criar o plano de deploy no Render

```
No projeto Elo Financeiro, leia docs/DEPLOY.md e o Dockerfile na raiz.
Com base nesses arquivos, escreva um checklist passo a passo para que um membro da equipe
sem experiência prévia com Render possa publicar a demonstração sintética hoje.
O checklist deve cobrir: verificação local da imagem Docker, criação do serviço no Render,
configuração de ELO_PUBLIC_ORIGIN, teste do health check e conferência das três jornadas
em janela anônima. Para cada passo, indique o que verificar e o que registrar em VERIFICACAO.md.
Não incluir credenciais IBM no ambiente público.
```

**Artefato esperado:** checklist operacional, possivelmente atualização de `docs/DEPLOY.md`.
**Critério atendido:** demonstra uso do Bob para tarefas de operação e documentação técnica.

---

### Prompt 7: Validar a chamada real ao watsonx.ai com o Bob

Antes de abrir o Bob, configure no terminal integrado as variáveis `IBM_CLOUD_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_MODEL_ID` e `WATSONX_URL` da conta do programa. Não cole os valores no chat do Bob.

```
No projeto Elo Financeiro, as credenciais do IBM watsonx.ai já estão configuradas como variáveis de ambiente no terminal. Não leia, não imprima e não grave os valores delas.
1. Execute python -m elo.prova_watsonx e leia o JSON gerado em docs/evidencias/watsonx/.
2. Para cada cenário, diga se a chamada real aconteceu (modo watsonx, model_id devolvido pela API) ou se caiu na contingência, e por quê.
3. Execute python -m unittest tests.test_ibm_validation -v e resuma: casos aprovados, modelo informado pela API, latência média e máxima, e cada falha com a causa provável.
4. Se houver falhas causadas pelo formato da resposta do modelo, proponha a menor mudança no prompt de elo/watsonx.py, sem alterar a política de ferramentas em elo/core.py, e não aplique antes da minha aprovação.
5. Atualize a seção do watsonx.ai em docs/DECLARACAO_TECNICA.md e a tabela de docs/VERIFICACAO.md com os números reais.
```

**Artefato esperado:** JSON em `docs/evidencias/watsonx/`, saída dos 30 casos, declaração técnica atualizada com números reais.
**Critério atendido:** tira o watsonx.ai de "não validado" (área C) e mostra o Bob operando dentro do fluxo de validação IBM (área B).

---

### Prompt 8: Revisar os três cenários sintéticos

```
No projeto Elo Financeiro, leia data/scenarios.json.
Para cada um dos três cenários (scenario-month, scenario-purchase, scenario-pix):
1. Verifique se os valores, datas e eventos são internamente consistentes.
2. Identifique qualquer inconsistência que possa confundir o avaliador durante a demonstração.
3. Sugira um ajuste mínimo para corrigir inconsistências, sem alterar os números que aparecem no roteiro (DEMO.md).
Não altere o arquivo sem minha aprovação; apenas apresente o diagnóstico e as sugestões.
```

**Artefato esperado:** diagnóstico dos cenários, lista de ajustes sugeridos para aprovação humana.
**Critério atendido:** demonstra uso do Bob para revisão de dados de demonstração; reduz risco de erro visível durante a gravação.

---

### Prompt 9: Revisar docs/ARQUITETURA.md para alinhar com a narrativa do gerente de relacionamento

```
No projeto Elo Financeiro, leia docs/ARQUITETURA.md e docs/PROPOSTA.md.
O stakeholder principal agora é o gerente de relacionamento do Banco do Brasil, que usa o agente
durante a preparação do atendimento ao cliente.
Revise docs/ARQUITETURA.md para:
1. Garantir que a descrição dos papéis (Coordenador, Caixa, Planejamento, Segurança, Conhecimento)
   seja compreensível para alguém que não é desenvolvedor.
2. Adicionar um parágrafo curto descrevendo o fluxo do ponto de vista do gerente:
   o que ele vê, o que aprova e o que o sistema faz sem sua intervenção.
3. Não alterar nenhum detalhe técnico; apenas tornar a descrição mais acessível.
Mostre apenas as seções alteradas, não o arquivo completo.
```

**Artefato esperado:** seção nova em `docs/ARQUITETURA.md`, perspectiva do stakeholder documentada.
**Critério atendido:** alinha arquitetura técnica com a narrativa de produto para o avaliador.

---

### Prompt 10: Modo agente: ingestão de documentos em paralelo

Este prompt demonstra o modo Agent do Bob com tarefas paralelas, que é especificamente citado no feedback do avaliador.

```
No projeto Elo Financeiro, execute as seguintes tarefas em paralelo:
Tarefa A: leia todos os arquivos em docs/ e identifique qualquer inconsistência entre eles
(por exemplo, uma métrica declarada em VALIDACAO.md que contradiz algo em PROPOSTA.md,
ou um requisito em ENTREGA.md que ainda não aparece em nenhum outro documento).
Tarefa B: leia todos os arquivos em bob_sessions/ e verifique se os campos obrigatórios
do MODELO.md estão preenchidos em cada registro existente. Liste os campos em branco.
Ao final, apresente os resultados das duas tarefas em seções separadas, com referências
aos arquivos específicos.
```

**Artefato esperado:** relatório de inconsistências entre documentos, campos em branco nos registros.
**Critério atendido:** demonstra explicitamente o modo agente com tarefas paralelas e ingestão de múltiplos documentos: os dois pontos mencionados no feedback B.

---

## O Bob no fluxo principal: a visão do analista

O feedback pediu o Bob ligado ao fluxo principal de um stakeholder específico, com ingestão de documentos, tarefas paralelas e subagentes. A visão do analista ainda não passou por uma sessão do Bob. Os três prompts abaixo foram desenhados para isso: cada um produz um artefato útil para o analista, gera um número que entra nas métricas e mostra um recurso do modo Agent na tela. Rode-os nesta ordem, grave a tela e registre cada um em `bob_sessions/`.

### Prompt 11: Ingestão de documentos para medir o que o analista consegue perguntar

```
No projeto Elo Financeiro, o stakeholder principal é a analista de negócios de uma agência do Banco do Brasil que pergunta em português sobre a carteira de clientes (visão /analista).
Leia, antes de alterar qualquer coisa: data/carteira.json, elo/carteira.py, docs/PROPOSTA.md, docs/VALIDACAO.md e web/analista.html.
1. Escreva 30 perguntas realistas que essa analista faria sobre a carteira, variando o jeito de falar (formal, coloquial, com erro de digitação), segmento, prazo e cliente específico.
2. Para cada pergunta, diga qual consulta estruturada seria a correta (intencao, segmento, dias, limite, cliente) e rode python -c "from elo.carteira import interpretar_por_regras as f; print(f('PERGUNTA'))" para ver o que as regras entendem.
3. Grave tudo em docs/PERGUNTAS_ANALISTA.md, numa tabela com: pergunta, consulta esperada, consulta obtida, acertou (sim/não).
4. Informe a taxa de acerto das regras. Não altere elo/carteira.py ainda; só proponha as mudanças para as perguntas que falharam.
```

**Artefato:** `docs/PERGUNTAS_ANALISTA.md`, um gabarito de 30 perguntas e a taxa de acerto das regras, que vira métrica na proposta.
**O que aparece na tela:** o Bob abrindo os cinco arquivos antes de escrever e executando os comandos de verificação.

### Prompt 12: Tarefas paralelas por segmento da carteira

```
No projeto Elo Financeiro, divida o trabalho abaixo em três tarefas independentes e execute-as em paralelo (se a sua edição permitir delegar subtarefas ou subagentes, use; se não, faça em sequência e diga isso no relatório):
Tarefa A, segmento "renda-variavel"; Tarefa B, segmento "mei"; Tarefa C, segmento "aposentado".
Para cada segmento: leia os clientes desse segmento em data/carteira.json, rode elo.carteira.analisar_cliente em cada um e escreva, em tests/test_carteira.py, um teste que confira um caso de borda real desse segmento (por exemplo, recebimento no último dia do horizonte, gasto flexível depois do pior dia, cliente sem consentimento).
Depois junte os resultados: rode python -m unittest tests.test_carteira -v e apresente um relatório com uma seção por segmento.
```

**Artefato:** novos testes de borda por segmento em `tests/test_carteira.py`.
**O que aparece na tela:** as três tarefas abertas na lista do Bob, ou o próprio Bob dizendo que fez em sequência. Registre o que de fato aconteceu.

### Prompt 13: Concordância entre o IBM watsonx.ai e o gabarito

Rode depois do Prompt 11, com as credenciais IBM já configuradas no terminal (sem colar valores no chat).

```
No projeto Elo Financeiro, use o gabarito de docs/PERGUNTAS_ANALISTA.md.
1. Para cada pergunta, chame elo.watsonx.WatsonxPlanner().interpret(pergunta) e valide com elo.carteira.validar_consulta.
2. Compare com a consulta esperada e com o resultado das regras.
3. Acrescente ao documento duas colunas (watsonx.ai, acertou) e informe: taxa de acerto do modelo, taxa de acerto das regras, quantas respostas do modelo saíram do contrato e o model_id informado pela API em planner.last_call.
4. Rode python -m elo.prova_watsonx e anexe o nome do arquivo de evidência gerado.
Não leia, não imprima e não grave as variáveis de ambiente.
```

**Artefato:** taxa de acerto do watsonx.ai contra a das regras, medida em 30 perguntas, e o JSON de evidência da chamada real.
**Por que importa:** é o número que mostra o ganho da IA para o analista. Hoje, sem esse teste, não dá para afirmar que o modelo interpreta melhor que as regras.

---

## Mapeamento de evidências por critério de avaliação

| Critério do avaliador | Evidência existente | Próxima evidência |
| --- | --- | --- |
| Critério 3: como e onde o Bob foi usado | Cinco registros em `bob_sessions/` com commits e capturas; tabela acima | Prompt 7 ou 10 gravado em vídeo |
| Área A: Bob incorporado ao projeto | Código de parcelas, propostas, validação IBM e lint feito em sessões do Bob | Prompts 11 a 13, sobre a visão do analista |
| Área B: ingestão de documentos | Sessão de parcelas (dez arquivos lidos antes de alterar); sessão de 2026-11-11 (13 arquivos explorados) | Prompt 11 |
| Área B: tarefas paralelas ou encadeadas | Sessão de propostas (cinco etapas com verificação); sessão de 2026-11-11 (8 de 8 tarefas) | Prompt 12 |
| Área B: subagentes | Sem registro | Prompt 12; gravar só se a edição do Bob mostrar delegação |
| Área B: benefício mensurável para a equipe | Ver abaixo | Cronometrar uma tarefa com e sem o Bob |
| Área C: produtos IBM nomeados | `docs/DECLARACAO_TECNICA.md` | Prompt 7 com credenciais reais |

### Benefício do Bob para a equipe: o que dá para afirmar

Contamos o que as sessões produziram, não o tempo economizado. Exemplo: a sessão de redução personalizada entregou 37 testes novos e o endpoint de prévia entre o commit de partida e o commit `6d68d07`; a sessão de propostas produziu três commits em 1 hora e 10 minutos (17:47 a 18:57 BRT). Quanto tempo a equipe levaria sem o Bob não foi medido. [SUPOSIÇÃO A VALIDAR] Para medir, escolha uma tarefa pequena e parecida (por exemplo, um novo caso de teste de borda), faça uma vez sem o Bob e uma vez com o Bob, cronometre as duas e registre em `bob_sessions/`.

---

## Como gravar uma sessão que apareça no vídeo

O feedback pede o Bob operando no fluxo principal. A forma mais direta:

1. Abrir o Bob no repositório e colar o Prompt 11 (ou o Prompt 13, se as credenciais IBM estiverem configuradas).
2. Gravar a tela enquanto o Bob trabalha: a lista de tarefas, os arquivos sendo abertos e o relatório final.
3. No vídeo, usar esse trecho na cena do Bob (153 a 172 segundos em `docs/DEMO.md`).
4. Na narração, dizer os números que apareceram de fato na tela, por exemplo: "O Bob leu [número real] documentos, encontrou [número real] inconsistências e listou os campos em branco." Não usar números de um ensaio anterior.
5. Depois de gravar, criar a pasta da sessão em `bob_sessions/` com registro e captura, como nas outras cinco.
