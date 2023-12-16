from __future__ import annotations

import logging
from pathlib import Path
from typing import TypeAlias

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import get_checksum

logger = logging.getLogger(__name__)


BoxType: TypeAlias = list[tuple[str, int]]


def execute_add(boxes: list[BoxType], label: str, lens: int) -> None:
    box_id = get_checksum(label)
    box = boxes[box_id]
    for i, (exising_label, existing_lens) in enumerate(box):
        if exising_label == label:
            box[i] = (label, lens)  # replace
            break
    else:
        box.append((label, lens))


def execute_remove(boxes: list[BoxType], label: str) -> None:
    box_id = get_checksum(label)
    boxes[box_id] = [
        (existing_label, existing_lens)
        for existing_label, existing_lens in boxes[box_id]
        if existing_label != label
    ]


def execute(boxes: list[BoxType], part: str) -> None:
    if part.endswith("-"):
        label = part[:-1]
        execute_remove(boxes, label)
    else:
        label, focal = part.split("=")
        execute_add(boxes, label, int(focal))


def print_boxes(boxes: list[BoxType]) -> None:
    for i, box in enumerate(boxes):
        if box:
            logger.debug("\tBox %d: %s", i, box)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    (line,) = lines
    parts = line.split(",")
    boxes: list[BoxType] = [[] for _ in range(256)]
    for part in parts:
        logger.debug("Executing %s", part)
        execute(boxes, part)
        print_boxes(boxes)
    return ""


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
