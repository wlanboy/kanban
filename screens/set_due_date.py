from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical
from model import Card

import re

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SetDueDateScreen(ModalScreen[str | None]):
    def __init__(self, card: Card) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label("Fälligkeitsdatum setzen", classes="modal-title")
            yield Input(
                value=self.card.DueDate,
                placeholder="JJJJ-MM-TT (leer = kein Datum)",
                id="due-date-input",
                max_length=10,
            )
            yield Label("", id="due-error", classes="modal-error")
            yield Button("Speichern", id="confirm", variant="primary", classes="modal-btn-full")
            yield Button("Löschen",   id="clear",   classes="modal-btn-full")
            yield Button("Abbrechen", id="cancel",  classes="modal-btn-full")

    def on_mount(self) -> None:
        inp = self.query_one("#due-date-input", Input)
        inp.focus()
        inp.cursor_position = len(inp.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "clear":
            self.dismiss("")
        else:
            self._submit()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            self._submit()

    def _submit(self) -> None:
        value = self.query_one("#due-date-input", Input).value.strip()
        if value == "":
            self.dismiss("")
            return
        if not _DATE_RE.match(value):
            self.query_one("#due-error", Label).update("Format: JJJJ-MM-TT (z.B. 2026-05-15)")
            return
        from datetime import date
        try:
            date.fromisoformat(value)
        except ValueError:
            self.query_one("#due-error", Label).update("Ungültiges Datum.")
            return
        self.dismiss(value)
