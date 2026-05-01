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


class CardWidget(Widget):
    COMPONENT_CLASSES = {"card-id", "card-name", "severity-low", "severity-medium", "severity-high"}
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
            yield Label(sym, classes=cls)

    def watch_dimmed(self, value: bool) -> None:
        self.set_class(value, "dimmed")

    def refresh_card(self, card: Card) -> None:
        self.card = card
        self.remove_children()
        self.mount(*list(self.compose()))
