# Verificação desta preparação

Em 7 de outubro de 2026, a base inicial passou em 20 testes automatizados de domínio e HTTP. Foram verificados cálculos de calendário, integridade dos valores, restrições a gastos essenciais, consentimento, revogação, aprovação vinculada ao contexto, repetição idempotente, isolamento de sessões e reavaliação.

Também passaram a compilação Python e a checagem de sintaxe do JavaScript. O texto de problema e solução contém 362 palavras, abaixo do limite de 500, e os links locais da documentação foram conferidos.

Não foi possível renderizar a interface em um navegador neste ambiente: o executável Chromium não estava disponível e sua instalação falhou. A inspeção visual em desktop/celular e os testes com leitores de tela continuam pendentes. Nenhuma captura de interface ou validação visual foi fabricada.

Não foram executadas chamadas reais ao watsonx, sessões IBM Bob, transações bancárias ou testes com clientes. A existência do adaptador e da documentação não substitui essas evidências.

## Reproduzir os testes

```bash
python -m unittest discover -s tests -v
python -m compileall -q elo tests
node --check web/app.js
```

Node é opcional e necessário apenas para a última checagem. A demonstração não depende dele.
