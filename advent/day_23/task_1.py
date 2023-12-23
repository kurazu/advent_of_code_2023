import logging
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, TypeAlias

import numpy as np
from contexttimer import Timer
from matplotlib import cm, colors
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

BoardType: TypeAlias = npt.NDArray[np.uint8]
PathType: TypeAlias = list[NodeType]
DistanceType: TypeAlias = int
GraphType: TypeAlias = dict[NodeType, dict[NodeType, DistanceType]]

MOVES: list[tuple[NodeType, int]] = [
    ((-1, 0), SLOPE_UP),
    ((+1, 0), SLOPE_DOWN),
    ((0, -1), SLOPE_LEFT),
    ((0, +1), SLOPE_RIGHT),
]


def get_neighbors(
    board: BoardType, node: NodeType
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


def build_graph(board: BoardType, start_node: NodeType) -> GraphType:
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


def visualize_path(board: BoardType, path: PathType, distance: DistanceType) -> None:
    cmap: Any
    cmap = colors.ListedColormap(  # type: ignore
        ["yellow", "brown", "green", "green", "green", "green"]
    )
    bounds = [0, 1, 2, 3, 4, 5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(board, cmap=cmap, norm=norm)

    # for y in range(board.shape[0]):
    #     for x in range(board.shape[1]):
    #         cell = board[y, x]
    #         if cell in INVERSE_CHAR_MAP:
    #             char = INVERSE_CHAR_MAP[cell]
    #             ax.text(x, y, char, ha="center", va="center")

    path_board = np.zeros_like(board, dtype=np.uint32)
    for i, node in enumerate(path, 1):
        y, x = node
        path_board[y, x] = i
        # ax.text(x, y, str(i), ha="center", va="center")
    cmap = cm.get_cmap("Blues", len(path))
    cmap = colors.ListedColormap([(0, 0, 0, 0)] + [cmap(i) for i in range(len(path))])  # type: ignore # noqa
    ax.imshow(path_board, cmap=cmap)

    ax.set_title(f"Path length {distance}")

    plt.show()


ALMOST_INFINITY = 2**32


def dfs(
    graph: GraphType, start_node: NodeType, end_node: NodeType
) -> Iterable[tuple[PathType, DistanceType]]:
    # cache - current path, current_node -> best path, best distance
    cache: dict[
        tuple[tuple[NodeType, ...], NodeType], tuple[PathType, DistanceType] | None
    ] = {}
    cache_hits: int = 0
    cache_misses: int = 0

    def maybe_log_cache_stats() -> None:
        if (cache_hits + cache_misses) % 10000 == 0:
            logger.debug(
                "Cache stats: hits=%d, misses=%d, hit ratio=%.2f",
                cache_hits,
                cache_misses,
                cache_hits / (cache_hits + cache_misses),
            )

    def _dfs(
        path: PathType,
        current_node: NodeType,
        current_distance: DistanceType,
    ) -> Iterable[tuple[PathType, DistanceType]]:
        nonlocal cache_hits, cache_misses
        if current_node == end_node:
            yield path, current_distance
            return

        cache_key = (tuple(path), current_node)
        if cache_key in cache:
            cache_hits += 1
            maybe_log_cache_stats()

            cached_item = cache[cache_key]
            if cached_item is None:
                return
            else:
                yield cached_item
                return

        cache_misses += 1
        maybe_log_cache_stats()
        best_path: PathType = []
        best_distance: DistanceType = -ALMOST_INFINITY
        neighbours_not_in_path = set(graph[current_node]) - set(path)
        for neighbor in neighbours_not_in_path:
            distance = graph[current_node][neighbor]
            for sub_path, sub_distance in _dfs(
                path + [neighbor],
                neighbor,
                current_distance + distance,
            ):
                if sub_distance > best_distance:
                    best_path = sub_path
                    best_distance = sub_distance
        if best_path:
            cache[cache_key] = best_path, best_distance
            yield best_path, best_distance
        else:
            cache[cache_key] = None

    yield from _dfs([start_node], start_node, 0)
    logger.debug(
        "Cache size %d. Hits: %d, misses: %d, ratio: %.2f",
        len(cache),
        cache_hits,
        cache_misses,
        cache_hits / (cache_hits + cache_misses),
    )


def find_best_path(
    graph: GraphType, start_node: NodeType, end_node: NodeType
) -> tuple[PathType, DistanceType]:
    with Timer() as timer:
        best_distance = -ALMOST_INFINITY
        best_path: PathType = []
        for path, distance in dfs(graph, start_node, end_node):
            logger.info("Found path of length %d", distance)
            if best_distance < distance:
                best_distance = distance
                best_path = path
        assert best_path
    logger.info("Found best path of length %d in %.2fs", best_distance, timer.elapsed)
    return best_path, best_distance


def simplify_graph(graph: GraphType) -> None:
    queue: deque[NodeType] = deque(graph)

    def _simplify_node(node_a: NodeType) -> None:
        for node_b, distance_a_b in graph[node_a].items():
            if len(graph[node_b]) == 2 and node_a in graph[node_b]:
                # this node has only two connections, a - b - c
                # so we can simplify it to a - c
                (node_c,) = set(graph[node_b]) - {node_a}
                if node_b not in graph[node_c]:
                    continue
                distance_b_c = graph[node_b][node_c]
                distance_a_c = distance_a_b + distance_b_c
                graph[node_a][node_c] = distance_a_c
                graph[node_c][node_a] = distance_a_c
                del graph[node_a][node_b]
                del graph[node_b][node_a]

                del graph[node_b][node_c]
                del graph[node_c][node_b]

                assert not graph[node_b]
                del graph[node_b]

                # logger.debug(
                #     "Simplified graph by merging %s --- [%s] --> %s",
                #     node_a,
                #     node_b,
                #     node_c,
                # )
                queue.append(node_a)  # recheck for further simplification
                break

    while queue:
        node = queue.popleft()
        _simplify_node(node)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    height, width = board.shape
    logger.debug("Board:\n%s", board)
    start_node: NodeType = (0, 1)
    end_node: NodeType = (height - 1, width - 2)
    graph = build_graph(board, start_node)
    logger.debug("Graph has %d vertices", sum(map(len, graph.values())))
    simplify_graph(graph)
    logger.info("Simplified graph has %d vertices", sum(map(len, graph.values())))

    assert start_node in graph
    assert end_node in graph

    best_path, best_distance = find_best_path(graph, start_node, end_node)

    visualize_path(board, best_path, best_distance)

    return str(best_distance)


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    setup_logging(logging.DEBUG)
    main()
