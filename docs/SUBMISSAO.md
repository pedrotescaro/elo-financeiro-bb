# Problema e solução

Texto para revisão da equipe antes de copiar para o formulário. Não representa uma submissão enviada.

O gerente de relacionamento do Banco do Brasil atende clientes que chegam à agência ou ao chat depois de já ter enfrentado o problema: saldo zerou antes do recebimento, parcelamento comprometeu a margem do mês, ou um PIX urgente gerou dúvida sobre a segurança. Reconstruir o cenário financeiro desse cliente durante o atendimento (identificar quando o aperto vai acontecer, qual gasto contribuiu e qual ajuste é viável) consome tempo e depende de dados que nem sempre estão organizados de forma legível. O Elo Financeiro propõe um agente que faz essa análise com antecedência, apresenta o calendário de saldo diário e sugere uma ação com efeito calculado, antes que o cliente precise ligar.

A demonstração usa três cenários sintéticos. No primeiro, o saldo começa em R$ 1.500, mas compromissos futuros levam o menor saldo a menos R$ 100 antes do recebimento. O agente identifica esse ponto, propõe reduzir R$ 300 em gastos flexíveis previstos e, após aprovação, o menor saldo passa a R$ 200. Uma nova despesa de R$ 150 atualiza a projeção para R$ 50, e o sistema avisa que um novo plano é necessário. No segundo cenário, a comparação de um celular de R$ 3.500 com o calendário de contas mostra o impacto à vista, o efeito da primeira parcela e a opção de criar uma meta. No terceiro, sinais ilustrativos em um PIX (destinatário novo, valor atípico, mensagem de urgência) levam o agente a orientar uma verificação antes de prosseguir.

O gerente usa o agente para preparar o atendimento: em vez de montar o calendário manualmente, abre a análise já calculada, confere as hipóteses e os limites, e parte para a conversa com o cliente. O tempo de preparação por atendimento passa de estimados quinze a vinte minutos para dois a três minutos. Essa estimativa é uma suposição de trabalho a validar com gerentes reais; não é um resultado medido.

A equipe usou o IBM Bob em modo Agent em cinco sessões de dois integrantes: projeção das parcelas de uma compra, redução personalizada com prévia no servidor, correção do fluxo de propostas, trinta casos de validação IBM e a revisão desta proposta. Cada sessão tem registro, captura e commits em `bob_sessions/`.

## Tecnologia e limites

Python 3.11 com biblioteca padrão executa os cálculos em centavos inteiros e controla permissões. HTML, CSS e JavaScript compõem a interface. O modo padrão é determinístico e não requer dependências externas.

O adaptador opcional IBM watsonx.ai autentica no IBM IAM, envia o cenário ao modelo Granite configurado e recebe a seleção de ferramentas permitidas. Cálculos e permissões permanecem no código Python; o modelo não executa operações financeiras. Falhas de rede, configuração incompleta ou resposta inválida ativam a contingência por regras, identificada na interface. Um selo no topo da análise mostra quem planejou. Os testes com respostas simuladas passam; a chamada real na conta do programa ainda precisa ser executada com `python -m elo.prova_watsonx`, que grava a evidência sem chaves.

Não há conexão bancária, transferência, contratação de crédito ou confirmação de fraude. Os cenários são sintéticos. A efetividade com clientes reais, a integração com sistemas do BB e os resultados financeiros dependem de avaliação e parceria que vão além deste protótipo acadêmico.
