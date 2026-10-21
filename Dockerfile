FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY elo/ ./elo/
COPY web/ ./web/
COPY data/ ./data/

# A demonstração não precisa escrever arquivos nem executar como root.
USER 10001:10001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os; from urllib.parse import urlsplit; from urllib.request import Request, urlopen; origin = os.getenv('ELO_PUBLIC_ORIGIN', ''); headers = {'Host': urlsplit(origin).netloc} if origin else {}; request = Request('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/healthz', headers=headers); response = urlopen(request, timeout=3); response.close()"]

CMD ["python", "-m", "elo.server", "--host", "0.0.0.0"]
