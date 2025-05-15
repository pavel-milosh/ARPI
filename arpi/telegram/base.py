from aiogram import Bot, Router, Dispatcher

from ..config import _ as config


bot: Bot = Bot(config["telegram"]["token"])
dp: Dispatcher = Dispatcher()
router: Router = Router()
