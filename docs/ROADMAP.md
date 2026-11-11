# Roadmap

Revisão de 11 de novembro de 2026. Confirmar na plataforma do programa o prazo de reenvio antes de distribuir as tarefas.

## Estado atual

| Frente | Situação |
| --- | --- |
| Visão do analista (carteira, perguntas, lista de contatos, CSV) | Pronta e testada |
| Atendimento ao cliente (projeção, proposta, aprovação, reavaliação, compra, PIX) | Pronto e testado |
| IBM watsonx.ai (interpretar perguntas e escolher ferramentas) | Implementado com contingência; chamada real pendente |
| IBM Bob | Cinco sessões registradas; sessões sobre a visão do analista pendentes |
| Documentação para o reenvio | Pronta; ver `RESPOSTA_AO_FEEDBACK.md` |
| Testes e CI | 264 testes Python e 43 de interface; lint limpo |
| Publicação | Pendente; Docker não estava ativo nesta máquina |
| Vídeo | Pendente; roteiro pronto |

## Antes do reenvio (P0)

| Ordem | Tarefa | Quem | Evidência de conclusão |
| --- | --- | --- | --- |
| 1 | Rodar no Bob os Prompts 11, 12 e 13 de `USO_DO_BOB.md`, gravando a tela | Equipe | Três pastas novas em `bob_sessions/` |
| 2 | Chamada real ao watsonx.ai (`python -m elo.prova_watsonx`) | Quem tiver as credenciais | JSON em `docs/evidencias/watsonx/` com `chamada_real_comprovada: true` |
| 3 | Parágrafo de revisão nos cinco registros do Bob | Pedro (3) e Guilherme (2) | Nenhum `[...]` restante nos registros |
| 4 | Publicar a demonstração (Render, plano gratuito) | Equipe | URL HTTPS testada em janela anônima, registrada em `VERIFICACAO.md` |
| 5 | Gravar e publicar o vídeo com `DEMO.md` | Equipe | Link aberto sem login |
| 6 | Atualizar números reais na declaração e no formulário e reenviar todos os entregáveis | Equipe | Confirmação de envio da plataforma |

## Depois do reenvio (P1)

- Cronometrar a triagem com 5 analistas voluntários, com a mesma carteira sintética, e substituir as suposições de tempo por medição.
- Ampliar o vocabulário das regras com as perguntas que falharam no gabarito do Prompt 11.
- Expor as funções do agente como ferramentas no IBM watsonx Orchestrate.
- Avaliar a interface com leitores de tela.

## Evolução do produto (P2)

- Perguntas por tendência e por produto; histórico de semanas anteriores.
- Recuperação semântica sobre normas internas, com fontes controladas.
- Dados reais via sistemas do banco e Open Finance, só com parceria, autorização e avaliação de LGPD.
- Integração da lista de contatos com a agenda e o CRM do gerente.

## O que não fazer

- Não declarar uso de watsonx Orchestrate ou Consulting Advantage sem uma integração real.
- Não apresentar [SUPOSIÇÃO A VALIDAR] como resultado.
- Não atribuir ao Bob trabalho que não foi feito em uma sessão registrada.
