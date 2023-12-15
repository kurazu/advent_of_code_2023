from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, TypeAlias

import numpy as np
from numpy import typing as npt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


def get_checksum(part: str) -> int:
    current = 0
    for c in part:
        current += ord(c)
        current *= 17
        current %= 256
    return current


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    (line,) = lines
    parts = line.split(",")
    checksums = map(get_checksum, parts)
    return str(sum(checksums))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
