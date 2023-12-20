from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Module, parse_modules, setup_modules

logger = logging.getLogger(__name__)


class RxActivated(Exception):
    pass


def press(modules: dict[str, Module], name: str, value: bool) -> None:
    queue: deque[tuple[str, str, bool]] = deque([("", name, value)])
    while queue:
        source, target, value = queue.popleft()
        if target == "rx" and not value:
            raise RxActivated()
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


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    modules = parse_modules(lines)
    setup_modules(modules)
    logger.debug("Modules:\n%s", modules)
    i = 1
    while True:
        try:
            press(modules, "broadcaster", False)
        except RxActivated:
            return str(i)
        else:
            i += 1
            if i % 1000 == 0:
                logger.info("Iteration %d", i)


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
