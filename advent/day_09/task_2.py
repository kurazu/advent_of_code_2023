import logging
from functools import reduce
from pathlib import Path

import numpy as np

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import History, parse_history

logger = logging.getLogger(__name__)


def find_prev_element(history: History) -> int:
    first_elements: list[int] = [history[0]]
    logger.debug("Finding next element for history: %s", history)
    seq = history
    while np.count_nonzero(seq) > 1:
        seq = np.diff(seq)
        first_elements.append(seq[0])
        logger.debug("seq: %s", seq)
    logger.debug("first elements: %s", first_elements)
    result = reduce(lambda p, n: n - p, reversed(first_elements))
    logger.info("result: %s", result)
    return result


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    histories = map(parse_history, lines)
    prev_elements = map(find_prev_element, histories)
    return str(sum(prev_elements))


if __name__ == "__main__":
    setup_logging()
    main()
