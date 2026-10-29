# Projeção de compras parceladas

Implementado em `feat/installment-cashflow`.

## O que mudou

### `elo/core.py`

Duas funções auxiliares privadas foram adicionadas antes de `purchase()`:

**`_installment_dates(start, n)`**
Retorna `n` datas mensais a partir de `start`. O dia de referência é preservado sempre que possível. Quando o dia não existe no mês de destino (ex.: dia 31 em fevereiro), usa-se o último dia do mês via `calendar.monthrange`.

**`_split_installments(price, n)`**
Divide `price` em `n` parcelas inteiras. A base é `price // n`; os `price % n` centavos restantes são distribuídos, um a um, pelas primeiras parcelas, de modo que a soma seja sempre exatamente igual ao preço total.

**`purchase()` — campos novos no retorno**

| Campo | Descrição |
| --- | --- |
| `schedule` | Lista das parcelas dentro do horizonte: `number`, `date` (ISO-8601) e `amount_cents` |
| `out_of_horizon` | Quantidade de parcelas com data posterior ao `horizon`; não entram no cálculo do menor saldo |
| `installment_projected_minimum_cents` | Menor saldo projetado com todas as parcelas de `schedule` aplicadas ao cenário |
| `installment_projected_closing_cents` | Saldo de encerramento projetado com as mesmas parcelas |

Os campos `cash_minimum_cents`, `cash_closing_cents`, `first_installment_cents` e `installment_minimum_cents` foram mantidos sem alteração para preservar a compatibilidade com o comportamento anterior.

O cenário original nunca é modificado: a projeção usa um `deepcopy` interno com os eventos de parcela simulados.

**`_explanations()`**
A seção `purchase` do dicionário de explicações passa a informar:
- O menor saldo com as parcelas do horizonte (quando `schedule` tem mais de uma entrada).
- A quantidade de parcelas fora do horizonte em `not_considered`, quando `out_of_horizon > 0`.

### `web/app.js`

O bloco de renderização da compra (`purchase?.available`) foi reescrito:

- O card central exibe o menor saldo projetado com todas as parcelas do horizonte, em vez de apenas a primeira.
- Uma tabela acessível (`role="region"`, `aria-label`, `scope="col"`) lista cada parcela projetada com número, data e valor.
- Um parágrafo de aviso (`class="footnote"`) aparece quando `out_of_horizon > 0`, informando quantas parcelas ficaram fora do período analisado.

## Regras de calendário

1. A primeira parcela cai em `as_of` (data de referência do cenário).
2. Cada parcela seguinte avança exatamente um mês, preservando o dia.
3. Se o dia não existir no mês destino, usa-se o último dia daquele mês.
4. Anos bissextos são tratados corretamente pelo módulo `calendar` da biblioteca padrão.

Exemplos:

| `as_of` | Parcela 2 | Parcela 3 |
| --- | --- | --- |
| 2026-01-15 | 2026-02-15 | 2026-03-15 |
| 2026-01-31 | 2026-02-28 | 2026-03-31 |
| 2024-01-31 | 2024-02-29 (bissexto) | 2024-03-31 |
| 2026-10-31 | 2026-11-30 | 2026-12-31 |

## Limites do horizonte

Apenas as parcelas com data em `[as_of, horizon]` (inclusive) entram no cálculo do `cashflow()` projetado. As demais são contadas em `out_of_horizon` e exibidas como aviso na interface. Isso garante que o menor saldo informado reflita somente o período que o cenário cobre, sem inventar receitas ou despesas futuras.

O cenário padrão `"purchase"` tem horizonte de 8 dias (`2026-10-07` a `2026-10-15`) e 10 parcelas mensais, portanto apenas a primeira parcela cabe no horizonte e `out_of_horizon = 9`. Para ver mais parcelas projetadas, o horizonte do cenário precisaria ser estendido.

## Testes adicionados

### `tests/test_core.py` — classe `InstallmentTests` (22 casos)

| Grupo | Casos |
| --- | --- |
| Datas mensais | Preservação do dia; travamento ao fim do mês; anos bissextos; virada de ano |
| Divisão de parcelas | Divisão exata; centavos restantes nas primeiras; soma igual ao preço em vários casos |
| Parcela única | Campos corretos; projeção igual ao comportamento anterior |
| Múltiplas parcelas | Datas e soma corretas dentro do horizonte; centavos restantes distribuídos |
| Menor saldo projetado | Recálculo com todas as parcelas do horizonte; saldo de encerramento |
| Parcelas fora do horizonte | Contagem correta; não incluídas na projeção; texto no campo `assumption` |
| Cenário original | Preservado após a chamada (dois testes) |
| Compra à vista | Campos anteriores mantidos sem alteração |
| Fim de mês no cronograma | Data travada para 30/11 quando referência é dia 31 |
| Validações | Preço inválido rejeitado; número de parcelas inválido rejeitado; preço zero aceito |

### `tests/web_behaviors.cjs` (2 casos)

| Caso | O que verifica |
| --- | --- |
| `purchase section renders installment schedule table and out-of-horizon warning` | Tabela com `role=region` presente; 4 linhas (1 cabeçalho + 3 dados); ausência de aviso quando `out_of_horizon === 0` |
| `purchase section shows out-of-horizon warning when installments exceed horizon` | Parágrafo de aviso presente; texto contém a contagem correta de parcelas fora do horizonte |

### `tests/test_explanations.py` (1 caso atualizado)

`test_purchase_explanation_discloses_omitted_installments`: a asserção foi atualizada de `"Parcelas futuras depois da primeira"` para `"fora do horizonte"`, refletindo o novo texto gerado quando `out_of_horizon > 0`.

## Resultados das verificações

Executados localmente após a implementação:

```
python -m ruff check elo tests         → All checks passed
python -m compileall -q elo tests      → (sem erros)
python -m unittest discover -s tests -v → Ran 127 tests — OK
node --check web/app.js                → (sem erros de sintaxe)
node --test tests/web_behaviors.cjs    → 13 passed, 0 failed
```

## Limitações que permanecem

- O protótipo não simula juros, IOF nem outras tarifas de parcelamento.
- O horizonte do cenário padrão é curto (8 dias); com 10 parcelas, 9 ficam fora da projeção. Isso é esperado e informado ao usuário.
