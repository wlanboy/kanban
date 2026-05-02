from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea
from textual.containers import Vertical, Horizontal
from model import Card


class EditDescriptionScreen(ModalScreen[str | None]):
    def __init__(self, card: Card) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container description-container"):
            yield Label(f"Beschreibung: {self.card.Name}", classes="modal-title")
            yield TextArea(self.card.Description, id="desc-input")
            with Horizontal(classes="modal-buttons"):
                yield Button("Abbrechen", id="cancel")
                yield Button("Speichern", id="confirm", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#desc-input", TextArea).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        else:
            self.dismiss(self.query_one("#desc-input", TextArea).text)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "ctrl+s":
            self.dismiss(self.query_one("#desc-input", TextArea).text)
