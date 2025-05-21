import asyncio
import os
import random
import string
import subprocess

from .copy import _ as copy
from .hash import _ as hash


def _algorithm(distribution: str, device: str) -> None:
    ventoy: str = os.getenv("ventoy")
    folder_distribution: str = os.getenv(distribution)
    dev_device: str = os.path.join("/dev", device)
    postfix: str = "".join(random.choices(string.ascii_uppercase, k=8))
    mount_point: str = os.path.join("/tmp", f"ARPI_FLASH_{device.upper()}_{postfix}")

    os.makedirs(mount_point, exist_ok=True)
    subprocess.run(f"yes | sudo bash {ventoy} -I -L ARnoLD {dev_device}", shell=True, check=True)
    subprocess.run(f"sudo mount -o sync {dev_device}1 {mount_point}", shell=True, check=True)
    copy(folder_distribution, mount_point)
    subprocess.run("sync", shell=True, check=True)
    hash(mount_point)
    subprocess.run(f"sudo umount -l {mount_point}", shell=True, check=True)
    os.rmdir(mount_point)
    print(f"Done {device}")


async def start(distribution: str, devices: list[str]) -> None:
    tasks = [
        asyncio.to_thread(_algorithm, distribution, device)
        for device in devices
    ]
    await asyncio.gather(*tasks)