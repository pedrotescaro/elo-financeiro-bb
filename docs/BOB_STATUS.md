# BOB_STATUS — Checkpoint

## Sessão — 5 de novembro de 2026: Conclusão do MVP (Bob)

### Resumo

Trabalho realizado nesta sessão do Bob como agente de desenvolvimento:

**Etapa 2 – Fluxo de propostas corrigido:**
- Descarte de prévia agora cancela a pendência no servidor via `POST /api/preview/discard` (persiste após recarregar).
- `preview_id` (sequência monótona) adicionado a cada prévia; aprovação com ID desatualizado é rejeitada com 400.
- `decline()` cancela a prévia pendente vinculada ao mesmo relatório.
- Histórico registra `kind` (default/custom/goal/declined), `applied_cents` e `preview_id`.
- Frontend envia `preview_id` na aprovação personalizada; botão de descarte usa `/api/preview/discard`.
- 19 novos testes Python (182 total) + 5 novos testes JS (29 total).

**Etapa 4 – Validação IBM:**
- `tests/test_ibm_validation.py` com 30 casos sintéticos inéditos.
- Cobre cashflow (10), compra (7), PIX (6) e mistos (7).
- Modo simulado: 30/30 aprovados. Modo real: ativado com credenciais IBM.

**Etapa 5 – Hospedagem:**
- `/healthz` verificado em processo: `{"status":"ok","synthetic":true}`.
- Três jornadas de usuário verificadas em servidor local.
- Docker daemon indisponível; build e deploy externos continuam pendentes.

### Arquivos alterados

- [`elo/server.py`](../elo/server.py) — `discard_preview()`, `preview_id`, `approve(preview_id=)`, `decline()` cancela prévia, `kind`/`applied_cents` no histórico, endpoint `/api/preview/discard`
- [`web/app.js`](../web/app.js) — descarte chama servidor, aprovação envia `preview_id`, histórico com kind/valor
- [`tests/test_core.py`](../tests/test_core.py) — 19 novos testes de versionamento, descarte, recusa, histórico
- [`tests/test_http.py`](../tests/test_http.py) — 8 novos testes HTTP para discard, two-tab, histórico kind
- [`tests/web_behaviors.cjs`](../tests/web_behaviors.cjs) — 5 novos testes JS (preview_id, descarte, histórico)
- [`tests/test_ibm_validation.py`](../tests/test_ibm_validation.py) — **novo** — 30 casos de validação IBM
- [`docs/VALIDACAO.md`](../docs/VALIDACAO.md) — RF11 marcado como implementado/testado
- [`docs/VERIFICACAO.md`](../docs/VERIFICACAO.md) — resultados atualizados (212 testes, 3 jornadas verificadas)

### Testes executados

| Comando | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | ✅ 212 testes — 0 falhas |
| `python -m ruff check elo tests` | ✅ `All checks passed!` |
| `python -m compileall -q elo tests` | ✅ Sem erros |
| `node --check web/app.js` | ✅ Sem erros |
| `node --test tests/web_behaviors.cjs` | ✅ 29/29 aprovados |

---

## Alteração — Etapa 3: Ajuste de propostas de redução de gastos flexíveis (Bob)

### Campo "Quanto consigo reduzir" na proposta de orçamento

Campo de entrada `reduction-input` adicionado ao painel de ações em [`web/index.html`](../web/index.html). Aceita valores em reais (ex.: `150,00`). `parseCents()` em [`web/app.js`](../web/app.js) converte string para centavos inteiros sem ponto flutuante intermediário. Validação de formato e positividade ocorre no cliente; validação de limite ocorre exclusivamente no servidor.

### Prévia de redução calculada no servidor

`preview_saving()` em [`elo/core.py`](../elo/core.py) calcula o menor saldo previsto após a redução, a diferença para a margem e emite aviso quando a margem desejada não é atingida. A prévia é sempre calculada no servidor via `POST /api/preview`. O orçamento nunca é modificado pela prévia; apenas a aprovação explícita aplica a redução.

### Ajuste pendente vinculado ao relatório

`DemoSession.preview_adjustment()` em [`elo/server.py`](../elo/server.py) armazena o ajuste pendente vinculado ao `report_id` vigente. `DemoSession.approve()` usa a redução personalizada quando há ajuste pendente para o relatório correto. Aprovações repetidas da mesma proposta são idempotentes.

### Descarte de estados pendentes

`set_consent(False)` e `set_scenario()` descartam `pending_adjustment`. O cliente descarta a prévia visualmente ao clicar "Descartar prévia".

### Arquivos modificados

- [`elo/core.py`](../elo/core.py) — nova função `preview_saving()`
- [`elo/server.py`](../elo/server.py) — `preview_adjustment()`, endpoint `/api/preview`, descarte nos hooks de revogação e troca de cenário
- [`web/index.html`](../web/index.html) — painel de redução com campo, botões e elementos de feedback
- [`web/app.js`](../web/app.js) — `parseCents()`, integração com `/api/preview`, exibição de prévia e aviso
- [`tests/test_core.py`](../tests/test_core.py) — 18 novos testes de domínio (`ReductionPreviewTests`)
- [`tests/test_http.py`](../tests/test_http.py) — 8 novos testes HTTP
- [`tests/web_behaviors.cjs`](../tests/web_behaviors.cjs) — 11 novos testes de interface

### Testes executados

| Comando | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | ✅ 163 testes — 0 falhas |
| `python -m ruff check elo tests` | ✅ `All checks passed!` |
| `node --check web/app.js` | ✅ Sem erros |
| `node --test tests/web_behaviors.cjs` | ✅ 24/24 aprovados |

---

## Alteração — Etapa 2: Redução de chamadas IBM

### IAM token reuse (`elo/watsonx.py`)
`_TokenCache` em memória com expiração (`expires_in` do IAM) e margem de 60 s. Lock garante
renovação única quando threads concorrentes encontram token expirado. Token nunca exposto em logs.

### Cache de inferência por sessão
`_InferenceCache` por instância de `WatsonxPlanner`. Plano reutilizado quando digest do snapshot
e da configuração coincidem. Falhas não são cacheadas. `invalidate_cache()` chamado automaticamente
em `set_consent(False)` e `set_scenario()`.

### Orçamento de 25 s compartilhado
Tempo de autenticação descontado do orçamento antes da chamada de geração.
`TimeoutError` levantado se restante ≤ 0.

## Arquivos modificados
- `elo/watsonx.py` — `_TokenCache`, `_InferenceCache`, `WatsonxPlanner` (clock injetável)
- `elo/server.py` — `invalidate_cache()` em `set_consent` e `set_scenario`
- `tests/test_ibm_cache.py` — 14 novos testes (reuso, expiração, invalidação, concorrência, isolamento, falha, orçamento)
- `tests/test_watsonx.py` — isolamento de cache entre subtestes

## Testes executados
- `python -m unittest discover -s tests` → **105 tests, OK**
- `node --test tests/web_behaviors.cjs` → **11/11 pass**
- `node --check web/app.js` → sem erros
- Ruff: não instalado no ambiente

## Limitações
- `_GLOBAL_TOKEN_CACHE` é compartilhado entre instâncias do mesmo processo (intencionalmente).
- Cache de inferência limitado a 1 entrada por sessão; múltiplos cenários simultâneos não têm benefício.

## Próximas etapas
1. Cenários fictícios editáveis pelo usuário
2. Planos ajustáveis e fluxo de recusa
3. Parcelas completas no comparativo de compra
4. Contribuição contextual da IA nas metas
5. Verificação de entrega (smoke test end-to-end)
