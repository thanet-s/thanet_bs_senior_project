FROM python:3.11-slim-bullseye as builder

RUN mkdir /wheels
COPY . /wheels
WORKDIR /wheels
COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN pip install --upgrade pip && pip wheel --wheel-dir=/wheels -r requirements.txt


FROM python:3.11-slim-bullseye as prod

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y libpq5 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels

WORKDIR /wheels

RUN pip install --no-index --find-links=/wheels --no-cache-dir -r requirements.txt

COPY ./app /app

WORKDIR /app

COPY serve.sh /app/serve.sh
RUN chmod +x serve.sh && rm -rf /wheels

EXPOSE 8000

CMD ["./serve.sh"]
