---
name: Elo Financeiro
description: A carteira da agência numa conversa, e o contato com o cliente antes do aperto.
colors:
  marinho-de-agencia: "#132C5C"
  marinho-profundo: "#1D3B78"
  marinho-nevoa: "#EEF2F9"
  marinho-contorno: "#DDE4F2"
  marca-texto-do-aperto: "#F2C94C"
  marca-texto-claro: "#F7D978"
  papel-de-extrato: "#F3F5F9"
  folha: "#FFFFFF"
  linha: "#E4E8EF"
  linha-firme: "#D3D9E4"
  tinta: "#18233D"
  tinta-suave: "#5B667C"
  legenda: "#646F86"
  sobre-marinho: "#C9D3E8"
  sobre-marinho-suave: "#9FB0D3"
  negativo: "#B42F47"
  negativo-fundo: "#FCECEF"
  atencao: "#935D00"
  atencao-fundo: "#FDF3DE"
  atencao-sobre-marinho: "#F5C26B"
  positivo: "#117A56"
  positivo-fundo: "#E6F4EE"
  positivo-sobre-marinho: "#A7E3C7"
typography:
  display:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(2.25rem, 1.3rem + 2.8vw, 3.75rem)"
    fontWeight: 700
    lineHeight: 1.12
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(1.375rem, 1.1rem + .8vw, 1.625rem)"
    fontWeight: 600
    lineHeight: 1.35
    letterSpacing: "-0.015em"
  lead:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.01em"
  numeral:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "clamp(1.5rem, 1.3rem + .6vw, 1.75rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
    fontFeature: "\"tnum\" 1"
  body:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.6
    fontFeature: "\"tnum\" 1"
  ui:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.5
  label:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.04em"
  caption:
    fontFamily: "Mulish, Segoe UI, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  control: "8px"
  card: "12px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.marinho-de-agencia}"
    textColor: "{colors.folha}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.marinho-profundo}"
    textColor: "{colors.folha}"
  button-secondary:
    backgroundColor: "{colors.folha}"
    textColor: "{colors.marinho-de-agencia}"
    rounded: "{rounded.control}"
    padding: "10px 16px"
    height: "40px"
  button-secondary-hover:
    backgroundColor: "{colors.marinho-nevoa}"
  chip:
    backgroundColor: "{colors.folha}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
    height: "34px"
  card:
    backgroundColor: "{colors.folha}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.card}"
    padding: "22px 24px"
  metric-card:
    backgroundColor: "{colors.folha}"
    textColor: "{colors.tinta}"
    typography: "{typography.numeral}"
    rounded: "{rounded.card}"
    padding: "20px 22px 24px"
  reading-band:
    backgroundColor: "{colors.marinho-de-agencia}"
    textColor: "{colors.folha}"
    rounded: "{rounded.card}"
    padding: "22px 24px"
  input:
    backgroundColor: "{colors.folha}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    height: "44px"
  nav-item-active:
    textColor: "{colors.marinho-de-agencia}"
    height: "48px"
  status-negative:
    backgroundColor: "{colors.negativo-fundo}"
    textColor: "{colors.negativo}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
  status-warning:
    backgroundColor: "{colors.atencao-fundo}"
    textColor: "{colors.atencao}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
  status-positive:
    backgroundColor: "{colors.positivo-fundo}"
    textColor: "{colors.positivo}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
---

# Design System: Elo Financeiro

## Overview

**Creative North Star: "O Extrato Antecipado"**

O Elo é a leitura limpa do que ainda vai acontecer na conta do cliente. As telas se comportam como um extrato bem impresso: papel claro levemente azulado, tinta marinho firme, números grandes e alinhados, e uma única marca amarela passada sobre a linha onde o saldo falta. Nada compete com essa marca.

A densidade é a de uma ferramenta de trabalho da agência: a analista e o gerente precisam achar tudo no lugar, sem descobrir o layout a cada visita. Barra lateral com grupos, barra superior com a trilha de navegação, cartões brancos de borda fina e indicadores no padrão rótulo, valor e régua. O caráter é firme e confiável: o marinho e os números carregam o peso, a superfície fica plana em repouso e só ganha sombra quando o usuário interage.

A apresentação embutida é o único lugar onde o marinho toma a tela inteira e o amarelo aparece com mais frequência, porque ali o objetivo é convencer a banca, não operar. Gradientes decorativos, efeito de vidro, manchas de cor no fundo e ladrilhos coloridos atrás de ícones foram descartados de propósito.

**Key Characteristics:**
- Papel claro, tinta marinho, um único amarelo de alerta.
- Superfícies planas com borda de 1px; sombra só ao interagir.
- Números em peso forte, algarismos tabulares.
- Ícones de traço fino (Phosphor, peso light), sem fundo.
- Um momento de movimento por tela.

## Colors

Paleta tirada do logo: marinho e amarelo sobre neutros levemente azulados, com três cores de estado usadas só quando carregam significado.

### Primary
- **Marinho de Agência** (#132C5C): botão principal, item ativo da navegação, linha do gráfico de saldo, faixa de leitura da análise, resposta do agente, fundo inteiro da apresentação. É a cor do logo e a voz do produto.
- **Marinho Profundo** (#1D3B78): hover do botão principal e cor dos links da trilha de navegação.
- **Névoa Marinho** (#EEF2F9) e **Contorno Marinho** (#DDE4F2): fundo e borda de áreas de destaque suave, como a resposta do agente, o impacto da proposta e o aviso de cliente aberto pela carteira.

### Secondary
- **Marca-Texto do Aperto** (#F2C94C) e **Marca-Texto Claro** (#F7D978, hover dos botões amarelos da apresentação): marca o pior dia no gráfico, o halo que pulsa sobre ele, os destaques da apresentação e a seleção de texto. Nunca usado como fundo de bloco nem em botão da área de trabalho, com uma exceção: o botão "Avançar" da apresentação.

### Neutral
- **Papel de Extrato** (#F3F5F9): chão de todas as telas e da barra lateral.
- **Folha** (#FFFFFF): cartões, barra superior, grupos de navegação, campos.
- **Linha** (#E4E8EF) e **Linha Firme** (#D3D9E4): bordas de 1px; a firme vai em campos, botões secundários e divisores do cabeçalho.
- **Tinta** (#18233D): texto principal e números.
- **Tinta Suave** (#5B667C): texto secundário e rótulos; 5.3:1 sobre o Papel de Extrato.
- **Legenda** (#646F86): legendas de grupo e setas da navegação; passa de 4.5:1 sobre branco e sobre o Papel de Extrato.

### Sobre o marinho
- **Sobre Marinho** (#C9D3E8): texto de apoio na faixa de leitura, no painel de consentimento e na apresentação.
- **Sobre Marinho Suave** (#9FB0D3): legendas, ícones e abas inativas sobre o marinho.
- **Atenção sobre Marinho** (#F5C26B) e **Positivo sobre Marinho** (#A7E3C7): selo de contingência e estado positivo quando aparecem dentro de áreas marinho.

### Estados
- **Negativo** (#B42F47, fundo #FCECEF): saldo abaixo de zero, proposta recusada.
- **Atenção** (#935D00, fundo #FDF3DE): saldo abaixo da margem sem ficar negativo.
- **Positivo** (#117A56, fundo #E6F4EE): margem atingida, plano aprovado, indicador de dados sintéticos, "check" de confirmação.

### Named Rules
**The Marca-Texto Rule.** O amarelo marca o aperto, e só o aperto. Na área de trabalho, se ele aparece em mais de um ponto da tela, um deles está errado.

**The State-Earns-Color Rule.** Vermelho, âmbar e verde aparecem apenas quando descrevem a situação de um cliente ou de uma ação. Nunca como decoração ou para diferenciar seções.

## Typography

**Display Font:** Mulish (com Segoe UI e system-ui de reserva)
**Body Font:** Mulish (com Segoe UI e system-ui de reserva)

**Character:** uma única família variável, servida pelo próprio site, que vai de leve e arejada no corpo a firme nos números e títulos. A hierarquia vem de peso e tamanho, nunca de cor ou gradiente.

### Hierarchy
- **Display** (700, de 2.25rem a 3.75rem conforme a largura, 1.12): títulos da apresentação; o trecho de destaque fica no Marca-Texto do Aperto.
- **Headline** (600, de 1.375rem a 1.625rem, 1.35): título de cada tela ("Sua visão financeira", "Olá, Carla") e do painel de consentimento.
- **Lead** (650, 1.25rem, 1.35): título da faixa de leitura, passos da apresentação, valores de comparação.
- **Title** (650, 1.0625rem, 1.35): título de cartões e seções, sempre acompanhado de um ícone de traço.
- **Numeral** (700, de 1.5rem a 1.75rem, 1.2, algarismos tabulares): valores dos indicadores e saldos de destaque.
- **Body** (400, 0.9375rem, 1.6): texto corrido, respostas do agente, tabelas.
- **UI** (600, 0.875rem, 1.5): botões, trilha de navegação, rótulos de campo, aviso curto.
- **Label** (600, 0.8125rem, 0.04em, caixa-alta nos indicadores): rótulo dos indicadores e texto de tabela; também o tamanho de notas de apoio.
- **Caption** (400 a 700, 0.75rem, 1.6): legendas, rodapés, etiquetas de estado, cabeçalho de tabela em caixa-alta, títulos de grupo da navegação (0.06em).

### Named Rules
**The Nine-Steps Rule.** Todo tamanho de fonte sai da escala (caption, label, ui, body, title, lead, headline, numeral, display). Tamanho novo entra primeiro no DESIGN.md.

**The Uppercase-Is-A-Label Rule.** Caixa-alta só em rótulos de indicador, cabeçalhos de tabela e títulos de grupo da navegação. Nunca acima de um título como etiqueta ou numeração de seção.

## Layout

Casca de aplicativo: barra lateral fixa de 272px à esquerda (236px abaixo de 1180px), área principal com respiro lateral de 32px (24px abaixo de 1180px, 16px no celular) e largura máxima de 1512px. A barra superior ocupa a largura toda da área principal, com 64px de altura. Abaixo dela vêm o cabeçalho da tela (título e subtítulo à esquerda, contexto colado ao botão principal à direita), as etapas, a faixa de leitura, a linha de indicadores e a grade de trabalho.

Os indicadores ficam em três colunas, com 16px de intervalo; viram duas colunas abaixo de 960px (o primeiro ocupa a linha inteira) e uma coluna no celular. A grade de trabalho do atendimento é gráfico à esquerda (cerca de 60%) e proposta à direita, empilhando abaixo de 960px. No celular (até 700px), a barra lateral vira faixa no topo com as visões lado a lado e os cenários em três blocos, e o contexto do cabeçalho empilha sobre o botão principal.

Ritmo de espaçamento em 4, 8, 16, 24 e 32px; mais espaço acima de um título do que abaixo dele.

## Elevation & Depth

Plano em repouso, com camadas por tom e borda, e sombras sempre neutras (preto com pouca opacidade, nunca tingidas de marinho): papel de extrato no chão, folha branca nos cartões, borda de 1px separando os planos. Os cartões carregam uma sombra quase imperceptível, só para descolá-los do chão. A sombra de verdade aparece como resposta à interação, nos controles com superfície, e nos avisos que flutuam sobre a tela.

### Shadow Vocabulary
- **Repouso** (`box-shadow: 0 1px 2px rgba(0, 0, 0, .05)`): cartões, indicadores e o painel de consentimento.
- **Interação** (`box-shadow: 0 6px 14px -6px rgba(0, 0, 0, .18)`): hover de botões, chips, botões de linha, link de download e botão de reiniciar.
- **Flutuante** (`box-shadow: 0 12px 28px -12px rgba(0, 0, 0, .28)`): aviso curto no canto da tela.
- **Palco** (`box-shadow: 0 24px 48px -28px rgba(0, 0, 0, .55)`): cartões brancos sobre o marinho da apresentação.

### Named Rules
**The Flat-Until-Touched Rule.** Superfícies ficam planas em repouso. A sombra de interação aparece no hover e some ao sair; nunca é estado permanente de um cartão.

## Shapes

Cantos suavemente arredondados e consistentes: 8px em botões, campos e controles; 12px em cartões, grupos de navegação, faixa de leitura e avisos; pílula completa em chips, etiquetas de estado, selo de dados sintéticos e selo do planejador. Bordas sempre de 1px. A única forma fora dessa regra é o círculo: número das etapas, avatar do agente e pontos de estado.

As réguas dos indicadores são faixas de 4px encostadas na base do cartão, sem arredondamento, cortadas pela borda do próprio cartão.

## Components

### Buttons
Firmes, com o marinho carregando o peso.
- **Shape:** cantos de 8px; altura mínima de 40px.
- **Primary:** fundo Marinho de Agência, texto branco em 700, 10px por 16px, ícone de 18px à esquerda quando houver.
- **Hover / Focus:** fundo Marinho Profundo e sombra de interação; foco com contorno de 2px Marinho Profundo afastado 3px.
- **Secondary:** fundo branco, texto marinho, borda Linha Firme; no hover, Névoa Marinho e sombra de interação.
- **Text button:** sem borda, texto Tinta Suave em 600; no hover, fundo Névoa Marinho e texto marinho.
- **Grupo de contexto:** no cabeçalho, o bloco de contexto (cenário ou período) e o botão principal se encostam, como um campo com botão acoplado.

### Chips
- **Style:** pílula branca, borda Linha Firme, texto Tinta em 600, 13px.
- **State:** no hover, borda e texto marinho com sombra de interação. São perguntas prontas: um clique envia a pergunta.

### Cards / Containers
- **Corner Style:** 12px.
- **Background:** Folha sobre Papel de Extrato.
- **Shadow Strategy:** repouso; ver Elevation & Depth.
- **Border:** 1px Linha.
- **Internal Padding:** 22px por 24px (18px por 16px no celular).
- **Título:** Title com ícone de traço marinho de 22px à esquerda, sem ladrilho atrás.

### Inputs / Fields
- **Style:** fundo branco, borda 1px Linha Firme, cantos de 8px, altura de 44px.
- **Focus:** borda marinho e anel de 3px em Névoa Marinho.
- **Error:** mensagem em bloco com fundo #FCEBF0 e texto #8E263D logo abaixo do campo.

### Navigation
- **Style:** grupos em caixa branca de 12px com título em caixa-alta e legenda logo abaixo; itens de 48px com ícone de 20px, texto em 550 e seta à direita, separados por linha de 1px.
- **Default / Hover:** ícone Tinta Suave; no hover, texto e ícone marinho.
- **Active:** texto e ícone marinho em 700.
- **Mobile:** títulos de grupo somem, visões ficam lado a lado e os cenários viram três blocos com borda; o ativo ganha borda marinho.

### Indicador com régua (signature)
O componente que mais define o Elo. Rótulo em caixa-alta Tinta Suave, valor em Numeral, legenda curta, ícone marinho de 26px no canto superior direito e uma régua de 4px na base. A régua sempre mede algo real: no atendimento, quanto da margem desejada o menor saldo cobre; no analista, a fatia da carteira em cada situação. A cor da régua segue o estado (negativo, atenção, positivo).

### Faixa de leitura
Bloco marinho de 12px com o título da análise em branco, texto de apoio em #C9D3E8 e o selo do planejador (pílula com ponto: amarelo quando o IBM watsonx.ai interpretou, cinza nas regras locais, laranja na contingência).

### Gráfico de saldo
Linha marinho de 2.5px sobre área em degradê marinho de 14% a 0%, linha tracejada da margem, ponto amarelo com contorno marinho no pior dia e halo amarelo pulsando sobre ele. Ao carregar, a linha se desenha uma vez.

### Movimento e micro-interações
Um momento por tela. No atendimento, a linha do saldo se desenha e o pior dia pulsa. No analista, três pontos em Lottie enquanto a pergunta é analisada e um "check" em Lottie ao incluir clientes na lista. Ao aprovar um plano, o mesmo "check" no aviso curto. Na apresentação, cada tela entra uma vez e o gráfico do primeiro slide se desenha. Curva de saída exponencial (cubic-bezier(.16, 1, .3, 1)). Com "reduzir movimento" ligado, nada se move.

## Do's and Don'ts

### Do:
- **Do** usar o Marinho de Agência (#132C5C) no botão principal, no item ativo e na faixa de leitura, e o Marca-Texto do Aperto (#F2C94C) apenas no pior dia e nos destaques da apresentação.
- **Do** dar a todo indicador uma régua que meça algo verdadeiro; sem dado, sem régua.
- **Do** manter superfícies planas com borda de 1px e reservar a sombra de interação (0 6px 14px -6px rgba(0, 0, 0, .18)) para o hover.
- **Do** escrever números em Numeral (700, algarismos tabulares) e hierarquia por peso e tamanho.
- **Do** usar ícones Phosphor no peso light, na cor do texto ou do estado, sem fundo.

### Don't:
- **Don't** colocar etiqueta, eyebrow ou numeração acima de títulos.
- **Don't** usar texto com gradiente, efeito de vidro, manchas de cor no fundo ou degradês de azul para roxo.
- **Don't** colocar ícone dentro de ladrilho colorido.
- **Don't** usar borda colorida grossa à esquerda de cartões ou avisos.
- **Don't** repetir a mesma animação de entrada em todos os blocos.
- **Don't** usar logotipos oficiais do Banco do Brasil ou da IBM.
