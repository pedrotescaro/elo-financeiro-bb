# Publicar a demonstração sintética

O pacote prepara uma demonstração pública por regras atrás de um proxy HTTPS. Não há autenticação bancária, persistência ou garantia de disponibilidade de produção. **Nenhum serviço Render foi criado ou validado por esta preparação.** Não configurar chaves IBM no ambiente público: esse modo recusa o planejador externo para impedir consumo anônimo da conta.

## Conferir localmente

O modo usual continua sendo `python -m elo.server`. Para conferir o pacote em uma máquina com Docker funcionando:

```bash
docker build -t elo-financeiro-demo .
docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges -p 127.0.0.1:8000:8000 elo-financeiro-demo
```

Abrir `http://127.0.0.1:8000`, autorizar, aprovar o plano, simular a despesa e revogar. Em outro terminal, consultar `http://127.0.0.1:8000/healthz`. A imagem usa Python 3.14, usuário sem privilégios e apenas biblioteca padrão. `PORT` define a porta; o padrão é 8000.

Na preparação de 21/10/2026, o Docker CLI estava disponível, mas o daemon local não estava ativo. Portanto, a execução desta imagem continua pendente.

## Render: passos manuais

1. Revisar a branch e os testes no GitHub. Na conta Render da equipe, escolher **New > Web Service > Git Provider**, autorizar acesso ao repositório e selecionar a revisão aprovada. Não tornar o repositório público apenas para hospedar.
2. Definir nome e região, selecionar **Language: Docker**, arquivo `Dockerfile` na raiz e plano **Free**. Manter o comando padrão da imagem. O processo escuta em `0.0.0.0` e lê `PORT`, definido pela Render.
3. Em **Environment**, configurar `ELO_PUBLIC_ORIGIN=https://pendente.invalid` como domínio provisório. Não adicionar `ELO_PLANNER=watsonx` nem credenciais IBM. Em **Health Checks**, definir `/healthz`.
4. Criar o serviço e copiar a URL HTTPS atribuída pela Render. Substituir imediatamente a origem provisória pela URL exata, sem barra final ou caminho, por exemplo `https://nome-atribuido.onrender.com`. Salvar e executar um novo deploy. Enquanto a origem divergir da URL, a interface e a API serão rejeitadas. `/healthz` continua respondendo 200, sem criar sessão nem consumir o limite de requisições.
5. Conferir o commit em **Deploys**, aguardar o health check passar e abrir a URL em janela anônima. Se alterar o domínio, atualizar também `ELO_PUBLIC_ORIGIN`. Não copiar um endereço de exemplo como se fosse a URL publicada.
6. Conferir a jornada completa em dois navegadores: consentimento e planos devem permanecer separados. Após expiração ou reinício, atualizar a página para iniciar outra sessão. Registrar URL, commit, data e resultado reais em `docs/VERIFICACAO.md`.

A Render documenta [deploy com Docker](https://render.com/docs/docker), [configuração de serviços e porta](https://render.com/docs/web-services), [health checks](https://render.com/docs/health-checks) e [TLS gerenciado](https://render.com/docs/tls). O HTTPS termina na borda da plataforma; o processo recebe HTTP interno. Não expor diretamente a porta do contêiner na internet.

## Limites da demonstração

Sessões expiram após 30 minutos de inatividade e são limitadas a 100; requisições têm limite de 120 por minuto por IP da conexão, e há no máximo 16 workers. A origem pública configurada determina Host, Origin e cookie `Secure`. A API aceita apenas a própria origem, sem liberar CORS para outros sites.

O servidor ignora cabeçalhos de IP enviados pelo visitante. Atrás de um proxy, vários visitantes podem compartilhar o mesmo limite. Esses controles são conservadores e não substituem a proteção da borda nem constituem defesa medida contra DDoS. O modo público contém somente os cenários sintéticos do repositório.

No [plano Free](https://render.com/docs/free), o serviço dorme após 15 minutos sem tráfego e a retomada leva cerca de um minuto. Reinícios descartam sessões. As 750 horas mensais são compartilhadas pelo workspace; há limites de tráfego e builds. Excedentes podem suspender recursos ou gerar cobrança quando há meio de pagamento. Conferir as condições e os limites na conta antes de criar o serviço; não presumir gratuidade ilimitada. Fontes consultadas em 21/10/2026.

Continuam manuais: criar a hospedagem, conferir custos e permissões, executar o teste externo, gravar evidências e fornecer o link aos avaliadores.
