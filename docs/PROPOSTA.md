# Proposta amadurecida

## Definição em uma frase

**Elo Financeiro é um agente de IA conversacional para o analista de negócios de uma agência do Banco do Brasil: ele pergunta em português sobre a carteira de clientes, o agente aponta quem vai ficar sem dinheiro antes do próximo recebimento e por quê, e o gerente de relacionamento abre cada caso com o calendário de saldo, uma proposta calculada e aprovação explícita.**

## O que mudou depois do feedback

O consultor de submissão sugeriu redirecionar o foco para IA conversacional voltada a analistas de negócios e para dados corporativos. Acatamos a sugestão sem descartar o que já funcionava: o motor de projeção de caixa, que antes atendia um cliente por vez, agora também roda sobre uma carteira inteira (dado corporativo da agência) e responde a perguntas do analista. A tela de atendimento continua existindo e virou o segundo passo do fluxo.

## Problema central

O analista de negócios responsável por uma carteira de pessoas físicas precisa decidir, toda semana, quais clientes o gerente de relacionamento deve procurar antes que o problema aconteça. Para isso ele teria de olhar cliente por cliente: saldo, contas a vencer, data do próximo recebimento e o que dá para ajustar. Com dezenas de clientes, a triagem fica para depois, e o contato só acontece quando o cliente já entrou no negativo, no cheque especial ou numa renegociação.

## Stakeholders

### Principal: analista de negócios da agência

**Persona de trabalho:** Carla, analista de negócios de uma agência de médio porte, acompanha a carteira de pessoas físicas de três gerentes.

**Rotina relevante:** uma vez por semana prepara a lista de clientes que os gerentes devem procurar. Usa relatórios do banco para saldo e histórico, mas não tem uma visão de saldo futuro por cliente, com as contas que ainda vão vencer.

**Dor:** a triagem manual não cabe na semana. Ela prioriza pelos casos que já deram problema, não pelos que vão dar.

**Frequência:** semanal, sobre a carteira inteira [SUPOSIÇÃO A VALIDAR].

### Secundário: gerente de relacionamento

**Persona de trabalho:** Marcos, gerente de relacionamento, recebe a lista e liga para cada cliente. Precisa chegar à conversa com o calendário de saldo, o pior dia, as hipóteses e uma alternativa já calculada.

As duas personas são hipotéticas, construídas a partir do problema. Não foram validadas em entrevistas com funcionários do BB.

## Caso de uso de ponta a ponta

1. Carla abre a visão do analista. O agente já analisou os 37 clientes da carteira sintética que deram consentimento de compartilhamento; 3 sem consentimento ficaram de fora.
2. Ela pergunta "quem fica no vermelho nos próximos 7 dias?". O IBM watsonx.ai interpreta a pergunta (ou, sem credenciais, as regras locais) e o código calcula a resposta: quais clientes, a falta somada para a margem e o próximo passo de cada um.
3. Ela pergunta "quem resolve com ajuste de gastos flexíveis?" e separa os casos simples (6) dos que pedem conversa mais longa. Pode filtrar por segmento, prazo ou gerente ("clientes do gerente 2 em risco").
4. Ela monta a **lista de contatos da semana** com um clique ("Adicionar à lista") e baixa o CSV com cliente, gerente, situação, pior dia e próximo passo para distribuir aos gerentes.
5. Marcos clica em "Abrir no atendimento" num desses clientes. A tela de atendimento mostra o calendário diário, o menor saldo e a proposta de ajuste com efeito calculado.
6. Na conversa com o cliente, Marcos aprova o ajuste, ou ajusta o valor, ou registra a recusa. Nenhum dinheiro é movimentado. Se surgir uma nova despesa, a projeção é recalculada e a aprovação anterior deixa de valer.
7. O desfecho volta para a lista da Carla: "plano aprovado" ou "proposta recusada". Contatos feitos fora da tela são marcados como "contatado". No fim da semana ela sabe quem foi atendido e quem ainda falta.

## Meta de desempenho

| Dimensão | Antes (sem o agente) | Com o agente | Fonte ou método | Amostra |
| --- | --- | --- | --- | --- |
| Tempo do computador para analisar a carteira | Não se aplica | Cerca de 3 ms para 37 clientes; cerca de 4 ms por pergunta respondida | **Medido**: `tempo_analise_ms` e `tempo_resposta_ms`, exibidos na tela e devolvidos pela API, em notebook da equipe | Carteira sintética de 40 clientes |
| Tempo do analista para a triagem semanal | 3 a 5 min por cliente, cerca de 2 a 3 h para 37 clientes [SUPOSIÇÃO A VALIDAR] | Menos de 15 min para ler as respostas e revisar os casos [SUPOSIÇÃO A VALIDAR] | Cronometrar analistas voluntários fazendo a mesma triagem com planilha e com o Elo | 5 analistas, mesma carteira sintética |
| Clientes em risco identificados | Depende da revisão manual [SUPOSIÇÃO A VALIDAR] | 15 de 37 (11 negativos e 4 abaixo da margem), com 6 resolvíveis por ajuste | **Medido** na carteira sintética | 37 clientes com consentimento |
| Antecedência do aviso | Contato depois do aperto [SUPOSIÇÃO A VALIDAR] | Mediana de 7 dias antes do primeiro saldo negativo (mínimo de 3) | **Medido** na carteira sintética (`dias_ate_risco`) | 11 clientes com saldo negativo |
| Coerência entre a visão do analista e a do atendimento | Não se aplica | 100%: menor saldo, data e "resolve com ajuste" iguais nas duas telas | **Verificado** por teste automatizado cliente a cliente (`tests/test_carteira.py`) | 37 clientes |
| Lista da semana pronta para os gerentes | Montada à mão [SUPOSIÇÃO A VALIDAR] | Gerada a partir das respostas, com desfecho atualizado pelo atendimento | **Verificado** por teste: aprovação e recusa no atendimento mudam o status na lista | Fluxo completo nos testes HTTP |
| Ação sem aprovação | Não se aplica | Zero | **Verificado** nos testes automatizados | 264 testes Python e 43 de interface |

As linhas marcadas como **Medido** ou **Verificado** são resultados do protótipo com dados sintéticos. As linhas com [SUPOSIÇÃO A VALIDAR] são hipóteses de trabalho, não resultados.

## Aderência à trilha Banco do Brasil

| Dimensão da trilha | Decisão de produto | Evidência demonstrável |
| --- | --- | --- |
| Escala | Uma pergunta analisa a carteira inteira, com o mesmo cálculo da tela de atendimento | Visão do analista com 37 clientes; tempo medido na tela |
| Personalização | Cada cliente tem calendário, margem e gastos próprios | Respostas por segmento, prazo e cliente |
| Segurança e consentimento | Só entram clientes com consentimento de compartilhamento, no modelo do Open Finance; aprovação vinculada à versão dos dados | Clientes sem consentimento são recusados na análise e no atendimento (testes) |
| Inclusão | Perguntas em português comum; telas com teclado, foco visível e texto ampliável | Interface verificada; avaliação com leitores de tela pendente |
| Responsabilidade | O agente não oferece crédito, não move dinheiro e mostra hipóteses e limites | Textos de limite em cada resposta; trilha da sessão |
| Prevenção de golpes | Sinais de risco em PIX na tela de atendimento | Cenário PIX; sem confirmação de fraude |

## Antes e depois

| Momento | Hoje (estimado) | Com o Elo |
| --- | --- | --- |
| Escolher quem procurar | Triagem manual, cliente a cliente [SUPOSIÇÃO A VALIDAR] | Pergunta em português sobre a carteira inteira |
| Saber quando o aperto acontece | Cálculo manual sujeito a omissão de contas | Data do primeiro saldo negativo por cliente |
| Separar casos simples de casos difíceis | Depende da experiência | "Resolve com ajuste de gastos flexíveis" calculado |
| Preparar a conversa com o cliente | Montar o calendário de novo | Abrir o cliente direto na tela de atendimento |
| Rever após nova despesa | Nova análise manual | Reavaliação automática; aprovação anterior não vale |

## O que entra e o que fica para depois

**Nesta versão:** visão do analista com perguntas em português sobre a carteira sintética (por intenção, segmento, prazo e gerente), interpretação pelo IBM watsonx.ai com contingência por regras, lista de contatos da semana com exportação em CSV e desfecho vindo do atendimento, abertura do cliente na tela de atendimento, projeção de caixa, proposta com aprovação, compra parcelada e sinais de PIX.

**Depois:** orquestrar os papéis do agente no IBM watsonx Orchestrate (recomendado pelo guia do programa); ampliar as perguntas do analista (por gerente, por produto, por tendência); recuperação semântica sobre normas internas; dados reais via Open Finance, só com parceria e autorização do BB.

## Como funcionaria dentro do banco

Este protótipo roda sozinho, com dados sintéticos. Dentro do BB, a mesma lógica dependeria de peças que não existem aqui, e que só a parceria com o banco pode fornecer:

| Peça | No protótipo | Em produção (proposta, a validar com o BB) |
| --- | --- | --- |
| Dados da carteira | `data/carteira.json`, 40 clientes sintéticos | Saldos e compromissos dos sistemas do banco e, com consentimento, de outras instituições via Open Finance |
| Quem pode perguntar | Qualquer sessão da demonstração | Analistas e gerentes autenticados, cada um vendo só a própria carteira |
| Consentimento | Campo `consentimento_open_finance` por cliente | Consentimento registrado, com validade e revogação respeitadas pela análise |
| IA | IBM watsonx.ai interpreta a pergunta; regras como contingência | O mesmo papel, com o modelo e a região aprovados pelo banco, e avaliação contínua do acerto |
| Lista de contatos | Sessão de 30 minutos, exportada em CSV | Integrada à agenda e ao CRM do gerente, com histórico |
| Registro | Trilha temporária da sessão | Auditoria de produção de cada pergunta, lista e decisão |

## Privacidade, LGPD e uso responsável

- **Finalidade definida:** a análise serve para oferecer ajuda antes do aperto. Não serve para cortar limite, negar crédito ou ranquear clientes para cobrança. O agente não oferece nenhum produto de crédito.
- **Minimização:** o modelo recebe a pergunta do analista, não os dados dos clientes. Na tela de atendimento, recebe apenas o cenário do cliente aberto. CPF, nome real e extratos não são necessários para o cálculo.
- **Consentimento:** clientes sem consentimento de compartilhamento não entram na análise, não aparecem nas respostas e não podem ser abertos no atendimento. Os testes cobrem os três casos.
- **Explicação:** cada resposta mostra o que foi considerado (quem interpretou, quantos clientes, o tempo) e cada número do atendimento tem hipótese e limite visíveis.
- **Decisão humana:** o agente sugere; o gerente conversa; o cliente aprova. Nada é executado automaticamente.
- **Base legal e retenção** em produção precisam ser definidas com o jurídico e o encarregado de dados do banco. Este protótipo não faz essa avaliação.

## Plano de piloto

| Etapa | Duração estimada | O que medir | Critério para seguir |
| --- | --- | --- | --- |
| 1. Teste de uso com a carteira sintética | 2 semanas | Tempo da triagem com e sem o Elo; perguntas que o agente não entende; confiança nas respostas | Ganho de tempo percebido por pelo menos 4 de 5 analistas |
| 2. Avaliação da IA | Em paralelo à etapa 1 | Acerto do IBM watsonx.ai contra o gabarito de perguntas (`docs/PERGUNTAS_ANALISTA.md`, a criar); respostas fora do contrato | Acerto acima das regras locais, com zero números inventados |
| 3. Piloto assistido em uma agência | 8 semanas | Clientes contatados antes do primeiro saldo negativo; planos aprovados; reclamações | Aprovação do banco, jurídico e segurança antes de usar dados reais |

As durações e critérios são proposta da equipe [SUPOSIÇÃO A VALIDAR].

## Riscos e como tratamos

| Risco | Como o protótipo trata | O que falta |
| --- | --- | --- |
| O modelo interpretar errado a pergunta | Consulta validada contra lista fechada; contingência por regras; a tela diz como a pergunta foi entendida | Medir o acerto com o gabarito (Prompt 13) |
| O modelo inventar números | O modelo não produz números; respostas montadas pelo código | Manter isso em qualquer evolução |
| Injeção de instruções na pergunta | Pergunta entre marcadores e tratada como dado; consulta validada | Testes adversariais com perguntas maliciosas |
| Projeção errada por dado incompleto | Hipóteses e limites visíveis; recebimento e contas tratados como previsão | Dados reais e conciliação |
| Uso para fins que prejudiquem o cliente | Finalidade declarada; sem oferta de crédito | Política do banco e auditoria |
| Excesso de alertas | Lista priorizada por pior saldo e por "resolve com ajuste" | Preferências do cliente e frequência máxima de contato |

## Papel do Banco do Brasil e modelo de valor

Posicionamento: ferramenta interna de apoio a analistas e gerentes, que poderia ser incorporada aos sistemas do banco mediante parceria e integrações autorizadas. O protótipo é independente e não simula afiliação oficial.

Valor esperado para o banco: contato proativo antes do aperto, menos tempo de triagem e conversa mais curta com o cliente. Redução de inadimplência, de uso de crédito caro ou de reclamações são hipóteses de negócio a medir, não resultados obtidos.

## Autonomia com finalidade clara

O agente lê dados consentidos, calcula, responde perguntas e propõe ajustes. Registra plano ou meta somente após aprovação específica. Não contrata crédito, não transfere dinheiro, não presume elegibilidade a produtos e não decide quem o banco deve ou não atender.

## Pesquisa necessária

Validar com analistas e gerentes reais: quanto tempo leva a triagem semanal hoje; quais perguntas fazem sobre a carteira; que antecedência torna o contato útil; que informações precisam ver antes de ligar; quais respostas do agente geram desconfiança. Entrevistas não devem coletar dados de clientes, CPF ou extratos; usar a carteira sintética e registrar só respostas anônimas permitidas pelo programa.
