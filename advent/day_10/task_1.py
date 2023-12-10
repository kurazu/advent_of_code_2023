from __future__ import annotations

import logging
import math
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, NamedTuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Cell(str, Enum):
    EMPTY = " "
    NORTH_SOUTH = "║"
    EAST_WEST = "═"
    SOUTH_EAST = "╔"
    SOUTH_WEST = "╗"
    NORTH_EAST = "╚"
    NORTH_WEST = "╝"
    START = "●"


PARSE_MAP: dict[str, Cell] = {
    ".": Cell.EMPTY,
    "|": Cell.NORTH_SOUTH,
    "-": Cell.EAST_WEST,
    "F": Cell.SOUTH_EAST,
    "7": Cell.SOUTH_WEST,
    "L": Cell.NORTH_EAST,
    "J": Cell.NORTH_WEST,
    "S": Cell.START,
}


class Position(NamedTuple):
    y: int
    x: int

    def add(self, other: Position) -> Position:
        return Position(y=self.y + other.y, x=self.x + other.x)


class MoveTuple(NamedTuple):
    position_offset: Position
    current_cells: set[Cell]
    next_cells: set[Cell]


MOVES: dict[str, MoveTuple] = {
    "north": MoveTuple(
        position_offset=Position(y=-1, x=0),
        current_cells={Cell.NORTH_EAST, Cell.NORTH_SOUTH, Cell.NORTH_WEST},
        next_cells={Cell.SOUTH_EAST, Cell.SOUTH_WEST, Cell.NORTH_SOUTH},
    ),
    "south": MoveTuple(
        position_offset=Position(y=1, x=0),
        current_cells={Cell.SOUTH_EAST, Cell.SOUTH_WEST, Cell.NORTH_SOUTH},
        next_cells={Cell.NORTH_EAST, Cell.NORTH_SOUTH, Cell.NORTH_WEST},
    ),
    "east": MoveTuple(
        position_offset=Position(y=0, x=1),
        current_cells={Cell.NORTH_EAST, Cell.EAST_WEST, Cell.SOUTH_EAST},
        next_cells={Cell.NORTH_WEST, Cell.EAST_WEST, Cell.SOUTH_WEST},
    ),
    "west": MoveTuple(
        position_offset=Position(y=0, x=-1),
        current_cells={Cell.NORTH_WEST, Cell.EAST_WEST, Cell.SOUTH_WEST},
        next_cells={Cell.NORTH_EAST, Cell.EAST_WEST, Cell.SOUTH_EAST},
    ),
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

    def __getitem__(self, position: Position) -> Cell:
        return self.tiles[position.y][position.x]

    def is_valid_position(self, position: Position) -> bool:
        return 0 <= position.y < self.height and 0 <= position.x < self.width

    def find_starting_point(self) -> Position:
        for y in range(self.height):
            for x in range(self.width):
                position = Position(y, x)
                if self[position] == Cell.START:
                    return position
        raise ValueError("No starting point found!")


def parse_board(lines: Iterable[str]) -> Board:
    tiles = [[PARSE_MAP[c] for c in line] for line in lines]
    return Board(tiles)


class BlindAlleyException(Exception):
    pass


def dfs(board: Board, history: list[Position]) -> list[Position]:
    tabs = "".join(" " for _ in range(len(history)))
    target_point = history[0]  # we want to come back to the starting point
    previous_point = history[-2]  # we only push forward, no backtracking
    current_point = history[-1]  # we are at the last position in history
    logger.debug(
        "%sCurrent position: %s [%s]", tabs, current_point, board[current_point].value
    )
    for name, move in MOVES.items():
        next_point = current_point.add(move.position_offset)
        if not board.is_valid_position(next_point):
            logger.warning(
                "%sCannot go %s from point %s (invalid position)",
                tabs,
                name,
                current_point,
            )
            continue
        if next_point == previous_point:
            logger.debug(
                "%sCannot go %s from point %s (backtracking)", tabs, name, current_point
            )
            continue
        current_cell = board[current_point]
        if current_cell not in move.current_cells:
            logger.warning(
                "%sCannot go %s from point %s (invalid current %s)",
                tabs,
                name,
                current_point,
                current_cell.value,
            )
            continue
        if next_point == target_point:
            logger.debug(
                "%sFound path %s by going %s from point %s [%s]",
                tabs,
                history,
                name,
                current_point,
                board[current_point].value,
            )
            return history
        next_cell = board[next_point]
        if next_cell not in move.next_cells:
            logger.warning(
                "%sCannot go %s from point %s (invalid next %s)",
                tabs,
                name,
                next_point,
                next_cell.value,
            )
            continue
        logger.debug(
            "%sExploring %s from point %s [%s] to %s [%s]",
            tabs,
            name,
            current_point,
            current_cell.value,
            next_point,
            next_cell.value,
        )
        try:
            history = dfs(board, [*history, next_point])
        except BlindAlleyException:
            logger.warning(
                "%sGoing %s from %s [%s] is a blind alley",
                tabs,
                name,
                current_point,
                current_cell.value,
            )
        else:
            logger.debug(
                "%sFound path %s by going %s from %s [%s]",
                tabs,
                history,
                name,
                current_point,
                current_cell.value,
            )
            return history
    logger.warning(
        "%sNo way out from point %s [%s]",
        tabs,
        current_point,
        board[current_point].value,
    )
    raise BlindAlleyException()


def traverse_board(board: Board, starting_point: Position) -> list[Position]:
    logger.debug(
        "Traversing board from starting point %s [%s]",
        starting_point,
        board[starting_point].value,
    )
    # from the starting point we can actually go in any direction
    for name, move in MOVES.items():
        next_point = starting_point.add(move.position_offset)
        if not board.is_valid_position(next_point):
            logger.warning("Cannot go %s from starting point (invalid position)", name)
            continue
        next_cell = board[next_point]
        if next_cell not in move.next_cells:
            logger.warning(
                "Cannot go %s from starting point (invalid cell %s)",
                name,
                next_cell,
            )
            continue
        logger.debug("Going %s from starting point [%s]", name, next_cell.value)
        try:
            history = dfs(board, [starting_point, next_point])
        except BlindAlleyException:
            logger.warning("Going %s from starting point is a blind alley", name)
        else:
            logger.debug("Found path %s by going %s from starting point", history, name)
            return history
    logger.warning("No way out from starting point")
    raise BlindAlleyException()


def format_history(board: Board, history: list[Position]) -> str:
    return " ".join(f"{board[position].value}" for position in history)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board:\n%s", board)
    starting_point = board.find_starting_point()
    logger.debug("Starting point: %s", starting_point)
    # increase max recursion depth
    sys.setrecursionlimit(board.height * board.width)
    history = traverse_board(board, starting_point)
    logger.debug("History: %s (len %d)", format_history(board, history), len(history))
    return str(math.ceil(len(history) / 2))


if __name__ == "__main__":
    setup_logging(logging.CRITICAL)
    main()
