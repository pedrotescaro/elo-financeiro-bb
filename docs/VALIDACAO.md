# Requisitos e validação

## Requisitos do MVP

| ID | Requisito | Critério de aceite | Estado |
| --- | --- | --- | --- |
| RF01 | Ler apenas após consentimento demonstrativo | Sem autorização, não retorna análise financeira | Implementado/testado |
| RF02 | Antecipar falta de caixa | Detecta saldo negativo antes da entrada, mesmo com saldo final positivo | Implementado/testado |
| RF03 | Explicar o calendário | Exibe datas, eventos e saldos calculados | Implementado |
| RF04 | Oferecer plano viável | Reduz somente previsões flexíveis e informa quando a margem não é atingida | Implementado/testado |
| RF05 | Solicitar aprovação específica | Vincula ação ao relatório vigente | Implementado/testado |
| RF06 | Acompanhar mudança | Nova despesa atualiza projeção e recomendação | Simulação implementada/testada |
| RF07 | Comparar uma compra | Expõe impacto à vista e limite da simulação parcelada | Implementado/testado |
| RF08 | Explicar sinais de risco | Exibe motivos sem afirmar confirmação de fraude | Regras sintéticas implementadas |
| RF09 | Revogar leitura | Oculta relatório e limpa planos desta sessão | Implementado/testado |
| RF10 | Usar IA na seleção de ferramentas | Chamada IBM real e plano validado em casos inéditos | Adaptador pronto; validação pendente |
| RF11 | Permitir ajuste ou recusa explícita | Usuário consegue alterar proposta e registrar recusa | Backlog |
| RF12 | Mostrar uso real do Bob | Capturas/relatórios da equipe no repositório | Pendente |

## Requisitos de qualidade

Valores em centavos, estados explícitos, isolamento de sessões e contingência identificada já estão implementados. A interface oferece controles semânticos, foco visível, tabela com cabeçalhos e mensagens de erro. Esses recursos não constituem certificação de acessibilidade; falta avaliar contraste e uso com leitor de tela e participantes.

Privacidade de produção, autenticação, retenção, disponibilidade, capacidade de carga e integração transacional ainda não estão implementadas. O servidor atual é para demonstração local.

## Métricas: metas propostas, não resultados

| Dimensão | Medida | Meta inicial de avaliação |
| --- | --- | --- |
| Cálculo | Casos sintéticos com saldo e datas exatos | 100% dos casos financeiros definidos |
| Controle | Ações sem consentimento/aprovação | Zero ações aceitas |
| Agente | Escolha correta de ferramentas em 30 casos inéditos | Pelo menos 90%; analisar cada falha |
| Recuperação | Falhas de modelo identificadas e sem ação financeira | 100% dos casos de falha injetados |
| Compreensão | Participante explica risco, hipótese e efeito da aprovação | Pelo menos 4 de 5 testes exploratórios |
| Usabilidade | Completar a jornada sem orientação do facilitador | Pelo menos 4 de 5 testes exploratórios |
| Clareza | Confundir saldo projetado com dinheiro garantido | Registrar qualquer ocorrência e revisar a interface |
| Tempo | Tempo até identificar o aperto | Comparar com uma tela de saldo/calendário convencional |
| Segurança | Falsos alertas e riscos omitidos nos casos anotados | Medir separadamente; sem meta de fraude real nesta POC |

Os 20 testes automatizados existentes verificam comportamentos específicos. Não demonstram a acurácia de um LLM, classificação de fraude, aceitação por clientes ou retorno financeiro para o banco.

## Pesquisa exploratória

Recrutar cinco pessoas adultas com perfis de experiência digital diferentes. Apresentar cenários fictícios; não coletar identificação, contas, extratos, renda real ou dados de clientes. A pesquisa precisa respeitar as regras do programa e o consentimento para participação.

Tarefas: descobrir a data do menor saldo, explicar uma proposta, aceitar ou recusar, revogar a leitura, comparar uma compra e descrever o limite do alerta PIX. Registrar apenas resultados e observações anônimos.

Perguntas: "O que você acha que vai acontecer se aprovar?", "Esse dinheiro está garantido?", "Quais informações faltam para decidir?", "Em qual momento o alerta seria útil?", "Você sentiu que havia pressão para contratar um produto?"

Comparar o tempo e os erros com o mesmo cenário apresentado em uma tela simples de saldo e compromissos. Não generalizar resultados de cinco testes para toda a população.

## Casos que ainda devem entrar na avaliação

Recebimento atrasado; ausência de renda confirmada; pouca flexibilidade no orçamento; cartão com vencimento depois do horizonte; parcelas com juros; múltiplas contas e transferências internas; dados desatualizados; falta de contexto; sinais de PIX insuficientes; preferência por não receber alertas; ferramentas indisponíveis; tentativa de instrução maliciosa dentro de um texto recuperado.

Usar um conjunto separado do que foi usado para escrever prompts e regras. Medir seleção de ferramentas e adequação das recomendações, não só se o JSON é válido.
