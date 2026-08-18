FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8008 \
    HOST=0.0.0.0

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY examples /app/examples

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data

EXPOSE 8008

CMD ["python", "-m", "radar_comercial.web_cli"]
