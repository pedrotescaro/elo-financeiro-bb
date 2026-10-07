# Proposta amadurecida

## Definição em uma frase

**Elo Financeiro é um agente pessoal proativo, concebido para o ecossistema do Banco do Brasil, que transforma dados autorizados em decisões explicadas e planos acompanhados para preservar a margem financeira do usuário.**

## Problema central

O usuário sabe quanto tem hoje, mas pode não conseguir relacionar esse saldo às próximas contas, ao cartão e às datas dos recebimentos. A dúvida importante é: "Se eu decidir isso agora, ainda consigo cumprir o que preciso até receber de novo?"

Nossa hipótese é que a fragmentação das informações e a carga de comparar cenários aumentam decisões impulsivas e atrasam a percepção de apertos financeiros. Isso deve ser verificado em pesquisa; não temos dados que comprovem prevalência ou impacto dessa hipótese.

## Público inicial e persona de trabalho

Pessoas adultas em início de autonomia financeira, incluindo jovens trabalhadores e autônomos com renda variável, que usam serviços digitais e encontram dificuldade para antecipar compromissos. Não tentaremos atender todos os públicos da trilha no primeiro MVP.

**Persona hipotética:** uma pessoa que recebe em datas diferentes, consulta o saldo pelo celular e precisa decidir entre pagar contas, fazer uma compra e manter algum dinheiro disponível. Quer orientações curtas, respeitosas e verificáveis. Não quer que o banco escolha ou movimente dinheiro por ela.

Não é uma persona baseada em entrevistas já realizadas. Sua idade, renda e hábitos não serão apresentados como fatos de pesquisa.

**Ponto de vista:** essa pessoa precisa enxergar as consequências de uma decisão no tempo, porque saldo atual e categorias de gastos não explicam sozinhos o risco de faltar dinheiro antes do próximo recebimento.

**Pergunta de design:** como tornar esse risco compreensível e oferecer uma ação viável, preservando o controle da pessoa sobre dados e escolhas?

## Experiência proposta

O produto começa pela meta "Quero manter R$ X de margem até meu próximo recebimento". Essa margem é definida pelo usuário e pode ser zero; não é um valor imposto como adequado para todas as pessoas.

O agente combina compromissos conhecidos, entradas esperadas e preferências autorizadas. Ao encontrar uma situação relevante, apresenta uma mensagem com quatro partes:

1. **O que pode acontecer:** menor saldo previsto e a data do risco.
2. **Por quê:** compromissos que contribuíram para a projeção, origem dos dados e hipóteses.
3. **Alternativas:** ajustes em gastos flexíveis, adiamento de uma compra ou conversa com atendimento quando o problema permanece.
4. **O que acontece se aceitar:** efeito exato da ação e o que o agente acompanhará.

O usuário pode aceitar, ajustar ou recusar. A versão inicial implementa aceitar e recusar por ausência de ação; edição livre do plano entra no backlog. Quando um evento novo muda o contexto, o sistema reavalia o plano. Um plano anterior não autoriza uma nova ação financeira.

## Antes e depois

| Momento | Experiência atual hipotética | Experiência com o Elo |
| --- | --- | --- |
| Consultar saldo | Vê o valor disponível agora | Vê também o menor saldo previsto até receber |
| Decidir uma compra | Compara preço e parcela isoladamente | Compara impacto no calendário e hipóteses |
| Perceber um aperto | Descobre após gastar ou perto do vencimento | Recebe um alerta priorizado com motivos |
| Organizar gastos | Precisa montar um plano do zero | Avalia uma sugestão que respeita despesas essenciais |
| Rever o plano | Refaz a análise manualmente | Recebe atualização quando chegam novos eventos |

## Diferencial a testar

O diferencial não é a presença de um chat, mas o ciclo **objetivo → antecipação → alternativa explicada → aprovação → acompanhamento**. A hipótese de inovação é ligar segurança de decisão, educação contextual e previsibilidade em uma jornada curta.

Não afirmamos que esse recurso seja inédito no mercado. A equipe deve comparar assistentes, agregadores e funcionalidades do BB antes de declarar exclusividade ou vantagem competitiva.

## Aderência à trilha Banco do Brasil

| Dimensão da trilha | Decisão de produto | Evidência demonstrável |
| --- | --- | --- |
| Segurança | Explica sinais de atenção, controla permissões e limita execução | Cenário PIX e rejeição de ação não permitida |
| Inclusão | Português simples, caminhos curtos e funcionamento inicial com poucos dados | Teste de compreensão e uso por teclado |
| Personalização | Usa calendário, margem e compromissos do cenário | Comparação de cenários com resultados diferentes |
| Escala | Separa ferramentas, política, modelo e conectores | Arquitetura modular; teste de escala ainda pendente |
| Responsabilidade | Diferencia fatos, hipóteses e limites; usuário aprova | Aprovação vinculada aos dados e revogação |
| Educação e engajamento | Explica a consequência da decisão no momento relevante | Comparação de compra e meta escolhida |

Alertas de fraude também cabem na trilha do BB, mas não serão a única narrativa. Nosso foco é a experiência financeira pessoal, com proteção integrada.

## O que entra e o que fica para depois

**MVP:** previsão de caixa com eventos conhecidos, decisão de compra, alertas ilustrativos de segurança, consentimento, aprovação e reavaliação. A jornada de caixa deve receber a maior parte do esforço e do tempo de vídeo.

**Expansão:** planos ajustáveis, educação por RAG com fontes curadas e versionadas, memória de preferências autorizadas, múltiplas contas, comparação de crédito com custo total e critérios explícitos, acessibilidade validada e encaminhamento humano.

**FGTS:** permanece como possível assunto de orientação futura. O agente precisaria consultar regras oficiais atuais e esclarecer condições. Não prometemos descobrir saldo, elegibilidade ou sacar FGTS; não é uma funcionalidade central do MVP.

**Investimentos:** somente simulações e educação numa expansão. Recomendações personalizadas, suitability e contratação exigiriam processos próprios do banco. Não entraremos nisso para a primeira entrega.

## Papel do Banco do Brasil e modelo de valor

Posicionamento inicial: serviço digital que poderia ser incorporado ao aplicativo ou ecossistema do BB, condicionado a uma parceria e a integrações autorizadas. O protótipo independente apenas demonstra essa experiência; não simula uma afiliação oficial.

O usuário ganha clareza e controle. O banco poderia ganhar engajamento útil, relacionamento e atendimento mais contextual. Redução de atrasos, perdas ou custo de atendimento são hipóteses de negócio a medir, não resultados obtidos.

O modelo principal não exige assinatura do cliente. A discussão de SaaS cabe como opção B2B futura: uma plataforma de agentes fornecida a instituições financeiras. Isso não deve ampliar o escopo do trabalho atual.

## Autonomia com finalidade clara

O sistema pode consultar dados consentidos, executar cálculos, recuperar orientações e apresentar recomendações dentro do objetivo escolhido. Pode registrar orçamento, meta ou lembrete após autorização específica.

Não contrata crédito, não compra ativos, não transfere dinheiro e não presume que um benefício esteja disponível. Em produção, pagamentos seriam uma jornada separada com autorização específica e controles do banco.

## Pesquisa necessária

Validar: se o público entende "menor saldo previsto"; que margem deseja; quais alertas considera úteis; quais compromissos não devem ser tratados como flexíveis; como prefere recusar; quando deseja atendimento humano; quais dados aceita compartilhar.

Entrevistas não devem coletar extratos, CPF, credenciais ou dados financeiros identificáveis. Usar situações fictícias e registrar apenas respostas anônimas permitidas pelas regras do programa.
