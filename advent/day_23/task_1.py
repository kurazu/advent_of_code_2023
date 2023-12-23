import logging
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable, TypeAlias

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging

logger = logging.getLogger(__name__)

EMPTY = 0
WALL = 1
SLOPE_DOWN = 2
SLOPE_RIGHT = 3
SLOPE_UP = 4
SLOPE_LEFT = 5

CHAR_MAP = {
    ".": EMPTY,
    "#": WALL,
    "v": SLOPE_DOWN,
    ">": SLOPE_RIGHT,
    "<": SLOPE_LEFT,
    "^": SLOPE_UP,
}
NodeType: TypeAlias = tuple[int, int]

GraphType: TypeAlias = dict[NodeType, set[NodeType]]

MOVES: list[tuple[NodeType, int]] = [
    ((-1, 0), SLOPE_UP),
    ((+1, 0), SLOPE_DOWN),
    ((0, -1), SLOPE_LEFT),
    ((0, +1), SLOPE_RIGHT),
]


def get_neighbors(board: npt.NDArray[np.uint8], node: NodeType) -> Iterable[NodeType]:
    height, width = board.shape
    y, x = node
    for (dy, dx), slope in MOVES:
        ny = y + dy
        nx = x + dx
        if not (0 <= ny < height and 0 <= nx < width):
            continue  # move is out of bounds
        elif board[ny, nx] == EMPTY:
            yield ny, nx  # move is valid
        elif board[ny, nx] == slope:  # move over a slope
            yield y + dy * 2, x + dx * 2
        else:
            continue  # move is blocked by a wall


def build_graph(board: npt.NDArray[np.uint8], start_node: NodeType) -> GraphType:
    graph = defaultdict(set)
    visited: set[NodeType] = set()
    queue: deque[NodeType] = deque([start_node])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in get_neighbors(board, node):
            graph[node].add(neighbor)
            if neighbor not in visited:
                queue.append(neighbor)
    return graph


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    height, width = board.shape
    logger.debug("Board:\n%s", board)
    start_node: NodeType = (0, 1)
    end_node: NodeType = (height - 1, width - 2)
    graph = build_graph(board, start_node)
    logger.debug("Graph has %d vertices", sum(map(len, graph.values())))
    assert start_node in graph
    assert end_node in graph
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
