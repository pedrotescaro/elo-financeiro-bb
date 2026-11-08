# Inscrição — campos para copiar e colar

Rascunho de entrega. Os textos abaixo descrevem a implementação e os registros disponíveis; este arquivo não representa uma inscrição enviada.

## 1. URL pública do vídeo

**PENDENTE — URL pública. O usuário escolheu manter o vídeo somente no computador.**

Foi gerado `output/video/elo-financeiro-demonstracao.mp4`: 2min48s, 1280×720, com narração em português e legendas. É uma montagem de nove capturas reais do programa, não uma gravação contínua. O arquivo está apenas no computador e não fornece uma URL pública para o formulário. O roteiro está em [DEMO.md](DEMO.md).

No formulário da equipe, descrição, declaração tecnológica e repositório foram preenchidos como rascunho. O campo do vídeo foi mantido vazio e o botão de envio final não foi acionado.

## 2. Problema e solução — até 500 palavras

Copiar somente os cinco parágrafos abaixo para o campo de descrição.

Um saldo positivo hoje pode esconder um aperto amanhã. Contas vencem antes do recebimento, uma compra compromete a margem e uma mensagem urgente pode pressionar uma decisão de PIX. O problema que orienta o Elo Financeiro é a dificuldade de enxergar essas consequências no calendário antes de decidir. A proposta tem como público inicial pessoas que estão organizando sua autonomia financeira ou convivem com renda variável; essa hipótese de público ainda precisa de pesquisa com usuários.

O Elo Financeiro é um protótipo acadêmico de assistente financeiro que reúne antecipação, explicação e controle. Após autorizar a leitura dos dados fictícios, a pessoa vê o saldo projetado por dia, o menor saldo e a margem desejada. As explicações mostram os valores, as hipóteses e o que não foi considerado.

Na jornada principal, o cenário começa com R$ 1.500, mas as contas levam o menor saldo a menos R$ 100 antes do próximo recebimento. O Elo propõe reduzir R$ 300 de gastos flexíveis previstos. Somente após aprovação, o plano altera a projeção e o menor saldo passa a R$ 200. Uma nova despesa simulada de R$ 150 reduz essa margem para R$ 50. Esses números demonstram o funcionamento do cenário, sem representar resultados obtidos com clientes.

Outras duas jornadas permitem comparar uma compra com o calendário e registrar uma meta, ou consultar sinais ilustrativos de risco em um PIX. A pessoa pode recusar propostas, ajustar a redução, consultar a trilha temporária e revogar a leitura, limpando planos e metas da sessão.

O diferencial pretendido é transformar informações dispersas em uma próxima decisão compreensível, acompanhada de cálculo verificável e autorização explícita. A demonstração padrão usa regras e dados sintéticos. Não conecta contas bancárias, movimenta dinheiro ou confirma fraudes. A efetividade com usuários e as integrações IBM em ambiente real ainda precisam de validação.

## 3. Declaração clara das tecnologias utilizadas

Copiar o texto abaixo para o campo de tecnologias, mantendo a distinção entre desenvolvimento, demonstração e integração.

**IBM Bob:** o checkpoint de 5 de novembro de 2026, em `docs/BOB_STATUS.md`, registra apoio do Bob no desenvolvimento do fluxo de propostas, redução personalizada, descarte e versionamento de prévias, cache IBM e testes. Essa atribuição vem do registro da equipe. As capturas e os relatórios originais de sessão ainda precisam ser anexados em `bob_sessions/`; o checkpoint não substitui esses anexos.

**IBM watsonx Orchestrate:** não foi utilizado na implementação atual. Não há agente, fluxo ou implantação Orchestrate neste repositório. A coordenação executável da demonstração é implementada em Python.

**IBM watsonx.ai:** existe um adaptador REST opcional em `elo/watsonx.py`, com autenticação IBM IAM, modelo configurável e seleção de ferramentas permitidas. Cálculos e permissões permanecem no código; falhas ativam a contingência por regras. Os registros disponíveis comprovam testes com respostas simuladas, sem comprovar uma chamada real à conta IBM. Esse adaptador não é uma integração com watsonx Orchestrate.

**Demais tecnologias:** Python 3.11 ou superior, HTML, CSS e JavaScript; cálculos em centavos inteiros, recuperação local de orientações e sessões temporárias em memória. O modo padrão funciona sem dependências Python externas.

## 4. Repositório público do código

[Elo Financeiro no GitHub](https://github.com/pedrotescaro/elo-financeiro-bb)

Visibilidade pública conferida pela integração GitHub nesta preparação. Antes do envio, conferir se a revisão demonstrada e os documentos finais estão publicados na `main`.

## 5. Links complementares opcionais

- [Arquitetura e limites](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/ARQUITETURA.md)
- [Checkpoint de desenvolvimento atribuído ao Bob](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/BOB_STATUS.md)
- [Verificação técnica registrada](https://github.com/pedrotescaro/elo-financeiro-bb/blob/main/docs/VERIFICACAO.md)
- **Protótipo hospedado: pendente.** A execução em `http://127.0.0.1:8000` serve para apresentação local e não é um link público para avaliadores.
- **Capturas e relatórios originais do Bob: pendentes.** Adicionar os links depois de anexar os arquivos reais revisados.

## Conferência antes de enviar

- Substituir o campo pendente pelo vídeo publicado e testar o acesso sem login do autor.
- Confirmar que o formulário aceita a declaração tecnológica acima; não declarar uso de Orchestrate enquanto ele não estiver implementado.
- Anexar as evidências originais do Bob e atualizar a declaração conforme o material efetivamente disponível.
- Conferir a revisão pública do código e os links complementares. Publicação do protótipo, gravação e submissão não são comprovadas pela existência deste documento.
