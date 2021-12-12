from dataclasses import dataclass
from pathlib import Path
from typing import List
import logging


@dataclass(frozen=True)
class Args:
    token: str
    email: str
    email_pass: str
    logging_level: int = logging.DEBUG

    @classmethod
    def parse(cls, argv: List[str]) -> "Args":
        return cls(argv[1], argv[2], argv[3], logging.__dict__[argv[4].upper()])


def parse_chips(p: Path):
    with p.open("rt") as f:
        c = {int(c, 16) for c in f.readlines() if not c.startswith("#")}
    return c

