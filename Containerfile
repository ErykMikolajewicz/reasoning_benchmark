FROM python:3.13-slim-trixie AS builder

COPY pyproject.toml uv.lock ./
RUN apt-get update &&  apt-get install -y build-essential python3-dev

RUN pip install --no-cache uv==0.10.*
RUN uv sync --group google-cloud --no-dev --compile-bytecode


FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        tini \
        stockfish \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m benchmark_performer
USER benchmark_performer

ENV PATH="/.venv/bin:$PATH"
COPY --from=builder .venv /.venv

COPY /src /src
COPY /prompts /prompts
COPY /models_params /models_params

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "src/main.py"]
