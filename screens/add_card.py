from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, RadioSet, RadioButton
from textual.widgets.select import NoSelection
from textual.containers import Vertical, Horizontal
from model import Workspace, Severity


class AddCardScreen(ModalScreen[tuple[int, str, Severity] | None]):
    def __init__(self, workspace: Workspace, default_lane_index: int = 0) -> None:
        super().__init__()
        self.workspace = workspace
        self.default_lane_index = default_lane_index

    def compose(self) -> ComposeResult:
        options = [(lane.Name, str(i)) for i, lane in enumerate(self.workspace.Lanes)]
        with Vertical(classes="modal-container"):
            yield Label("Neue Card", classes="modal-title")
            yield Input(placeholder="Name (2–20 Zeichen)", id="card-name", max_length=20)
            yield Label("", id="card-error", classes="modal-error")
            yield Label("Lane:")
            yield Select(options, value=str(self.default_lane_index), id="card-lane")
            yield Label("Priorität:")
            with RadioSet(id="card-severity"):
                yield RadioButton("LOW",    value=True,  id="sev-low")
                yield RadioButton("MEDIUM", value=False, id="sev-medium")
                yield RadioButton("HIGH",   value=False, id="sev-high")
            with Horizontal(classes="modal-buttons"):
                yield Button("Abbrechen", id="cancel")
                yield Button("Anlegen", id="confirm", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#card-name", Input).focus()

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
        name = self.query_one("#card-name", Input).value.strip()
        if len(name) < 2:
            self.query_one("#card-error", Label).update("Mindestens 2 Zeichen erforderlich.")
            return
        lane_select = self.query_one("#card-lane", Select)
        lane_value = lane_select.value
        lane_index = int(lane_value) if not isinstance(lane_value, NoSelection) else 0
        radio = self.query_one("#card-severity", RadioSet)
        severity_map = {"sev-low": Severity.LOW, "sev-medium": Severity.MEDIUM, "sev-high": Severity.HIGH}
        severity = severity_map.get(radio.pressed_button.id if radio.pressed_button else "sev-low", Severity.LOW)  # type: ignore[union-attr]
        self.dismiss((lane_index, name, severity))
