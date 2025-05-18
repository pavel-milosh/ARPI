import asyncio
import random
import re
import string
from asyncio import Lock

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from .. import base


class Process:
    processes: dict = {}

    def __init__(self, chat_id: int, command: str) -> None:
        self.chat_id = chat_id
        self.command = command
        self.process = None
        self.output = ""
        self.identifier = "".join([random.choice(string.ascii_letters) for _ in range(16)])
        self._lock = Lock()
        Process.processes[self.identifier] = self
        asyncio.create_task(self._start())


    async def _start(self) -> None:
        self.process = await asyncio.create_subprocess_shell(self.command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        while True:
            line: bytes = await self.process.stdout.readline()
            if not line:
                break
            async with self._lock:
                self.output += re.sub(r"\[.*?m", "", line.decode())
            await asyncio.sleep(0.1)
        await self.process.wait()
        await base.bot.send_message(self.chat_id,  f"{self.description}\n\t\t\t\t<b>Process executed</b>"[-4000:], parse_mode="html")
        del Process.processes[self.identifier]


    @property
    def description(self) -> str:
        return (f"{self.output}\n"
                f"\t\t\t\tCommand: <code>{self.command}</code>\n"
                f"\t\t\t\tReturncode: <code>{self.process.returncode}</code>")


@base.router.callback_query(F.data.startswith("update_output"))
async def _update_output(callback: CallbackQuery) -> None:
    identifier: str = callback.data.replace("update_output ", "")
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text="Update output", callback_data=f"update_output {identifier}")]]
    try:
        await callback.message.edit_text(Process.processes[identifier].description[-4096:], parse_mode="html", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await callback.answer("Output updated")
    except TelegramBadRequest:
        await callback.answer("Output NOT updated", show_alert=True)
        pass


@base.router.callback_query(F.data.startswith("process"))
async def _process(callback: CallbackQuery) -> None:
    await callback.answer()
    identifier: str = callback.data.replace("process ", "")
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text="Update output", callback_data=f"update_output {identifier}")]]
    await callback.message.answer(Process.processes[identifier].description[-4096:], parse_mode="html", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@base.router.message(Command("processes"))
async def _processes(message: Message) -> None:
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text=process.command, callback_data=f"process {process.identifier}")] for process in Process.processes.values()]
    await message.answer(f"All alive processes:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@base.router.message(Command("sh"))
async def _sh(message: Message) -> None:
    command: str = message.text.replace("/sh", "", 1).lstrip()
    if command:
        Process(message.chat.id, command)
        await message.answer(f"Process created: <code>{command}</code>", parse_mode="html")
    else:
        await message.answer("Empty command")
