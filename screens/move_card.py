from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RadioSet, RadioButton
from textual.containers import Vertical, Horizontal
from model import Workspace, Card


class MoveCardScreen(ModalScreen[int | None]):
    def __init__(self, workspace: Workspace, card: Card, current_lane_index: int) -> None:
        super().__init__()
        self.workspace = workspace
        self.card = card
        self.current_lane_index = current_lane_index

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label(f'Card verschieben: "{self.card.Name}"', classes="modal-title")
            yield Label("Ziel-Lane wählen:")
            with RadioSet(id="lane-select"):
                for i, lane in enumerate(self.workspace.Lanes):
                    suffix = " (aktuell)" if i == self.current_lane_index else ""
                    yield RadioButton(
                        f"{lane.Name}{suffix}",
                        value=(i == self.current_lane_index),
                        id=f"lane-{i}",
                    )
            with Horizontal(classes="modal-buttons"):
                yield Button("Abbrechen", id="cancel")
                yield Button("Bewegen", id="confirm", variant="primary")

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
        radio = self.query_one("#lane-select", RadioSet)
        if radio.pressed_button is None:
            self.dismiss(None)
            return
        btn_id = radio.pressed_button.id  # type: ignore[union-attr]
        if btn_id is None:
            self.dismiss(None)
            return
        target = int(btn_id.split("-")[1])
        self.dismiss(target)
