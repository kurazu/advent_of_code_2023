from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import more_itertools as mit
from tqdm import tqdm

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Shape, drop, parse_shape

logger = logging.getLogger(__name__)


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    shapes = sorted(map(parse_shape, lines), key=lambda s: s.low_z)
    logger.debug("Dropping %d shapes", len(shapes))
    shapes = drop(shapes)
    logger.debug("Analyzing %d shapes", len(shapes))
    original_shapes_by_id = {s.id: s for s in shapes}

    def get_score(shape: Shape) -> int:
        shapes_without_this_one = [s for s in shapes if s is not shape]
        dropped = drop(shapes_without_this_one)
        dropped_shapes_by_id = {s.id: s for s in dropped}

        shapes_moved_by_absence = sum(
            dropped.low_z != original_shapes_by_id[id].low_z
            for id, dropped in dropped_shapes_by_id.items()
        )
        logger.debug(
            "Shape %s absence moved %d other shapes",
            shape.id,
            shapes_moved_by_absence,
        )
        return shapes_moved_by_absence

    scores = map(get_score, tqdm(shapes, desc="Analyzing shape"))
    return str(sum(scores))


if __name__ == "__main__":
    setup_logging()
    main()
