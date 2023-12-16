from pathlib import Path
from typing import Iterable

import numpy as np
from numpy import typing as npt


def get_data_path(day: int, filename: str) -> Path:
    base_path = Path(__file__).parent.parent / "data"
    return base_path / f"day{day:02d}" / filename


def get_stripped_lines(filename: Path) -> Iterable[str]:
    with filename.open() as f:
        for line in f:
            yield line.rstrip("\n")


def parse_board(filename: Path, char_mapping: dict[str, int]) -> npt.NDArray[np.uint8]:
    return np.array(
        [[char_mapping[c] for c in line] for line in get_stripped_lines(filename)],
        dtype=np.uint8,
    )
