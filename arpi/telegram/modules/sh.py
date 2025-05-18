import asyncio
import re
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
        self._lock = Lock()
        self.process = None
        self.output = ""
        Process.processes[self.command] = self
        asyncio.create_task(self._start())


    async def _start(self) -> None:
        self.process = await asyncio.create_subprocess_shell(self.command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        while True:
            line: bytes = await self.process.stdout.readline()
            if not line:
                break
            async with self._lock:
                self.output += re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", line.decode())
            await asyncio.sleep(0.1)
        await self.process.wait()
        await base.bot.send_message(self.chat_id, "Process executed\n" + self.description[-4000:], parse_mode="html")
        del Process.processes[self.command]


    @property
    def description(self) -> str:
        return (f"\t\t\t\tCommand: <code>{self.command}</code>\n"
                f"\t\t\t\tReturncode: <code>{self.process.returncode}</code>\n"
                f"\t\t\t\tOutput: <code>{self.output}</code>")


@base.router.callback_query(F.data.startswith("update_output"))
async def _update_output(callback: CallbackQuery) -> None:
    await callback.answer()
    index: int = int(callback.data.replace("process ", ""))
    process: Process = list(Process.processes.values())[index]
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text="Update output", callback_data=f"update_output {index}")]]
    try:
        await callback.message.edit_text(process.description[-4096:], parse_mode="html", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    except TelegramBadRequest:
        pass


@base.router.callback_query(F.data.startswith("process"))
async def _process(callback: CallbackQuery) -> None:
    await callback.answer()
    index: int = int(callback.data.replace("process ", ""))
    process: Process = list(Process.processes.values())[index]
    buttons: list[list[InlineKeyboardButton]] = [[InlineKeyboardButton(text="Update output", callback_data=f"update_output {index}")]]
    await callback.message.answer(process.description[-4096:], parse_mode="html", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


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
