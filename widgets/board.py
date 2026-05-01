from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button
from textual.containers import Horizontal
from model import Workspace
from widgets.card import CardWidget
from widgets.lane import LaneWidget


class BoardView(Widget):
    DEFAULT_CSS = "BoardView { height: 1fr; overflow-x: auto; }"

    def __init__(self, workspace: Workspace) -> None:
        super().__init__()
        self.workspace = workspace

    def compose(self) -> ComposeResult:
        with Horizontal():
            for i, lane in enumerate(self.workspace.Lanes):
                yield LaneWidget(lane, lane_index=i)
            yield Button("+ Lane", id="add-lane-btn", classes="add-lane-column")

    def set_edit_mode(self, edit_mode: bool) -> None:
        self.set_class(edit_mode, "edit-mode")

    def refresh_board(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self.remove_children()
        lanes = [LaneWidget(lane, lane_index=i) for i, lane in enumerate(workspace.Lanes)]
        button = Button("+ Lane", id="add-lane-btn", classes="add-lane-column")
        horizontal = Horizontal(*lanes, button)
        self.mount(horizontal)

    def filter_cards(self, query: str) -> None:
        q = query.lower()
        for card_widget in self.query(CardWidget):
            match = q == "" or q in card_widget.card.Name.lower()
            card_widget.set_class(not match and q != "", "dimmed")

    def focused_card_id(self) -> int | None:
        focused = self.app.focused
        if isinstance(focused, CardWidget):
            return focused.card.ID
        return None

    def focused_lane_index(self) -> int | None:
        widget = self.app.focused
        while widget is not None:
            if isinstance(widget, LaneWidget):
                return widget.lane_index
            widget = widget.parent  # type: ignore[assignment]
        return None
