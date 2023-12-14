from __future__ import annotations

import itertools as it
import logging
from pathlib import Path
from typing import Tuple

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import (
    ChecksumType,
    InputType,
    count_possibilities,
    parse_input,
    parse_totals,
)

logger = logging.getLogger(__name__)


def parse(line: str) -> Tuple[InputType, ChecksumType]:
    left, right = line.split(" ")
    left = "?".join(left for _ in range(5))
    right = ",".join(right for _ in range(5))
    return parse_input(left), parse_totals(right)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    entries = map(parse, lines)
    counts = it.starmap(count_possibilities, entries)
    return str(sum(counts))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
