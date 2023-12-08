import itertools as it
import logging
import math
import operator
from functools import reduce
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Direction, Node, parse_instructions, parse_map, traverse_map

logger = logging.getLogger(__name__)


def find_lcm(num1, num2):
    return (num1 * num2) // math.gcd(num1, num2)


def find_lcm_list(numbers):
    return reduce(find_lcm, numbers)


@wrap_main
def main(filename: Path) -> str:
    lines = iter(get_stripped_lines(filename))
    instructions = parse_instructions(lines)
    map = parse_map(lines)
    ending_nodes = {node for node in map if node.endswith("Z")}
    starting_nodes = [node for node in map if node.endswith("A")]
    steps_per_node = [
        traverse_map(map, instructions, start=node, ends=ending_nodes)
        for node in starting_nodes
    ]
    common_denominator = find_lcm_list(steps_per_node)
    return str(common_denominator)


if __name__ == "__main__":
    setup_logging()
    main()
