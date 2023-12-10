import logging
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, TypeAlias

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Cell(str, Enum):
    EMPTY = " "
    NORTH_SOUTH = "║"
    EAST_WEST = "═"
    NORTH_EAST = "╔"
    NORTH_WEST = "╗"
    SOUTH_EAST = "╚"
    SOUTH_WEST = "╝"
    INTERSECTION = "╬"


PARSE_MAP: dict[str, Cell] = {
    ".": Cell.EMPTY,
    "|": Cell.NORTH_SOUTH,
    "-": Cell.EAST_WEST,
    "F": Cell.NORTH_EAST,
    "7": Cell.NORTH_WEST,
    "L": Cell.SOUTH_EAST,
    "J": Cell.SOUTH_WEST,
    "S": Cell.INTERSECTION,
}


@dataclass
class Board:
    tiles: list[list[Cell]]

    @property
    def height(self) -> int:
        return len(self.tiles)

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    def __str__(self) -> str:
        return "\n".join("".join(cell.value for cell in row) for row in self.tiles)


def parse_cell(value: str) -> Cell:
    return PARSE_MAP[value]


def parse_board(lines: Iterable[str]) -> Board:
    tiles = [[parse_cell(c) for c in line] for line in lines]
    return Board(tiles)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board:\n%s", board)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
