# Texto de problema e solução

Rascunho abaixo de 500 palavras. Descreve a proposta; atualizar o estado da tecnologia após a implementação real. Não representa uma submissão realizada.

## Declaração

O Elo Financeiro propõe responder à trilha de Serviços Financeiros Digitais Inteligentes, Seguros e Inclusivos do Banco do Brasil com um agente pessoal voltado à previsibilidade financeira e à proteção das decisões do usuário.

Nosso problema central é que conhecer o saldo atual não basta para entender se haverá dinheiro para cumprir os compromissos antes do próximo recebimento. Contas, cartão, gastos previstos e entradas em datas diferentes tornam essa análise difícil, especialmente para pessoas em início de autonomia financeira ou com renda variável. Essa hipótese será avaliada com usuários por meio de cenários fictícios.

A proposta permite definir uma margem desejada e acompanhar o calendário financeiro. Com acesso autorizado, o agente consulta ferramentas, identifica apertos futuros e apresenta o menor saldo previsto, a data do risco e os compromissos envolvidos. Em seguida, oferece alternativas compreensíveis, como ajustar gastos flexíveis ou adiar uma compra. Se o usuário aceitar, registra o plano permitido e reavalia a situação quando novos eventos alteram a projeção.

O protótipo inicial demonstra três jornadas com dados sintéticos: antecipar falta de saldo, comparar uma compra e explicar sinais ilustrativos de risco em uma intenção de PIX. Os cálculos financeiros e as permissões são validados pelo código. A aprovação se vincula à versão dos dados apresentados, e a leitura pode ser revogada. Nenhuma transferência, contratação de crédito ou aplicação é executada.

O diferencial a validar é conectar antecipação, educação contextual e acompanhamento em um mesmo ciclo de decisão. A experiência usa português simples, explicita as hipóteses das projeções e preserva o controle do usuário.

A arquitetura prevê IBM watsonx.ai com modelo Granite para selecionar ferramentas, funções especializadas de caixa, planejamento e segurança, conteúdo curado e autorização específica. O adaptador IBM está preparado; a demonstração padrão ainda funciona por regras. A equipe deverá comprovar o uso central do IBM Bob e avaliar a integração real antes da submissão.

Em uma evolução autorizada pelo banco, o serviço poderia ser integrado ao ecossistema do BB e utilizar dados de outras instituições via Open Finance mediante consentimento. A prova de conceito avalia compreensão do risco, correção dos cálculos, controle de ações e utilidade das recomendações; não promete resultados financeiros ou eficácia antifraude ainda não medidos.

## Declaração tecnológica: estado atual

O protótipo usa Python com biblioteca padrão, interface HTML/CSS/JavaScript, cenários sintéticos e ferramentas determinísticas para projeção de caixa, comparação de compra e sinais ilustrativos de risco. Há um adaptador REST opcional para IBM watsonx.ai, que solicita a seleção de ferramentas e valida a saída contra uma lista permitida. A chamada real ao serviço IBM ainda precisa ser testada na conta provisionada da equipe. Não há implantação watsonx Orchestrate, RAG semântico nem conexão bancária real.

**O uso do IBM Bob não foi comprovado nesta preparação.** Antes da entrega, substituir este parágrafo por uma descrição do trabalho efetivamente realizado com Bob, indicando tarefas, arquivos, testes, contribuições revisadas e links para as evidências em `bob_sessions/`. Não afirmar que Bob gerou esta base.

## Campos que só a equipe pode finalizar

Link do vídeo; link do protótipo publicado; membros já registrados; identificação da equipe na plataforma; modelo e região realmente utilizados; resultados da avaliação; capturas reais do Bob. Nenhum desses dados foi inventado.
