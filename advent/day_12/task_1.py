from __future__ import annotations

import itertools as it
import logging
import operator
from pathlib import Path
from typing import Iterable, List, Literal, Tuple, TypeAlias

import numpy as np
from numpy import typing as npt
from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)

BROKEN = 1
FINE = 0
UNKNOWN = 2

InputType: TypeAlias = npt.NDArray[np.uint8]
ChecksumType: TypeAlias = List[int]


def parse_input(value: str) -> InputType:
    mapping = {"#": BROKEN, ".": FINE, "?": UNKNOWN}
    arr: List[int] = [mapping[c] for c in value]
    return np.array(arr, dtype=np.uint8)


def parse_totals(value: str) -> ChecksumType:
    return [int(i) for i in value.split(",")]


def parse(line: str) -> Tuple[InputType, ChecksumType]:
    left, right = line.split(" ")
    return parse_input(left), parse_totals(right)


def count(candidate: InputType) -> Iterable[int]:
    broken = 0
    for c in candidate:
        if c == BROKEN:
            broken += 1
        elif broken:
            yield broken
            broken = 0
        else:
            pass
    if broken:
        yield broken


def is_valid(checksum: ChecksumType, candidate: InputType) -> bool:
    return all(it.starmap(operator.eq, zip(checksum, count(candidate))))


def get_candidates(input: InputType, checksum: ChecksumType) -> InputType:
    base = np.where(input == BROKEN, np.uint8(BROKEN), np.uint8(FINE))
    candidate = np.zeros_like(base)
    already = np.count_nonzero(base)
    total = sum(checksum)
    missing = total - already
    unknown_positions = np.argwhere(input == UNKNOWN)
    for positions in it.combinations(unknown_positions, missing):
        candidate[:] = base
        candidate[list(positions)] = BROKEN
        yield candidate


def count_possibilities(input: InputType, checksum: ChecksumType) -> int:
    candidates = get_candidates(input, checksum)
    are_valid = map(partial(is_valid, checksum), candidates)
    sum_valid = sum(are_valid)
    logger.debug("Input %s %s produces %d valid positions", input, checksum, sum_valid)
    return sum_valid


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    entries = map(parse, lines)
    counts = it.starmap(count_possibilities, entries)
    return str(sum(counts))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
