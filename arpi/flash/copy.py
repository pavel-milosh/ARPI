import os

from tqdm import tqdm


CHUNK_SIZE: int = 1024 * 1024


class CopyError(Exception):
    pass


def _single(source: str, destination: str) -> None:
    with open(source, "rb") as f_source, open(destination, "wb") as f_destination, tqdm(
        total=os.path.getsize(source),
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Copying {os.path.basename(destination)}"
    ) as bar:
        while True:
            chunk: bytes = f_source.read(CHUNK_SIZE)
            if not chunk:
                break
            f_destination.write(chunk)
            bar.update(len(chunk))


def _(source_folder: str, destination_folder: str) -> None:
    for root, _, filenames in os.walk(source_folder):
        destination_root: str = os.path.join(destination_folder, os.path.relpath(root, source_folder))
        os.makedirs(destination_root, exist_ok=True)
        for filename in filenames:
            source: str = os.path.join(root, filename)
            destination: str = os.path.join(destination_root, filename)
            try:
                _single(source, destination)
            except:
                raise CopyError()
