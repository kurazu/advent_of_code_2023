from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Iterable, NamedTuple

import cv2
import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Direction(str, Enum):
    UP = "U"
    DOWN = "D"
    LEFT = "L"
    RIGHT = "R"


class Instruction(NamedTuple):
    direction: Direction
    distance: int
    color: str


def parse_instruction(line: str) -> Instruction:
    dir, dist, color = line.split()
    return Instruction(Direction(dir), int(dist), color[2:-1])


class Point(NamedTuple):
    y: int
    x: int

    def add(self, other: Point) -> Point:
        return Point(y=self.y + other.y, x=self.x + other.x)

    def multiply(self, factor: int) -> Point:
        return Point(y=self.y * factor, x=self.x * factor)


DIRECTION_TO_SHIFT = {
    Direction.UP: Point(y=-1, x=0),
    Direction.DOWN: Point(y=1, x=0),
    Direction.LEFT: Point(y=0, x=-1),
    Direction.RIGHT: Point(y=0, x=1),
}


def make_board(instructions: Iterable[Instruction]) -> npt.NDArray[np.uint8]:
    current = Point(0, 0)
    indices = [current]
    for instruction in instructions:
        shift = DIRECTION_TO_SHIFT[instruction.direction]
        for _ in range(instruction.distance):
            current = current.add(shift)
            indices.append(current)
    indices_array = np.array(indices)
    min_y = indices_array[:, 0].min()
    max_y = indices_array[:, 0].max()
    min_x = indices_array[:, 1].min()
    max_x = indices_array[:, 1].max()
    y_range = max_y - min_y + 1
    x_range = max_x - min_x + 1
    board = np.zeros((1 + y_range + 1, 1 + x_range + 1), dtype=np.uint8)
    for y, x in indices_array:
        board[y - min_y + 1, x - min_x + 1] = 1
    return board


def fill_board(board: npt.NDArray[np.uint8]) -> None:
    cv2.floodFill(board, None, (0, 0), 2)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    instructions = map(parse_instruction, lines)
    board = make_board(instructions)
    fill_board(board)
    volume = np.count_nonzero((board == 1) | (board == 0))
    return str(volume)


if __name__ == "__main__":
    setup_logging()
    main()
