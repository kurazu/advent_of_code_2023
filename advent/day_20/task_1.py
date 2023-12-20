from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Iterable

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class ModuleType(Enum):
    PLAIN = auto()
    FLIP_FLOP = auto()
    CONJUNCTION = auto()


@dataclass
class Module:
    connections: set[str]

    def setup(self, incoming: set[str]) -> None:
        pass

    def __call__(self, source: str, value: bool) -> Iterable[tuple[str, bool]]:
        raise NotImplementedError()


@dataclass
class PlainModule(Module):
    def __call__(self, source: str, value: bool) -> Iterable[tuple[str, bool]]:
        for connection in self.connections:
            yield connection, value


@dataclass
class FlipFlopModule(Module):
    state: bool = field(default=False, init=False)

    def __call__(self, source: str, value: bool) -> Iterable[tuple[str, bool]]:
        if value:
            pass  # nothing happens on high pulse
        else:
            self.state = not self.state
            for connection in self.connections:
                yield connection, self.state


@dataclass
class ConjunctionModule(Module):
    memory: dict[str, bool] = field(init=False, default_factory=dict)

    def setup(self, incoming: set[str]) -> None:
        for name in incoming:
            self.memory[name] = False

    def __call__(self, source: str, value: bool) -> Iterable[tuple[str, bool]]:
        self.memory[source] = value
        new_value = not all(self.memory.values())

        for connection in self.connections:
            yield connection, new_value


def parse_module(line: str) -> tuple[str, Module]:
    name_part, connections_part = line.split(" -> ")
    connections = set(connections_part.split(", "))
    name: str
    module: Module
    if name_part.startswith("%"):
        name = name_part[1:]
        module = FlipFlopModule(connections=connections)
    elif name_part.startswith("&"):
        name = name_part[1:]
        module = ConjunctionModule(connections=connections)
    else:
        name = name_part
        module = PlainModule(connections=connections)
    return name, module


def parse_modules(lines: Iterable[str]) -> dict[str, Module]:
    modules = dict(map(parse_module, lines))
    additional_modules: dict[str, Module] = {}
    for module in modules.values():
        for connection in module.connections:
            if connection not in modules:
                logger.warning("Adding additional module %s", connection)
                additional_modules[connection] = PlainModule(connections=set())
    return {
        **modules,
        **additional_modules,
    }


def press(modules: dict[str, Module], name: str, value: bool) -> tuple[int, int]:
    queue: deque[tuple[str, str, bool]] = deque([("", name, value)])
    counter: dict[bool, int] = defaultdict(int)
    while queue:
        source, target, value = queue.popleft()
        counter[value] += 1
        logger.debug("Processing %s --- %s --> %s", source, value, target)
        target_module = modules[target]
        for trigger_name, trigger_value in target_module(source, value):
            logger.debug(
                "\tTriggering %s --- %s --> %s",
                target,
                trigger_value,
                trigger_name,
            )
            queue.append((target, trigger_name, trigger_value))
    return counter[True], counter[False]


def setup_modules(modules: dict[str, Module]) -> None:
    incoming: dict[str, set[str]] = defaultdict(set)
    for name, module in modules.items():
        for connection in module.connections:
            incoming[connection].add(name)
    for name, module in modules.items():
        module.setup(incoming[name])


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    modules = parse_modules(lines)
    setup_modules(modules)
    logger.debug("Modules:\n%s", modules)
    high_count, low_count = 0, 0
    for _ in range(1000):
        high, low = press(modules, "broadcaster", False)
        high_count += high
        low_count += low
    return str(high_count * low_count)


if __name__ == "__main__":
    setup_logging()
    main()
