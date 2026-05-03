from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static
from textual.containers import Vertical, Horizontal

import store
from model import ArchivedCard, Severity

_SEV_ICON = {Severity.LOW: "○", Severity.MEDIUM: "◐", Severity.HIGH: "●"}


class ArchiveScreen(ModalScreen[ArchivedCard | None]):
    def __init__(self) -> None:
        super().__init__()
        archive = store.load_archive()
        self._cards = sorted(archive, key=lambda c: c.ArchivedAt, reverse=True)

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container archive-container"):
            yield Label("Archiv  [readonly]", classes="modal-title")
            with ListView(id="archive-list"):
                if not self._cards:
                    yield ListItem(Static("Keine archivierten Karten."))
                else:
                    for card in self._cards:
                        icon = _SEV_ICON[card.Severity]
                        date = card.ArchivedAt[:10] if card.ArchivedAt else ""
                        due  = f"  fällig {card.DueDate}" if card.DueDate else ""
                        line = f"{icon} #{card.ID}  {card.Name}  [{card.LaneName}]  {date}{due}"
                        yield ListItem(Static(line))
            with Horizontal(classes="modal-buttons"):
                yield Button("Schließen", id="close")
                yield Button("Kopieren", id="copy", variant="primary", disabled=not self._cards)

    def on_mount(self) -> None:
        self.query_one("#archive-list", ListView).focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.query_one("#copy", Button).disabled = (
            not self._cards or event.item is None
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss(None)
        elif event.button.id == "copy":
            self._copy_selected()

    def on_key(self, event) -> None:
        if event.key in ("escape", "q"):
            self.dismiss(None)

    def _copy_selected(self) -> None:
        lv = self.query_one("#archive-list", ListView)
        idx = lv.index
        if idx is None or idx >= len(self._cards):
            return
        self.dismiss(self._cards[idx])
