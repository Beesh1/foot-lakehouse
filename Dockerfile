FROM python:3.12-slim
RUN pip install duckdb==0.10.2 fastapi uvicorn

RUN apt-get update && apt-get install -y wget

RUN wget https://github.com/benbjohnson/litestream/releases/download/v0.3.13/litestream-v0.3.13-linux-arm64.tar.gz \
    && tar -C /usr/local/bin -xzf litestream-v0.3.13-linux-arm64.tar.gz \
    && rm litestream-v0.3.13-linux-arm64.tar.gz

WORKDIR /app

COPY data /app/data

COPY scripts /app/scripts