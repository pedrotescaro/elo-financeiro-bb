# Changelog

## [Unreleased]

### Novo sistema visual, 11 de novembro de 2026

Feito fora do IBM Bob. Inspirado em capturas de painéis escolhidas pela equipe e nos critérios do guia impeccable.

- Paleta tirada do logo (marinho `#132C5C`, amarelo `#F2C94C`) sobre neutros azulados; superfícies planas com borda de 1px.
- Fonte Mulish servida pelo próprio site; ícones Phosphor (light) em sprite SVG.
- Barra lateral com grupos, barra superior com trilha de navegação, indicadores com régua que mede algo real.
- Removidos: etiquetas numeradas acima de títulos, texto com gradiente, vidro, manchas de fundo, ladrilhos de ícone e entrada animada repetida.
- Micro-interações em Lottie feitas pela equipe (confirmação e "analisando"), com player `lottie_light`.
- Sistema documentado em `DESIGN.md` (formato DESIGN.md, com tokens) e `.impeccable/design.json`; registro do produto em `PRODUCT.md`.
- Números dos indicadores em peso 700 e sombra leve só ao interagir, conforme decisões da equipe no `document` do impeccable.
- `web/style.css` reescrito como folha única com tokens: todo tamanho, cor e canto vem de `:root` e está no `DESIGN.md`. O detector do impeccable passou de 151 notas de deriva para zero, e as páginas renderizadas passam sem antipadrões nem texto abaixo de 12px.
- Contraste ajustado para WCAG AA: texto secundário, legenda e as três cores de estado; sombras neutras em vez de tingidas.

### Visão do analista, lista de contatos e resposta ao feedback, 11 de novembro de 2026

Feito fora do IBM Bob, depois da sessão do Bob de 2026-11-11 (ver `bob_sessions/2026-11-11-resposta-ao-feedback/registro.md`).

- Visão do analista (`/analista`): carteira sintética de 40 clientes, perguntas em português por intenção, segmento, prazo, gerente e cliente; interpretação pelo IBM watsonx.ai (`WatsonxPlanner.interpret`) com contingência por regras; números sempre do código e tempo medido.
- Lista de contatos da semana: inclusão a partir das respostas, status (pendente, contatado, plano aprovado, proposta recusada), exportação em CSV e desfecho atualizado pela aprovação ou recusa no atendimento.
- Cliente da carteira abre direto no atendimento; clientes sem consentimento são recusados.
- Selo do planejador no atendimento; `python -m elo.prova_watsonx` para comprovar a chamada real; modo real dos 30 casos só conta acerto do modelo.
- Apresentação dentro do app atualizada para a narrativa do analista e do gerente.
- 264 testes Python e 43 de interface.

### Correção do contrato de aprovação — 5 de novembro de 2026

- Aprovação sem `preview_id` aplica exclusivamente a proposta padrão; ajustes personalizados exigem a identidade exata da prévia revisada.
- Prévias canceladas ou substituídas são rejeitadas, sem aplicar a proposta padrão como alternativa.
- A idempotência distingue proposta padrão e cada prévia personalizada; identificadores de prévia inválidos são rejeitados.
- Alterações dos dados que mudam o relatório, incluindo a simulação de nova despesa, invalidam a prévia pendente.
- Regressões de domínio e HTTP cobrem valores padrão e personalizados, descarte, recusa, mudança dos dados e repetição de aprovações.

### Ajuste de propostas de redução de gastos flexíveis — Bob

**Data:** 2025
**Branch:** `feature/ajuste-reducao-gastos-flexiveis`
**Contribuição:** Bob

#### O que foi implementado

**`elo/core.py` — nova função `preview_saving()`**
- Calcula uma prévia de redução sem modificar o snapshot original.
- Retorna menor saldo previsto, diferença para a margem, flag `meets_buffer` e aviso explícito quando a margem não é atingida.
- Rejeita valores nulos, negativos, não inteiros e que excedam o total de gastos flexíveis.
- Preserva despesas essenciais (`flexible=False`) na íntegra.
- Todos os cálculos operam em centavos inteiros.

**`elo/server.py` — novo método `preview_adjustment()` e endpoint `/api/preview`**
- `DemoSession.preview_adjustment()`: calcula a prévia no servidor, armazena o ajuste pendente vinculado ao `report_id` vigente.
- `DemoSession.approve()`: quando há ajuste pendente para o relatório correto, aplica a redução personalizada em vez da padrão.
- `DemoSession.set_consent(False)`: descarta `pending_adjustment` ao revogar o consentimento.
- `DemoSession.set_scenario()`: descarta `pending_adjustment` ao trocar de cenário.
- `DemoSession.public_state()`: expõe `pending_adjustment` (sem dados sensíveis) no estado público.
- Endpoint `POST /api/preview`: valida tipos, exige CSRF e consentimento, delega ao `preview_adjustment()`.

**`web/index.html` — painel de redução personalizada**
- Campo `reduction-input` (tipo texto, inputmode decimal) para o usuário informar o valor a reduzir.
- Botões `reduction-preview`, `reduction-approve`, `reduction-discard`.
- Elementos `reduction-error`, `reduction-preview-result`, `reduction-preview-warning` para feedback visual.
- Painel exibido apenas quando há proposta `budget-plan` ativa.

**`web/app.js` — lógica de redução, prévia e aprovação**
- `parseCents()`: converte string de reais para centavos inteiros sem ponto flutuante intermediário.
- Validação imediata no cliente (formato, valor positivo); limite de gastos flexíveis validado exclusivamente no servidor.
- Integração com `/api/preview` e `/api/approve` para o fluxo de redução personalizada.
- Exibição de prévia e aviso de margem não atingida com base no `pending_adjustment` retornado pelo servidor.
- Descarte de prévia pelo botão "Descartar prévia".

**`tests/test_core.py` — 18 novos testes de domínio (`ReductionPreviewTests`)**
Cobrem: prévia de redução, valores inválidos (nulo, negativo, float, string), limite de gastos flexíveis, preservação de despesas essenciais, idempotência de aprovação, revogação de consentimento, troca de cenário, consentimento obrigatório, relatório desatualizado, e aplicação de redução personalizada.

**`tests/test_http.py` — 8 novos testes HTTP**
Cobrem: prévia via endpoint, aprovação com versão correta, rejeição com versão desatualizada, rejeição de tipo inválido, rejeição de valor negativo, rejeição de valor acima do limite, proteção CSRF, consentimento obrigatório, e isolamento da prévia.

**`tests/web_behaviors.cjs` — 11 novos testes de interface**
Cobrem: renderização do campo, painel oculto sem budget-plan, erro com valor inválido, erro com valor vazio, exibição da prévia, aviso de margem não atingida, aviso oculto quando margem atingida, aprovação, recusa, descarte e descarte ao trocar de cenário.

#### Funcionalidades preservadas sem alteração

- Aprovação e recusa explícita de propostas de orçamento
- Metas de compra
- Cálculo de parcelas dentro do horizonte de planejamento
- Proteção CSRF, isolamento de sessões, rejeição de propostas desatualizadas

#### Resultado das verificações

| Comando | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | ✅ 163 testes aprovados — 0 falhas |
| `python -m ruff check elo tests` | ✅ `All checks passed!` — 0 erros |
| `node --check web/app.js` | ✅ Sem erros de sintaxe |
| `node --test tests/web_behaviors.cjs` | ✅ 24/24 testes aprovados — 0 falhas |

---

### `tests/test_ibm_cache.py` — Correções de lint (ruff)

**Data:** 2025  
**Motivação:** Resolver as 12 violações reportadas por `ruff check elo tests` sem alterar o comportamento dos testes.

---

#### Imports removidos

| Símbolo | Regra | Justificativa |
|---|---|---|
| `unittest.mock.call` | F401 | Não referenciado em nenhum ponto do arquivo. As asserções existentes usam `call_count` e `call_args_list` diretamente. |
| `elo.watsonx._InferenceCache` | F401 | Nunca usado diretamente nos testes. O comportamento da classe é coberto por completo através de `WatsonxPlanner` nos testes de `InferenceCacheTests`. |
| `elo.watsonx._TOKEN_RENEW_MARGIN` | F401 | O valor da constante (`60` segundos) já está embutido na lógica dos testes com segundos concretos (`61.0`, `139.0`). Os testes de fronteira de margem cobrem o comportamento sem necessitar do símbolo importado. |

**Antes:**
```python
from unittest.mock import call, patch

from elo.watsonx import (
    _InferenceCache, _TokenCache, _TOKEN_RENEW_MARGIN, _PLAN_BUDGET,
    WatsonxPlanner,
)
```

**Depois:**
```python
from unittest.mock import patch

from elo.watsonx import (
    _TokenCache, _PLAN_BUDGET,
    WatsonxPlanner,
)
```

---

#### Atribuições de `lambda` substituídas por `def` (regra E731)

Todas as 9 ocorrências de `clock = lambda: t[0]` foram substituídas pela forma equivalente com `def`. O comportamento do relógio simulado foi preservado integralmente: `clock` continua sendo uma closure que lê `t[0]`, variável que os testes mutam para avançar o tempo simulado.

**Antes:**
```python
t = [0.0]
clock = lambda: t[0]
```

**Depois:**
```python
t = [0.0]
def clock():
    return t[0]
```

Ocorrências alteradas (métodos afetados):

| Classe | Método |
|---|---|
| `TokenCacheTests` | `test_token_reused_within_validity_window` |
| `TokenCacheTests` | `test_token_renewed_after_expiry_margin` |
| `TokenCacheTests` | `test_token_not_renewed_just_before_margin` |
| `InferenceCacheTests` | `test_cache_hit_skips_network_calls` |
| `InferenceCacheTests` | `test_cache_invalidated_on_snapshot_change` |
| `InferenceCacheTests` | `test_failure_not_cached` |
| `InferenceCacheTests` | `test_cache_invalidated_by_explicit_call` |
| `InferenceCacheTests` | `test_session_isolation` |
| `BudgetTests` | `test_generation_timeout_uses_remaining_budget` |

---

#### Validação

| Comando | Resultado |
|---|---|
| `ruff check elo tests` | ✅ `All checks passed!` — 0 erros |
| `pytest tests/ -v` | ✅ 105 testes aprovados, 85 subtestes aprovados — 0 falhas |

Nenhum arquivo de produção foi alterado.
