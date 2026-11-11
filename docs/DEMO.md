# Roteiro de demonstração: até três minutos

Objetivo: mostrar o problema da analista de negócios da agência, o agente respondendo em português sobre a carteira, o caso aberto no atendimento do gerente e o IBM Bob operando de verdade no desenvolvimento. Duração total: 180 segundos, com mais de 90 segundos de software.

## Preparação antes de gravar

1. Rodar uma sessão real do Bob com o Prompt 11 ou 12 de `docs/USO_DO_BOB.md` e gravar a tela enquanto ele trabalha. Esse trecho entra nas cenas do Bob. Não usar captura de ensaio.
2. Executar `python -m elo.server` na raiz do projeto e abrir `http://127.0.0.1:8000/analista`.
3. Se as credenciais IBM estiverem configuradas no terminal (com `ELO_PLANNER=watsonx`), o selo da tela diz "IBM watsonx.ai". Sem elas, diz "regras locais". Gravar com o que estiver ativo e falar o que o selo mostra.
4. Fechar outros programas e notificações. Nenhuma chave, e-mail ou dado pessoal pode aparecer na tela.

## Cenas e narração

| Tempo | Tela e ação | Narração |
| --- | --- | --- |
| 0 a 15 s | Bob IDE com o repositório aberto, executando o Prompt 11 ou 12: arquivos sendo lidos e tarefas na lista. | "O Elo Financeiro foi construído com o IBM Bob em modo Agent. Aqui ele está lendo a carteira e o código da visão do analista para [dizer o que a sessão real está fazendo]." |
| 15 a 30 s | Visão do analista carregada: título com "15 clientes precisam de atenção" e os três números. | "Carla é analista de negócios de uma agência do Banco do Brasil. Toda semana ela precisa dizer aos gerentes quem procurar antes que o cliente fique sem dinheiro. Cliente por cliente, isso leva horas; é uma estimativa nossa que ainda vamos medir com analistas." |
| 30 a 55 s | Digitar "Quais clientes ficam no vermelho nos próximos 7 dias?" e enviar. Mostrar a resposta, a linha "Como respondi" e o selo. | "Ela pergunta em português. O agente analisa os 37 clientes que deram consentimento e responde: seis ficam negativos nos próximos sete dias. A linha de baixo mostra quem interpretou a pergunta, aqui [o IBM watsonx.ai / as regras locais], e quanto tempo levou: poucos milissegundos. Os números vêm sempre do cálculo, não do modelo." |
| 55 a 70 s | Clicar em "Quem resolve com ajuste?". Mostrar os 6 clientes. | "Ela separa os casos simples: seis clientes se resolvem só reduzindo gastos flexíveis já previstos. Os outros vão precisar de uma conversa mais longa." |
| 70 a 80 s | Clicar em "Abrir no atendimento" no Cliente 06. | "Marcos, o gerente, abre o Cliente 06 direto na tela de atendimento." |
| 80 a 110 s | Clicar em **Autorizar dados da demonstração**. Mostrar o selo do planejador, o menor saldo de −R$ 120,00 em 11/10 e o gráfico. | "Saldo de mil duzentos e noventa reais hoje, mas as contas deixam o saldo negativo no dia dez, daqui a três dias, e o pior ponto é menos cento e vinte, no dia onze. O aviso chega antes do problema." |
| 110 a 130 s | Mostrar a proposta: reduzir R$ 230,00 de gastos flexíveis, menor saldo passa a R$ 110,00. Clicar em **Ativar plano de gastos**. | "O agente propõe reduzir duzentos e trinta reais de gastos flexíveis previstos. O menor saldo passa a cento e dez, que é a margem do cliente. Nada é movimentado; o gerente aprova com o cliente." |
| 130 a 145 s | Clicar em **Simular nova despesa**. Mostrar a projeção recalculada. | "Se aparece uma despesa nova, a projeção é refeita e a aprovação anterior deixa de valer. Uma autorização antiga não cobre um cenário diferente." |
| 145 a 160 s | Abrir **Por que o Elo sugeriu isso** e a trilha da sessão. | "Cada número tem hipótese e limite visíveis, e a trilha registra consultas e aprovações. Clientes sem consentimento nem entram na análise." |
| 160 a 172 s | Voltar ao Bob: relatório final da sessão gravada e os testes passando. | "De volta ao Bob: [dizer o resultado real, por exemplo quantas perguntas o agente acertou ou quantos testes foram criados]. Todas as sessões estão registradas com commits no repositório." |
| 172 a 180 s | Encerrar na visão do analista. | "Elo Financeiro: a carteira inteira numa conversa, e o contato com o cliente antes do aperto." |

## Pontos de precisão

- Os números da carteira (15 em atenção, 6 negativos em 7 dias, 6 que se resolvem) e do Cliente 06 vêm de `data/carteira.json`. Se a carteira for regerada, conferir de novo antes de gravar.
- Dizer "estimativa" para o tempo da triagem manual. O tempo do agente é medido e aparece na tela.
- Ler o selo como ele está. Se disser "regras locais", não dizer que é o watsonx.
- Na cena do Bob, só mostrar uma sessão real e só narrar o que aconteceu nela. A visão do analista não foi construída com o Bob; não dizer isso no vídeo.
- Não anunciar hospedagem publicada se ela ainda não existir; dizer "execução local".

## Conferência após gravar

1. Duração entre 170 e 180 segundos.
2. Os valores −R$ 120,00, R$ 230,00 e R$ 110,00 legíveis na tela.
3. O selo e a linha "Como respondi" legíveis pelo menos uma vez.
4. O Bob trabalhando aparece por pelo menos 20 segundos no total.
5. Publicar o vídeo, testar o link em janela anônima e preencher `docs/INSCRICAO.md`.
