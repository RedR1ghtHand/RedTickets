# Use Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv lock
RUN uv sync

COPY . .

CMD ["uv", "run", "python", "-m", "main"]