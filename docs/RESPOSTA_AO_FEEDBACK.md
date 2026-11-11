# Resposta ao feedback do avaliador

Este documento é o primeiro que um avaliador deve abrir para entender o que mudou após o feedback de "precisa de uma segunda olhada". Cada ponto do feedback original está listado com o que foi feito, qual arquivo foi alterado, e qual evidência verificar.

---

## Tabela de rastreabilidade

| Ponto do feedback | O que mudou | Arquivo(s) alterado(s) | Evidência |
| --- | --- | --- | --- |
| **Critério 1:** não demonstra como o projeto aborda produtividade pessoal e/ou da equipe | Definido stakeholder único (gerente de relacionamento do BB), caso de uso de ponta a ponta com baseline e meta, método de medição e marcação [SUPOSIÇÃO A VALIDAR] | `docs/PROPOSTA.md`, `docs/VALIDACAO.md` | Seção "Stakeholder e caso de uso" em VALIDACAO.md; seção "Caso de uso de ponta a ponta" em PROPOSTA.md |
| **Critério 2:** dossiê não demonstra isso com clareza | Criado dossiê com onze slides em sequência: problema → stakeholder → solução → Bob → watsonx → arquitetura → evidências → métricas → limites → próximos passos | `docs/DOSSIE.md` (novo) | Arquivo criado com título e conteúdo de cada slide |
| **Critério 3:** não fica claro como e onde o IBM Bob foi usado | Criado `docs/USO_DO_BOB.md` com a tabela das cinco sessões, o que cada uma produziu, 10 prompts prontos e instrução de gravação. Os quatro registros antigos foram conferidos com `git log` e tiveram datas, commits de partida e links corrigidos. Novo registro da sessão de 2026-11-11 | `docs/USO_DO_BOB.md` (novo), `bob_sessions/README.md`, `bob_sessions/*/registro.md`, `bob_sessions/2026-11-11-resposta-ao-feedback/` (novo) | Tabela "O que já foi feito" em USO_DO_BOB.md; cinco pastas em `bob_sessions/` com registro, captura e commits |
| **Área A:** protótipo não incorpora o IBM Bob nem aborda problemas de dados corporativos | Reposicionado como ferramenta de apoio ao atendimento do gerente do BB (não apenas finanças pessoais); stakeholder é corporativo; narrativa reescrita em SUBMISSAO.md e PROPOSTA.md | `docs/SUBMISSAO.md`, `docs/PROPOSTA.md` | Parágrafo do gerente em SUBMISSAO.md; seção de stakeholder em PROPOSTA.md |
| **Área A (continuação):** considerar redirecionar para solução de IA conversacional para analistas de negócio | Mantemos a Rota 1 (defender): o problema de produtividade do gerente de relacionamento é corporativo e mensurável. A trilha 1 abrange serviços financeiros digitais para o ecossistema do BB, não exclusivamente dados corporativos internos. | `docs/PROPOSTA.md` | Seção "Stakeholder: gerente de relacionamento do Banco do Brasil" |
| **Área B:** Bob não vinculado ao fluxo de trabalho principal para um stakeholder específico | O Bob aparece operando no vídeo (0 a 15 s e 153 a 172 s); o stakeholder é o gerente de relacionamento; o Prompt 7 leva a validação do watsonx.ai para dentro de uma sessão do Bob | `docs/DEMO.md`, `docs/USO_DO_BOB.md` | Cenas do Bob no roteiro; seção "Onde o modo Agent aparece nessas sessões" em USO_DO_BOB.md |
| **Área B (continuação):** adicionar caso de uso concreto com benefícios mensuráveis | Caso de uso com baseline (15-20 min), meta (2-3 min), método (cronometrar com gerentes voluntários) e amostra (5-10 gerentes, 3 cenários) adicionado | `docs/PROPOSTA.md`, `docs/VALIDACAO.md` | Tabela "Meta de desempenho" em PROPOSTA.md |
| **Área B (continuação):** demonstrar modo agente do Bob (ingestão de documentos, tarefas paralelas, subagentes) em fluxo completo | Prompt 10 em USO_DO_BOB.md demonstra explicitamente ingestão paralela de múltiplos documentos; instrução passo a passo para executar e gravar no vídeo | `docs/USO_DO_BOB.md` | Seção "Prompt 10" e "Como gravar uma sessão que apareça no vídeo" em USO_DO_BOB.md |
| **Área C:** declaração técnica deve nomear produtos IBM específicos e explicar como são usados | Criado `docs/DECLARACAO_TECNICA.md` com produto, finalidade, arquivo que chama e estado de cada item, e o passo a passo de como o watsonx.ai entra no fluxo | `docs/DECLARACAO_TECNICA.md` (novo), `docs/SUBMISSAO.md` | Tabela "Resumo" em DECLARACAO_TECNICA.md |
| **Área A e C:** watsonx.ai fora do fluxo principal e sem prova de chamada real | Selo do planejador no topo da análise; script `python -m elo.prova_watsonx` que grava `model_id`, `created_at` e latência devolvidos pela API, sem segredos; no modo real, os 30 casos só contam acerto quando quem respondeu foi o modelo | `web/index.html`, `web/app.js`, `web/style.css`, `elo/watsonx.py`, `elo/prova_watsonx.py` (novo), `tests/test_prova_watsonx.py` (novo), `tests/test_ibm_validation.py`, `tests/web_behaviors.cjs` | 233 testes Python e 36 de interface passando em 2026-11-11; a chamada real em si continua pendente |
| **Área A:** recuperação de orientações | Vocabulário da recuperação local ampliado com termos coloquiais; continua sem embeddings e assim está declarado | `elo/retrieval.py`, `tests/test_retrieval.py` | Três testes novos de paráfrase |

---

## Itens que ainda precisam de execução humana

Estes itens não foram e não podem ser resolvidos apenas com documentação. Estão aqui para que o avaliador saiba o que ainda falta e a equipe saiba o que executar antes do envio.

| Item | O que falta | Onde registrar |
| --- | --- | --- |
| Parágrafo de revisão nos registros do Bob | Pedro (três registros) e Guilherme (dois) escrevem, com as próprias palavras, o que conferiram em cada sessão. Os demais campos já estão preenchidos | `bob_sessions/*/registro.md`, seção "Revisão do integrante na época da sessão" |
| Chamada real ao watsonx.ai | Rodar `python -m elo.prova_watsonx` e `python -m unittest tests.test_ibm_validation -v` com credenciais reais, de preferência pelo Prompt 7 dentro do Bob | `docs/evidencias/watsonx/`, `docs/VERIFICACAO.md`, nova pasta em `bob_sessions/` |
| Commit e push | Commitar as mudanças de 2026-11-11 e publicar na `main` | Repositório público |
| Vídeo gravado e publicado | Seguir roteiro em `docs/DEMO.md`; publicar e testar link sem login | `docs/INSCRICAO.md` (campo URL do vídeo) |
| Deploy público no Render | Seguir `docs/DEPLOY.md`; registrar URL e commit | `docs/VERIFICACAO.md` |
| Formulário de submissão enviado | Preencher campos na plataforma IBM SkillsBuild e confirmar envio | `docs/ENTREGA.md` (checklist) |

---

## O que não mudou e por quê

| Decisão mantida | Motivo |
| --- | --- |
| Escopo de finanças pessoais do cliente | É o núcleo técnico que demonstra o ciclo agêntico; o reposicionamento para o gerente do BB mantém esse escopo como ferramenta de apoio ao atendimento, não como mudança de produto |
| Sem watsonx Orchestrate | Não foi utilizado; declarar uso falso é pior do que não declarar |
| Modo por regras como padrão da demonstração | O modo watsonx depende de credenciais que não ficam na demo pública; o modo por regras é honesto e funcional |
| Métricas com [SUPOSIÇÃO A VALIDAR] | Inventar números comprovados comprometeria a credibilidade do projeto inteiro |

---

## Checklist do pacote completo de reenvio

O reenvio exige todos os entregáveis de novo, não só os alterados.

### Campos do formulário

- [ ] Problema e solução: texto de `docs/SUBMISSAO.md`, seção "Problema e solução" (abaixo de 500 palavras)
- [ ] Declaração das tecnologias: texto da seção 3 de `docs/INSCRICAO.md`, coerente com `docs/DECLARACAO_TECNICA.md`
- [ ] URL pública do vídeo novo, gravado com `docs/DEMO.md`, aberta em janela anônima
- [ ] URL do repositório público, com o commit final já na `main`
- [ ] URL do protótipo publicado, ou a nota de execução local se a publicação não sair a tempo
- [ ] Links complementares da seção 5 de `docs/INSCRICAO.md`

### Documentos (em `docs/`)

- [x] `RESPOSTA_AO_FEEDBACK.md`: este arquivo
- [x] `DECLARACAO_TECNICA.md`: produtos IBM com finalidade, arquivo e estado
- [x] `USO_DO_BOB.md`: cinco sessões, prompts e mapeamento por critério
- [x] `PROPOSTA.md` e `VALIDACAO.md`: stakeholder, caso de uso e métricas com fonte ou [SUPOSIÇÃO A VALIDAR]
- [x] `SUBMISSAO.md` e `INSCRICAO.md`: textos do formulário alinhados à nova narrativa
- [x] `DEMO.md`: roteiro de até 3 minutos com o Bob e o selo do planejador
- [x] `DOSSIE.md`: onze slides na ordem pedida
- [x] `PLANO_TECNICO.md`: validação do watsonx, recuperação, interface e publicação
- [ ] `VERIFICACAO.md`: acrescentar a linha da chamada real e a URL publicada quando existirem

### Evidências do Bob (em `bob_sessions/`)

- [x] Cinco pastas com `registro.md` e `resumo-sessao.png`
- [x] Datas e commits conferidos com `git log`
- [ ] Parágrafo de revisão escrito por cada integrante (5 registros)
- [ ] Sessão gravada para o vídeo (Prompt 7 ou 10), com pasta própria

### Evidências do watsonx.ai

- [ ] JSON de `python -m elo.prova_watsonx` em `docs/evidencias/watsonx/` com `chamada_real_comprovada: true`
- [ ] Saída dos 30 casos em modo real

### Código e testes

- [x] `python -m unittest discover -s tests`: 233 testes OK em 2026-11-11
- [x] `python -m ruff check elo tests`: sem apontamentos
- [x] `node --test tests/web_behaviors.cjs`: 36 de 36
- [ ] Mesmos comandos verdes no GitHub Actions depois do push

### Segurança antes de publicar

- [ ] Nenhuma chave, token ou ID de projeto em commit (`git grep -n "IBM_CLOUD_API_KEY=."` deve voltar vazio)
- [ ] Nenhum logotipo oficial do BB ou da IBM
- [ ] Capturas revisadas: mostram e-mail da conta, sem chaves nem dados de clientes
