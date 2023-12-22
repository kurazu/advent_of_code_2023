from __future__ import annotations

import logging
import math
import multiprocessing as mp
from pathlib import Path

import numpy as np
import tqdm
from matplotlib import pyplot as plt
from numpy import typing as npt
from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import parse_board
from ..logs import setup_logging
from .task_1 import CHAR_MAPPING, EMPTY, START, Position, dijkstra

logger = logging.getLogger(__name__)


def get_distances(
    original_board: npt.NDArray[np.uint8],
    original_start_tuple: Position,
    max_distance: int,
) -> npt.NDArray[np.uint32]:
    original_height, original_width = original_board.shape
    extra_tiles = math.ceil(max_distance / min(original_height, original_width))
    board = np.tile(original_board, (extra_tiles * 2 + 1, extra_tiles * 2 + 1))
    start_tuple = Position(
        original_start_tuple.y + original_height * extra_tiles,
        original_start_tuple.x + original_width * extra_tiles,
    )
    distances = dijkstra(board, start_tuple, max_distance=max_distance)
    return distances


@wrap_main
def main(filename: Path) -> str:
    original_board = parse_board(filename, CHAR_MAPPING)
    (start,) = np.argwhere(original_board == START)
    original_start_tuple = Position(*start)
    original_board[original_start_tuple] = EMPTY

    max_distance = 3000
    distances = get_distances(original_board, original_start_tuple, max_distance)
    x = []
    y = []
    for dist in range(1, max_distance + 1, 2):
        possible_plots = distances <= dist
        if dist % 2 == 0:
            possible_plots &= distances % 2 == 0
        number_of_plots = np.count_nonzero(possible_plots)
        x.append(dist)
        y.append(number_of_plots)

    np.save("/tmp/result_max_distances.npy", x)
    np.save("/tmp/result_number_of_plots.npy", y)
    plt.plot(x, y)
    plt.show()
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
