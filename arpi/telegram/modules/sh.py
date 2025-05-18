import asyncio

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
        Process.processes[self.command] = self
        asyncio.create_task(self.__start())


    async def __start(self) -> None:
        self.process = await asyncio.create_subprocess_shell(self.command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        await self.process.wait()
        text: str = (f"Process executed\n"
                     f"\t\t\t\tCommand: <code>{self.command}</code>\n"
                     f"\t\t\t\tReturncode: <code>{self.process.returncode}</code>\n"
                     f"\t\t\t\tOutput: <code>{(await self.process.stdout.read()).decode().strip()}</code>")
        await base.bot.send_message(self.chat_id, text, parse_mode="html")
        del Process.processes[self.command]


    async def output(self) -> str:
        output: str = ""
        while True:
            line: bytes = await self.process.stdout.readline()
            if not line:
                break
            output += line.decode()
        return output


@base.router.callback_query(F.data.startswith("process"))
async def _process(callback: CallbackQuery) -> None:
    message: Message = await callback.message.answer(".")
    process: Process = list(Process.processes.values())[int(callback.data.replace("process ", ""))]
    await callback.answer()
    while True:
        if process not in Process.processes.values():
            return
        text: str = (f"Command: <code>{process.command}</code>\n"
                     f"Returncode: <code>{process.process.returncode}</code>\n"
                     f"Output: <code>{await process.output()}</code>")
        try:
            await message.edit_text(text, parse_mode="html")
        except TelegramBadRequest:
            pass
        await asyncio.sleep(0.5)


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
