import simplematrixbotlib as botlib
import http.client
import json
import yaml
import re
import asyncio
from urllib.parse import urlparse

# Загрузка конфигурации из YAML файла
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Настройки для подключения к Matrix и Linkwarden
# Обработка base_url (без схемы)
linkwarden_base = config["linkwarden"]["base_url"]
if linkwarden_base.startswith("https://"):
    linkwarden_base = urlparse(linkwarden_base).hostname  # Убираем схему

# Обработка homeserver (с схемой)
homeserver = config["matrix"]["homeserver"]
if not homeserver.startswith("https://"):
    homeserver = "https://" + homeserver  # Добавляем схему

user_id = config["matrix"]["user_id"]
password = config["matrix"]["password"]  # Пароль для входа в Matrix
linkwarden_token = config["linkwarden"]["api_token"]
collection_id = config["linkwarden"].get("collection_id", 1)  # Используем collection_id из конфигурации, по умолчанию 1

# Паттерн для извлечения URL из сообщений
url_pattern = re.compile(r"https?://\S+")

# Функция отправки ссылки в Linkwarden
def send_to_linkwarden(url: str) -> bool:
    conn = http.client.HTTPSConnection(linkwarden_base)
    payload = json.dumps({
        "name": url,  # Можно установить имя ссылки как сам URL
        "url": url,
        "type": "url",
        "description": "No description provided",  # Можете добавить описание, если нужно
        "tags": [],  # Можете добавить теги, если нужно
        "collection": {
            "id": collection_id  # Используем collection_id из конфигурации
        }
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {linkwarden_token}'
    }
    
    try:
        # Отправляем запрос
        conn.request("POST", "/api/v1/links", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(f"Linkwarden API response: {data.decode('utf-8')}")
        
        # Проверка статус-кода ответа
        if res.status == 200:
            # Преобразуем ответ в JSON и проверяем наличие id в response
            response_json = json.loads(data.decode('utf-8'))
            if 'response' in response_json and 'id' in response_json['response']:
                return True
            else:
                error_message = response_json.get('error', 'Unknown error')
                print(f"Error adding link: {error_message}")
                return False
        else:
            # Если статус не 200, выводим сообщение из ответа
            response_json = json.loads(data.decode('utf-8'))
            error_message = response_json.get('response', 'Unknown error')
            print(f"Error adding link: {error_message}")
            return False
    except Exception as e:
        print(f"Error while connecting to Linkwarden API: {e}")
        return False


# Конфигурация бота
config = botlib.Config()
config.emoji_verify = True
config.ignore_unverified_devices = True
config.encryption_enabled = True  # Включаем поддержку шифрования для зашифрованных сообщений

# Создаем бота
creds = botlib.Creds(homeserver, user_id, password=password)
bot = botlib.Bot(creds, config)

# Префикс для команды
PREFIX = '!'

# Обработка сообщений
@bot.listener.on_message_event
async def handle_message(room, message):
    # Проверяем, что это не сообщение от самого бота
    if message.sender == bot.creds.username:  # Используем username вместо user_id
        return
    
    # Извлекаем ссылки из сообщения
    urls = url_pattern.findall(message.body)
    if not urls:
        return
    
    # Отправляем ссылки в Linkwarden
    for url in urls:
        success = send_to_linkwarden(url)
        if success:
            await bot.api.send_text_message(room.room_id, f"✅ Добавлено в Linkwarden: {url}")
        else:
            await bot.api.send_text_message(room.room_id, f"❌ Не удалось добавить ссылку: {url}")

# Запуск бота с асинхронным ожиданием
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(bot.run())  # Ожидаем завершения работы бота
except Exception as e:
    print(f"Ошибка при запуске бота: {e}")
finally:
    print("Бот завершил свою работу.")
