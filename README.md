<p align="center">
  <img src="assets/logo-elo-financeiro.png" alt="Logo do Elo Financeiro" width="460" />
</p>

# Elo Financeiro

**Sua próxima decisão, com mais clareza.**

Proposta acadêmica para a **Trilha 1 do IBM SkillsBuild AI Experiential Learning Lab: Serviços Financeiros Digitais Inteligentes, Seguros e Inclusivos com Banco do Brasil**.

O Elo propõe um agente pessoal que antecipa apertos de caixa, explica o impacto de decisões e acompanha planos escolhidos pelo usuário. Seu objetivo central é **preservar uma margem financeira até o próximo recebimento**.

O saldo de hoje pode parecer suficiente, mesmo quando as contas dos próximos dias vão deixá-lo negativo. O Elo considera o calendário: identifica o problema antes do vencimento, consulta ferramentas de cálculo e orientação, apresenta alternativas e acompanha o resultado de uma ação autorizada.

> Status: proposta amadurecida + protótipo inicial executável. A demonstração padrão usa regras e dados sintéticos. Não é uma integração oficial do Banco do Brasil nem uma entrega IBM finalizada.

## Executar em dois comandos

Requisito: Python 3.11 ou superior. Não há dependências externas no modo de demonstração.

```bash
cd elo-financeiro-bb
python -m elo.server
```

Abra **http://127.0.0.1:8000**. A sessão existe apenas na memória; reiniciar o servidor limpa os dados.

```bash
python -m unittest discover -s tests -v
```

## O que está pronto

| Capacidade | Situação |
| --- | --- |
| Três cenários e interface responsiva em português | Implementados |
| Projeção de caixa por fechamento diário | Implementada, com centavos inteiros |
| Consentimento demonstrativo e revogação | Implementados por sessão |
| Plano de redução de gastos flexíveis | Implementado; depende de aprovação |
| Aprovação vinculada à versão dos dados | Implementada; rejeita plano desatualizado |
| Simulação de compra e criação de meta | Implementadas; parcelas futuras não projetadas |
| Sinais ilustrativos de risco em PIX | Implementados por regras; sem detecção validada |
| Reavaliação após nova despesa | Implementada; evento simulado pela interface |
| Planejador IBM watsonx.ai | Adaptador REST implementado; chamada real não validada |
| RAG | Busca local por tópico; RAG semântico pendente |
| IBM Bob | Uso e evidências precisam ser realizados pela equipe |
| BB / Open Finance / pagamentos / crédito | Integrações de produção fora deste protótipo |
| Publicação acessível aos avaliadores | Pendente |

## Três jornadas com uma mesma finalidade

1. **Previsibilidade:** R$ 1.500 de saldo atual, compromissos antes do recebimento e uma previsão de -R$ 100. O usuário autoriza reduzir R$ 300 de lazer previsto, e o menor saldo passa a R$ 200. Uma nova despesa de R$ 150 reduz essa margem para R$ 50.
2. **Decisão de compra:** um celular de R$ 3.500 é comparado com o calendário de contas. A interface apresenta impacto à vista, efeito da primeira parcela de um exemplo sem juros e a alternativa de criar uma meta.
3. **Decisão protegida:** uma intenção de PIX reúne sinais sintéticos de urgência, destinatário novo e valor atípico. O agente orienta a conferir; o protótipo não realiza nem bloqueia o pagamento.

## Por que a proposta envolve IA agêntica

O produto pretendido trabalha com um objetivo persistente, ferramentas especializadas, autorização, estado e replanejamento após eventos. A IA deve selecionar consultas e combinar contexto para propor um próximo passo, com cálculos e permissões validados fora do modelo.

**O modo padrão deste código é uma base determinística para demonstrar a jornada.** Não deve ser apresentado como raciocínio generativo ou como sistema multiagente completo. O adaptador opcional permite um modelo IBM escolher uma lista limitada de ferramentas; o próximo marco é validar esse funcionamento na conta da equipe e ampliar a avaliação. Leia [Arquitetura](docs/ARQUITETURA.md).

## Conectar o planejador IBM

Use o projeto e um modelo Granite realmente disponíveis na conta do programa. Configure as variáveis de `.env.example` no terminal. O arquivo não é carregado automaticamente. Não salve chaves em commits.

Exemplo Linux/macOS, com valores obtidos pela equipe:

```bash
export ELO_PLANNER=watsonx
export IBM_CLOUD_API_KEY='sua-chave'
export WATSONX_PROJECT_ID='seu-projeto'
export WATSONX_MODEL_ID='modelo-granite-disponivel'
export WATSONX_URL='https://us-south.ml.cloud.ibm.com'
python -m elo.server
```

No PowerShell, configure cada variável com `$env:NOME='valor'`. O endpoint precisa corresponder à região da conta. Sem configuração, o código não faz chamadas externas. Com o adaptador ativado, somente cenários sintéticos são enviados à IBM. Se a resposta falhar ou não estiver no formato permitido, o sistema exibe que voltou à demonstração por regras.

## Documentação do projeto

- [Proposta completa, público e modelo de valor](docs/PROPOSTA.md)
- [Arquitetura, ferramentas e fronteiras de autonomia](docs/ARQUITETURA.md)
- [Requisitos, métricas e pesquisa com usuários](docs/VALIDACAO.md)
- [Cronograma até a entrega e backlog](docs/ROADMAP.md)
- [Texto do problema e da solução, abaixo de 500 palavras](docs/SUBMISSAO.md)
- [Roteiro de demonstração de até três minutos](docs/DEMO.md)
- [Como comprovar o uso real do IBM Bob](bob_sessions/README.md)
- [Referências e limites da fundamentação](docs/REFERENCIAS.md)

## Estrutura

```text
elo/          Ferramentas, coordenador, servidor e adaptador IBM
web/          Interface da demonstração
data/         Cenários sintéticos e orientações curadas
tests/        Verificações de cálculos, consentimento e aprovação
docs/         Proposta, arquitetura, pesquisa e entrega
bob_sessions/ Evidências reais a inserir pela equipe
```

## Limites e próximos passos

Este servidor serve para demonstração local. Não possui autenticação de produção, banco persistente, integração Open Finance ou proteção completa para exposição pública. Antes de publicar, siga o item de hospedagem do [roadmap](docs/ROADMAP.md).

Os relatórios são estimativas com entradas conhecidas, não previsões treinadas. O ajuste modifica um orçamento futuro, não transações realizadas. Os três exemplos não demonstram eficácia contra fraude, redução de endividamento ou impacto em clientes reais.

O nome Elo Financeiro é provisório. A equipe deve verificar disponibilidade de marca antes de qualquer lançamento comercial. Este projeto não utiliza logotipos oficiais do BB ou da IBM.
