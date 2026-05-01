from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label
from textual.containers import Vertical, Horizontal


class AddLaneScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label("Neue Lane", classes="modal-title")
            yield Input(placeholder="Name (2–20 Zeichen)", id="lane-name", max_length=20)
            yield Label("", id="lane-error", classes="modal-error")
            with Horizontal(classes="modal-buttons"):
                yield Button("Abbrechen", id="cancel")
                yield Button("Anlegen", id="confirm", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#lane-name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        else:
            self._submit()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            self._submit()

    def _submit(self) -> None:
        name = self.query_one("#lane-name", Input).value.strip()
        if len(name) < 2:
            self.query_one("#lane-error", Label).update("Mindestens 2 Zeichen erforderlich.")
            return
        self.dismiss(name)
