# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Principal: analista de negócios de uma agência do Banco do Brasil.** Uma vez por semana decide quais clientes de pessoa física da carteira os gerentes devem procurar. Faz isso no escritório da agência, entre outras tarefas. Hoje a triagem depende de olhar cliente por cliente e não cabe na semana.

**Secundário: gerente de relacionamento.** Recebe a lista da analista, abre cada caso e conversa com o cliente. Precisa chegar à conversa com o calendário de saldo, o pior dia, as hipóteses e uma alternativa já calculada.

As duas personas (Carla e Marcos na documentação) são hipotéticas. Ainda não foram validadas com funcionários do BB.

## Product Purpose

O Elo encontra, na carteira da agência, quem vai ficar sem dinheiro antes do próximo recebimento, a tempo de o gerente ligar antes do problema.

**Sucesso:** o cliente é procurado antes do primeiro saldo negativo. Na carteira sintética, o aviso chega com mediana de 7 dias de antecedência. O tempo de triagem da analista é um ganho secundário e ainda não foi medido.

## Positioning

Um agente que a analista consulta em português sobre a carteira inteira, com o mesmo cálculo que o gerente vê no atendimento do cliente. O IBM watsonx.ai só interpreta a pergunta e escolhe ferramentas; saldos, prazos e propostas vêm sempre do código, e a tela diz quem interpretou cada pergunta. O agente não oferece crédito.

## Operating Context

- Proposta acadêmica da equipe Fatec Ferraz Heal para a Trilha 1 do IBM SkillsBuild AI Experiential Learning Lab Brasil (Serviços Financeiros Digitais Inteligentes com Banco do Brasil), finalização #17.
- Fluxo: a analista pergunta sobre a carteira, monta a lista de contatos da semana e exporta em CSV; o gerente abre cada cliente no atendimento, o cliente aprova, ajusta ou recusa a proposta, e o desfecho volta para a lista.
- Duas telas: visão do analista (`/analista`) e atendimento ao cliente (`/`), mais uma apresentação embutida para banca e vídeo.
- A avaliação é feita por avaliadores do programa, que leem o repositório, o vídeo de até 3 minutos e a declaração técnica.

## Capabilities and Constraints

- Dados sempre sintéticos: carteira de 40 clientes de uma agência fictícia (`data/carteira.json`) e três cenários de atendimento. Nenhuma conexão bancária, transferência, oferta de crédito ou confirmação de fraude.
- Só entram na análise clientes com consentimento de compartilhamento, no modelo do Open Finance.
- Nada é executado sem aprovação explícita; uma despesa nova invalida a aprovação anterior.
- IBM watsonx.ai com contingência por regras. A chamada real na conta do programa ainda não foi comprovada.
- IBM Bob é a ferramenta de desenvolvimento da equipe. IBM watsonx Orchestrate e IBM Consulting Advantage não são usados.
- Servidor Python com biblioteca padrão, sessões em memória, política de segurança de conteúdo restrita à própria origem.
- **Em aberto:** publicação em URL pública, vídeo novo, medição com analistas reais, uso de dados reais (só com parceria e avaliação de LGPD).

## Brand Commitments

- Nome provisório **Elo Financeiro**; logo em `assets/logo-elo-financeiro.png`. A identidade visual parte desse logo (marinho e amarelo).
- Nenhum logotipo oficial do Banco do Brasil ou da IBM. Sem simular afiliação oficial.
- Voz: português do Brasil, prosa natural, sem travessão, sem jargão de marketing e sem frases genéricas de IA. Escrever como alguém da equipe escreveria.
- Honestidade sobre o estado: toda métrica tem fonte, método declarado ou a marca [SUPOSIÇÃO A VALIDAR].

## Evidence on Hand

- Carteira sintética e números medidos nela: 15 de 37 clientes em risco, 6 resolvíveis com ajuste, aviso com mediana de 7 dias, análise em cerca de 3 ms (`docs/PROPOSTA.md`).
- Testes automatizados: 264 em Python e 43 de interface (`docs/VERIFICACAO.md`).
- Cinco sessões reais do IBM Bob com registro, captura e commits (`bob_sessions/`).
- **Não existem e não devem ser inventados:** depoimentos, clientes ou funcionários reais, resultados com usuários, chamada real ao watsonx.ai comprovada, URL pública, parceria com o BB.

## Product Principles

1. Avisar antes do aperto vale mais do que explicar depois.
2. Os números são do código; o modelo interpreta, nunca calcula.
3. O cliente decide: nada acontece sem aprovação, e aprovação antiga não cobre cenário novo.
4. Consentimento primeiro: quem não consentiu não aparece.
5. Mostrar o que é medido e o que é suposição, sempre separados.

## Accessibility & Inclusion

Meta: WCAG 2.2 nível AA. Já existem navegação por teclado, foco visível, rótulos, mensagens de estado, opção de ampliar texto, layout de celular e respeito a "reduzir movimento". A avaliação com leitores de tela e com participantes ainda não foi feita.
