# Plano de validação IBM e evolução técnica

Este documento cobre quatro áreas pendentes identificadas no feedback: validação real do watsonx.ai, especificação do RAG semântico, integração do Bob/watsonx na interface principal, e publicação acessível aos avaliadores.

---

## 1. Validar a chamada real ao watsonx.ai

### O que configurar

```bash
export IBM_CLOUD_API_KEY='sua-chave-da-conta-do-programa'
export WATSONX_PROJECT_ID='id-do-projeto-na-conta'
export WATSONX_MODEL_ID='ibm/granite-13b-instruct-v2'   # ou o modelo disponível na conta
export WATSONX_URL='https://us-south.ml.cloud.ibm.com'  # ajustar à região da conta
export ELO_PLANNER=watsonx
```

No PowerShell: substituir `export` por `$env:NOME='valor'`. O endpoint deve corresponder exatamente à região ativa na conta IBM do programa. Não salvar esses valores em nenhum arquivo do repositório.

### Como executar

Primeiro a prova curta, depois os 30 casos:

```bash
python -m elo.prova_watsonx
python -m unittest tests.test_ibm_validation -v
```

`python -m elo.prova_watsonx` (código novo, `elo/prova_watsonx.py`) roda os três cenários com o planejador real e grava em `docs/evidencias/watsonx/AAAA-MM-DD_HHMMSS.json` o que a API devolveu: `model_id`, `model_version`, `created_at`, contagem de tokens, latência e ferramentas finais. Sem as quatro variáveis, ele não chama nada, não grava nada e sai com código 2. Só marca `"chamada_real_comprovada": true` quando os três cenários saem em modo `watsonx`.

Os 30 casos de `tests/test_ibm_validation.py` usam a chamada real quando as quatro variáveis existem; sem elas, usam respostas simuladas. O resumo final indica o modo, o modelo informado pela API e as latências. No modo real, um caso só passa se o relatório vier em modo `watsonx`; se a contingência por regras assumir, o caso falha com a causa, para não contar como acerto do modelo.

### O que registrar como evidência

- O JSON gerado em `docs/evidencias/watsonx/`, commitado. Ele já não contém chave, token nem ID do projeto (o projeto aparece como digest de 8 caracteres).
- A captura do terminal com o resumo dos 30 casos.
- Uma pasta em `bob_sessions/` se a validação for conduzida no Bob (Prompt 7 de `docs/USO_DO_BOB.md`).
- A linha correspondente em `docs/VERIFICACAO.md` e a atualização do estado em `docs/DECLARACAO_TECNICA.md`.

### Comportamento esperado

Para cada cenário, o modelo deve devolver `{"tools": [...]}` com as ferramentas pertinentes. A política em `build_report()` aceita o plano se ele for válido e completa as ferramentas obrigatórias. Falha de rede, resposta inválida ou estouro dos 25 segundos levam ao modo `demo_fallback`.

### Fallback honesto

Quando o watsonx não está disponível ou falha, a interface mostra o aviso "O planejador IBM não respondeu com um plano válido. Demonstração por regras ativada." e o selo no topo muda para "Planejador: contingência por regras". Não ocultar esse aviso; ele mostra que uma falha externa não derruba a análise.

### Log que serve de evidência

O JSON de `python -m elo.prova_watsonx` é a evidência principal, porque traz o `model_id` e o `created_at` devolvidos pela própria API, coisa que uma resposta simulada não teria. A saída dos 30 casos complementa com acurácia e latência.

---

## 2. RAG semântico: o que implementar e o que especificar

O protótipo atual usa recuperação local por conceitos curados e TF-IDF (`elo/retrieval.py`). É uma base pequena e funcional, mas sem embeddings ou geração de respostas. O RAG semântico completo é um marco de expansão. Esta seção separa o que pode ser feito agora do que é especificação.

### O que pode ser feito agora (código novo)

**Ampliar a base de conhecimento em `data/knowledge.json`:** adicionar mais trechos curados sobre fluxo de caixa pessoal, parcelamento e verificação de PIX, com fonte e data de revisão declaradas. Não requer biblioteca externa. Melhora a cobertura da recuperação existente sem mudar a arquitetura.

**Adicionar sinônimos e conceitos ao dicionário em `elo/retrieval.py`:** feito em 2026-11-11 (código novo, fora do Bob). O vocabulário agora reconhece termos como "sufoco", "apertado", "vermelho", "zerou", "holerite", "prestação", "urgente" e "desconhecido", com três testes novos em `tests/test_retrieval.py`.

A ampliação da base em `data/knowledge.json` continua aberta e pode ser feita numa sessão do Bob.

### O que é especificação (marco futuro)

**Embeddings semânticos:** substituir TF-IDF por vetores de embeddings de uma base maior. Requer biblioteca (ex.: `sentence-transformers`) e modelo. Fora do escopo do MVP por criar dependência externa e custo de execução.

**Geração de respostas com watsonx.ai:** usar o modelo Granite para gerar uma resposta contextualizada com base nos trechos recuperados. Requer integração com o adaptador watsonx já existente. O contrato seria: `guidance(snapshot)` envia os trechos para o modelo e retorna a resposta gerada, em vez do texto cru dos trechos.

**Base sobre `docs/`:** indexar os documentos técnicos do repositório para que o gerente possa perguntar "como funciona a aprovação?" durante o atendimento. Útil mas não central para o MVP.

### Como declarar honestamente

Na demonstração e na documentação: "A recuperação atual usa correspondência de conceitos curados e similaridade de termos. Embeddings e geração de respostas são marcos futuros." Não chamar o que existe de "RAG semântico" sem qualificação.

---

## 3. Bob e watsonx no fluxo principal da interface

O feedback pede que o Bob e o watsonx apareçam no fluxo principal, não como anexo lateral. As mudanças necessárias na UI são:

### Indicador de modo do planejador (feito)

Implementado em 2026-11-11, fora do Bob. O selo fica logo abaixo do título da análise (`web/index.html`), é preenchido em `web/app.js` a partir do campo `mode` do relatório e tem cor própria para cada estado (`web/style.css`):

| `mode` | Texto do selo |
| --- | --- |
| `watsonx` | Planejador: IBM watsonx.ai escolheu as ferramentas · cálculos feitos no código, não pelo modelo |
| `demo_fallback` | Planejador: contingência por regras · o IBM watsonx.ai não respondeu com um plano válido |
| `demo_rules` | Planejador: regras locais · IBM watsonx.ai desligado nesta execução |

O teste "planner badge names IBM watsonx.ai only when the model actually planned" em `tests/web_behaviors.cjs` garante que o nome do watsonx só aparece quando o modelo de fato planejou. Nenhuma lógica de backend mudou.

### Onde o Bob aparece na interface

O Bob não aparece na interface de usuário final porque é uma ferramenta de desenvolvimento, não um componente do produto. O que aparece é o resultado do trabalho feito com o Bob: os cálculos que ele ajudou a testar, os bugs que ele identificou, os casos de validação que ele escreveu.

A forma de mostrar isso no vídeo é mostrar o Bob operando em uma sessão de desenvolvimento (ver Prompt 10 em `docs/USO_DO_BOB.md`) e cortar para a interface mostrando o resultado dessa sessão rodando.

### Mudança de UI recomendada para o vídeo

O selo já está aplicado. Quando o modo watsonx estiver ativo, o avaliador lê "IBM watsonx.ai" no topo da análise durante a demonstração. Sem credenciais, o selo diz "regras locais", e é isso que o vídeo deve mostrar enquanto a chamada real não for feita.

---

## 4. Publicação acessível aos avaliadores

### Opção recomendada: Render (custo zero)

O guia completo está em `docs/DEPLOY.md`. Resumo dos passos:

1. Garantir que o Docker daemon está ativo localmente.
2. Testar `docker build -t elo-financeiro-demo . && docker run --rm -p 127.0.0.1:8000:8000 elo-financeiro-demo` e verificar as três jornadas.
3. Criar conta no Render (render.com), conectar o repositório GitHub, selecionar Language: Docker.
4. Configurar `ELO_PUBLIC_ORIGIN=https://nome-atribuido.onrender.com` e `/healthz` como health check.
5. Não configurar `ELO_PLANNER=watsonx` nem credenciais IBM na demo pública: o modo público já recusa o planejador externo por design.
6. Após o deploy, testar em janela anônima e em celular externo à rede local.
7. Registrar URL, commit, data e resultado em `docs/VERIFICACAO.md`.

### O que remover antes de expor

- Nunca incluir `IBM_CLOUD_API_KEY`, `WATSONX_PROJECT_ID` ou qualquer credencial no ambiente público.
- Verificar que `.gitignore` cobre `.env` e qualquer arquivo com valores reais.
- Confirmar que `resumo-sessao.png` nas `bob_sessions/` não contém tokens ou chaves visíveis antes de fazer push final.
- O arquivo `.env.example` já está no repositório com placeholders; usá-lo como referência.

### Plano de contingência

Se o Render não estiver disponível ou o Docker daemon continuar indisponível, a alternativa é executar o servidor localmente durante a gravação do vídeo e mostrar o endereço `http://127.0.0.1:8000` na tela. Nesse caso, deixar claro no vídeo que é uma demonstração local e indicar que o link público está pendente. Na submissão, informar no campo de URL do protótipo que está disponível localmente e pode ser executado via `python -m elo.server`.

### Checklist antes de publicar

- [ ] Nenhuma chave, token ou credencial no repositório ou no ambiente de deploy
- [ ] `ELO_PUBLIC_ORIGIN` configurado com a URL exata do Render
- [ ] `/healthz` respondendo 200 em janela anônima
- [ ] Três jornadas completas funcionando sem login
- [ ] Sessões isoladas entre dois navegadores diferentes
- [ ] URL registrada em `docs/VERIFICACAO.md` com commit e data
