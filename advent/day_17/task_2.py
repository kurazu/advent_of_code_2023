import logging
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import Node, build_graph, find_path

logger = logging.getLogger(__name__)


OFFSETS = [-10, -9, -8, -7, -6, -5, -4, 4, 5, 6, 7, 8, 9, 10]


@wrap_main
def main(filename: Path) -> str:
    board = parse_board(filename, {c: int(c) for c in "123456789"})
    height, width = board.shape
    logger.debug("Board:\n%s", board)
    graph = build_graph(board, OFFSETS)
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
