from __future__ import annotations

import itertools as it
import logging
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, NamedTuple, TypeAlias

import more_itertools as mit
import pytest
from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


@dataclass
class Range:
    start: int
    end: int

    def __post_init__(self) -> None:
        assert self.start >= 0
        assert self.end > self.start

    def __len__(self) -> int:
        return self.end - self.start

    def __add__(self, other: int) -> Range:
        return Range(start=self.start + other, end=self.end + other)

    def __str__(self) -> str:
        return f"[{self.start}-{self.end})"


def parse_seeds(lines: Iterator[str]) -> Iterable[Range]:
    line = next(lines)
    assert next(lines) == ""
    assert line.startswith("seeds: ")
    _, ids = line.split(": ")
    for start, len in mit.batched(map(int, ids.split()), 2):
        yield Range(start=start, end=start + len)


@dataclass
class RangeTransform:
    range: Range
    offset: int


Transforms: TypeAlias = List[RangeTransform]


def parse_map(name: str, lines: Iterator[str]) -> Transforms:
    line = next(lines)
    assert line == f"{name} map:", f"expected {name!r} but got {line!r}"
    entries: list[RangeTransform] = []
    for line in lines:
        if not line:
            break
        dest_start, source_start, range_len = map(int, line.split())
        entries.append(
            RangeTransform(
                Range(start=source_start, end=source_start + range_len),
                offset=dest_start - source_start,
            )
        )
    entries.sort(key=lambda e: e.range.start)
    return entries


def intersect(*, base: Range, other: Range) -> Iterable[tuple[Range, bool]]:
    """
    Find the common and parts of two ranges.
    As the output a new set of ranges that sum of to `base` range are returned.
    """
    # most complex scenario:
    # BBBBBBBBBBBBBBBB base
    #      OOOO        other
    # SSSSSIIIIEEEEEEE parts: S - start, I - intersect, E - end
    try:
        start_range = Range(base.start, min(base.end, other.start))
    except AssertionError:
        pass
    else:
        yield start_range, False
    try:
        intersect_range = Range(max(base.start, other.start), min(base.end, other.end))
    except AssertionError:
        pass
    else:
        yield intersect_range, True
    try:
        end_range = Range(max(base.start, other.end), base.end)
    except AssertionError:
        pass
    else:
        yield end_range, False


def apply_transforms(transforms: Transforms, range: Range) -> Iterable[Range]:
    ranges_not_processed = deque([range])
    while ranges_not_processed:
        range = ranges_not_processed.popleft()
        # check if range intersects with any of the transforms
        for transform in transforms:
            intersections = list(intersect(base=range, other=transform.range))
            if any(is_intersecting for _, is_intersecting in intersections):
                # The range intersects with the transform.
                for intersecting_range, is_intersecting in intersections:
                    if is_intersecting:
                        # return a transformed part of the range
                        logger.debug(
                            "Transforming %s by %d",
                            intersecting_range,
                            transform.offset,
                        )
                        yield intersecting_range + transform.offset
                    else:
                        # leave the non-intersecting part of the range for further
                        # processing
                        ranges_not_processed.append(intersecting_range)
                # skip the rest of the transforms
                break
            else:
                # The range does not intersect with the transform.
                continue
        else:
            # none of the transforms intersect with the range, return the range verbatim
            logger.debug("No transform for %s", range)
            yield range


def apply_maps(maps: list[Transforms], range: Range) -> Iterable[Range]:
    ranges: Iterable[Range] = [range]
    for m in maps:
        ranges = it.chain.from_iterable(map(partial(apply_transforms, m), ranges))
    return ranges


@wrap_main
def main(filename: Path) -> str:
    lines = iter(get_stripped_lines(filename))
    seeds = list(parse_seeds(lines))
    logger.debug(f"seeds: {seeds}")
    maps = [
        parse_map("seed-to-soil", lines),
        parse_map("soil-to-fertilizer", lines),
        parse_map("fertilizer-to-water", lines),
        parse_map("water-to-light", lines),
        parse_map("light-to-temperature", lines),
        parse_map("temperature-to-humidity", lines),
        parse_map("humidity-to-location", lines),
    ]
    locations = it.chain.from_iterable(map(partial(apply_maps, maps), seeds))
    min_location = min(locations, key=lambda r: r.start)
    return str(min_location.start)


if __name__ == "__main__":
    setup_logging()
    main()
