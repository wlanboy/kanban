from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum


class Severity(IntEnum):
    LOW    = 0
    MEDIUM = 1
    HIGH   = 2


@dataclass
class Card:
    ID:          int
    Name:        str
    Severity:    Severity = Severity.LOW
    Description: str      = ""


@dataclass
class Lane:
    UUID:  str
    Name:  str
    Items: list[Card] = field(default_factory=list)


@dataclass
class ArchivedCard:
    ID:          int
    Name:        str
    Severity:    Severity
    Description: str
    LaneName:    str
    ArchivedAt:  str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Workspace:
    Name:   str        = "Kanban"
    NextID: int        = 1
    Lanes:  list[Lane] = field(default_factory=list)
