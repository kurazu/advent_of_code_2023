import logging
import sys
from pathlib import Path

import numpy as np

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import (
    CHAR_MAP,
    EMPTY,
    WALL,
    NodeType,
    build_graph,
    find_best_path,
    simplify_graph,
    visualize_path,
)

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
    logger.info("Graph has %d vertices", sum(map(len, graph.values())))
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
