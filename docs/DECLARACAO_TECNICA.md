# Declaração técnica

Este documento lista cada produto IBM usado no projeto, com a finalidade, o arquivo ou módulo onde aparece e o estado real de validação. Separamos de propósito o que já roda do que ainda depende de execução, para que o avaliador saiba exatamente o que foi comprovado.

## Resumo

| Produto | Finalidade | Onde aparece | Estado em 2026-11-11 |
| --- | --- | --- | --- |
| IBM Bob 2.3.0 (modo Agent) | Ferramenta de desenvolvimento da equipe | `bob_sessions/` (cinco registros), commits citados em cada registro | Uso comprovado: cinco sessões de dois integrantes, com commits e capturas do painel |
| IBM watsonx.ai, API de geração de texto | Escolher quais ferramentas do agente rodam em cada cenário | `elo/watsonx.py`, chamado por `build_report()` em `elo/core.py` | Implementado e testado com respostas simuladas; chamada real na conta do programa ainda não executada |
| IBM Cloud IAM | Obter o token de acesso antes de cada chamada ao watsonx.ai | `elo/watsonx.py`, classe `_TokenCache` | Implementado e testado com respostas simuladas; execução real junto com o watsonx.ai |
| IBM watsonx Orchestrate | Nenhuma | Nenhum arquivo | Não utilizado |

Não há outros serviços IBM neste projeto.

## IBM Bob

**Produto:** IBM Bob 2.3.0, modo Agent, plano enterprise, usado por dois integrantes em duas contas do mesmo programa (`ibm-skillsbuild-ell` e `ELL BR 2026H2`, região us-east).

**Finalidade:** ferramenta de desenvolvimento. O Bob lê o repositório, implementa código, escreve testes e documentação, e explica o que fez. Não é o agente financeiro que aparece na interface; é a ferramenta com que a equipe construiu esse agente.

**Sessões registradas:**

| Data da sessão | Integrante | Tarefa | Commits |
| --- | --- | --- | --- |
| 2026-10-28 | Guilherme | Corrigir 12 apontamentos do Ruff em `tests/test_ibm_cache.py` | `a6107cb`, merge `a62e2d2` (PR #2) |
| 2026-10-28 | Guilherme | Projetar todas as parcelas de uma compra no fluxo de caixa | `560b59b`, `67bb80a`, merge `10f58e3` (PR #3) |
| 2026-11-05 | Pedro | Redução personalizada de gastos flexíveis com prévia no servidor | `6d68d07`, merge `16038dd` |
| 2026-11-05 | Pedro | Descarte e versionamento de prévias, 30 casos de validação IBM | `7c5e853`, `a121388`, `d76f00d` |
| 2026-11-11 | Pedro | Diagnóstico do feedback e documentação de resposta (sem código) | ainda não commitado |

Cada pasta em `bob_sessions/` tem `registro.md` e `resumo-sessao.png`. Os registros foram conferidos com `git log` em 2026-11-11; datas e commits de partida que estavam errados foram corrigidos, e a correção está anotada no próprio registro.

**O que não foi feito com o Bob:** o selo do planejador na interface, o script `elo/prova_watsonx.py`, o ajuste do modo real em `tests/test_ibm_validation.py` e a ampliação do vocabulário em `elo/retrieval.py` foram feitos em 2026-11-11 fora do Bob. Esses itens estão listados no registro de 2026-11-11 e não são apresentados como uso do Bob.

## IBM watsonx.ai

**Produto:** IBM watsonx.ai, API REST de geração de texto (`POST /ml/v1/text/generation?version=2024-05-31`) no endpoint regional da conta, por exemplo `https://us-south.ml.cloud.ibm.com`. O modelo é escolhido pela equipe na variável `WATSONX_MODEL_ID`, entre os modelos Granite liberados no projeto da conta. Não fixamos um ID de modelo no código porque a disponibilidade depende da conta.

**Finalidade:** seleção de ferramentas. O modelo recebe o cenário sintético (eventos, presença de compra ou de PIX) entre marcadores de contexto e devolve apenas `{"tools": [...]}` com nomes da lista permitida: `cashflow`, `purchase`, `safety`, `guidance`. Saldos, parcelas, permissões e aprovações são calculados no código Python. O modelo não calcula valores e não executa nenhuma operação.

**Como entra no fluxo:**

1. O servidor (`elo/server.py`) cria um `WatsonxPlanner` quando `ELO_PLANNER=watsonx` e ele roda só em `127.0.0.1`. O modo público (`ELO_PUBLIC_ORIGIN`) recusa o planejador, para que a conta IBM não seja consumida por visitantes anônimos.
2. A cada relatório, `build_report()` em `elo/core.py` chama `planner.plan(snapshot)`.
3. `elo/watsonx.py` obtém o token IAM (reaproveitado até 60 segundos antes de vencer), envia o prompt e valida a resposta. Planos válidos ficam em cache por cenário; falhas não.
4. Se o plano for válido, o relatório sai com `mode: "watsonx"`. Se a configuração estiver incompleta, a rede falhar, o tempo de 25 segundos acabar ou a resposta sair do contrato, o relatório sai com `mode: "demo_fallback"` e as ferramentas são escolhidas por regras.
5. A interface mostra esse estado no topo da análise, num selo: "Planejador: IBM watsonx.ai escolheu as ferramentas", "Planejador: contingência por regras" ou "Planejador: regras locais".

**Como provar a chamada real:** com as variáveis configuradas só no terminal, `python -m elo.prova_watsonx` roda os três cenários e grava em `docs/evidencias/watsonx/` um JSON com o `model_id`, `model_version` e `created_at` devolvidos pela própria API, a contagem de tokens, a latência e as ferramentas finais. Chave, token e ID do projeto não são gravados. O script só declara "chamada_real_comprovada" quando os três cenários saem em modo `watsonx`. Em seguida, `python -m unittest tests.test_ibm_validation -v` roda os 30 casos inéditos; no modo real, um caso só conta como acerto se quem respondeu foi o modelo, e não a contingência.

**Testes:** `tests/test_watsonx.py`, `tests/test_ibm_cache.py`, `tests/test_prova_watsonx.py` e `tests/test_ibm_validation.py`, todos com respostas simuladas quando não há credenciais.

**Estado:** implementado e testado com respostas simuladas. **A chamada real na conta do programa ainda não foi executada.** Enquanto o arquivo de evidência não existir em `docs/evidencias/watsonx/`, a demonstração deve ser apresentada como "modo por regras".

## IBM Cloud IAM

**Produto:** IBM Cloud IAM, endpoint `https://iam.cloud.ibm.com/identity/token`.

**Finalidade:** trocar a chave de API por um token de acesso antes das chamadas ao watsonx.ai. O token fica só em memória e nunca aparece em logs, respostas HTTP ou arquivos de evidência.

**Onde aparece:** `elo/watsonx.py`, classe `_TokenCache`.

**Estado:** implementado e testado com respostas simuladas; a execução real acontece junto com a do watsonx.ai.

## IBM watsonx Orchestrate

Não utilizado. Não há agente, fluxo, conexão ou implantação Orchestrate neste repositório. A coordenação das ferramentas é feita em Python (`elo/core.py`). Este produto não deve ser declarado na submissão.

## O que não é IBM

Python 3.11 ou superior com a biblioteca padrão, HTML, CSS e JavaScript sem dependências. A recuperação de orientações (`elo/retrieval.py`) é local, por conceitos curados e similaridade de termos; não usa embeddings nem modelo de linguagem.
