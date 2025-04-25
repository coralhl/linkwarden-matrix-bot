FROM python:3.13-alpine as base

FROM base as builder
RUN apk add --no-cache \
    build-base \
    cmake
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
# RUN pip install --install-option="--prefix=/install" -r /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY bot.py /app/bot.py
WORKDIR /app
CMD ["python", "bot.py"]
