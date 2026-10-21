# Problema e solução

Texto preparado para revisão da equipe; não representa uma submissão realizada.

O Elo Financeiro é uma proposta acadêmica para a trilha de serviços financeiros digitais do Banco do Brasil. Seu objetivo é ajudar a pessoa a entender se o dinheiro disponível será suficiente até o próximo recebimento e a avaliar decisões com mais clareza.

O problema é que o saldo atual, sozinho, não mostra o efeito das contas e das entradas em datas diferentes. Uma pessoa pode ter dinheiro hoje e ficar sem margem antes de receber. A relevância dessa hipótese para pessoas em início de autonomia financeira ou com renda variável ainda precisa ser avaliada com usuários.

O protótipo apresenta três jornadas com dados sintéticos: antecipar falta de saldo, comparar uma compra e conferir sinais ilustrativos de risco em um PIX. Após autorizar a leitura, a pessoa vê o calendário, um gráfico diário e o menor saldo previsto. Pode consultar os números usados, as hipóteses e o que ficou fora da análise.

Quando há gastos flexíveis, o Elo apresenta um ajuste de orçamento e seu efeito. O plano depende de aprovação vinculada à versão dos dados. Uma nova despesa simulada atualiza a projeção. Também é possível registrar uma meta de compra e revogar a leitura, limpando os planos da sessão. A trilha temporária mostra consultas, autorizações e revogações.

As orientações vêm de uma pequena base curada, com recuperação local por conceitos, sinônimos e similaridade de termos. A interface usa português simples e inclui navegação por teclado e ampliação de texto. Esses recursos ainda precisam de avaliação com participantes e leitores de tela.

## Tecnologia e limites

Python com biblioteca padrão executa os cálculos em centavos e valida as permissões. HTML, CSS e JavaScript compõem a interface. O modo padrão é determinístico. O adaptador opcional IBM watsonx.ai permite selecionar ferramentas de uma lista limitada, com contingência por regras; a chamada real na conta da equipe ainda não foi validada.

O pacote inclui controles e instruções para uma demonstração pública sintética, mas o deploy não foi realizado. O uso central do IBM Bob e suas evidências também permanecem pendentes.

Não há conexão bancária, transferência, contratação de crédito ou confirmação de fraude. A compra parcelada considera apenas a primeira parcela no horizonte. Não foram medidos resultados financeiros ou eficácia antifraude. O projeto não é um produto oficial do Banco do Brasil nem uma entrega IBM concluída.

Antes de enviar, a equipe deve comprovar o trabalho real no Bob, validar a tecnologia IBM, avaliar a jornada, publicar a demonstração e informar os links do protótipo e do vídeo.
