import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import aiohttp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
API_TOKEN = os.getenv('TELEGRAM_BOT_ML_API_KEY')
API_ENDPOINT_URL = os.getenv('API_ENDPOINT_URL_ML')
RECOGNIZE_URL = f"http://backend:8000/ml/recognize-license-plate"

# Проверка токена
if not API_TOKEN:
    logger.critical("Переменная окружения TELEGRAM_BOT_ML_API_KEY не найдена или пуста!")
    exit("Ошибка: TELEGRAM_BOT_ML_API_KEY не установлен.")

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру с кнопкой
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Отправить фото автомобиля")],
        [KeyboardButton(text="🆘 Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# --- Реальная интеграция с ML API ---
async def call_ml_api(image_bytes: bytes, endpoint_url: str):
    """Отправляет изображение в указанный API-эндпоинт"""
    logger.info("ML API called (image size: %d bytes)", len(image_bytes))
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file',
                           image_bytes,
                           filename='image.jpg',
                           content_type='image/jpeg')
            async with session.post(endpoint_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("ML API response: %s", result)
                    return result
                else:
                    logger.error("ML API returned error: %d", response.status)
                    return None
    except Exception as e:
        logger.exception("Network error while calling ML API:")
        return None


# --- Обработчики сообщений ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🚗 Gate Opener Bot\n\n"
        "Я бот для автоматического открытия шлагбаума. "
        "Отправьте фото автомобиля для распознавания.",
        reply_markup=start_keyboard
    )


@dp.message(F.text == "🚗 Отправить фото автомобиля")
async def request_photo(message: types.Message):
    await message.answer("Пожалуйста, отправьте фото автомобиля:")


@dp.message(F.text == "🆘 Помощь")
async def show_help(message: types.Message):
    await message.answer(
        "ℹ️ **Помощь**\n\n"
        "1. Нажмите '🚗 Отправить фото автомобиля'\n"
        "2. Сделайте четкое фото номерного знака\n"
        "3. Дождитесь результата распознавания\n\n"
        "Техподдержка: @support_username"
    )


@dp.message(F.photo)
async def handle_car_photo(message: types.Message):
    try:
        logger.info("Received photo from user %s", message.from_user.id)
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)

        image_bytes_io = await bot.download_file(file.file_path)
        image_bytes = image_bytes_io.read()
        image_bytes_io.close()

        logger.info("Photo downloaded, size: %d bytes", len(image_bytes))

        # === 2. Распознавание текста на номерном знаке (recognize) ===
        recognize_result = await call_ml_api(image_bytes, RECOGNIZE_URL)
        if recognize_result and "license_plate" in recognize_result:
            plate_number = recognize_result["license_plate"]
            confidence = recognize_result["confidence"]
            await message.reply(f"🔢 Номер: `{plate_number}` (уверенность: {confidence:.2f})", reply_markup=start_keyboard)
        elif recognize_result and "message" in recognize_result:
            await message.reply(f"❌ Не распознано: {recognize_result['message']}", reply_markup=start_keyboard)
        else:
            await message.reply("⚠️ Ошибка при распознавании номерного знака.", reply_markup=start_keyboard)

    except Exception as e:
        logger.exception("Error processing photo:")
        await message.reply(
            "⚠️ Произошла ошибка при обработке изображения. Попробуйте позже.",
            reply_markup=start_keyboard
        )


# --- Запуск бота ---
async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())