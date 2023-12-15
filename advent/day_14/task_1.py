from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import numpy as np
from numpy import typing as npt
from typing_extensions import TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)

BoardType: TypeAlias = npt.NDArray[np.uint8]
EMPTY = 0
STATIC = 1
MOVING = 2

MAP = {
    "O": MOVING,
    "#": STATIC,
    ".": EMPTY,
}


def parse(lines: Iterable[str]) -> BoardType:
    return np.array([[MAP[c] for c in line] for line in lines], dtype=np.uint8)


def drop(board: BoardType) -> None:
    height, width = board.shape
    for row in range(1, height):
        logger.debug("Analyzing row %d", row)
        for col in range(width):
            if board[row][col] != MOVING:  # this one can't fall
                continue
            # this stone can fall
            logger.debug("Stone at %d,%d is movable", row, col)
            for candidate_row in range(row - 1, 0 - 1, -1):
                if board[candidate_row, col] == EMPTY:
                    logger.debug(
                        "Stone from %d,%d can fall to row %d", row, col, candidate_row
                    )
                    pass
                else:
                    logger.debug(
                        "Stone %d,%d cannot fall past row %d", row, col, candidate_row
                    )
                    break
            else:
                # Can fall off the board
                logger.debug("Stone from %d,%d could fall off the map", row, col)
                candidate_row = -1
                pass
            logger.debug(
                "Stone from %d,%d fell to %d,%d", row, col, candidate_row + 1, col
            )
            board[row, col] = EMPTY
            board[candidate_row + 1, col] = MOVING


def get_load(board: BoardType) -> int:
    height, width = board.shape
    weights = np.arange(height, 0, -1)[:, None]
    loads = (board == MOVING) * weights
    sum_of_load: int = np.sum(loads)
    return sum_of_load


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse(lines)
    logger.debug("Board:\n%s", board)
    drop(board)
    logger.debug("Dropped:\n%s", board)
    load = get_load(board)
    return str(load)


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
