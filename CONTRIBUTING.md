# Contribuir para o Elo

Crie uma branch para a mudança, preserve os dados sintéticos e execute `python -m unittest discover -s tests -v` antes de abrir uma revisão. Documente qualquer alteração em cálculos, permissões ou limites.

Para desenvolvimento, instale `ruff==0.16.0` e execute `python -m ruff check elo tests`. Para mudanças na interface, execute também `node --check web/app.js` e `node --test tests/web_behaviors.cjs` com Node 18 ou superior. Ruff e Node são ferramentas opcionais de desenvolvimento; a demonstração continua exigindo apenas Python. O CI verifica Python 3.11 e 3.14, lint e os comportamentos JavaScript.

Não inclua dados de clientes, dados pessoais, senhas, tokens ou arquivos `.env`. Evidências do Bob devem retratar trabalho realmente realizado e ser revisadas antes da inclusão.

A equipe deve decidir licença, autoria e créditos antes de abrir o código ao público. Nenhuma licença de distribuição foi presumida nesta preparação.
