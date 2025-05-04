import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram import html
import re
from datetime import datetime
import time
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from spots import get_spots, format_spots
from telegram.users_bot.common.constants import CMD_RESERVE, CALLBACK_RESERVE, CMD_VIEW_RESERVATIONS, CALLBACK_CANCEL_RESERVATION
from telegram.users_bot.common.base import ru_car_plate_pattern

reserves_router = Router()

AVAILABLE_SPOTS_KEY = "available_spots"
SPOT_ID_KEY = "spot_id"
CAR_PLATE_KEY = "car_plate"
START_TIME_KEY = "start_time"
RESERVATION_IDS_KEY = "reservation_ids"

# Time format regex pattern
time_format_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d) (0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-\d{4}$')


class ReservationStates(StatesGroup):
    waiting_for_spot_number = State()
    waiting_for_car_plate = State()
    waiting_for_start_time = State()
    waiting_for_end_time = State()


class CancelReservationStates(StatesGroup):
    waiting_for_spot_number = State()


@reserves_router.callback_query(F.data == CALLBACK_RESERVE)
async def process_reserve_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    spots_data = await get_spots()

    if spots_data is None:
        await callback_query.message.answer("Не удалось подключиться к сервису. Пожалуйста, попробуйте позже")
        return

    if not spots_data:
        await callback_query.message.answer("В данный момент нет свободных мест")
        return

    await state.update_data({AVAILABLE_SPOTS_KEY: spots_data})

    await callback_query.message.answer("Пожалуйста, введите номер места, которое вы хотите забронировать")
    await state.set_state(ReservationStates.waiting_for_spot_number)


@reserves_router.message(Command(CMD_RESERVE))
async def reserve_command_handler(message: Message, state: FSMContext) -> None:
    try:
        spots_data = await get_spots()

        if spots_data is None:
            await message.answer("Не удалось подключиться к сервису. Пожалуйста, попробуйте позже")
            return

        if spots_data:
            await state.update_data({AVAILABLE_SPOTS_KEY: spots_data})
            await message.answer("Пожалуйста, выберите место для бронирования, введя его номер")
            spots_text = format_spots(spots_data)
            await message.answer(spots_text)
            await state.set_state(ReservationStates.waiting_for_spot_number)
        else:
            await message.answer("В данный момент нет свободных мест")
    except httpx.RequestError:
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже")
        return


@reserves_router.message(ReservationStates.waiting_for_spot_number)
async def process_spot_number(message: Message, state: FSMContext) -> None:
    entered_number = message.text.strip()

    state_data = await state.get_data()
    available_spots = state_data.get(AVAILABLE_SPOTS_KEY, [])

    selected_spot = None
    for spot in available_spots:
        if str(spot.get('parking_spot_number')) == entered_number:
            selected_spot = spot
            break

    if not selected_spot:
        await message.answer(f"Место с номером {entered_number} не найдено. Пожалуйста, введите действительный номер места")
        return

    spot_id = selected_spot.get('id')

    await state.update_data({SPOT_ID_KEY: spot_id})
    await state.set_state(ReservationStates.waiting_for_car_plate)
    await message.answer("Пожалуйста, введите номер вашего автомобиля (формат: а123вс99, русские буквы)")


@reserves_router.message(ReservationStates.waiting_for_car_plate)
async def process_car_plate(message: Message, state: FSMContext) -> None:
    car_plate = message.text.strip().lower()

    if not car_plate:
        await state.set_state(ReservationStates.waiting_for_car_plate)
        await message.answer("Номер автомобиля не может быть пустым. Пожалуйста, введите номер вашего автомобиля (формат: а123вс99, русские буквы)")
        return

    if not ru_car_plate_pattern.match(car_plate):
        await state.set_state(ReservationStates.waiting_for_car_plate)
        await message.answer("Неверный номер автомобиля. Пожалуйста, используйте формат типа а123вс99 или а123вс77, используя русские буквы")
        return

    await state.update_data({CAR_PLATE_KEY: car_plate})
    await state.set_state(ReservationStates.waiting_for_start_time)
    await message.answer("Пожалуйста, введите время начала (формат: ЧЧ:ММ ДД-ММ-ГГГГ)")


@reserves_router.message(ReservationStates.waiting_for_start_time)
async def process_start_time(message: Message, state: FSMContext) -> None:
    start_time = message.text.strip()

    if not time_format_pattern.match(start_time):
        await message.answer("Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ ДД-ММ-ГГГГ")
        return

    try:
        datetime.strptime(start_time, "%H:%M %d-%m-%Y")
    except ValueError:
        await message.answer("Неверная дата. Пожалуйста, используйте формат ЧЧ:ММ ДД-ММ-ГГГГ с корректной датой и попробуйте снова")
        return
    await state.update_data({START_TIME_KEY: start_time})
    await state.set_state(ReservationStates.waiting_for_end_time)
    await message.answer(f"Пожалуйста, введите {html.bold('время окончания')} (формат: ЧЧ:ММ ДД-ММ-ГГГГ)")


@reserves_router.message(ReservationStates.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext) -> None:
    end_time = message.text.strip()

    if not time_format_pattern.match(end_time):
        await message.answer("Неверный формат времени. Пожалуйста, используйте формат ЧЧ:ММ ДД-ММ-ГГГГ")
        return

    try:
        datetime.strptime(end_time, "%H:%M %d-%m-%Y")
    except ValueError:
        await message.answer("Неверная дата. Пожалуйста, используйте формат ЧЧ:ММ ДД-ММ-ГГГГ с корректной датой и попробуйте снова")
        return
        
    end_datetime = datetime.strptime(end_time, "%H:%M %d-%m-%Y")

    state_data = await state.get_data()
    start_time = state_data.get(START_TIME_KEY)
    spot_id = state_data.get(SPOT_ID_KEY)
    car_plate = state_data.get(CAR_PLATE_KEY)

    start_datetime = datetime.strptime(start_time, "%H:%M %d-%m-%Y")
    if end_datetime <= start_datetime:
        await message.answer("Время окончания должно быть позже времени начала. Пожалуйста, введите действительное время окончания")
        return
        
    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/booking/reserve-parking?tg_id={message.from_user.id}&place_id={spot_id}&car_plate={car_plate}&start_time={start_timestamp}&end_time={end_timestamp}"
            )
            await state.clear()
            if response.status_code == 200:
                await message.answer(
                    f"Бронирование успешно!\nМашина: {car_plate}\nС: {start_time}\nДо: {end_time}")
            elif response.status_code == 422:
                await message.answer("Неверный формат данных. Пожалуйста, попробуйте снова")
                await reserve_command_handler(message, state) # Re-prompt the reservation flow
            else:
                await message.answer("Не удалось забронировать место. Пожалуйста, попробуйте снова")
                await reserve_command_handler(message, state) # Re-prompt the reservation flow
    except httpx.RequestError:
        await state.clear()
        await message.answer("Не удалось подключиться к сервису бронирования. Пожалуйста, попробуйте позже")


@reserves_router.message(Command(CMD_VIEW_RESERVATIONS))
async def view_reservations_handler(message: Message, state: FSMContext) -> None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/booking/view-reservations?tg_id={message.from_user.id}"
            )
            
            if response.status_code == 200:
                reservations = response.json()
                
                if not reservations:
                    await message.answer("У вас нет активных бронирований")
                    return
                
                text = "Ваши бронирования:\n\n"
                
                # Store mapping between spot numbers and reservation IDs
                spot_to_reservation_id = {}
                
                for reservation in reservations:
                    start_datetime = datetime.fromtimestamp(reservation.get('start_time'))
                    end_datetime = datetime.fromtimestamp(reservation.get('end_time'))
                    
                    start_str = start_datetime.strftime("%H:%M %d-%m-%Y")
                    end_str = end_datetime.strftime("%H:%M %d-%m-%Y")
                    
                    spot_id = reservation.get('spot_id')
                    text += f"🅿️ Парковочное место: {spot_id}\n"
                    text += f"🚘 Машина: {reservation.get('car_plate')}\n"
                    text += f"🕒 Начало: {start_str}\n"
                    text += f"🕕 Конец: {end_str}\n\n"
                    
                    spot_to_reservation_id[str(spot_id)] = reservation.get('id')
                
                await state.update_data({RESERVATION_IDS_KEY: spot_to_reservation_id})
                
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Отменить бронирование", callback_data=CALLBACK_CANCEL_RESERVATION)]
                    ]
                )
                
                await message.answer(text, reply_markup=keyboard)
                
            elif response.status_code == 404:
                await message.answer("У вас нет бронирований")
            else:
                await message.answer("Не удалось получить ваши бронирования. Пожалуйста, попробуйте позже")
                
    except httpx.RequestError:
        await message.answer("Не удалось подключиться к серверу. Пожалуйста, попробуйте позже")


@reserves_router.callback_query(F.data == CALLBACK_CANCEL_RESERVATION)
async def process_cancel_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    
    state_data = await state.get_data()
    spot_to_reservation_id = state_data.get(RESERVATION_IDS_KEY, {})
    
    if not spot_to_reservation_id:
        await callback_query.message.answer("Нет бронирований для отмены")
        return
    
    await callback_query.message.answer("Пожалуйста, введите номер парковочного места, для которого вы хотите отменить бронирование:")
    await state.set_state(CancelReservationStates.waiting_for_spot_number)


@reserves_router.message(CancelReservationStates.waiting_for_spot_number)
async def process_cancel_spot_number(message: Message, state: FSMContext) -> None:
    entered_spot = message.text.strip()
    
    state_data = await state.get_data()
    spot_to_reservation_id = state_data.get(RESERVATION_IDS_KEY, {})
    
    if entered_spot not in spot_to_reservation_id:
        await message.answer(f"Не найдено бронирование для места {entered_spot}. Пожалуйста, введите действительный номер места")
        return
    
    reservation_id = spot_to_reservation_id[entered_spot]
    
    await state.clear()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:8000/booking/cancel-reservation/{reservation_id}"
            )
            
            if response.status_code == 200:
                await message.answer(f"Бронирование для места {entered_spot} успешно отменено")
            elif response.status_code == 404:
                await message.answer("Бронирование не найдено или уже отменено")
            else:
                await message.answer("Не удалось отменить бронирование. Пожалуйста, попробуйте позже")
    except httpx.RequestError:
        await message.answer("Не удалось подключиться к серверу. Пожалуйста, попробуйте позже")