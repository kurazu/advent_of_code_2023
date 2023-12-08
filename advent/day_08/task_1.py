import itertools as it
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Literal, NamedTuple, TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)
Direction: TypeAlias = Literal[0, 1]
Node: TypeAlias = str


def parse_instructions(lines: Iterator[str]) -> list[Direction]:
    line = next(lines)
    assert next(lines) == ""
    return [0 if c == "L" else 1 for c in line]


pattern = re.compile(r"(?P<node>\w{3}) = \((?P<left>\w{3}), (?P<right>\w{3})\)")


def parse_map(lines: Iterator[str]) -> dict[Node, tuple[Node, Node]]:
    result: dict[Node, tuple[Node, Node]] = {}
    # sample format:
    # 'FLR = (SXT, CRV)'
    for line in lines:
        match = pattern.match(line)
        assert match is not None
        node = match.group("node")
        left = match.group("left")
        right = match.group("right")
        result[node] = (left, right)
    return result


def traverse_map(
    map: dict[Node, tuple[Node, Node]], instructions: list[Direction]
) -> int:
    steps = 0
    node: Node = "AAA"
    for direction in it.cycle(instructions):
        node = map[node][direction]
        steps += 1
        if node == "ZZZ":
            break
    return steps


@wrap_main
def main(filename: Path) -> str:
    lines = iter(get_stripped_lines(filename))
    instructions = parse_instructions(lines)
    map = parse_map(lines)
    steps = traverse_map(map, instructions)
    return str(steps)


if __name__ == "__main__":
    setup_logging()
    main()
