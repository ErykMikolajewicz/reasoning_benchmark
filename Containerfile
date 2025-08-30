FROM python:3.13-slim-bookworm AS builder

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache uv==0.8.*
RUN uv sync --group google-cloud --no-dev --compile-bytecode


FROM python:3.13-slim-bookworm
ARG IMAGE_VERSION

LABEL org.opencontainers.image.authors="Eryk Mikołajewicz <eryk.mikolajewicz@gmail.com>" \
      org.opencontainers.image.version=${IMAGE_VERSION} \
      org.opencontainers.image.description="LLM reasoning benchmark, by playing chess." \
      org.opencontainers.image.source="https://github.com/ErykMikolajewicz/reasoning_benchmark" \
      maintainer="Eryk Mikołajewicz"

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
COPY /models_params /models_params
COPY /settings /settings
COPY main.py main.py

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "-m", "main"]
