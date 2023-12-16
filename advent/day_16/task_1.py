from __future__ import annotations

import logging
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
) -> None:
    height, width = board.shape
    while True:
        new_position = position.add(direction)
        if not (0 <= new_position.y < height and 0 <= new_position.x < width):
            return  # out of bounds
        new_cell = board[new_position]
        energized[new_position] = True  # the light made it this far
        if new_cell == EMPTY:
            position = new_position
        elif new_cell == MIRROR_SLASH:
            direction = Point(direction.x, direction.y)
            position = new_position
        elif new_cell == MIRROR_BACKSLASH:
            direction = Point(-direction.x, -direction.y)
            position = new_position
        elif new_cell == HORIZONTAL_SPLITTER and direction.y == 0:
            position = new_position
        elif new_cell == HORIZONTAL_SPLITTER:
            light_up(
                board=board, energized=energized, position=new_position, direction=LEFT
            )
            light_up(
                board=board, energized=energized, position=new_position, direction=RIGHT
            )
            return
        elif new_cell == VERTICAL_SPLITTER and direction.x == 0:
            position = new_position
        elif new_cell == VERTICAL_SPLITTER:
            light_up(
                board=board, energized=energized, position=new_position, direction=UP
            )
            light_up(
                board=board, energized=energized, position=new_position, direction=DOWN
            )
            return
        else:
            raise ValueError(f"Unknown cell: {new_cell}")


def visualize_energized(energized: npt.NDArray[np.bool_]) -> str:
    return "\n".join("".join("#" if cell else "." for cell in row) for row in energized)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    energized = np.zeros_like(board, dtype=np.bool_)
    # start just beyond the board heading right
    position = Point(0, -1)
    direction = RIGHT
    light_up(board=board, energized=energized, position=position, direction=direction)
    logger.debug("Board:\n%s", visualize_energized(energized))
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
