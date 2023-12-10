import logging
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import ClassVar, Iterable, NamedTuple, TypeAlias

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
    START = "●"


PARSE_MAP: dict[str, Cell] = {
    ".": Cell.EMPTY,
    "|": Cell.NORTH_SOUTH,
    "-": Cell.EAST_WEST,
    "F": Cell.NORTH_EAST,
    "7": Cell.NORTH_WEST,
    "L": Cell.SOUTH_EAST,
    "J": Cell.SOUTH_WEST,
    "S": Cell.START,
}


class Position(NamedTuple):
    y: int
    x: int


@dataclass
class Board:
    APPROACHABLE_FROM_EAST: ClassVar[set[Cell]] = {
        Cell.EAST_WEST,
        Cell.NORTH_EAST,
        Cell.SOUTH_EAST,
    }
    APPROACHABLE_FROM_WEST: ClassVar[set[Cell]] = {
        Cell.EAST_WEST,
        Cell.NORTH_WEST,
        Cell.SOUTH_WEST,
    }
    APPROACHABLE_FROM_NORTH: ClassVar[set[Cell]] = {
        Cell.NORTH_SOUTH,
        Cell.NORTH_EAST,
        Cell.NORTH_WEST,
    }
    APPROACHABLE_FROM_SOUTH: ClassVar[set[Cell]] = {
        Cell.NORTH_SOUTH,
        Cell.SOUTH_EAST,
        Cell.SOUTH_WEST,
    }
    CAN_GO_EAST_FROM: ClassVar[set[Cell]] = {
        Cell.EAST_WEST,
        Cell.NORTH_EAST,
        Cell.SOUTH_EAST,
        Cell.START,
    }
    CAN_GO_WEST_FROM: ClassVar[set[Cell]] = {
        Cell.EAST_WEST,
        Cell.NORTH_WEST,
        Cell.SOUTH_WEST,
        Cell.START,
    }
    CAN_GO_NORTH_FROM: ClassVar[set[Cell]] = {
        Cell.NORTH_SOUTH,
        Cell.NORTH_EAST,
        Cell.NORTH_WEST,
        Cell.START,
    }
    CAN_GO_SOUTH_FROM: ClassVar[set[Cell]] = {
        Cell.NORTH_SOUTH,
        Cell.SOUTH_EAST,
        Cell.SOUTH_WEST,
        Cell.START,
    }
    tiles: list[list[Cell]]

    @property
    def height(self) -> int:
        return len(self.tiles)

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    def __str__(self) -> str:
        return "\n".join("".join(cell.value for cell in row) for row in self.tiles)

    def find_starting_point(self) -> Position:
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x] == Cell.START:
                    return Position(y, x)
        raise ValueError("No starting point found!")

    def maybe_go_east(self, position: Position) -> Position | None:
        new_position = Position(position.y, position.x + 1)
        # check if position is valid (not out of bounds)
        if new_position.x >= self.width:
            return None
        # get the cell at the new position
        cell = self.tiles[new_position.y][new_position.x]
        # check if the cell is approachable from the west
        if cell in self.APPROACHABLE_FROM_WEST:
            return new_position
        else:
            return None

    def maybe_go_west(self, position: Position) -> Position | None:
        new_position = Position(position.y, position.x - 1)
        # check if position is valid (not out of bounds)
        if new_position.x < 0:
            return None
        # get the cell at the new position
        cell = self.tiles[new_position.y][new_position.x]
        # check if the cell is approachable from the east
        if cell in self.APPROACHABLE_FROM_EAST:
            return new_position
        else:
            return None

    def maybe_go_north(self, position: Position) -> Position | None:
        new_position = Position(position.y - 1, position.x)
        # check if position is valid (not out of bounds)
        if new_position.y < 0:
            return None
        # get the cell at the new position
        cell = self.tiles[new_position.y][new_position.x]
        # check if the cell is approachable from the south
        if cell in self.APPROACHABLE_FROM_SOUTH:
            return new_position
        else:
            return None

    def maybe_go_south(self, position: Position) -> Position | None:
        new_position = Position(position.y + 1, position.x)
        # check if position is valid (not out of bounds)
        if new_position.y >= self.height:
            return None
        # get the cell at the new position
        cell = self.tiles[new_position.y][new_position.x]
        # check if the cell is approachable from the north
        if cell in self.APPROACHABLE_FROM_NORTH:
            return new_position
        else:
            return None

    def can_go_east_from(self, position: Position) -> bool:
        cell = self.tiles[position.y][position.x]
        return cell in self.CAN_GO_EAST_FROM

    def can_go_west_from(self, position: Position) -> bool:
        cell = self.tiles[position.y][position.x]
        return cell in self.CAN_GO_WEST_FROM

    def can_go_north_from(self, position: Position) -> bool:
        cell = self.tiles[position.y][position.x]
        return cell in self.CAN_GO_NORTH_FROM

    def can_go_south_from(self, position: Position) -> bool:
        cell = self.tiles[position.y][position.x]
        return cell in self.CAN_GO_SOUTH_FROM


def parse_cell(value: str) -> Cell:
    return PARSE_MAP[value]


def parse_board(lines: Iterable[str]) -> Board:
    tiles = [[parse_cell(c) for c in line] for line in lines]
    return Board(tiles)


def _traverse(board: Board, history: list[Position]) -> list[Position]:
    target = history[0]
    previous = history[-2]
    current = history[-1]
    if current == target:
        logger.debug("Reached target %s with steps %s", target, history)
        return history
    if (
        board.can_go_east_from(current)
        and (candidate := board.maybe_go_east(current)) is not None
        and candidate != previous
    ):
        logger.debug("Going east to %s", candidate)
        try:
            return _traverse(board, [*history, candidate])
        except BlindAlleyException:
            logger.warning("Going east from %s is a blind alley", current)
            pass
    if (
        board.can_go_west_from(current)
        and (candidate := board.maybe_go_west(current)) is not None
        and candidate != previous
    ):
        logger.debug("Going west to %s", candidate)
        try:
            return _traverse(board, [*history, candidate])
        except BlindAlleyException:
            logger.warning("Going west from %s is a blind alley", current)
            pass
    if (
        board.can_go_north_from(current)
        and (candidate := board.maybe_go_north(current)) is not None
        and candidate != previous
    ):
        logger.debug("Going north to %s", candidate)
        try:
            return _traverse(board, [*history, candidate])
        except BlindAlleyException:
            logger.warning("Going north from %s is a blind alley", current)
            pass
    if (
        board.can_go_south_from(current)
        and (candidate := board.maybe_go_south(current)) is not None
        and candidate != previous
    ):
        logger.debug("Going south to %s", candidate)
        try:
            return _traverse(board, [*history, candidate])
        except BlindAlleyException:
            logger.warning("Going south from %s is a blind alley", current)
            pass
    logger.warning("No way out from %s", current)
    raise BlindAlleyException()


class BlindAlleyException(Exception):
    pass


def traverse_board(board: Board, starting_point: Position) -> list[Position]:
    logger.debug("Traversing board from %s", starting_point)
    if (east_point := board.maybe_go_east(starting_point)) is not None:
        logger.debug("Going east to %s", east_point)
        try:
            return _traverse(board, [starting_point, east_point])
        except BlindAlleyException:
            logger.warning("Going east from %s is a blind alley", starting_point)
            pass
    else:
        logger.debug("Can't go east from %s", starting_point)

    if (west_point := board.maybe_go_west(starting_point)) is not None:
        logger.debug("Going west to %s", west_point)
        try:
            return _traverse(board, [starting_point, west_point])
        except BlindAlleyException:
            logger.warning("Going west from %s is a blind alley", starting_point)
            pass
    else:
        logger.debug("Can't go west from %s", starting_point)

    if (north_point := board.maybe_go_north(starting_point)) is not None:
        logger.debug("Going north to %s", north_point)
        try:
            return _traverse(board, [starting_point, north_point])
        except BlindAlleyException:
            logger.warning("Going north from %s is a blind alley", starting_point)
            pass
    else:
        logger.debug("Can't go north from %s", starting_point)

    if (south_point := board.maybe_go_south(starting_point)) is not None:
        logger.debug("Going south to %s", south_point)
        try:
            return _traverse(board, [starting_point, south_point])
        except BlindAlleyException:
            logger.warning("Going south from %s is a blind alley", starting_point)
            pass
    else:
        logger.debug("Can't go south from %s", starting_point)
    logger.warning("No way out from %s", starting_point)
    raise BlindAlleyException()


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    board = parse_board(lines)
    logger.debug("Board:\n%s", board)
    starting_point = board.find_starting_point()
    logger.debug("Starting point: %s", starting_point)
    history = traverse_board(board, starting_point)
    logger.debug("History: %s", history)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
