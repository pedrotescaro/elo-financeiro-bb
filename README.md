<p align="center">
  <img src="assets/logo-elo-financeiro.png" alt="Logo do Elo Financeiro" width="460" />
</p>

# Elo Financeiro

**Sua próxima decisão, com mais clareza.**

Proposta acadêmica para a **Trilha 1 do IBM SkillsBuild AI Experiential Learning Lab: Serviços Financeiros Digitais Inteligentes, Seguros e Inclusivos com Banco do Brasil**.

O Elo propõe um agente que antecipa apertos de caixa, explica o impacto de decisões e acompanha planos aprovados. Seu objetivo central é **preservar uma margem financeira até o próximo recebimento**. Na proposta atual, quem usa o agente é o gerente de relacionamento do BB, ao preparar o atendimento de um cliente; os dados são sempre sintéticos.

O saldo de hoje pode parecer suficiente, mesmo quando as contas dos próximos dias vão deixá-lo negativo. O Elo considera o calendário: identifica o problema antes do vencimento, consulta ferramentas de cálculo e orientação, apresenta alternativas e acompanha o resultado de uma ação autorizada.

> Status: protótipo executável com dados sintéticos, 233 testes Python e 36 de interface, e pacote para hospedagem demonstrativa. O stakeholder é o gerente de relacionamento do BB. Cinco sessões do IBM Bob, de dois integrantes, estão documentadas com commits e capturas. A chamada IBM real, a publicação e o vídeo novo continuam pendentes. O que mudou depois do feedback está em [Resposta ao feedback](docs/RESPOSTA_AO_FEEDBACK.md). Não é uma integração oficial do Banco do Brasil nem uma entrega IBM finalizada.

## Executar localmente

Requisito: Python 3.11 ou superior. Não há dependências externas no modo de demonstração.

```bash
git clone https://github.com/pedrotescaro/elo-financeiro-bb.git elo-financeiro
cd elo-financeiro
python -m elo.server
```

Abra **http://127.0.0.1:8000**. Não é necessário instalar pacotes. A sessão existe apenas na memória, expira após 30 minutos sem uso e é descartada ao reiniciar o servidor.

Para explicar a proposta, clique em **Apresentar a ideia**. A apresentação percorre problema, proposta, jornada prática e tecnologias, com navegação pelos tópicos ou pelas setas do teclado. **Demonstrar na prática** abre o cenário real; a leitura dos dados continua dependendo da autorização na interface. **Reiniciar cenário** restaura os dados fictícios e limpa os planos, mantendo o consentimento atual.

Os textos dos campos da competição estão em [Inscrição](docs/INSCRICAO.md), e a narração sugerida está em [Roteiro](docs/DEMO.md).

```bash
python -m unittest discover -s tests -v
```

Para comprovar a chamada real ao IBM watsonx.ai, configure as variáveis da seção "Conectar o planejador IBM" e rode `python -m elo.prova_watsonx`. A evidência vai para `docs/evidencias/watsonx/`, sem chave nem token.

## O que está pronto

| Capacidade | Situação |
| --- | --- |
| Três cenários e interface responsiva em português | Implementados |
| Projeção de caixa por fechamento diário | Todos os dias do horizonte, gráfico com o menor saldo e tabela; centavos inteiros |
| Consentimento demonstrativo e revogação | Implementados por sessão |
| Plano de redução de gastos flexíveis | Implementado; depende de aprovação; valor ajustável pelo gerente |
| Aprovação vinculada à versão dos dados | Implementada; rejeita plano desatualizado; versionamento por `preview_id` |
| Recusa explícita de proposta | Implementada; cancela a prévia vinculada |
| Simulação de compra e criação de meta | Implementadas; parcelas projetadas dentro do horizonte, sem juros |
| Sinais ilustrativos de risco em PIX | Implementados por regras; sem detecção validada |
| Reavaliação após nova despesa | Implementada; evento simulado pela interface |
| Planejador IBM watsonx.ai | Adaptador REST testado com respostas simuladas; selo no topo da análise mostra quem planejou; `python -m elo.prova_watsonx` grava a evidência da chamada real. A chamada real com credenciais do programa ainda não foi executada |
| Recuperação de orientações | Conceitos e sinônimos curados, incluindo termos coloquiais, mais similaridade TF-IDF local; busca por tópico como contingência; sem embeddings nem geração de respostas |
| Explicações e trilha da sessão | Números, hipóteses, exclusões, consultas, autorizações e revogações visíveis |
| Recursos de acesso | Teclado, foco visível, rótulos, mensagens de estado e opção de ampliar texto; avaliação com leitores de tela pendente |
| Controles da demonstração pública | Expiração, limites de recursos, origem restrita e cabeçalhos; Dockerfile e guia de deploy preparados; execução da imagem e deploy externos pendentes |
| IBM Bob | Cinco sessões (28/10 a 11/11/2026) com registro, captura e commits em `bob_sessions/`, conferidas com `git log`; falta o parágrafo de revisão de cada integrante |
| Stakeholder e caso de uso | Gerente de relacionamento do BB definido como stakeholder; caso de uso com baseline e meta; métricas marcadas como [SUPOSIÇÃO A VALIDAR] |
| Declaração técnica dos produtos IBM | `docs/DECLARACAO_TECNICA.md` criado com produtos, finalidades, arquivos e estado de validação |
| Dossiê de apresentação | `docs/DOSSIE.md` criado com onze slides em sequência definida |
| Roteiro do vídeo com Bob operando | `docs/DEMO.md` reescrito com cena do Bob no início e no encerramento; vídeo novo ainda não gravado |
| Resposta ao feedback | `docs/RESPOSTA_AO_FEEDBACK.md` criado com rastreabilidade ponto a ponto |
| BB / Open Finance / pagamentos / crédito | Integrações de produção fora deste protótipo |
| Publicação acessível aos avaliadores | Pendente; guia em `docs/DEPLOY.md` e checklist em `docs/PLANO_TECNICO.md` |
| Vídeo gravado e publicado | Pendente |
| Chamada IBM real executada | Pendente; rodar `python -m elo.prova_watsonx` com credenciais (passos em `docs/PLANO_TECNICO.md`) |

## Três jornadas com uma mesma finalidade

1. **Previsibilidade:** R$ 1.500 de saldo atual, compromissos antes do recebimento e uma previsão de -R$ 100. O usuário autoriza reduzir R$ 300 de lazer previsto, e o menor saldo passa a R$ 200. Uma nova despesa de R$ 150 reduz essa margem para R$ 50.
2. **Decisão de compra:** um celular de R$ 3.500 é comparado com o calendário de contas. A interface apresenta impacto à vista, efeito da primeira parcela de um exemplo sem juros e a alternativa de criar uma meta.
3. **Decisão protegida:** uma intenção de PIX reúne sinais sintéticos de urgência, destinatário novo e valor atípico. O agente orienta a conferir; o protótipo não realiza nem bloqueia o pagamento.

## Por que a proposta envolve IA agêntica

O produto pretendido trabalha com um objetivo persistente, ferramentas especializadas, autorização, estado e replanejamento após eventos. A IA deve selecionar consultas e combinar contexto para propor um próximo passo, com cálculos e permissões validados fora do modelo.

**O modo padrão deste código é uma base determinística para demonstrar a jornada.** Não deve ser apresentado como raciocínio generativo ou como sistema multiagente completo. O adaptador opcional permite um modelo IBM escolher uma lista limitada de ferramentas; o próximo marco é validar esse funcionamento na conta da equipe e ampliar a avaliação. Leia [Arquitetura](docs/ARQUITETURA.md).

## Conectar o planejador IBM

Use o projeto e um modelo Granite realmente disponíveis na conta do programa. Configure as variáveis de `.env.example` no terminal. O arquivo não é carregado automaticamente. Não salve chaves em commits.

Exemplo Linux/macOS, com valores obtidos pela equipe:

```bash
export ELO_PLANNER=watsonx
export IBM_CLOUD_API_KEY='sua-chave'
export WATSONX_PROJECT_ID='seu-projeto'
export WATSONX_MODEL_ID='modelo-granite-disponivel'
export WATSONX_URL='https://us-south.ml.cloud.ibm.com'
python -m elo.server
```

No PowerShell, configure cada variável com `$env:NOME='valor'`. O endpoint precisa corresponder à região da conta. Sem configuração, o código não faz chamadas externas. Com o adaptador ativado localmente, somente cenários sintéticos são enviados à IBM. Configuração ausente, falha de rede ou resposta fora do contrato ativam a contingência por regras, identificada na interface. Os testes do adaptador usam respostas simuladas; não comprovam uma chamada IBM real.

O modo público, definido por `ELO_PUBLIC_ORIGIN`, recusa o planejador externo para impedir consumo anônimo da conta IBM. Não colocar credenciais IBM na hospedagem demonstrativa.

## Verificar e hospedar

O comando de testes acima usa apenas a biblioteca padrão. O lint é uma ferramenta de desenvolvimento: `python -m pip install ruff==0.16.0`, seguido de `python -m ruff check elo tests`. O GitHub Actions executa lint e testes a cada push e pull request; os resultados efetivos desta revisão ficam em [Verificação](docs/VERIFICACAO.md).

Para hospedar os cenários sintéticos atrás de HTTPS, siga [Deploy](docs/DEPLOY.md). O pacote inclui Dockerfile sem dependências Python externas e usuário sem privilégios. A execução da imagem e o deploy externo ainda precisam ser realizados pela equipe; não existe URL pública validada nesta preparação.

## Documentação do projeto

- [Proposta completa, stakeholder e métricas](docs/PROPOSTA.md)
- [Arquitetura, ferramentas e fronteiras de autonomia](docs/ARQUITETURA.md)
- [Requisitos, métricas e validação](docs/VALIDACAO.md)
- [Cronograma até a entrega e backlog](docs/ROADMAP.md)
- [Texto do problema e da solução, para o formulário](docs/SUBMISSAO.md)
- [Declaração técnica dos produtos IBM usados](docs/DECLARACAO_TECNICA.md)
- [Roteiro de demonstração de até três minutos](docs/DEMO.md)
- [Uso do IBM Bob: evidências, prompts e mapeamento](docs/USO_DO_BOB.md)
- [Como registrar evidências reais do Bob](bob_sessions/README.md)
- [Dossiê de apresentação em slides](docs/DOSSIE.md)
- [Resposta ao feedback do avaliador](docs/RESPOSTA_AO_FEEDBACK.md)
- [Plano de validação IBM, RAG e publicação](docs/PLANO_TECNICO.md)
- [Checklist final e pendências da equipe](docs/ENTREGA.md)
- [Publicar a demonstração sintética](docs/DEPLOY.md)
- [Referências e limites da fundamentação](docs/REFERENCIAS.md)

## Estrutura

```text
elo/          Cálculos e coordenação em core.py; recuperação, servidor e adaptador IBM
web/          Interface da demonstração
data/         Cenários sintéticos e orientações curadas
tests/        Verificações de cálculos, consentimento e aprovação
docs/         Proposta, arquitetura, pesquisa e entrega
bob_sessions/ Registros e capturas das sessões reais do IBM Bob
```

## Limites e próximos passos

O servidor suporta uma demonstração sintética com controles limitados de exposição: até 100 sessões, expiração por inatividade, limite de requisições e workers, cookie seguro no modo público e validação da origem. Deve ficar atrás de um proxy HTTPS, conforme o [guia de deploy](docs/DEPLOY.md). Esses controles não demonstram resistência a DDoS, disponibilidade ou segurança bancária de produção.

Não há identidade bancária, persistência, conexão Open Finance ou movimentação financeira. A trilha visível registra até 200 eventos da sessão e desaparece ao expirar ou reiniciar; não é uma auditoria de produção. As orientações vêm de uma base pequena, carregada na inicialização, sem atualização automática das fontes.

Os relatórios são estimativas com entradas conhecidas, não previsões treinadas. O ajuste modifica um orçamento futuro, não transações realizadas. Os três exemplos não demonstram eficácia contra fraude, redução de endividamento ou impacto em clientes reais.

O nome Elo Financeiro é provisório. A equipe deve verificar disponibilidade de marca antes de qualquer lançamento comercial. Este projeto não utiliza logotipos oficiais do BB ou da IBM.
