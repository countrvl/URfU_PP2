import re
from aiogram import Router

ru_car_plate_pattern = re.compile(r'^[авсенкмортху]\d{3}[авсенкмортху]{2}\d{2,3}$')
