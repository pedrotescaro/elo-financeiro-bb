# BOB_STATUS — Checkpoint

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
