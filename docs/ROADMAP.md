# Plano até a entrega

Referência de prazo: **8 de novembro de 2026**, conforme a página de conclusão anexada. Confirmar o horário e qualquer atualização na plataforma. Plano organizado a partir de 7 de outubro, sem pressupor etapas anteriores concluídas.

| Período | Objetivo | Evidência de conclusão |
| --- | --- | --- |
| 7–11/out | Validar recorte do problema e revisar a base no Bob | Proposta revisada, feedback do mentor e primeiras sessões reais |
| 12–18/out | Integrar e avaliar watsonx/Granite | Chamadas reais, casos inéditos, contingência e registro de ferramentas |
| 19–25/out | Melhorar planos, fontes e experiência | Ajuste/recusa, orientação versionada e testes exploratórios |
| 26/out–1/nov | Preparar hospedagem e corrigir falhas | URL acessível, validação externa e evidências organizadas |
| 2–6/nov | Gravar vídeo e revisar declarações | Vídeo ≤180 s, ≥90 s de demonstração, evidência Bob visível |
| 7–8/nov | Conferir acesso e submeter na plataforma | Última revisão dos links e todos os campos obrigatórios |

## Prioridade de implementação

**P0, antes da submissão:** uso central do Bob com evidências reais; integração IBM validada; completar e avaliar uma jornada agêntica; publicação segura do protótipo; pesquisa exploratória; vídeo; declarações finais honestas.

**P1, se houver capacidade:** edição e recusa de planos; testes de atraso de renda; horizonte de parcelas completo; RAG sobre conteúdo permitido; preferências de alertas; melhoria de acessibilidade.

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

O servidor embutido atual não deve ser tratado como serviço pronto para produção. A hospedagem precisa de HTTPS, servidor de aplicação apropriado, limitação de requisições, expiração de sessões, limites de chamadas IBM e armazenamento protegido de variáveis. Manter apenas dados sintéticos e deixar explícito o modo de execução.

Impedir que uma demonstração pública gere chamadas ilimitadas cobradas na conta IBM. Validar as permissões do ambiente do programa, testar o endereço em janela anônima e manter o vídeo acessível mesmo se o serviço do lab for encerrado.

## Checklist de entrega do programa

- [ ] Equipe e aprendizagem obrigatória conferidas na plataforma.
- [ ] Checkpoint intermediário e feedback revisados, quando aplicável.
- [ ] IBM Bob utilizado de forma central no trabalho real da equipe.
- [ ] Capturas/relatórios exigidos em `bob_sessions/`.
- [ ] Tecnologia IBM executada e descrita conforme o que foi comprovado.
- [ ] Link público do protótipo funcional.
- [ ] Vídeo público de até três minutos, narrado, com pelo menos 90 segundos de uso na tela.
- [ ] Declaração de problema e solução com até 500 palavras.
- [ ] Declaração tecnológica com usos e limites reais.
- [ ] Apenas dados sintéticos e conteúdo permitido.
- [ ] Todos os links testados sem estar autenticado.

Não marcar itens como concluídos porque existe uma pasta ou um adaptador de código.
