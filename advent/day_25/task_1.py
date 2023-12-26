import logging
from collections import defaultdict
from pathlib import Path
from typing import Iterable, NewType, TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)
Node = NewType("Node", str)
GraphType: TypeAlias = dict[Node, set[Node]]


def parse(lines: Iterable[str]) -> GraphType:
    graph: GraphType = defaultdict(set)
    for line in lines:
        raw_node, children_part = line.split(": ")
        node = Node(raw_node)
        children = map(Node, children_part.split(" "))
        for child in children:
            graph[child].add(node)
            graph[node].add(child)
    return graph


def stoer_wagner(graph: GraphType) -> None:
    node = next(iter(graph))


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    graph = parse(lines)
    logger.debug("Graph: %s", graph)
    result = stoer_wagner(graph)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
