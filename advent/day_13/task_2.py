from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import BoardType, NotFound, parse_boards

logger = logging.getLogger(__name__)


def find_almost_vertical_line(board: BoardType) -> int:
    height, width = board.shape
    for col in range(1, width):
        left = board[:, :col]
        _, left_width = left.shape
        right = board[:, col:]
        _, right_width = right.shape

        left_part: BoardType
        right_part: BoardType
        if left_width < right_width:
            left_part = left
            right_part = right[:, :left_width]
        elif left_width > right_width:
            right_part = right
            left_part = left[:, -right_width:]
        else:  # equal
            left_part = left
            right_part = right_part
        condition = left_part == right_part[:, ::-1]
        if np.count_nonzero(~condition) == 1:
            return col
    raise NotFound()


def find_almost_horizontal_line(board: BoardType) -> int:
    height, width = board.shape
    for row in range(1, height):
        top = board[:row, :]
        top_height, _ = top.shape
        bottom = board[row:, :]
        bottom_height, _ = bottom.shape

        top_part: BoardType
        bottom_part: BoardType
        if top_height > bottom_height:
            bottom_part = bottom
            top_part = top[-bottom_height:, :]
        elif top_height < bottom_height:
            top_part = top
            bottom_part = bottom[:top_height, :]
        else:  # equal
            top_part = top
            bottom_part = bottom
        condition = top_part == bottom_part[::-1, :]
        if np.count_nonzero(~condition) == 1:
            return row
    raise NotFound()


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    boards = parse_boards(lines)
    summary = 0
    for i, board in enumerate(boards, 1):
        try:
            col = find_almost_vertical_line(board)
        except NotFound:
            pass
        else:
            logger.debug("Found vertical line at column %d in board %d", col, i)
            summary += col
            continue
        try:
            row = find_almost_horizontal_line(board)
        except NotFound:
            raise AssertionError(f"No split found in board {i}")
        else:
            logger.debug("Found horizontal line at line %d in board %d", row, i)
            summary += 100 * row

    return str(summary)


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
