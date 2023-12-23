import logging
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable, TypeAlias

import numpy as np
from matplotlib import colors
from matplotlib import pyplot as plt
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
INVERSE_CHAR_MAP = {v: k for k, v in CHAR_MAP.items()}
NodeType: TypeAlias = tuple[int, int]

DistanceType: TypeAlias = int
GraphType: TypeAlias = dict[NodeType, dict[NodeType, DistanceType]]

MOVES: list[tuple[NodeType, int]] = [
    ((-1, 0), SLOPE_UP),
    ((+1, 0), SLOPE_DOWN),
    ((0, -1), SLOPE_LEFT),
    ((0, +1), SLOPE_RIGHT),
]


def get_neighbors(
    board: npt.NDArray[np.uint8], node: NodeType
) -> Iterable[tuple[NodeType, DistanceType]]:
    height, width = board.shape
    y, x = node
    for (dy, dx), slope in MOVES:
        ny = y + dy
        nx = x + dx
        if not (0 <= ny < height and 0 <= nx < width):
            continue  # move is out of bounds
        elif board[ny, nx] == EMPTY:
            yield (ny, nx), 1  # move is valid
        elif board[ny, nx] == slope:  # move over a slope
            yield (y + dy * 2, x + dx * 2), 2
        else:
            continue  # move is blocked by a wall


def build_graph(board: npt.NDArray[np.uint8], start_node: NodeType) -> GraphType:
    graph: GraphType = defaultdict(dict)
    visited: set[NodeType] = set()
    queue: deque[NodeType] = deque([start_node])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor, distance in get_neighbors(board, node):
            graph[node][neighbor] = distance
            if neighbor not in visited:
                queue.append(neighbor)
    return graph


def visualize_path(
    board: npt.NDArray[np.uint8], path: set[NodeType], distance: DistanceType
) -> None:
    cmap = colors.ListedColormap(
        ["yellow", "brown", "green", "green", "green", "green"]
    )
    bounds = [0, 1, 2, 3, 4, 5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(board, cmap=cmap, norm=norm)

    for y in range(board.shape[0]):
        for x in range(board.shape[1]):
            cell = board[y, x]
            if cell in INVERSE_CHAR_MAP:
                char = INVERSE_CHAR_MAP[cell]
                ax.text(x, y, char, ha="center", va="center")

    path_board = np.zeros_like(board)
    for node in path:
        y, x = node
        path_board[y, x] = 1
    cmap = colors.ListedColormap([(0, 0, 0, 0), (1, 0, 0, 0.5)])
    ax.imshow(path_board, cmap=cmap)

    ax.set_title(f"Path length {distance}")

    plt.show()


def dfs(
    graph: GraphType, start_node: NodeType, end_node: NodeType
) -> Iterable[tuple[set[NodeType], DistanceType]]:
    def _dfs(
        path: set[NodeType], current_node: NodeType, current_distance: DistanceType
    ) -> Iterable[tuple[set[NodeType], DistanceType]]:
        if current_node == end_node:
            yield path, current_distance
        else:
            for neighbor, distance in graph[current_node].items():
                if neighbor in path:
                    continue
                else:
                    yield from _dfs(
                        path | {neighbor}, neighbor, current_distance + distance
                    )

    yield from _dfs({start_node}, start_node, 0)


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

    almost_infinity = 2**32
    best_distance = -almost_infinity
    best_path: set[NodeType] = set()
    for path, distance in dfs(graph, start_node, end_node):
        logger.info("Found path of length %d", distance)
        if best_distance < distance:
            best_distance = distance
            best_path = path

    visualize_path(board, best_path, best_distance)

    return str(best_distance)


if __name__ == "__main__":
    sys.setrecursionlimit(
        10000
    )  # Set the recursion limit to 10000 or any desired value
    setup_logging(logging.DEBUG)
    main()
