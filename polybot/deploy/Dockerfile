# Build from the polybot/ directory:  docker build -f deploy/Dockerfile -t polybot .
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Optional extras: anthropic (llm strategy), websockets (stream source).
# py-clob-client is intentionally omitted — install it only for live trading.
RUN pip install --no-cache-dir anthropic websockets

COPY polybot/ ./polybot/
COPY config.politics.json ./config.politics.json
COPY examples/ ./examples/

# Secrets come from the environment at runtime (-e / --env-file), never baked in.
ENTRYPOINT ["python", "-m", "polybot", "--config", "config.politics.json", "run", "--loop"]
