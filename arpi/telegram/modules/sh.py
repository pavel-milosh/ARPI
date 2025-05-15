import asyncio
import random
import string
from subprocess import Popen

import aiofiles
from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from .. import base


class Process:
    processes: dict = {}

    def __init__(self, chat_id: int, command: str) -> None:
        self.__chat_id = chat_id
        self.__command = command
        self.__log_file = "".join([random.choice(string.ascii_letters) for _ in range(8)])
        self.__end_marker = "".join([random.choice(string.ascii_letters) for _ in range(8)])
        self.__popen = Popen(f"({command}; echo {self.__end_marker}) >> logs/{self.__log_file} 2>&1", shell=True)
        Process.processes[command] = self
        asyncio.create_task(self.__check_alive())


    async def __check_alive(self) -> None:
        while True:
            if await asyncio.to_thread(self.__popen.poll) is None and await self.is_alive():
                await asyncio.sleep(1)
                continue

            await asyncio.sleep(2)
            if self.__popen.returncode == 0:
                text: str = f"Process executed successfully: <code>{self.__command}</code>"
            else:
                text: str = f"Process executed with error (returncode {self.__popen.returncode}): <code>{self.__command}</code>"
            text += f"\nStdout:\n<code>{await self.log()}</code>"
            del Process.processes[self.__command]
            await base.bot.send_message(self.__chat_id, text, parse_mode="html")


    async def log(self) -> str:
        async with aiofiles.open(f"logs/{self.__log_file}", "r") as f:
            return await f.read()


    async def is_alive(self) -> bool:
        return self.__end_marker not in await self.log()


    #____________________PROPERTIES____________________
    @property
    def command(self) -> str:
        return self.__command


    @property
    def returncode(self) -> int:
        return self.__popen.returncode


@base.router.callback_query(F.data.startswith("process"))
async def _process(callback: CallbackQuery) -> None:
    message: Message = await callback.message.answer(".")
    process: Process = list(Process.processes.values())[int(callback.data.replace("process ", ""))]
    await callback.answer()
    while True:
        if process not in Process.processes.values():
            return
        text: str = (
            f"Process: <code>{process.command}</code>\n"
            f"Returncode: <code>{process.returncode}</code>\n"
            f"Stdout: \n<code>{await process.log()}</code>"
        )
        try:
            await message.edit_text(text, parse_mode="html")
        except TelegramBadRequest:
            pass
        await asyncio.sleep(1)


@base.router.message(Command("processes"))
async def _processes(message: Message) -> None:
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=list(Process.processes.keys())[i], callback_data=f"process {i}")] for i in range(len(Process.processes.keys()))]
    await message.answer(f"All alive processes:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@base.router.message(Command("sh"))
async def _sh(message: Message) -> None:
    command: str = message.text.replace("/sh", "", 1).lstrip()
    if command:
        Process(message.chat.id, command)
        await message.answer(f"Process created: <code>{command}</code>", parse_mode="html")
    else:
        await message.answer("Empty command")
