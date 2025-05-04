from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from constants import COMMANDS_DESCRIPTION

async def _set_commands(bot: Bot):
    commands = [ BotCommand(command=cmd, description=desc) for cmd, desc in COMMANDS_DESCRIPTION.items() ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(bot: Bot):
    await _set_commands(bot)
