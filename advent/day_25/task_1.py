import logging
from collections import defaultdict
from pathlib import Path
from typing import Iterable, NewType, TypeAlias

import networkx as nx

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)
Node = NewType("Node", str)
GraphType: TypeAlias = dict[Node, set[Node]]


def parse(lines: Iterable[str]) -> nx.Graph:
    graph = nx.Graph()
    for line in lines:
        raw_node, children_part = line.split(": ")
        node = Node(raw_node)
        children = map(Node, children_part.split(" "))
        for child in children:
            graph.add_edge(node, child)
    return graph


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    graph = parse(lines)
    logger.debug("Graph: %s", graph)
    cut_value, (first_partition, second_partition) = nx.stoer_wagner(graph)
    assert cut_value == 3
    return str(len(first_partition) * len(second_partition))


if __name__ == "__main__":
    setup_logging()
    main()
