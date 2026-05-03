from datetime import date
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Horizontal
from model import Card, Severity

SEVERITY_INDICATOR: dict[Severity, tuple[str, str]] = {
    Severity.LOW:    ("·", "severity-low"),
    Severity.MEDIUM: ("●", "severity-medium"),
    Severity.HIGH:   ("●●", "severity-high"),
}


def _due_badge(due_date: str) -> tuple[str, str] | None:
    if not due_date:
        return None
    try:
        due = date.fromisoformat(due_date)
    except ValueError:
        return None
    days = (due - date.today()).days
    if days > 30:
        return ("M", "due-ok")
    if days > 7:
        return ("W", "due-ok")
    if days >= 2:
        return (str(days), "due-ok")
    if days == 1:
        return ("1", "due-warn")
    return ("!", "due-over") if days < 0 else ("0", "due-over")


class CardWidget(Widget):
    COMPONENT_CLASSES = {
        "card-id", "card-name", "card-desc-indicator",
        "severity-low", "severity-medium", "severity-high",
        "due-ok", "due-warn", "due-over",
    }
    can_focus = True

    dimmed: reactive[bool] = reactive(False)

    def __init__(self, card: Card) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        sym, cls = SEVERITY_INDICATOR[self.card.Severity]
        with Horizontal():
            yield Label(f"[{self.card.ID}]", classes="card-id")
            yield Label(self.card.Name, classes="card-name")
            if self.card.Description:
                yield Label("≡", classes="card-desc-indicator")
            badge = _due_badge(self.card.DueDate)
            if badge:
                text, badge_cls = badge
                yield Label(text, classes=badge_cls)
            yield Label(sym, classes=cls)

    def watch_dimmed(self, value: bool) -> None:
        self.set_class(value, "dimmed")

    def refresh_card(self, card: Card) -> None:
        self.card = card
        self.remove_children()
        self.mount(*list(self.compose()))
