import logging
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple, TypeAlias

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Node(NamedTuple):
    row: int
    col: int
    previous_move_was_vertical: bool


OFFSETS = [-3, -2, -1, 1, 2, 3]
GraphType: TypeAlias = dict[Node, dict[Node, int]]


def build_graph(board: npt.NDArray[np.uint8]) -> GraphType:
    # undirected graph
    # starting_node -> ending_node -> distance
    graph: GraphType = defaultdict(dict)
    height, width = board.shape
    for row in range(height):
        for col in range(width):
            for offset in OFFSETS:
                if 0 <= (target_row := row + offset) < height:
                    # consider vertical moves
                    current_node = Node(row, col, False)
                    target_node = Node(target_row, col, True)
                    cost = board[min(row, target_row) : max(row, target_row), col].sum()
                    graph[current_node][target_node] = cost
                if 0 <= (target_col := col + offset) < width:
                    # consider horizontal moves
                    current_node = Node(row, col, True)
                    target_node = Node(row, target_col, False)
                    cost = board[row, min(col, target_col) : max(col, target_col)].sum()
                    graph[current_node][target_node] = cost

    return graph


ALMOST_INFINITY = 2**32 - 1


def find_path(
    *, height: int, width: int, graph: GraphType, start: Node, ends: set[Node]
) -> int:
    unvisited: set[Node] = set()
    for row in range(height):
        for col in range(width):
            unvisited.add(Node(row, col, False))
            unvisited.add(Node(row, col, True))
    total = len(unvisited)
    logger.debug("Nodes to visit: %d", total)
    distances: dict[Node, int] = defaultdict(lambda: ALMOST_INFINITY)
    distances[start] = 0
    current = start
    while True:
        for neighbour, jump_cost in graph[current].items():
            if neighbour not in unvisited:
                continue
            cost = distances[current] + jump_cost
            distances[neighbour] = min(distances[neighbour], cost)
        unvisited.remove(current)
        if not unvisited:
            break
        current = min(unvisited, key=distances.__getitem__)
        assert distances[current] != ALMOST_INFINITY
        if len(unvisited) % 100 == 0:
            logger.debug(
                "Nodes to visit: %d/%d (%.1f%%)",
                len(unvisited),
                total,
                len(unvisited) / total * 100,
            )
    return min(distances[end] for end in ends)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, {c: int(c) for c in "123456789"})
    height, width = board.shape
    logger.debug("Board:\n%s", board)
    graph = build_graph(board)
    ends = {Node(height - 1, width - 1, False), Node(height - 1, width - 1, True)}
    cost_1 = find_path(
        graph=graph, start=Node(0, 0, False), ends=ends, height=height, width=width
    )
    cost_2 = find_path(
        graph=graph, start=Node(0, 0, True), ends=ends, height=height, width=width
    )
    return str(min(cost_1, cost_2))


if __name__ == "__main__":
    setup_logging()
    main()
