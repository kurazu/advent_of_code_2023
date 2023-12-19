import logging
import operator
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Literal, Protocol, TypedDict, cast

from returns.curry import partial

from ..cli_utils import wrap_main
from ..io_utils import get_stripped_lines
from ..logs import setup_logging

logger = logging.getLogger(__name__)


class Item(TypedDict):
    x: int
    m: int
    a: int
    s: int


class Instruction(Protocol):
    def __call__(self, item: Item) -> str | bool | None:
        ...


@dataclass
class Workflow:
    name: str
    instructions: list[Instruction]


@dataclass
class Accept:
    def __call__(self, item: Item) -> Literal[True]:
        return True


@dataclass
class Reject:
    def __call__(self, item: Item) -> Literal[False]:
        return False


@dataclass
class Redirect:
    workflow: str

    def __call__(self, item: Item) -> str:
        return self.workflow


@dataclass
class Condition:
    attribute: Literal["x", "m", "a", "s"]
    op: Callable[[int, int], bool]
    value: int
    target: Instruction

    def __call__(self, item: Item) -> str | bool | None:
        attr = item[self.attribute]
        if self.op(attr, self.value):
            return self.target(item)
        else:
            return None


def parse_static_instruction(part: str) -> Instruction:
    if part == "A":
        return Accept()
    elif part == "R":
        return Reject()
    else:
        return Redirect(part)


def parse_conditional_instruction(part: str) -> Instruction:
    condition, rest = part.split(":")
    if "<" in condition:
        attribute, value = condition.split("<")
        op = operator.lt
    else:
        assert ">" in condition
        attribute, value = condition.split(">")
        op = operator.gt
    assert attribute in {"x", "m", "a", "s"}
    parsed_value = int(value)
    target = parse_static_instruction(rest)
    return Condition(
        attribute=cast(Literal["x", "m", "a", "s"], attribute),
        op=op,
        value=parsed_value,
        target=target,
    )


def parse_instruction(part: str) -> Instruction:
    if ":" in part:
        return parse_conditional_instruction(part)
    else:
        return parse_static_instruction(part)


def parse_workflows(lines: Iterable[str]) -> Iterable[Workflow]:
    for line in lines:
        if not line:
            return
        name, rest = line.split("{", 1)
        rest = rest[:-1]  # cut the closing "}"
        instructions = list(map(parse_instruction, rest.split(",")))
        yield Workflow(name=name, instructions=instructions)


ITEM_PATTERN = re.compile(r"\{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)\}")


def parse_item(line: str) -> Item:
    match = ITEM_PATTERN.match(line)
    assert match is not None
    x = int(match.group("x"))
    m = int(match.group("m"))
    a = int(match.group("a"))
    s = int(match.group("s"))
    return Item(x=x, m=m, a=a, s=s)


def process(workflows: dict[str, list[Instruction]], item: Item) -> bool:
    current_workflow = "in"
    while True:
        for instruction in workflows[current_workflow]:
            result = instruction(item)
            if isinstance(result, bool):
                if result:
                    logger.debug(
                        "Accepting item %s in workflow %r", item, current_workflow
                    )
                else:
                    logger.debug(
                        "Rejecting item %s in workflow %r", item, current_workflow
                    )
                return result
            elif isinstance(result, str):
                logger.debug(
                    "Redirecting item %s to workflow %r from workflow %r",
                    item,
                    result,
                    current_workflow,
                )
                current_workflow = result
                break
            else:
                assert result is None
                logger.debug(
                    "Instruction %s does not apply to item %s in workflow %r",
                    instruction,
                    item,
                    current_workflow,
                )
                continue
        else:
            logger.error(
                "No instruction applied to item %s in workflow %r",
                item,
                current_workflow,
            )
            raise AssertionError()


def get_rating(item: Item) -> int:
    return item["x"] + item["m"] + item["a"] + item["s"]


@wrap_main
def main(filename: Path) -> str:
    lines = get_stripped_lines(filename)
    workflows = {
        workflow.name: workflow.instructions for workflow in parse_workflows(lines)
    }
    items = map(parse_item, lines)
    accepted_items = filter(partial(process, workflows), items)
    ratings = map(get_rating, accepted_items)
    return str(sum(ratings))


if __name__ == "__main__":
    setup_logging(logging.INFO)
    main()
