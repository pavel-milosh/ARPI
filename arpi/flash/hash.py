import hashlib
import os

from tqdm import tqdm


CHUNK_SIZE: int = 1024 * 1024


class HashError(Exception):
    pass


def _file(path: str) -> str:
    hash = hashlib.sha256()
    with open(path, "rb") as f, tqdm(
        total=os.path.getsize(path),
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Calculating hash for {os.path.basename(path)}"
    ) as pbar:
        while chunk := f.read(CHUNK_SIZE):
            hash.update(chunk)
            pbar.update(len(chunk))
    return hash.hexdigest()


def _(destination_folder: str) -> None:
    with open(os.path.join(destination_folder, "hashes.sha256"), "r") as f:
        for line in f:
            if not line.strip():
                continue
            expected_hash, rel_path = line.strip().split(None, 1)
            if _file(os.path.join(destination_folder, rel_path)).lower() != expected_hash.lower():
                raise HashError(f"Hash mismatch: {rel_path}")
