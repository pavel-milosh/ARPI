import os
import time

from blake3 import blake3
from tqdm import tqdm


CHUNK_SIZE: int = 1024 * 1024 # Mb
MAX_SPEED: int = 10 # Mb/s


class HashError(Exception):
    pass


def _(iso_path: str) -> None:
    hashsum: str = open(f"{iso_path}.blake3", "r").read()
    hash: blake3 = blake3()
    with open(iso_path, "rb") as f, tqdm(
        total=os.path.getsize(iso_path),
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Comparing hash for {os.path.basename(iso_path)}"
    ) as pbar:
        while chunk := f.read(CHUNK_SIZE):
            hash.update(chunk)
            pbar.update(len(chunk))
            time.sleep(1 / MAX_SPEED)
    if hash.hexdigest() != hashsum:
        raise HashError()
