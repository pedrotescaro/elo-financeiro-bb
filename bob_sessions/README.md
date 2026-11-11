# Evidências reais do IBM Bob

Esta pasta armazena os registros, capturas e relatórios das sessões do Bob realizadas no projeto Elo Financeiro. Cada subpasta corresponde a uma sessão real. O arquivo `MODELO.md` contém o formulário a preencher.

## O que registrar em cada sessão

Um registro completo contém:

| Campo | O que preencher |
| --- | --- |
| Data, hora e fuso | Data exata no formato AAAA-MM-DD e horário com fuso (ex.: 14:30 BRT) |
| Integrante responsável | Nome ou identificação da pessoa que realizou e revisou a sessão |
| Tarefa e objetivo | O que você pediu ao Bob; qual problema queria resolver |
| Ambiente/edição do Bob | Versão, modo (Agent/Ask/Plan) e plano da conta |
| Commit de partida | Hash e mensagem do commit antes de iniciar |
| O que o Bob fez | Lista dos arquivos lidos, código escrito, testes criados, decisões tomadas |
| O que eu revisei | O que você efetivamente abriu e conferiu. Este campo é humano e não pode ser gerado pelo Bob |
| Resultado revisado | Arquivos alterados, commits produzidos, testes executados com resultado, limitações |
| Evidências anexadas | Links para capturas, relatórios exportados, capturas de terminal |

O campo "O que eu revisei" é o mais importante. Ele prova que a sessão foi conduzida e supervisionada por uma pessoa, não apenas executada por automação.

## Protocolo de captura passo a passo

1. **Antes de começar:** anote o hash do commit atual (`git log --oneline -1`). Abra o Bob na conta autorizada do programa. Verifique que o repositório carregado é o correto.

2. **Durante a sessão:** mantenha uma aba com o terminal de testes aberto. Quando o Bob propuser alterações, leia o código antes de aceitar. Execute os testes após cada conjunto de mudanças.

3. **Captura obrigatória:** ao terminar a tarefa, abra o painel de configurações do Bob IDE (ícone de engrenagem ou nome de usuário) e capture a tela completa. A captura deve mostrar: conta, plano, uso acumulado, versão do Bob e a tarefa recém-concluída na lista de tarefas recentes. Salve como `resumo-sessao.png` na subpasta da sessão.

4. **Captura do terminal:** capture a saída do comando de testes (`python -m unittest discover -s tests -v` e `node --test tests/web_behaviors.cjs`). Salve como `testes-resultado.png` ou similar.

5. **Exportação de relatório:** se a edição do Bob disponibilizar exportação de relatório por tarefa, exporte o arquivo original e salve com a extensão real fornecida pela ferramenta. Se não houver essa opção, registre o limite no campo "Evidências anexadas" e guarde as capturas manuais.

6. **Revisão de privacidade:** antes de incluir qualquer arquivo na pasta, verifique que não há chaves de API, tokens, senhas, e-mails pessoais, nomes de clientes ou dados financeiros identificáveis. Use somente exemplos sintéticos.

7. **Preenchimento do registro:** copie `MODELO.md` para `bob_sessions/AAAA-MM-DD-nome-da-tarefa/registro.md` e preencha todos os campos. O campo "O que eu revisei" deve descrever o que você verificou pessoalmente, não o que o Bob relatou.

8. **Commit:** faça o commit da pasta da sessão com uma mensagem descritiva (ex.: `docs: registro sessão Bob 2026-11-12 validação watsonx`). Confirme que os arquivos estão no repositório antes de fechar.

## Sessões realizadas

| Data da sessão | Integrante | Tarefa | Commits | Pasta |
| --- | --- | --- | --- | --- |
| 2026-10-28 | Guilherme | Correção dos apontamentos do Ruff em `tests/test_ibm_cache.py` | `a6107cb`, PR #2 | `2026-11-08-lint-fix-test-ibm-cache/` |
| 2026-10-28 | Guilherme | Projeção de compras parceladas no fluxo de caixa | `560b59b`, `67bb80a`, PR #3 | `2026-11-08-parcelas-fluxo-caixa/` |
| 2026-11-05 | Pedro | Ajuste de redução de gastos flexíveis | `6d68d07`, `16038dd` | `2026-11-05-ajuste-reducao-gastos-flexiveis/` |
| 2026-11-05 | Pedro | Conclusão do MVP: fluxo de propostas e validação IBM | `7c5e853`, `a121388`, `d76f00d` | `2026-11-08-mvp-completion/` |
| 2026-11-11 | Pedro | Diagnóstico do feedback e documentos de resposta | ainda não commitado | `2026-11-11-resposta-ao-feedback/` |

Três pastas têm 2026-11-08 no nome porque foi a data em que o registro foi escrito. A data real de cada sessão, conferida com `git log`, está no próprio registro. Todos os campos estão preenchidos, exceto o parágrafo "Revisão do integrante na época da sessão", que precisa ser escrito por quem conduziu cada sessão.

## Próximas sessões sugeridas

Veja `docs/USO_DO_BOB.md` para 10 prompts prontos, cada um ligado a um artefato do repositório e a um critério de avaliação. Os prompts 1, 4 e 10 são os mais rápidos de executar e capturar hoje.

## O que não fazer

- Não criar imagens fictícias de painéis do Bob.
- Não preencher o campo "O que eu revisei" com texto gerado pelo Bob.
- Não declarar que uma sessão foi realizada se só foi planejada.
- Não incluir chaves, tokens, extratos ou dados pessoais nas evidências públicas.
- Não copiar o checkpoint de `docs/BOB_STATUS.md` e apresentá-lo como relatório exportado do Bob. São documentos diferentes com finalidades diferentes.
