from __future__ import annotations

import logging
from collections import deque
from pathlib import Path
from typing import Iterable, NamedTuple

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging

logger = logging.getLogger(__name__)

EMPTY = 0
WALL = 1
START = 2

CHAR_MAPPING = {
    ".": EMPTY,
    "#": WALL,
    "S": START,
}


class Position(NamedTuple):
    y: int
    x: int

    def add(self, other: Position) -> Position:
        return Position(self.y + other.y, self.x + other.x)


MOVES = [
    Position(-1, 0),
    Position(0, 1),
    Position(1, 0),
    Position(0, -1),
]


def get_neighbours(board: npt.NDArray[np.uint8], pos: Position) -> Iterable[Position]:
    height, width = board.shape
    for move in MOVES:
        new_pos = pos.add(move)
        if (
            0 <= new_pos.y < height
            and 0 <= new_pos.x < width
            and board[new_pos] != WALL
        ):
            yield new_pos


def dijkstra(
    board: npt.NDArray[np.uint8], start: Position, max_distance: int
) -> npt.NDArray[np.float32]:
    distances = np.full(board.shape, np.inf, dtype=np.float32)
    distances[start] = 0
    queue = deque([start])

    while queue:
        current = queue.popleft()
        neighbours = get_neighbours(board, current)
        for neighbour in neighbours:
            new_distance = distances[current] + 1
            if distances[neighbour] > new_distance:
                distances[neighbour] = new_distance
                queue.append(neighbour)

    return distances


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAPPING)
    (start,) = np.argwhere(board == START)
    start_tuple = Position(*start)
    board[start_tuple] = EMPTY
    logger.debug("Board:\n%s", board)
    logger.debug("Start: %s", start)
    max_distance = 64
    distances = dijkstra(board, start_tuple, max_distance=max_distance)
    logger.debug("Distances:\n%s", distances)
    possible_plots = (distances <= max_distance) & (distances % 2 == 0)
    logger.debug("Possible plots:\n%s", possible_plots)
    number_of_plots = np.count_nonzero(possible_plots)
    return str(number_of_plots)


if __name__ == "__main__":
    setup_logging()
    main()
