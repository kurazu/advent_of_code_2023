from __future__ import annotations

import logging
from collections import deque
from pathlib import Path
from typing import NamedTuple

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging

logger = logging.getLogger(__name__)


EMPTY = 0
MIRROR_SLASH = 1
MIRROR_BACKSLASH = 2
HORIZONTAL_SPLITTER = 3
VERTICAL_SPLITTER = 4

CHAR_MAP = {
    ".": EMPTY,
    "/": MIRROR_SLASH,
    "\\": MIRROR_BACKSLASH,
    "-": HORIZONTAL_SPLITTER,
    "|": VERTICAL_SPLITTER,
}


class Point(NamedTuple):
    y: int
    x: int

    def add(self, other: Point) -> Point:
        return Point(self.y + other.y, self.x + other.x)


LEFT = Point(0, -1)
RIGHT = Point(0, 1)
UP = Point(-1, 0)
DOWN = Point(1, 0)


def light_up(
    *,
    board: npt.NDArray[np.uint8],
    energized: npt.NDArray[np.bool_],
    position: Point,
    direction: Point,
    rays: deque[tuple[Point, Point]],
    memory: dict[tuple[Point, Point], bool],
) -> None:
    height, width = board.shape
    while True:
        if (position, direction) in memory:
            return
        memory[position, direction] = True
        new_position = position.add(direction)
        if not (0 <= new_position.y < height and 0 <= new_position.x < width):
            return  # out of bounds
        new_cell = board[new_position]
        energized[new_position] = True  # the light made it this far
        if new_cell == EMPTY:
            pass
        elif new_cell == MIRROR_SLASH:
            direction = Point(-direction.x, -direction.y)
        elif new_cell == MIRROR_BACKSLASH:
            direction = Point(direction.x, direction.y)
            pass
        elif new_cell == HORIZONTAL_SPLITTER and direction.y == 0:
            pass
        elif new_cell == HORIZONTAL_SPLITTER:
            rays.append((new_position, LEFT))
            rays.append((new_position, RIGHT))
            return
        elif new_cell == VERTICAL_SPLITTER and direction.x == 0:
            pass
        elif new_cell == VERTICAL_SPLITTER:
            rays.append((new_position, UP))
            rays.append((new_position, DOWN))
            return
        else:
            raise ValueError(f"Unknown cell: {new_cell}")
        position = new_position


def visualize_energized(energized: npt.NDArray[np.bool_]) -> str:
    return "\n".join("".join("#" if cell else "." for cell in row) for row in energized)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    energized = np.zeros_like(board, dtype=np.bool_)
    # start just beyond the board heading right
    rays = deque([(Point(0, -1), RIGHT)])
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

    logger.debug("Board:\n%s", visualize_energized(energized))
    return str(np.count_nonzero(energized))


if __name__ == "__main__":
    setup_logging()
    main()
