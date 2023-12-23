import logging
import sys
from pathlib import Path

import numpy as np
from contexttimer import Timer

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import CHAR_MAP, EMPTY, WALL, NodeType, build_graph, dfs, visualize_path

logger = logging.getLogger(__name__)


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
    assert start_node in graph
    assert end_node in graph

    with Timer() as timer:
        almost_infinity = 2**32
        best_distance = -almost_infinity
        best_path: frozenset[NodeType] = frozenset()
        for path, distance in dfs(graph, start_node, end_node):
            logger.info("Found path of length %d", distance)
            if best_distance < distance:
                best_distance = distance
                best_path = path

    logger.info("Found best path of length %d in %.2fs", best_distance, timer.elapsed)

    visualize_path(board, best_path, best_distance)

    return str(best_distance)


if __name__ == "__main__":
    sys.setrecursionlimit(
        10000
    )  # Set the recursion limit to 10000 or any desired value
    setup_logging(logging.DEBUG)
    main()
