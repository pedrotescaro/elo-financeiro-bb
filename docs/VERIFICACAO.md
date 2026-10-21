# Verificação técnica — 21 de outubro de 2026

Ambiente local: Windows, Python 3.14.3, Node 24.14.0 e Ruff 0.16.0. Os testes usam apenas dados sintéticos. A demonstração continua iniciando com `python -m elo.server`, sem instalar pacotes.

## Resultados reproduzidos

| Verificação | Resultado local |
| --- | --- |
| `python -m unittest discover -s tests -v` | 91 testes passaram |
| `python -m ruff check elo tests` | Passou |
| `python -m compileall -q elo tests` | Passou |
| `node --check web/app.js` | Passou |
| `node --test tests/web_behaviors.cjs` | 6 testes passaram, sem pacotes Node |
| Texto completo de `SUBMISSAO.md` | 429 palavras, abaixo de 500 |
| Links locais Markdown | Destinos existentes |

O workflow executa essas verificações em Python 3.11 e 3.14. O resultado remoto deve ser conferido na execução da revisão em [GitHub Actions](https://github.com/pedrotescaro/elo-financeiro-bb/actions/workflows/checks.yml); a tabela acima registra o ambiente local, sem presumir sucesso de CI.

Os casos cobrem saldo zero, múltiplas contas no mesmo dia, renda atrasada além do horizonte, aprovação realmente desatualizada por HTTP, revogação, idempotência, isolamento e concorrência. Também cobrem recuperação por conceitos, explicações vinculadas aos cálculos, URLs inseguras e falhas/respostas IBM simuladas. O adaptador não foi chamado em uma conta IBM real.

Os testes públicos usam conexões locais e relógio controlado: origem/Host, CSRF, cookie `Secure`, cabeçalhos, expiração por inatividade, limite de sessões, rate limit com memória limitada, workers, timeout de socket e rejeição de entradas HTTP inválidas. Não são testes de carga ou avaliação de resistência a ataques na internet.

## Navegador e interface

A jornada foi operada no navegador local: consentimento, menor saldo de −R$ 100, aprovação levando a R$ 200, despesa levando a R$ 50 e botão desativado. A criação da meta de compra, os três motivos ilustrativos do PIX e a revogação com relatório oculto/trilha visível também foram verificados.

Foram inspecionados um viewport compacto de 794 × 668 e quadros locais de 1440 × 900 e 360 × 800. Os quadros carregaram os mesmos arquivos e API em um servidor de teste local, com permissão de enquadramento restrita à própria origem apenas no harness temporário; o servidor entregue continua impedindo enquadramento. No quadro móvel, a opção de texto ampliado foi testada e o excesso horizontal de um texto oculto foi corrigido. Na confirmação, a largura útil e a largura de rolagem foram iguais a 345 pixels (360 menos a barra vertical). A tabela mantém sua própria rolagem quando necessário.

- [Gráfico e menor saldo na janela compacta](evidencias/projecao-desktop.png).
- [Desktop e celular, com texto ampliado no celular](evidencias/layouts-responsivos.png).

As capturas são evidências locais com dados sintéticos. A inspeção não certifica acessibilidade: avaliação com leitor de tela, teclado por participantes, aparelho físico e testes exploratórios continuam pendentes.

## O que ainda não foi validado

O Docker CLI existe, mas o daemon local não estava disponível; a imagem não foi construída nem executada. Nenhum serviço de hospedagem foi criado ou publicado. O guia em [Deploy](DEPLOY.md) descreve os passos manuais e os limites do modo público.

Não foram realizadas sessões IBM Bob, chamadas reais ao watsonx, conexão bancária, transações, pesquisa com clientes ou submissão do projeto. As metas de avaliação continuam sendo metas. Use o [checklist de entrega](ENTREGA.md) para reunir essas evidências reais.
