import logging
from dataclasses import dataclass
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
    name: str
    module_type: ModuleType
    connections: set[str]


def parse_module(line: str) -> Module:
    name_part, connections_part = line.split(" -> ")
    module_type: ModuleType
    if name_part.startswith("%"):
        module_type = ModuleType.FLIP_FLOP
        name = name_part[1:]
    elif name_part.startswith("&"):
        module_type = ModuleType.CONJUNCTION
        name = name_part[1:]
    else:
        module_type = ModuleType.PLAIN
        name = name_part
    connections = set(connections_part.split(", "))
    return Module(name=name, module_type=module_type, connections=connections)


def parse_modules(lines: Iterable[str]) -> dict[str, Module]:
    modules = {module.name: module for module in map(parse_module, lines)}
    additional_modules = {}
    for module in modules.values():
        for connection in module.connections:
            if connection not in modules:
                logger.warning("Adding additional module %s", connection)
                additional_modules[connection] = Module(
                    name=connection, module_type=ModuleType.PLAIN, connections=set()
                )
    return {
        **modules,
        **additional_modules,
    }


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    modules = parse_modules(lines)
    logger.debug("Modules:\n%s", modules)
    return ""


if __name__ == "__main__":
    setup_logging()
    main()
