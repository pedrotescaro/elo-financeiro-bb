# Publicação do repositório

Repositório criado em 7 de outubro de 2026: https://github.com/pedrotescaro/elo-financeiro-bb. Visibilidade inicial: privada. A criação foi realizada pelo navegador autorizado; os arquivos foram preparados para envio à branch `main`.

O pacote contém código e documentação sem os anexos originais, credenciais ou dados pessoais. A equipe pode revisar antes de abrir o código ao público. Os relatórios Bob reais entram após a realização do trabalho.

Depois de criar o repositório vazio, o código pode ser enviado por Git ou pelo conector GitHub. Se preferir usar GitHub CLI autenticado, a criação e envio podem ser feitos localmente após descompactar e inicializar o Git:

```bash
git init -b main
git add .
git commit -m "feat: initialize Elo Financeiro prototype"
gh repo create elo-financeiro-bb --private --source=. --push
```

A URL pública de demonstração solicitada pelo programa é diferente da URL do repositório. Um repositório privado não fornece, por si só, acesso ao protótipo para avaliadores. Confira permissões e hospedagem antes da submissão.
