<p align="center">
  <img src="assets/logo-elo-financeiro.png" alt="Logo do Elo Financeiro" width="460" />
</p>

# Elo Financeiro

**A carteira da agência numa conversa, e o contato com o cliente antes do aperto.**

Proposta acadêmica da equipe **Fatec Ferraz Heal** para a **Trilha 1 do IBM SkillsBuild AI Experiential Learning Lab: Serviços Financeiros Digitais Inteligentes, Seguros e Inclusivos com Banco do Brasil**.

O Elo é um agente de IA conversacional para o **analista de negócios de uma agência do Banco do Brasil**. O analista pergunta em português sobre a carteira de clientes ("quem fica no vermelho nos próximos 7 dias?"). O agente aponta quem vai ficar sem dinheiro antes do próximo recebimento, quando e quanto falta. O analista monta a lista de contatos da semana. O **gerente de relacionamento** abre cada caso numa tela de atendimento, com calendário de saldo, proposta calculada e aprovação explícita do cliente.

> **Status em 11/11/2026:**
> - Protótipo executável com dados sintéticos: 264 testes Python e 43 de interface, todos passando.
> - Cinco sessões do IBM Bob, de dois integrantes, registradas com commits e capturas em `bob_sessions/`.
> - Pendentes: a chamada real ao IBM watsonx.ai na conta do programa, a publicação e o vídeo novo.
> - O que mudou depois do feedback do avaliador está em [Resposta ao feedback](docs/RESPOSTA_AO_FEEDBACK.md).
> - Não é uma integração oficial do Banco do Brasil nem uma entrega IBM finalizada.

## O problema

Contas vencem antes do salário. O saldo de hoje parece suficiente, mas o calendário leva o cliente ao negativo dias antes de receber. Numa agência, isso acontece com dezenas de clientes ao mesmo tempo. Para agir antes, alguém precisaria olhar o saldo futuro de cada um, e essa triagem manual não cabe na semana. O contato acaba acontecendo depois do aperto, quando o cliente já está no cheque especial ou pedindo renegociação.

## O que o agente faz

| Visão | Quem usa | O que acontece |
| --- | --- | --- |
| **Analista da agência** (`/analista`) | Analista de negócios | Pergunta em português sobre a carteira. O agente analisa os clientes com consentimento e responde com quem está em risco, quando, quanto falta e quem se resolve com ajuste de gastos. Filtra por segmento, prazo e gerente. Monta a lista de contatos da semana e exporta em CSV. |
| **Atendimento ao cliente** (`/`) | Gerente de relacionamento | Abre o cliente da lista: calendário de saldo dia a dia, pior dia, hipóteses, proposta de ajuste com efeito calculado. O cliente aprova, ajusta ou recusa, e o desfecho volta para a lista do analista. Também trata compra parcelada e sinais de risco em PIX. |

Números da carteira sintética de demonstração (40 clientes, 37 com consentimento):

| Indicador | Valor |
| --- | --- |
| Clientes em risco nos próximos 14 dias | 15 (11 negativos, 4 abaixo da margem) |
| Resolvem só com ajuste de gastos flexíveis | 6 |
| Antecedência do aviso antes do primeiro saldo negativo | mediana de 7 dias |
| Tempo de análise da carteira | cerca de 3 ms, medido e exibido na tela |
| Coerência entre a tela do analista e a do atendimento | 100% dos clientes, verificada por teste |

O ganho de tempo do analista em relação à triagem manual ainda é uma estimativa a medir com analistas voluntários. Proposta completa, personas, métricas, piloto e riscos estão em [Proposta](docs/PROPOSTA.md).

## Como a IA é usada

- **IBM watsonx.ai** (API de geração de texto, modelo Granite da conta) tem dois papéis, e em nenhum deles produz números:
  - interpreta a pergunta do analista e a transforma numa consulta estruturada, conferida contra uma lista fechada antes de ser usada;
  - na tela de atendimento, escolhe quais ferramentas do agente rodam para o cliente aberto.
- Se o modelo falhar, estiver desligado ou responder fora do contrato, regras locais assumem, e um selo na tela diz quem interpretou.
- Saldos, prazos, propostas e permissões são sempre calculados pelo código Python, em centavos inteiros.
- **IBM Bob** é a ferramenta de desenvolvimento da equipe: cinco sessões em modo Agent, com registro, captura e commits em [`bob_sessions/`](bob_sessions/README.md). O mapeamento por critério e os próximos prompts estão em [Uso do Bob](docs/USO_DO_BOB.md).
- IBM watsonx Orchestrate e IBM Consulting Advantage não são usados nesta versão. Detalhes em [Declaração técnica](docs/DECLARACAO_TECNICA.md).

## Executar localmente

Requisito: Python 3.11 ou superior. Não há dependências externas.

```bash
git clone https://github.com/pedrotescaro/elo-financeiro-bb.git elo-financeiro
cd elo-financeiro
python -m elo.server
```

Abra **http://127.0.0.1:8000/analista** para a visão do analista ou **http://127.0.0.1:8000** para o atendimento. A sessão existe só na memória, expira após 30 minutos sem uso e é descartada ao reiniciar o servidor.

### Roteiro de cinco minutos

1. Em `/analista`, leia o resumo: quantos clientes precisam de atenção e por gerente.
2. Clique em **Quem fica no vermelho?** e depois em **Quem resolve com ajuste?**. Veja a linha "Como respondi", com quem interpretou e o tempo medido.
3. Pergunte algo seu, por exemplo "clientes do gerente 2 em risco nos próximos 7 dias".
4. Clique em **Adicionar N à lista** para incluir os clientes da última resposta e depois em **Baixar CSV para os gerentes**.
5. Em um cliente da lista, clique em **Abrir no atendimento**. Autorize os dados, confira o calendário e aprove o plano.
6. Volte para `/analista`: o contato aparece como "Plano aprovado no atendimento".
7. No atendimento, **Apresentar a ideia** abre uma apresentação de quatro telas sobre o projeto.

### Testes

```bash
python -m unittest discover -s tests
node --test tests/web_behaviors.cjs tests/analyst_behaviors.cjs
```

O lint usa `python -m pip install ruff==0.16.0` e `python -m ruff check elo tests`. O GitHub Actions roda lint, compilação e as duas suítes a cada push; resultados registrados em [Verificação](docs/VERIFICACAO.md).

### Ligar o IBM watsonx.ai

Use o projeto e um modelo Granite disponíveis na conta do programa. Configure as variáveis só no terminal; `.env.example` mostra os nomes, e nenhuma chave vai para o repositório.

```bash
export ELO_PLANNER=watsonx
export IBM_CLOUD_API_KEY='sua-chave'
export WATSONX_PROJECT_ID='seu-projeto'
export WATSONX_MODEL_ID='modelo-granite-disponivel'
export WATSONX_URL='https://us-south.ml.cloud.ibm.com'
python -m elo.server
```

No PowerShell, use `$env:NOME='valor'`. Para comprovar a chamada real, rode `python -m elo.prova_watsonx`: ele grava em `docs/evidencias/watsonx/` o modelo e o horário devolvidos pela API, sem chave nem token. Os 30 casos de validação rodam com `python -m unittest tests.test_ibm_validation -v`. O modo público (`ELO_PUBLIC_ORIGIN`) recusa o planejador externo, para que a conta IBM não seja consumida por visitantes anônimos.

## O que está pronto

| Capacidade | Situação |
| --- | --- |
| Visão do analista: perguntas em português sobre a carteira | Implementada e testada; filtros por intenção, segmento, prazo, gerente e cliente |
| Interpretação de perguntas pelo IBM watsonx.ai | Implementada com contingência por regras; testada com respostas simuladas; chamada real pendente |
| Lista de contatos da semana | Implementada: inclusão, status, exportação em CSV, desfecho vindo do atendimento |
| Abrir cliente da carteira no atendimento | Implementado; mesmo cálculo nas duas telas, verificado por teste |
| Projeção de caixa por fechamento diário | Gráfico com o menor saldo e tabela; centavos inteiros |
| Proposta de ajuste com aprovação | Valor ajustável, recusa explícita, aprovação vinculada à versão dos dados |
| Reavaliação após nova despesa | Implementada; a aprovação anterior deixa de valer |
| Compra parcelada e sinais de PIX | Parcelas projetadas no horizonte, sem juros; sinais de PIX por regras, sem confirmar fraude |
| Consentimento e revogação | Clientes sem consentimento ficam fora da análise e do atendimento |
| Explicações e trilha da sessão | Números, hipóteses, exclusões, perguntas, aprovações e revogações visíveis |
| Acessibilidade | Teclado, foco visível, rótulos, texto ampliável, layout de celular; avaliação com leitores de tela pendente |
| Demonstração pública | Controles de origem, limites e cabeçalhos; Dockerfile e guia prontos; imagem e hospedagem ainda não executadas |
| IBM Bob | Cinco sessões registradas; faltam o parágrafo de revisão de cada integrante e as sessões sobre a visão do analista |
| Chamada real ao IBM watsonx.ai | Pendente; script de prova pronto |
| Vídeo e publicação | Pendentes; roteiro em [Demo](docs/DEMO.md) e guia em [Deploy](docs/DEPLOY.md) |

## Arquitetura em uma página

```text
Analista ──pergunta──► /api/analista ──► interpretação (watsonx.ai ou regras) ──► consulta validada
                                                                                       │
                       data/carteira.json ──► análise da carteira (cashflow de cada cliente com consentimento)
                                                                                       │
                       resposta com números do código ◄──────────────────────────────────┘
                                │
                lista de contatos da semana (CSV) ──► gerente abre o cliente ──► /  (atendimento)
                                                                                   │
                     projeção, proposta, aprovação ◄── ferramentas escolhidas (watsonx.ai ou regras)
```

```text
elo/core.py          Ferramentas de caixa, compra, segurança e orientação; política de aprovação
elo/carteira.py      Carteira sintética, análise em lote e perguntas do analista
elo/watsonx.py       IBM watsonx.ai: interpretar perguntas e escolher ferramentas, com contingência
elo/prova_watsonx.py Evidência da chamada real, sem segredos
elo/server.py        Sessões, consentimento, limites, lista de contatos e rotas HTTP
web/                 analista.html e index.html, sem dependências
data/                Carteira de 40 clientes sintéticos, cenários e orientações curadas
tests/               Domínio, HTTP, modo público, adaptador IBM e interface
docs/                Proposta, arquitetura, declaração técnica, dossiê, roteiro e entrega
bob_sessions/        Registros e capturas das sessões reais do IBM Bob
```

Detalhes em [Arquitetura](docs/ARQUITETURA.md).

## Documentação

- [Proposta: problema, stakeholders, caso de uso, métricas, piloto e riscos](docs/PROPOSTA.md)
- [Resposta ao feedback do avaliador, ponto a ponto](docs/RESPOSTA_AO_FEEDBACK.md)
- [Declaração técnica dos produtos IBM](docs/DECLARACAO_TECNICA.md)
- [Uso do IBM Bob: sessões, prompts e mapeamento](docs/USO_DO_BOB.md)
- [Texto do problema e da solução para o formulário](docs/SUBMISSAO.md) e [campos da inscrição](docs/INSCRICAO.md)
- [Dossiê de apresentação em slides](docs/DOSSIE.md) e [roteiro do vídeo](docs/DEMO.md)
- [Arquitetura](docs/ARQUITETURA.md), [requisitos e validação](docs/VALIDACAO.md) e [verificação técnica](docs/VERIFICACAO.md)
- [Sistema visual: paleta, tipografia, ícones e movimento](DESIGN.md)
- [Registro do produto para o guia impeccable: usuários, propósito, restrições e evidências](PRODUCT.md)
- [Plano técnico do watsonx.ai, recuperação e publicação](docs/PLANO_TECNICO.md) e [deploy](docs/DEPLOY.md)
- [Roadmap](docs/ROADMAP.md), [pendências da entrega](docs/ENTREGA.md) e [referências](docs/REFERENCIAS.md)

## Limites

- Carteira, clientes e cenários são sintéticos. Não há conexão bancária, Open Finance real, transferência, oferta de crédito ou confirmação de fraude.
- As projeções usam eventos conhecidos; recebimentos podem atrasar e despesas novas podem surgir.
- O servidor guarda tudo em memória e serve a uma demonstração, não a um ambiente de produção. A lista de contatos e a trilha somem quando a sessão expira.
- A efetividade com analistas, gerentes e clientes reais ainda precisa ser medida.
- O nome Elo Financeiro é provisório. Este projeto não usa logotipos oficiais do BB ou da IBM.
