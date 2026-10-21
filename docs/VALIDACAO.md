# Requisitos e validação

## Requisitos do MVP

| ID | Requisito | Critério de aceite | Estado |
| --- | --- | --- | --- |
| RF01 | Ler apenas após consentimento demonstrativo | Sem autorização, não retorna análise financeira | Implementado/testado |
| RF02 | Antecipar falta de caixa | Detecta saldo negativo antes da entrada, mesmo com saldo final positivo | Implementado/testado |
| RF03 | Explicar o calendário | Exibe todos os fechamentos diários e destaca o menor saldo no gráfico e na tabela | Implementado; cálculos testados |
| RF04 | Oferecer plano viável | Reduz somente previsões flexíveis e informa quando a margem não é atingida | Implementado/testado |
| RF05 | Solicitar aprovação específica | Vincula ação ao relatório vigente | Implementado/testado |
| RF06 | Acompanhar mudança | Nova despesa atualiza projeção e recomendação | Simulação implementada/testada |
| RF07 | Comparar uma compra | Expõe impacto à vista e limite da simulação parcelada | Implementado/testado |
| RF08 | Explicar sinais de risco | Exibe motivos sem afirmar confirmação de fraude | Regras sintéticas implementadas |
| RF09 | Revogar leitura | Oculta relatório e limpa planos desta sessão | Implementado/testado |
| RF10 | Usar IA na seleção de ferramentas | Chamada IBM real e plano validado em casos inéditos | Adaptador pronto; validação pendente |
| RF11 | Permitir ajuste ou recusa explícita | Usuário consegue alterar proposta e registrar recusa | Backlog |
| RF12 | Mostrar uso real do Bob | Capturas/relatórios da equipe no repositório | Pendente |
| RF13 | Recuperar orientações relacionadas | Conceitos/sinônimos e similaridade local, com fallback por tópico e limites visíveis | Implementado/testado em paráfrases sintéticas |
| RF14 | Explicar cada decisão | Números em centavos, hipóteses e itens não considerados | Implementado/testado |
| RF15 | Mostrar a trilha da sessão | Consultas, autorizações e revogações, sem apagar o registro ao revogar | Implementado/testado; retenção temporária |
| RF16 | Facilitar leitura e operação | Teclado, rótulos, foco, ampliação de texto e estados de carregamento/erro | Implementado; avaliação assistiva pendente |
| RF17 | Preparar demo pública sintética | Origem exata, expiração, limites de recursos, cabeçalhos e Dockerfile | Controles implementados; deploy externo pendente |

## Requisitos de qualidade

Valores em centavos, estados explícitos, isolamento de sessões e contingência identificada estão implementados. A interface oferece navegação por teclado, atalho para o conteúdo, foco visível, rótulos, ampliação de texto, tabela com cabeçalhos, gráfico com descrição e mensagens de carregamento/erro. O menor saldo tem indicação textual, além da cor. O botão de simulação fica desativado após o uso.

Esses recursos não constituem certificação de acessibilidade. Evidências de navegador e testes efetivamente executados ficam em [Verificação](VERIFICACAO.md); avaliação com leitores de tela e participantes continua pendente.

O servidor tem expiração por inatividade, limites de sessões/requisições/workers, verificação de origem e cabeçalhos de segurança. O modo público recusa chamadas IBM e exige proxy HTTPS. Esses controles se destinam a dados sintéticos; autenticação bancária, persistência, conformidade, disponibilidade e capacidade de carga de produção não foram demonstradas. A imagem Docker e o deploy externo ainda precisam ser executados.

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

Os testes automatizados de domínio, HTTP, recuperação e adaptador verificam comportamentos específicos. A contagem atual aparece na execução de `python -m unittest discover -s tests -v`; o CI também executa Ruff, instalado somente como ferramenta de desenvolvimento. Consulte [Verificação](VERIFICACAO.md) para resultados e ambiente. Os testes não demonstram a acurácia de um LLM, classificação de fraude, aceitação por clientes ou retorno financeiro para o banco.

Já há regressões para saldo zero, múltiplas contas flexíveis no mesmo dia, renda além do horizonte, aprovação de relatório realmente desatualizado por HTTP, revogação no fluxo, respostas IBM malformadas e falhas de rede simuladas. As explicações são comparadas aos cálculos e a recuperação cobre paráfrases simples, ausência de correspondência e URLs inseguras. Esses casos não substituem avaliação independente.

## Pesquisa exploratória

Recrutar cinco pessoas adultas com perfis de experiência digital diferentes. Apresentar cenários fictícios; não coletar identificação, contas, extratos, renda real ou dados de clientes. A pesquisa precisa respeitar as regras do programa e o consentimento para participação.

Tarefas: descobrir a data do menor saldo, explicar uma proposta, aceitar ou recusar, revogar a leitura, comparar uma compra e descrever o limite do alerta PIX. Registrar apenas resultados e observações anônimos.

Perguntas: "O que você acha que vai acontecer se aprovar?", "Esse dinheiro está garantido?", "Quais informações faltam para decidir?", "Em qual momento o alerta seria útil?", "Você sentiu que havia pressão para contratar um produto?"

Comparar o tempo e os erros com o mesmo cenário apresentado em uma tela simples de saldo e compromissos. Não generalizar resultados de cinco testes para toda a população.

## Casos que ainda devem entrar na avaliação

Além das regressões automatizadas, avaliar em casos inéditos: renda variável e ausência de renda confirmada; pouca flexibilidade no orçamento; compromissos depois do horizonte; parcelas com juros; múltiplas contas; dados desatualizados; falta de contexto; sinais de PIX insuficientes; preferência por não receber alertas; ferramentas indisponíveis; tentativas de instrução maliciosa no contexto do planejador. Parcelas com juros e múltiplas contas não são capacidades implementadas nesta versão.

Usar um conjunto separado do que foi usado para escrever prompts e regras. Medir seleção de ferramentas e adequação das recomendações, não só se o JSON é válido.
