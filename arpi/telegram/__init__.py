from aiogram.types import BotCommand

from . import base
from . import modules
from ..config import _ as config


async def initialize() -> None:
    base.dp.include_router(base.router)
    await base.bot.set_my_commands([BotCommand(command=k, description=v) for k, v in config["telegram"]["commands"].items()])
    await base.dp.start_polling(base.bot)