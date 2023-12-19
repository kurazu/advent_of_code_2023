import logging
import operator
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TypedDict

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging
from .task_1 import Accept, Condition, Instruction, Redirect, Reject, parse_workflows

logger = logging.getLogger(__name__)


@dataclass
class Range:
    start: int
    end: int

    def __bool__(self) -> bool:
        return self.start < self.end

    def __len__(self) -> int:
        return self.end - self.start + 1


class RangeItem(TypedDict):
    x: Range
    m: Range
    a: Range
    s: Range


def is_non_empty_item(item: RangeItem) -> bool:
    return bool(item["x"]) and bool(item["m"]) and bool(item["a"]) and bool(item["s"])


def split_item(item: RangeItem, condition: Condition) -> tuple[RangeItem, RangeItem]:
    range = item[condition.attribute]
    if condition.op is operator.lt:
        positive_range = Range(range.start, condition.value - 1)
        negative_range = Range(condition.value, range.end)
    else:
        assert condition.op is operator.gt
        positive_range = Range(condition.value + 1, range.end)
        negative_range = Range(range.start, condition.value)
    return (
        {**item, condition.attribute: positive_range},  # type: ignore
        {**item, condition.attribute: negative_range},  # type: ignore
    )


def process(
    workflows: dict[str, list[Instruction]], starting_item: RangeItem
) -> Iterable[RangeItem]:
    def _process_simple_instruction(
        instruction: Instruction, item: RangeItem
    ) -> Iterable[RangeItem]:
        if isinstance(instruction, Accept):
            logger.info("Accepting %s", item)
            yield item
        elif isinstance(instruction, Reject):
            logger.debug("Rejecting %s", item)
            return
        else:
            assert isinstance(instruction, Redirect)
            logger.debug("Redirecting %s to %s", item, instruction.workflow)
            yield from _process(instruction.workflow, item)

    def _process(current_workflow: str, item: RangeItem) -> Iterable[RangeItem]:
        logger.debug("Processing %s through workflow %s", item, current_workflow)
        for instruction in workflows[current_workflow]:
            if isinstance(instruction, Condition):
                passing_item, failing_item = split_item(item, instruction)
                if is_non_empty_item(passing_item):
                    yield from _process_simple_instruction(
                        instruction.target, passing_item
                    )
                if not is_non_empty_item(failing_item):
                    return
                item = failing_item
            else:
                yield from _process_simple_instruction(instruction, item)
                break
        else:
            raise AssertionError("No accept or reject instruction found")

    yield from _process("in", starting_item)


def get_number_of_combinations(item: RangeItem) -> int:
    return len(item["x"]) * len(item["m"]) * len(item["a"]) * len(item["s"])


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    workflows = {
        workflow.name: workflow.instructions for workflow in parse_workflows(lines)
    }
    item = RangeItem(
        x=Range(1, 4000),
        m=Range(1, 4000),
        a=Range(1, 4000),
        s=Range(1, 4000),
    )
    items = process(workflows, item)
    combinations = map(get_number_of_combinations, items)
    return str(sum(combinations))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    main()
