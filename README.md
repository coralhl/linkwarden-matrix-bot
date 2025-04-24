# Matrix → Linkwarden Bot

Этот бот подключается к Matrix и добавляет отправленные в сообщениях ссылки в Linkwarden.

## 🧩 Возможности

- Поддержка E2EE (шифрованных чатов)
- Поиск и добавление ссылок из сообщений
- Отправка ссылок в указанную коллекцию Linkwarden

## 🛠 Настройка

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Создайте конфигурационный файл config.yaml:

```yaml
matrix:
  homeserver: "matrix.example.com"
  user_id: "@bot:example.com"
  password: "your_matrix_password"

linkwarden:
  base_url: "linkwarden.example.com"
  api_token: "your_linkwarden_api_token"
  collection_id: 1
```

3. Запуск бота:

```bash
python bot.py
```

4. 🚀 Docker

Для запуска через Docker:

```bash
docker build -t matrix-linkwarden-bot .
docker run --rm -v $(pwd)/config.yaml:/app/config.yaml matrix-linkwarden-bot
```

