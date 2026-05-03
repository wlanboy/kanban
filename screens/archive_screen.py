from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static
from textual.containers import Vertical

import store
from model import Severity

_SEV_ICON = {Severity.LOW: "○", Severity.MEDIUM: "◐", Severity.HIGH: "●"}


class ArchiveScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        archive = store.load_archive()
        with Vertical(classes="modal-container archive-container"):
            yield Label("Archiv  [readonly]", classes="modal-title")
            with ListView(id="archive-list"):
                if not archive:
                    yield ListItem(Static("Keine archivierten Karten."))
                else:
                    for card in sorted(archive, key=lambda c: c.ArchivedAt, reverse=True):
                        icon = _SEV_ICON[card.Severity]
                        date = card.ArchivedAt[:10] if card.ArchivedAt else ""
                        due  = f"  fällig {card.DueDate}" if card.DueDate else ""
                        line = f"{icon} #{card.ID}  {card.Name}  [{card.LaneName}]  {date}{due}"
                        yield ListItem(Static(line))
            yield Button("Schließen", id="close", variant="primary", classes="modal-btn-full")

    def on_mount(self) -> None:
        lv = self.query_one("#archive-list", ListView)
        lv.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key in ("escape", "q"):
            self.dismiss(None)
