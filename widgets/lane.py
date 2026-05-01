from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Label
from textual.containers import Vertical, Horizontal
from model import Lane
from widgets.card import CardWidget


class LaneWidget(Widget):
    can_focus = True

    def __init__(self, lane: Lane, lane_index: int) -> None:
        super().__init__()
        self.lane = lane
        self.lane_index = lane_index

    def compose(self) -> ComposeResult:
        with Horizontal(classes="lane-header"):
            yield Label(self.lane.Name, classes="lane-header-title")
            yield Button("✕", classes="lane-delete-btn", id=f"delete-lane-{self.lane_index}")
        with Vertical(classes="lane-cards"):
            for card in self.lane.Items:
                yield CardWidget(card)
        yield Button("+ Card", classes="add-card-btn", id=f"add-card-{self.lane_index}")

    def refresh_lane(self, lane: Lane, lane_index: int) -> None:
        self.lane = lane
        self.lane_index = lane_index
        self.remove_children()
        self.mount(*list(self.compose()))
