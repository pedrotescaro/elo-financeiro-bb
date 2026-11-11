# Inscrição: campos para copiar e colar

Rascunho de entrega. Os textos abaixo descrevem a implementação e os registros disponíveis; este arquivo não representa uma inscrição enviada.

## 1. URL pública do vídeo

**PENDENTE: URL pública. O usuário escolheu manter o vídeo somente no computador.**

Existe `output/video/elo-financeiro-demonstracao.mp4` (2min48s, montagem de nove capturas), mas ele é anterior ao feedback: não tem o Bob nem o stakeholder gerente. Para o reenvio, gravar um vídeo novo seguindo [DEMO.md](DEMO.md) e publicar com link aberto.

No formulário da equipe, descrição, declaração tecnológica e repositório foram preenchidos como rascunho. O campo do vídeo foi mantido vazio e o botão de envio final não foi acionado.

## 2. Problema e solução, até 500 palavras

Copiar a seção "Problema e solução" de [SUBMISSAO.md](SUBMISSAO.md). Ela foi reescrita após o feedback em torno da analista de negócios da agência e do gerente de relacionamento do BB, e substitui o texto anterior, que falava apenas com o cliente final.

## 3. Declaração clara das tecnologias utilizadas

Copiar o texto abaixo para o campo de tecnologias. Ele resume [DECLARACAO_TECNICA.md](DECLARACAO_TECNICA.md).

**IBM Bob (2.3.0, modo Agent):** ferramenta de desenvolvimento da equipe. Usado em cinco sessões por dois integrantes, entre 28/10 e 11/11/2026: projeção de parcelas no fluxo de caixa, correção de lint nos testes do adaptador IBM, redução personalizada de gastos com prévia no servidor, correção do fluxo de propostas com 30 casos de validação IBM, e diagnóstico do feedback com os documentos de resposta. Cada sessão tem registro, captura do painel e commits em `bob_sessions/`.

**IBM watsonx.ai (API de geração de texto, modelo Granite configurado pela equipe):** dois usos. Interpreta a pergunta do analista de negócios sobre a carteira em uma consulta estruturada, validada contra uma lista fechada (`elo/watsonx.py`, método `interpret`, chamado por `elo/carteira.py`), e escolhe quais ferramentas do agente rodam para o cliente aberto no atendimento (método `plan`, chamado por `build_report()` em `elo/core.py`). O modelo recebe só dados sintéticos e nunca produz números; saldos, prazos e permissões são calculados em Python. Falhas levam à contingência por regras, e um selo no topo da análise mostra quem planejou. Testado com respostas simuladas; [ATUALIZAR APÓS A EXECUÇÃO: a chamada real na conta do programa ainda não foi comprovada / foi comprovada em DATA com o modelo MODELO, evidência em docs/evidencias/watsonx/].

**IBM Cloud IAM:** autenticação antes das chamadas ao watsonx.ai, com token só em memória.

**IBM watsonx Orchestrate e IBM Consulting Advantage:** não utilizados nesta versão.

**Demais tecnologias:** Python 3.11 ou superior com biblioteca padrão, HTML, CSS e JavaScript; cálculos em centavos inteiros, recuperação local de orientações por conceitos e similaridade de termos, sessões temporárias em memória.

## 4. Repositório público do código

[Elo Financeiro no GitHub](https://github.com/pedrotescaro/elo-financeiro-bb)

Visibilidade pública conferida pela integração GitHub nesta preparação. Antes do envio, conferir se a revisão demonstrada e os documentos finais estão publicados na `main`.

## 5. Links complementares opcionais

- [Arquitetura e limites](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/ARQUITETURA.md)
- [Resposta ao feedback, ponto a ponto](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/RESPOSTA_AO_FEEDBACK.md)
- [Declaração técnica dos produtos IBM](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/DECLARACAO_TECNICA.md)
- [Uso do IBM Bob: cinco sessões e evidências](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/USO_DO_BOB.md)
- [Registros das sessões do Bob](https://github.com/pedrotescaro/elo-financeiro-bb/tree/main/bob_sessions)
- [Dossiê de apresentação](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/DOSSIE.md)
- [Verificação técnica registrada](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/VERIFICACAO.md)
- **Protótipo hospedado: pendente.** A execução em `http://127.0.0.1:8000` serve para apresentação local e não é um link público para avaliadores.

## Conferência antes de enviar

- Substituir o campo pendente pelo vídeo publicado e testar o acesso sem login do autor.
- Confirmar que o formulário aceita a declaração tecnológica acima; não declarar uso de Orchestrate enquanto ele não estiver implementado.
- Completar o trecho [ATUALIZAR APÓS A EXECUÇÃO] da declaração do watsonx.ai com o resultado real, seja ele qual for.
- Conferir a revisão pública do código e os links complementares. Publicação do protótipo, gravação e submissão não são comprovadas pela existência deste documento.
