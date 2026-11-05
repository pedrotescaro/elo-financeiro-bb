# Verificação técnica — 5 de novembro de 2026

Ambiente local: Windows, Python 3.14.3, Node 24.14.0 e Ruff 0.16.0. Os testes usam apenas dados sintéticos. A demonstração continua iniciando com `python -m elo.server`, sem instalar pacotes.

## Resultados reproduzidos

| Verificação | Resultado local |
| --- | --- |
| `python -m unittest discover -s tests -v` | 212 testes passaram |
| `python -m ruff check elo tests` | Passou |
| `python -m compileall -q elo tests` | Passou |
| `node --check web/app.js` | Passou |
| `node --test tests/web_behaviors.cjs` | 29 testes passaram, sem pacotes Node |
| Endpoint `/healthz` em processo | `{"status":"ok","synthetic":true}` |
| Jornada 1 (caixa): menor saldo −R$100 → aprovação → R$200 → nova despesa → R$50 | Verificada |
| Jornada 2 (compra): recomendação, meta criada | Verificada |
| Jornada 3 (PIX): `signal_level="atenção reforçada"`, 3 razões, `payment_executed=false` | Verificada |

O workflow executa essas verificações em Python 3.11 e 3.14. O resultado remoto deve ser conferido na execução da revisão em [GitHub Actions](https://github.com/pedrotescaro/elo-financeiro-bb/actions/workflows/checks.yml); a tabela acima registra o ambiente local, sem presumir sucesso de CI.

## Fluxo de propostas (Etapa 2)

Cenários verificados em servidor real local:

| Cenário | Resultado |
| --- | --- |
| Prévia → descartar → recarregar → aprovar padrão | `pending_adjustment: null` persiste após reload; histórico registra `kind: default` |
| Prévia → recusar | `pending_adjustment: null` após recusa; trilha registra `preview_cancelled_by_decline` |
| Duas abas (preview_id desatualizado) | Aprovação com pid antigo retorna HTTP 400 |
| Aprovação personalizada com preview_id correto | `kind: custom`, `applied_cents` registrado |
| Descarte de prévia via `/api/preview/discard` | Persiste no servidor após GET `/api/state` |

## Validação IBM (Etapa 4)

30 casos sintéticos em `tests/test_ibm_validation.py`, totalmente distintos dos cenários do catálogo. Modo simulado: 30/30 aprovados. Modo real: requer `IBM_CLOUD_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_MODEL_ID` e `WATSONX_URL` configurados; sem credenciais, os testes são executados com mock local e o modo é registrado na saída.

## Docker e hospedagem

O Docker CLI existe mas o daemon não estava disponível no ambiente de desenvolvimento; a imagem não foi construída nem executada nesta sessão. O endpoint `/healthz` foi verificado diretamente em processo. O guia em [Deploy](DEPLOY.md) descreve os passos manuais e os limites do modo público.

## O que ainda não foi validado

O Docker daemon local não estava disponível; a imagem não foi construída nem executada. Nenhum serviço de hospedagem foi criado ou publicado. Nenhuma credencial IBM real foi configurada; chamadas ao Watson foram executadas somente com mock. Não foram realizadas sessões IBM Bob presenciais, pesquisa com clientes ou submissão do projeto. As metas de avaliação continuam sendo metas. Use o [checklist de entrega](ENTREGA.md) para reunir essas evidências reais.
