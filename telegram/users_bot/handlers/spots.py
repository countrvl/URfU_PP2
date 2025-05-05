import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.users_bot.common.constants import CMD_SPOTS, CALLBACK_RESERVE

spots_router = Router()

@spots_router.message(Command(CMD_SPOTS))
async def get_spots_handler(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        try:
            spots_data = await get_spots()
            if spots_data is None:
                await message.answer("Не удалось подключиться к сервису. Пожалуйста, попробуйте позже")
                return

            if spots_data:
                spots_text = "Сейчас доступны следующие места:\n"

                spots_text += format_spots(spots_data)

                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Забронировать место", callback_data=CALLBACK_RESERVE)]
                    ]
                )
                await message.answer(
                    spots_text,
                    reply_markup=keyboard
                )
            else:
                await message.answer("В данный момент нет свободных мест")
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к сервису мест. Пожалуйста, попробуйте позже")

async def get_spots():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/booking/get-free-spots")
            if response.status_code == 200:
                spots_data = response.json()
                return spots_data
            else:
                return None
        except httpx.RequestError:
            return None

def format_spots(spots):
    spots_text = ""
    for spot in spots:
        description = spot.get('description', 'Без описания')
        number = spot.get('parking_spot_number', 'Без номера')
        spots_text += f"• Номер - {number}, описание: {description}\n"
    return spots_text
