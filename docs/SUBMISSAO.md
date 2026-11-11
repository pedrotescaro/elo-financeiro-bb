# Problema e solução

Texto para revisão da equipe antes de copiar para o formulário. Não representa uma submissão enviada.

Numa agência do Banco do Brasil, o analista de negócios responsável por uma carteira de pessoas físicas precisa saber quais clientes vão ficar sem dinheiro antes do próximo recebimento, a tempo de o gerente de relacionamento ligar antes do problema. Hoje essa triagem depende de consultar cliente por cliente, montar o calendário de contas e decidir quem priorizar. Com dezenas de clientes, o contato acaba acontecendo depois do aperto, quando o cliente já entrou no negativo ou no crédito caro.

O Elo Financeiro é um agente de IA conversacional para esse analista. Ele pergunta em português ("quem fica no vermelho nos próximos 7 dias?", "quem resolve com ajuste de gastos?") e o agente analisa a carteira inteira. A demonstração usa uma carteira sintética de 40 clientes de uma agência fictícia, com saldo, compromissos futuros e consentimento de compartilhamento no modelo do Open Finance. Clientes sem consentimento ficam fora da análise. Dos 37 analisados, o agente aponta 11 com saldo negativo e 4 abaixo da margem nos próximos 14 dias, e mostra quais 6 se resolvem só com ajuste de gastos flexíveis. A análise da carteira leva poucos milissegundos, medidos e exibidos na tela. O ganho de tempo do analista em relação à triagem manual é uma estimativa a validar com analistas voluntários.

Cada cliente encontrado abre na tela de atendimento do gerente: calendário de saldo diário, menor saldo, hipóteses usadas e uma proposta de ajuste com efeito calculado. Nada acontece sem aprovação. Uma nova despesa recalcula a projeção, e a aprovação anterior deixa de valer. A mesma tela trata compra parcelada e sinais de risco em PIX.

O IBM watsonx.ai entra em dois pontos. Ele interpreta a pergunta do analista, transformando-a em uma consulta estruturada, e, na tela de atendimento, escolhe quais ferramentas do agente rodam para o cliente aberto. Saldos, prazos e propostas são sempre calculados pelo código, e um selo na tela mostra se quem interpretou foi o modelo ou as regras de contingência.

O IBM Bob foi a ferramenta de desenvolvimento da equipe em cinco sessões de dois integrantes: projeção de parcelas, redução personalizada com prévia no servidor, correção do fluxo de propostas, trinta casos de validação IBM e o diagnóstico do feedback. Cada sessão tem registro, captura e commits em `bob_sessions/`.

## Tecnologia e limites

Python 3.11 com biblioteca padrão calcula em centavos inteiros e controla permissões; a interface usa HTML, CSS e JavaScript sem dependências. O adaptador IBM watsonx.ai autentica no IBM Cloud IAM e usa a API de geração de texto com um modelo Granite da conta. Falhas, configuração ausente ou resposta fora do contrato ativam a contingência por regras. Os testes com respostas simuladas passam; a chamada real na conta do programa precisa ser comprovada com `python -m elo.prova_watsonx`.

Não há conexão bancária, transferência, oferta de crédito nem confirmação de fraude. Carteira e cenários são sintéticos. A efetividade com analistas e clientes reais e a integração com sistemas do BB dependem de avaliação e parceria além deste protótipo acadêmico.
