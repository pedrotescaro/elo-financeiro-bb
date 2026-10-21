# Plano até a entrega

Revisão de 21 de outubro de 2026. A referência fornecida nos materiais é **8 de novembro de 2026**; o prazo não foi verificado na plataforma nesta revisão. Confirmar data, horário, requisitos e eventuais atualizações antes de organizar a entrega.

## Estado implementado

O repositório tem cálculos em centavos, consentimento e aprovação vinculada aos dados, contingência do planejador, recuperação local por conceitos/TF-IDF, explicações, trilha temporária, gráfico diário e recursos de teclado/leitura. Há testes e lint no CI, controles de exposição demonstrativa, Dockerfile e guia de deploy.

Isso não comprova uso do Bob, chamada IBM real, pesquisa com usuários, execução da imagem Docker, hospedagem pública ou submissão. A evidência técnica efetiva fica em [Verificação](VERIFICACAO.md).

## Próximas etapas propostas

| Período | Objetivo | Evidência de conclusão |
| --- | --- | --- |
| 21–25/out | Realizar trabalho no Bob, validar IBM localmente e avaliar a jornada | Sessões reais, chamadas/casos inéditos e observações anônimas |
| 26/out–1/nov | Executar Docker, hospedar a demo e corrigir falhas observadas | URL HTTPS testada externamente, commit e evidências organizadas |
| 2–6/nov | Gravar vídeo e revisar declarações | Vídeo ≤180 s, ≥90 s de demonstração, evidência Bob visível |
| 7–8/nov | Conferir acesso e submeter na plataforma | Última revisão dos links e todos os campos obrigatórios |

## Prioridade de implementação

**P0, antes da submissão:** uso central do Bob com evidências reais; integração IBM validada localmente; avaliação em casos inéditos; execução e verificação da hospedagem sintética; pesquisa exploratória; vídeo e declarações finais honestas. Confirmar com o mentor a expectativa sobre demonstração da tecnologia IBM, já que a hospedagem pública permanece por regras.

**P1, se houver capacidade:** edição e recusa explícita de planos; horizonte de parcelas completo; avaliação e ampliação da base de recuperação; preferências de alertas; correções apontadas por leitores de tela e participantes. Não ampliar o escopo antes de concluir as evidências P0.

**P2, expansão posterior:** conectores reais BB/Open Finance, operação financeira, crédito, FGTS, investimentos, múltiplos canais e arquitetura distribuída. Não dependem deles para demonstrar o problema central.

## Distribuição sugerida de trabalho

| Frente | Responsabilidade | Entrega |
| --- | --- | --- |
| Produto/pesquisa | Hipóteses, entrevistas e narrativa | Problema validado e resultados anônimos |
| Agente/IBM | Modelo, ferramentas, avaliação e Bob | Jornada real e evidências |
| Experiência | Interface, acessibilidade e teste | Jornada compreensível |
| Qualidade/entrega | Testes, hospedagem, vídeo e documentação | Links e submissão conferidos |

Adaptar às pessoas já cadastradas na equipe. Nenhum nome ou papel foi atribuído automaticamente.

## Antes de expor o protótipo à internet

O servidor embutido contém controles para uma demonstração limitada, sem identidade ou persistência de produção. Usar proxy HTTPS e a origem exata em `ELO_PUBLIC_ORIGIN`, conforme [Deploy](DEPLOY.md). Os limites de sessões, requisições e workers não são uma defesa medida contra abuso na internet; verificar também os limites e custos da plataforma.

O modo público recusa o planejador externo; não configurar credenciais IBM na hospedagem. Validar permissões do programa, executar a imagem, testar a URL em janela anônima e em duas sessões independentes e manter o vídeo acessível mesmo se o serviço do lab for encerrado.

## Checklist de entrega do programa

Usar [Entrega: pendências da equipe](ENTREGA.md) para registrar os itens manuais. Não marcar como concluídos porque existe uma pasta, um adaptador, um Dockerfile ou um comando de teste. Os documentos do programa fornecidos fundamentam o roteiro; a equipe deve confirmar as regras vigentes na plataforma.
