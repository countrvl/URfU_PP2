from common.constants import CMD_REGISTER, CMD_REGISTER_CAR
from common.base import ru_car_plate_pattern
import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message


registration_router = Router()

class CarRegistration(StatesGroup):
    waiting_for_plate = State()


@registration_router.message(Command(CMD_REGISTER))
async def register_handler(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"http://backend:8000/booking/register?tg_id={message.from_user.id}")
            if response.status_code == 200:
                await message.answer("Вы успешно зарегистрированы!")
            elif response.status_code == 400:
                await message.answer("Вы уже зарегистрированы")
            else:
                await message.answer("Регистрация не удалась. Пожалуйста, попробуйте позже")
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к сервису регистрации. Пожалуйста, попробуйте позже")

@registration_router.message(Command(CMD_REGISTER_CAR))
async def register_car_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(CarRegistration.waiting_for_plate)
    await message.answer("Пожалуйста, введите номер вашего автомобиля (формат: а123вс99 или а123вс77, русские буквы)")


@registration_router.message(CarRegistration.waiting_for_plate)
async def process_car_plate(message: Message, state: FSMContext) -> None:
    car_plate = message.text.strip().lower()
    
    if not car_plate:
        await message.answer("Номер автомобиля не может быть пустым. Пожалуйста, попробуйте снова с /register_car")
        return
    
    if not ru_car_plate_pattern.match(car_plate):
        await message.answer("Неверный номер автомобиля. Пожалуйста, используйте формат типа а123вс99 или а123вс77, используя русские буквы")
        return
    
    await state.clear()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://backend:8000/booking/register-car?tg_id={message.from_user.id}&car_plate={car_plate}")
            if response.status_code == 200:
                await message.answer("Автомобиль успешно зарегистрирован!")
            elif response.status_code == 400:
                await message.answer("Вы уже зарегистрированы с этим номером автомобиля")
            elif response.status_code == 422:
                await message.answer("Неверный номер автомобиля. Пожалуйста, попробуйте снова")
            else:
                await message.answer("Регистрация не удалась. Пожалуйста, попробуйте позже")
        except httpx.RequestError:
            await message.answer("Не удалось подключиться к сервису регистрации. Пожалуйста, попробуйте позже")