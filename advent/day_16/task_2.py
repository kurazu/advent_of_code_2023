from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import CHAR_MAP, DOWN, LEFT, RIGHT, UP, Point, light_up

logger = logging.getLogger(__name__)


def simulate(point: Point, direction: Point, board: npt.NDArray[np.uint8]) -> int:
    energized = np.zeros_like(board, dtype=np.bool_)
    rays = deque([(point, direction)])
    memory: dict[tuple[Point, Point], bool] = {}
    while rays:
        position, direction = rays.popleft()
        light_up(
            board=board,
            energized=energized,
            position=position,
            direction=direction,
            rays=rays,
            memory=memory,
        )
    return np.count_nonzero(energized)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    # start just beyond the board heading right
    max_energized = 0
    height, width = board.shape
    for row in range(height):
        # try rays going left-to-right
        energized = simulate(Point(row, -1), RIGHT, board)
        max_energized = max(max_energized, energized)
        # try rays going right-to-left
        energized = simulate(Point(row, width), LEFT, board)
        max_energized = max(max_energized, energized)
    for col in range(width):
        # try rays going top-to-bottom
        energized = simulate(Point(-1, col), DOWN, board)
        max_energized = max(max_energized, energized)
        # try rays going bottom-to-top
        energized = simulate(Point(height, col), UP, board)
        max_energized = max(max_energized, energized)

    return str(max_energized)


if __name__ == "__main__":
    setup_logging()
    main()
