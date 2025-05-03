import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any

# --- Библиотека aiogram (для бота) ---
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message

# --- Настройки Бота (Заменить 'xxxx' на реальный токен!) ---
API_TOKEN = 'хххххх'  # <--- ВАЖНО: Заменить на реальный токен бота!
API_ENDPOINT_URL = 'http://127.0.0.1:8000/recognize'

# --- Инициализация Бота и Диспетчера ---
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Объекты влияния: message.answer
@dp.message(CommandStart())
async def handle_start(message: Message):
    """Отправляет приветственное сообщение."""
    await message.answer("Привет! Отправь мне фото автомобильного номера, и я попробую его распознать.")

# Начало контракта
# Контракт: Обрабатывает полученное от пользователя фото.
# Эта функция вызывается, когда пользователь отправляет фотографию в чат с ботом.
# Она скачивает фото, отправляет его в API для распознавания и сообщает результат пользователю.
# Входные данные: message (объект сообщения aiogram, содержащий фото).
# Выходные данные: Сообщение пользователю в Telegram с результатом обработки.
# Тестовый условия:
# 1. Пользователь отправил фото -> бот ответил "Фото получено..." -> бот ответил результатом от API.
# 2. API вернул успех (номер разрешен) -> бот ответил "Номер X... Шлагбаум открыт".
# 3. API вернул успех (номер не разрешен) -> бот ответил "Номер X... отсутствует в списке".
# 4. API вернул ошибку распознавания -> бот ответил "Не удалось распознать...".
# 5. API недоступен или вернул ошибку сервера -> бот ответил "Произошла ошибка...".
# Ключевые понятия как ссылки на домены знаний: [чат-бот, Telegram Bot API, обработка медиафайлов, асинхронность, шлагбаум]
# Function handle_photo (message: Message)
# Объекты влияния: download_photo, send_photo_to_api, parse_api_response, message.answer
# Регистрируем хендлер, который сработает ТОЛЬКО на сообщения с фото (F.photo)
@dp.message(F.photo)
async def handle_photo(message: Message):
    """
    Обрабатывает входящее сообщение с фотографией от пользователя.
    """
    # Проверка на наличие фото уже не нужна, т.к. используется фильтр F.photo
    # Но на всякий случай оставим проверку самого объекта photo
    if not message.photo:
        logging.warning("Received message matched F.photo but message.photo is empty.")
        return

    await message.answer("Фото получено, обрабатываю...")
    logging.info(f"Received photo from user {message.from_user.id}")

    try:
        # 1. Скачиваем фото (лучшее качество - последний элемент списка)
        photo_bytes = await download_photo(bot, message.photo[-1].file_id)
        if not photo_bytes:
            await message.answer("Не удалось загрузить фото из Telegram.")
            return

        # 2. Отправляем фото в API
        logging.info(f"Sending photo to API: {API_ENDPOINT_URL}")
        api_response = await send_photo_to_api(photo_bytes, API_ENDPOINT_URL)
        logging.info(f"Received API response: {api_response}") # Логируем ответ API

        # 3. Обрабатываем ответ и отвечаем пользователю
        user_response = parse_api_response(api_response)
        await message.answer(user_response)

    except Exception as e:
        logging.error(f"Error handling photo for user {message.from_user.id}: {e}", exc_info=True) # Логирование ошибки со стеком
        await message.answer("Произошла внутренняя ошибка при обработке фото. Попробуйте позже.")
# Конец функции handle_photo


# Начало контракта
# Контракт: Скачивает файл фотографии с серверов Telegram.
# Эта функция использует file_id для получения и загрузки файла в виде байтов.
# Входные данные: bot (экземпляр aiogram.Bot), file_id (строка, идентификатор файла).
# Выходные данные: Байты файла фотографии (bytes) или None в случае ошибки.
# Тестовый условия:
# 1. Передан корректный file_id -> функция вернула bytes.
# 2. Передан некорректный file_id -> функция вернула None или вызвала исключение aiogram.
# 3. Ошибка сети при скачивании -> функция вернула None или вызвала исключение.
# Ключевые понятия как ссылки на домены знаний: [чат-бот, Telegram Bot API, работа с файлами, асинхронность]
# Function download_photo (bot: Bot, file_id: str)
# Объекты влияния: bot.get_file, bot.download_file
async def download_photo(bot_instance: Bot, file_id: str) -> Optional[bytes]:
    """
    Скачивает файл по file_id с серверов Telegram.
    """
    try:
        logging.info(f"Getting file info for file_id: {file_id}")
        file_info = await bot_instance.get_file(file_id)
        if not file_info.file_path:
             logging.warning(f"No file_path found for file_id: {file_id}")
             return None

        logging.info(f"Downloading file from path: {file_info.file_path}")
        # Используем download для получения байтов напрямую (если доступно в вашей версии aiogram)
        # или download_file для получения объекта BytesIO
        downloaded_io = await bot_instance.download(file_info)

        if downloaded_io:
             return downloaded_io.read()
        else:
             logging.warning(f"Failed to download file (download method returned None) for file_id: {file_id}")
             return None
    except Exception as e:
        logging.error(f"Error downloading file {file_id}: {e}", exc_info=True)
        return None
# Конец функции download_photo


# Начало контракта
# Контракт: Отправляет байты фотографии на API-эндпоинт распознавания.
# Эта функция формирует multipart/form-data запрос и отправляет его на указанный URL.
# Входные данные: photo_bytes (байты изображения), api_url (URL эндпоинта API).
# Выходные данные: Словарь (dict) с JSON-ответом от API или None в случае ошибки сети/API.
# Тестовый условия:
# 1. API доступен, запрос корректен -> функция вернула dict с ответом API.
# 2. API недоступен (Connection Error) -> функция вернула None.
# 3. API вернул статус не 200 OK -> функция вернула None.
# 4. API вернул невалидный JSON -> функция вернула None.
# Ключевые понятия как ссылки на домены знаний: [HTTP, REST API, multipart/form-data, aiohttp, асинхронность, сетевые запросы]
# Function send_photo_to_api (photo_bytes: bytes, api_url: str)
# Объекты влияния: aiohttp.ClientSession
async def send_photo_to_api(photo_bytes: bytes, api_url: str) -> Optional[Dict[str, Any]]:
    """
    Отправляет фото в виде байтов на API эндпоинт.
    """
    if not photo_bytes:
        logging.warning("send_photo_to_api called with empty photo_bytes")
        return None

    form_data = aiohttp.FormData()
    # Ключ 'file' должен совпадать с тем, что ожидает FastAPI эндпоинт (@app.post("/recognize", file: UploadFile = File(...)))
    form_data.add_field('file', photo_bytes, filename='image.jpg', content_type='image/jpeg')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=form_data) as response:
                logging.info(f"API response status: {response.status}")
                if response.status == 200:
                    try:
                        # Читаем ответ как JSON
                        response_data = await response.json()
                        return response_data
                    except aiohttp.ContentTypeError:
                        # Если API вернул не JSON, хотя статус 200
                        response_text = await response.text()
                        logging.error(f"API response is not valid JSON. Status: {response.status}. Body: {response_text[:500]}")
                        return None
                    except Exception as json_error:
                        # Другие ошибки при чтении JSON
                        logging.error(f"Error decoding API JSON response: {json_error}", exc_info=True)
                        return None
                else:
                    # Если статус ответа API не 200 OK
                    response_text = await response.text()
                    logging.error(f"API request failed with status: {response.status}. Body: {response_text[:500]}")
                    return None
    except aiohttp.ClientConnectorError as e:
        # Ошибка соединения с API (недоступен, неверный URL и т.д.)
        logging.error(f"Could not connect to API at {api_url}: {e}")
        return None
    except Exception as e:
        # Другие непредвиденные ошибки при отправке запроса
        logging.error(f"Error sending photo to API: {e}", exc_info=True)
        return None
# Конец функции send_photo_to_api


# Начало контракта
# Контракт: Парсит ответ от API и формирует сообщение для пользователя.
# Эта функция принимает JSON-ответ от API и преобразует его в человекочитаемую строку.
# Входные данные: api_response (словарь с ответом от API или None).
# Выходные данные: Строка с сообщением для пользователя.
# Тестовый условия:
# 1. api_response = None -> "Произошла ошибка при связи с сервером...".
# 2. api_response = {"status": "error", "message": "Plate not detected"} -> "Не удалось обнаружить номер на фото...".
# 3. api_response = {"status": "success", "plate": "A123BC77", "is_allowed": true} -> "Номер A123BC77 распознан. Шлагбаум открыт.".
# 4. api_response = {"status": "success", "plate": "X987YZ99", "is_allowed": false} -> "Номер X987YZ99 распознан, но отсутствует в списке разрешенных.".
# 5. api_response = {"status": "error", "message": "Recognition confidence too low"} -> "Не удалось распознать номер на фото...".
# Ключевые понятия как ссылки на домены знаний: [JSON, обработка ответов API, логика приложения, чат-бот, шлагбаум]
# Function parse_api_response (api_response: Optional[Dict[str, Any]])
# Объекты влияния: (нет прямых вызовов других функций)
def parse_api_response(api_response: Optional[Dict[str, Any]]) -> str:
    """
    Преобразует ответ от API в сообщение для пользователя.
    """
    if api_response is None:
        return "Произошла ошибка при связи с сервером распознавания. Попробуйте позже."

    status = api_response.get("status")

    if status == "success":
        plate = api_response.get("plate", "N/A") # Получаем номер или "N/A" если ключа нет
        is_allowed = api_response.get("is_allowed") # Получаем флаг доступа

        if is_allowed is None: # Проверка на случай, если ключ 'is_allowed' отсутствует
             logging.warning(f"API response 'is_allowed' key is missing for plate {plate}")
             return f"Номер {plate} распознан, но статус доступа не определен."
        elif is_allowed:
            # Имитация открытия шлагбаума (сообщением)
            return f"Номер {plate} распознан. Шлагбаум открыт."
        else:
            return f"Номер {plate} распознан, но отсутствует в списке разрешенных."

    elif status == "error":
        message = api_response.get("message", "Неизвестная ошибка распознавания")
        logging.warning(f"API returned error status: {message}")
        # Уточняем сообщения для пользователя
        if "Plate not detected" in message:
             return "Не удалось обнаружить номер на фото. Пожалуйста, попробуйте сделать более четкий снимок."
        elif "confidence too low" in message:
             return "Не удалось распознать номер на фото с достаточной уверенностью. Попробуйте сделать более четкий снимок."
        elif "Failed to crop" in message: # Добавлено для ошибки обрезки
             return "Ошибка при обработке области номера. Попробуйте другой ракурс."
        else:
            # Общее сообщение об ошибке от API
            return f"Ошибка обработки фото: {message}. Попробуйте позже."
    else:
        # Если структура ответа API не соответствует ожиданиям
        logging.error(f"Received unexpected API response format: {api_response}")
        return "Получен некорректный ответ от сервера распознавания."
# Конец функции parse_api_response


# --- Главная функция для запуска бота ---
async def main():
    """Основная функция для настройки и запуска бота."""
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.info("Starting bot...")

    # Опционально: Пропуск старых апдейтов при перезапуске
    # await bot.delete_webhook(drop_pending_updates=True)

    # Регистрация хендлеров (уже сделана с помощью @dp.message декораторов)
    # dp.message.register(handle_start, CommandStart())
    # dp.message.register(handle_photo, F.photo)

    # Запуск процесса получения апдейтов от Telegram
    try:
        await dp.start_polling(bot)
    finally:
        # Корректное завершение сессии бота при остановке
        await bot.session.close()
        logging.info("Bot stopped.")

# --- Точка входа для запуска скрипта ---
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.critical(f"Unhandled exception at top level: {e}", exc_info=True)
