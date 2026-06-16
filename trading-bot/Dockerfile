FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot
COPY config.json ./config.json

# State (open positions / stops) is persisted here — mount it as a volume.
VOLUME ["/app/state"]

# Live/demo trading. Keys come from the environment (see .env / compose).
CMD ["python", "-m", "bot.main", "--config", "config.json", "--mode", "live"]
