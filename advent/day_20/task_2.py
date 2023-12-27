from __future__ import annotations

import logging
import math
from collections import deque
from pathlib import Path
from typing import Callable, Type

import networkx as nx
from matplotlib import pyplot as plt

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import (
    ConjunctionModule,
    FlipFlopModule,
    Module,
    PlainModule,
    parse_modules,
    setup_modules,
)

logger = logging.getLogger(__name__)


class Stop(Exception):
    pass


def press(
    modules: dict[str, Module],
    name: str,
    value: bool,
    monitor: set[str],
    signal: Callable[[str], bool],
) -> None:
    queue: deque[tuple[str, str, bool]] = deque([("", name, value)])
    while queue:
        source, target, value = queue.popleft()
        if not value and target in monitor:
            logger.debug("Monitored module %s gets a low signal", target)
            if signal(target):
                logger.warning("Signal handler requests shutdown")
                raise Stop()
        # logger.debug("Processing %s --- %s --> %s", source, value, target)
        target_module = modules[target]
        for trigger_name, trigger_value in target_module(source, value):
            logger.debug(
                # "\tTriggering %s --- %s --> %s",
                target,
                trigger_value,
                trigger_name,
            )
            queue.append((target, trigger_name, trigger_value))


COLORS_BY_TYPE: dict[Type[Module], str] = {
    FlipFlopModule: "blue",
    ConjunctionModule: "red",
    PlainModule: "green",
}


def visualize_modules(modules: dict[str, Module]) -> None:
    graph = nx.DiGraph()
    for name, module in modules.items():
        graph.add_node(
            name, color=COLORS_BY_TYPE[type(module)]
        )  # Add node to graph with color
    for name, module in modules.items():
        for connection in module.connections:
            graph.add_edge(name, connection)

    nx.draw(
        graph,
        with_labels=True,
        node_color=[graph.nodes[node]["color"] for node in graph.nodes()],
    )

    plt.show()


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    modules = parse_modules(lines)
    setup_modules(modules)
    visualize_modules(modules)
    join_module = modules["vr"]
    assert join_module.connections == {"rx"}
    assert isinstance(join_module, ConjunctionModule)
    incoming_modules = set(join_module.memory)
    logger.debug("There are %d incoming modules", len(incoming_modules))
    assert len(join_module.memory) == 4
    logger.debug("Modules:\n%s", modules)
    i = 1

    monitored: dict[str, list[int]] = {name: [] for name in incoming_modules}

    def checker(name: str) -> bool:
        logger.info("Module %s gets low signal at iteration %d", name, i)
        monitored[name].append(i)
        return all(len(v) >= 4 for v in monitored.values())

    while True:
        try:
            press(
                modules, "broadcaster", False, monitor=incoming_modules, signal=checker
            )
        except Stop:
            logger.info("Monitored %s", monitored)
            cycle_lengths = {
                name: values[-1] - values[-2] for name, values in monitored.items()
            }
            logger.info("Cycle lengths %s", cycle_lengths)
            cycle_offsets = {
                name: values[0] - cycle_lengths[name]
                for name, values in monitored.items()
            }
            logger.info("Cycle offsets %s", cycle_offsets)
            assert all(offset == 0 for offset in cycle_offsets.values())
            lowest_common_denominator = math.lcm(*cycle_lengths.values())
            return str(lowest_common_denominator)
        else:
            i += 1
            if i % 10000 == 0:
                logger.info("Iteration %d", i)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
