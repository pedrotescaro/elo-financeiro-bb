# Proposta amadurecida

## Definição em uma frase

**Elo Financeiro é um agente de apoio ao atendimento, concebido para o ecossistema do Banco do Brasil, que transforma dados autorizados em um calendário de saldo diário com alternativas calculadas e aprovação explícita, para que o gerente de relacionamento chegue à conversa com o cliente já com o cenário mapeado.**

## Problema central

O gerente de relacionamento do BB atende clientes que chegam após o problema ter acontecido: saldo zerou antes do recebimento, parcelamento comprometeu a margem, ou uma mensagem urgente criou dúvida sobre um PIX. Para preparar esse atendimento, o gerente precisa reconstruir o cenário financeiro do cliente a partir de informações dispersas, montar o calendário de contas mentalmente ou em planilha, e identificar qual ajuste é viável antes de propor qualquer ação.

Nossa hipótese é que essa reconstrução consome entre quinze e vinte minutos por atendimento de perfil financeiro complexo. Com o agente, o gerente abre a análise já calculada em dois a três minutos: vê o calendário diário, o menor saldo previsto, as hipóteses usadas e o efeito de um possível ajuste. [SUPOSIÇÃO A VALIDAR: tanto o tempo atual quanto o tempo esperado são estimativas sem medição; precisam ser verificados em entrevistas com gerentes reais ou em um piloto supervisionado.]

## Stakeholder: gerente de relacionamento do Banco do Brasil

**Nome para a persona de trabalho:** Marcos, gerente de relacionamento de uma agência de médio porte, dez anos de banco.

**Rotina relevante:** atende de oito a doze clientes por dia, dos quais dois a três apresentam situações de fluxo de caixa pessoal que exigem análise antes de propor um produto ou encaminhamento. Usa o sistema do banco para consultar saldo e histórico, mas não tem uma ferramenta que projete o calendário de saídas e entradas futuras em uma tela.

**Dor principal:** o tempo gasto para montar o cenário manualmente compete com o tempo disponível para o atendimento em si. Quando a projeção não está pronta, a conversa começa pelo diagnóstico e não pela solução.

**Frequência:** dois a três atendimentos com esse perfil por dia, estimados [SUPOSIÇÃO A VALIDAR]. Em agências de maior volume, pode ser mais.

**Ponto de vista:** Marcos precisa chegar ao atendimento com o cenário mapeado, as alternativas calculadas e os limites declarados, para que a conversa comece na solução e não no diagnóstico.

Esta persona é hipotética e construída a partir do problema descrito. Não foi validada em entrevistas com gerentes do BB. Antes de declarar eficiência ou preferência, a equipe deve verificar com gerentes reais.

## Caso de uso de ponta a ponta

### Situação inicial (baseline)

O cliente liga para a agência dizendo que o saldo sumiu antes do recebimento. Marcos abre o sistema do banco, consulta saldo e histórico, monta o calendário de saídas previstas manualmente ou em uma planilha separada, calcula o menor saldo esperado, identifica os gastos flexíveis e verifica qual redução seria viável sem cortar despesas essenciais. Estimativa de tempo para essa preparação: quinze a vinte minutos. [SUPOSIÇÃO A VALIDAR]

### Com o Elo Financeiro

Marcos autoriza a leitura dos dados sintéticos do cliente no agente. O sistema apresenta o calendário diário, o menor saldo previsto, a data do risco, a proposta de redução de gastos flexíveis com efeito calculado, e os limites da análise. Marcos confere as hipóteses, aprova ou ajusta a proposta, e parte para o atendimento com o cenário documentado. Estimativa de tempo para essa preparação: dois a três minutos. [SUPOSIÇÃO A VALIDAR]

### Meta de desempenho

| Dimensão | Baseline estimado | Meta com o agente | Método de medição | Amostra |
| --- | --- | --- | --- | --- |
| Tempo de preparação por atendimento de perfil complexo | 15 a 20 min [SUPOSIÇÃO A VALIDAR] | 2 a 3 min [SUPOSIÇÃO A VALIDAR] | Cronometrar em sessões com gerentes voluntários usando cenários sintéticos | 5 a 10 gerentes, 3 cenários cada |
| Erros de identificação do pior dia de saldo | Não medido [SUPOSIÇÃO A VALIDAR] | Zero erros nos cenários sintéticos testados | Comparar resultado do agente com cálculo manual independente | Todos os cenários da demonstração |
| Aprovação explícita antes de qualquer ação | Não existe no fluxo atual | 100% das ações requerem aprovação | Verificado nos testes automatizados | 233 testes Python e 36 de interface |

Toda métrica sem fonte está marcada com [SUPOSIÇÃO A VALIDAR]. O avaliador deve tratar essas suposições como hipóteses de design, não como resultados obtidos.

## Experiência proposta

O gerente abre o agente durante a preparação do atendimento. Após autorizar a leitura do cenário:

1. **O que pode acontecer:** menor saldo previsto, data do risco, recebimentos e saídas que contribuem.
2. **Por quê:** valores em centavos, hipóteses usadas e o que não foi considerado, transparente para que o gerente possa corrigir premissas incorretas antes de apresentar ao cliente.
3. **Alternativas:** ajuste de gastos flexíveis com efeito calculado, ou indicação de que a margem não é atingida com os flexíveis disponíveis.
4. **O que acontece ao aprovar:** efeito exato, a que versão dos dados está vinculado, e a necessidade de reaprovar se uma nova despesa surgir.

O gerente pode aceitar a proposta padrão, ajustar o valor da redução, recusar e registrar a recusa, ou revogar o acesso ao final da sessão.

## Antes e depois

| Momento | Fluxo atual (estimado) | Com o Elo |
| --- | --- | --- |
| Preparar o atendimento | 15 a 20 min para montar calendário manualmente [SUPOSIÇÃO A VALIDAR] | 2 a 3 min para revisar análise já calculada [SUPOSIÇÃO A VALIDAR] |
| Identificar o pior dia de saldo | Cálculo manual sujeito a omissão de eventos | Calendário diário completo com o menor saldo destacado |
| Propor um ajuste | Depende da experiência do gerente e do tempo disponível | Proposta com efeito calculado, hipóteses visíveis e aprovação vinculada |
| Rever após nova despesa | Nova análise manual | Reavaliação automática; plano anterior não é reaproveitado |
| Documentar a conversa | Anotação livre | Trilha temporária de consultas, aprovações e revogações |

## Aderência à trilha Banco do Brasil

| Dimensão da trilha | Decisão de produto | Evidência demonstrável |
| --- | --- | --- |
| Segurança | Consentimento por sessão, aprovação vinculada à versão, sinais de risco em PIX | Cenário PIX e rejeição de ação não permitida nos testes |
| Inclusão | Português simples, teclado, ampliação de texto, limites visíveis | Interface verificada; avaliação com leitores de tela pendente |
| Personalização | Calendário, margem e gastos do cenário; ajuste editável pelo gerente | Comparação de cenários com resultados diferentes |
| Escala | Ferramentas separadas, política, modelo e conectores | Arquitetura modular; teste de escala ainda pendente |
| Responsabilidade | Hipóteses e limites visíveis; gerente aprova antes de qualquer ação | Aprovação vinculada aos dados, revogação e trilha temporária |
| Educação e engajamento | Explica o calendário no momento do atendimento | Comparação de compra e meta registrada pelo gerente |

## O que entra e o que fica para depois

**MVP:** previsão de caixa com eventos conhecidos, comparação de compra, sinais de risco em PIX, consentimento, aprovação e reavaliação. A jornada de caixa deve receber a maior parte do tempo no vídeo.

**Expansão:** planos editáveis com múltiplos ajustes, RAG semântico sobre documentação curada, memória de atendimentos autorizados, comparação de crédito com custo total, acessibilidade validada com leitores de tela, integração com dados reais do Open Finance mediante parceria com o BB.

## Papel do Banco do Brasil e modelo de valor

Posicionamento inicial: ferramenta de suporte ao atendimento que poderia ser incorporada ao sistema interno do BB, condicionada a parceria e integrações autorizadas. O protótipo independente demonstra a experiência; não simula uma afiliação oficial.

O gerente ganha tempo de preparação e documentação. O banco poderia ganhar eficiência no atendimento e satisfação do cliente por chegar mais rápido à solução. Redução de reclamações, inadimplência ou custo de atendimento são hipóteses de negócio a medir, não resultados obtidos.

## Autonomia com finalidade clara

O sistema consulta dados consentidos, executa cálculos, recupera orientações e apresenta recomendações dentro do objetivo do atendimento. Registra orçamento ou meta após aprovação específica do gerente.

Não contrata crédito, não compra ativos, não transfere dinheiro e não presume elegibilidade a qualquer produto. O gerente aprova cada ação. Em produção, operações financeiras seriam jornadas separadas com autorização específica e controles do banco.

## Pesquisa necessária

Validar com gerentes reais: quanto tempo levam hoje para preparar um atendimento de perfil complexo; quais informações consultam; quais hipóteses mais frequentemente estão erradas no primeiro olhar; quando prefeririam ver o cenário antes vs. durante o atendimento; o que precisariam ajustar na interface para confiar na análise; quais limites são inaceitáveis como suposições.

Entrevistas não devem coletar dados de clientes, extratos, CPF ou credenciais. Usar cenários fictícios e registrar apenas respostas anônimas permitidas pelas regras do programa.
