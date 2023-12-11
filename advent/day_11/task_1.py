from __future__ import annotations

import itertools as it
import logging
from pathlib import Path
from typing import Iterable

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


def parse_board(lines: Iterable[str]) -> npt.NDArray[np.bool_]:
    return np.array([[c == "#" for c in line] for line in lines], dtype=np.bool_)


def double_empty_rows(board: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
    pieces: list[npt.NDArray[np.bool_]] = []
    for row in board:
        if np.count_nonzero(row) == 0:
            pieces.append(row)
        pieces.append(row)
    expanded = np.stack(pieces)
    return expanded


def double_empty_columns(board: npt.NDArray[np.bool_]) -> npt.NDArray[np.bool_]:
    height, width = board.shape
    pieces: list[npt.NDArray[np.bool_]] = []
    for col_idx in range(width):
        col = board[:, col_idx]
        if np.count_nonzero(col) == 0:
            pieces.append(col)
        pieces.append(col)
    expanded = np.stack(pieces, axis=1)
    return expanded


def calculate_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # manhattan distance


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board %dx%d:\n%s", board.shape[0], board.shape[1], board)
    expanded_board = double_empty_columns(double_empty_rows(board))
    logger.debug(
        "Expanded board %dx%d:\n%s",
        expanded_board.shape[0],
        expanded_board.shape[1],
        expanded_board,
    )

    non_empty_indices = np.argwhere(expanded_board)
    # non_empty_indices is a numpy array with y and x indices of each non-empty entry
    distances = it.starmap(calculate_distance, it.combinations(non_empty_indices, 2))
    return str(sum(distances))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
