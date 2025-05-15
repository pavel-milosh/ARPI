import asyncio
import fcntl
import os
import subprocess
from subprocess import Popen

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from .. import base


class Process:
    processes: dict = {}

    def __init__(self, chat_id: int, command: str) -> None:
        self.__chat_id = chat_id
        self.__popen = Popen(command, shell=True, text=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.__buffer = ""
        fd = self.__popen.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        Process.processes[command] = self
        asyncio.create_task(self.__check_alive())


    async def __check_alive(self) -> None:
        await asyncio.to_thread(self.__popen.wait)
        if self.__popen.returncode == 0:
            text: str = f"Process executed successfully: <code>{self.command}</code>"
        else:
            text: str = f"Process executed with error (returncode {self.__popen.returncode}): <code>{self.command}</code>"
        text += f"\nStdout:\n<code>{self.stdout}</code>"
        del Process.processes[self.command]
        await base.bot.send_message(self.__chat_id, text, parse_mode="html")


    #____________________PROPERTIES____________________
    @property
    def command(self) -> str:
        return self.__popen.args


    @property
    def stdout(self) -> str:
        try:
            while True:
                chunk: str = self.__popen.stdout.read()
                if not chunk:
                    break
                self.__buffer += chunk
        except Exception:
            pass
        return self.__buffer


    @property
    def returncode(self) -> int:
        return self.__popen.returncode


@base.router.callback_query(F.data.startswith("process"))
async def _process(callback: CallbackQuery) -> None:
    message: Message = await callback.message.answer(".")
    process: Process = list(Process.processes.values())[int(callback.data.replace("process ", ""))]
    await callback.answer()
    while True:
        if process not in Process.processes:
            return
        text: str = (
            f"Process: <code>{process.command}</code>\n"
            f"Returncode: <code>{process.returncode}</code>\n"
            f"Stdout: \n<code>{process.stdout}</code>"
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
