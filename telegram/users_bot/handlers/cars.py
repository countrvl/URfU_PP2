import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from telegram.users_bot.common.constants import CMD_CARS

cars_router = Router()

@cars_router.message(Command(CMD_CARS))
async def view_cars_handler(message: Message) -> None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/booking/residents/tg_id/{message.from_user.id}/cars"
            )
            
            if response.status_code == 200:
                response_data = response.json()
                cars = response_data.get('cars', [])
                
                if not cars:
                    await message.answer("У вас нет зарегистрированных автомобилей")
                    return
                
                text = "Ваши зарегистрированные автомобили:\n\n"
                
                for i, car in enumerate(cars, 1):
                    car_plate = car.get('car_plate', 'Неизвестно')
                    text += f"{i}. {car_plate}\n"
                
                await message.answer(text)
            elif response.status_code == 404:
                await message.answer("У вас нет зарегистрированных автомобилей или вам необходимо зарегистрироваться")
            else:
                await message.answer("Не удалось получить список автомобилей. Пожалуйста, попробуйте позже")
                
    except httpx.RequestError:
        await message.answer("Не удалось подключиться к серверу. Пожалуйста, попробуйте позже") 