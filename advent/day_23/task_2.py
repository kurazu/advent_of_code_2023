import logging
import sys
from collections import deque
from pathlib import Path

import numpy as np

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import (
    CHAR_MAP,
    EMPTY,
    WALL,
    GraphType,
    NodeType,
    build_graph,
    find_best_path,
    visualize_path,
)

logger = logging.getLogger(__name__)


def simplify_graph(graph: GraphType) -> None:
    queue: deque[NodeType] = deque(graph)

    def _simplify_node(node_a: NodeType) -> None:
        for node_b, distance_a_b in graph[node_a].items():
            if len(graph[node_b]) == 2:
                # this node has only two connections, a - b - c
                # so we can simplify it to a - c
                (node_c,) = set(graph[node_b]) - {node_a}
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

                logger.debug(
                    "Simplified graph by merging %s --- [%s] --> %s",
                    node_a,
                    node_b,
                    node_c,
                )
                queue.append(node_a)  # recheck for further simplification
                break

    while queue:
        node = queue.popleft()
        _simplify_node(node)


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, CHAR_MAP)
    board = np.where(board == WALL, WALL, EMPTY)
    height, width = board.shape
    logger.debug("Board:\n%s", board)
    start_node: NodeType = (0, 1)
    end_node: NodeType = (height - 1, width - 2)
    graph = build_graph(board, start_node)
    logger.debug("Graph has %d vertices", sum(map(len, graph.values())))
    simplify_graph(graph)
    logger.debug("Simplified graph has %d vertices", sum(map(len, graph.values())))
    assert start_node in graph
    assert end_node in graph

    best_path, best_distance = find_best_path(graph, start_node, end_node)

    visualize_path(board, best_path, best_distance)

    return str(best_distance)


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    setup_logging(logging.DEBUG)
    main()
