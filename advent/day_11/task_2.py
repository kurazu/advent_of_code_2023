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
from .task_1 import parse_board

logger = logging.getLogger(__name__)


def get_row_weights(
    board: npt.NDArray[np.bool_], multiplication: int
) -> npt.NDArray[np.uint32]:
    return np.where(np.any(board, axis=1), np.uint64(1), np.uint64(multiplication))


def get_col_weights(
    board: npt.NDArray[np.bool_], multiplication: int
) -> npt.NDArray[np.uint32]:
    return np.where(np.any(board, axis=0), np.uint64(1), np.uint64(multiplication))


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board %dx%d:\n%s", board.shape[0], board.shape[1], board)
    multiplication = 1_000_000
    row_weights = get_row_weights(board, multiplication)
    col_weights = get_col_weights(board, multiplication)

    def calculate_distance(a: npt.NDArray[np.int64], b: npt.NDArray[np.int64]) -> int:
        (a_y, a_x) = a
        (b_y, b_x) = b
        min_y = min(a_y, b_y)
        max_y = max(a_y, b_y)
        min_x = min(a_x, b_x)
        max_x = max(a_x, b_x)
        y_range = slice(min_y + 1, max_y + 1)
        x_range = slice(min_x + 1, max_x + 1)
        y_weights = row_weights[y_range]
        x_weights = col_weights[x_range]
        y_sum: int = y_weights.sum()
        x_sum: int = x_weights.sum()
        return y_sum + x_sum

    non_empty_indices = np.argwhere(board)
    # non_empty_indices is a numpy array with y and x indices of each non-empty entry
    distances = it.starmap(calculate_distance, it.combinations(non_empty_indices, 2))
    return str(sum(distances))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
