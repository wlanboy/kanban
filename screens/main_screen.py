from textual.app import ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Header, Input, Label
from textual.binding import Binding
from textual.reactive import reactive
import store
import actions
from actions import UndoStack
from model import Workspace
from widgets.board import BoardView
from widgets.card import CardWidget
from widgets.lane import LaneWidget
from widgets.statusbar import StatusBar
from screens.add_card import AddCardScreen
from screens.add_lane import AddLaneScreen
from screens.confirm import ConfirmScreen
from screens.move_card import MoveCardScreen

class MainScreen(Screen):
    BINDINGS = [
        Binding("e",         "toggle_edit", "Bearbeiten",    show=False),
        Binding("n",         "add_card",    "Card anlegen"),
        Binding("u",         "undo",        "Undo"),
        Binding("slash",     "search",      "Suche"),
        Binding("right,l",   "move_next",   "Weiter",        show=False),
        Binding("left,h",    "move_prev",   "Zurück",        show=False),
        Binding("d",         "delete_card", "Löschen",       show=False),
        Binding("a",         "add_lane",    "Lane anlegen",  show=False),
        Binding("D",         "delete_lane", "Lane löschen",  show=False),
        Binding("s",         "cycle_sev",   "Priorität",     show=False),
        Binding("m",         "move_card",   "Verschieben",   show=False),
        Binding("r",         "rename_card", "Umbenennen",    show=False),
        Binding("j",         "focus_next",  "Nächste Card",  show=False),
        Binding("k",         "focus_prev",  "Vorherige Card",show=False),
    ]

    edit_mode: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        super().__init__()
        self.workspace: Workspace = store.load()
        self.undo_stack = UndoStack()

    def compose(self) -> ComposeResult:
        yield Header()
        yield BoardView(self.workspace)
        yield Input(placeholder="Suche... (Escape zum Schließen)", id="search-bar", classes="search-bar")
        yield StatusBar()

    def on_mount(self) -> None:
        self._update_statusbar()

    # --- edit mode ---

    def action_toggle_edit(self) -> None:
        self.edit_mode = not self.edit_mode

    def watch_edit_mode(self, edit_mode: bool) -> None:
        self.query_one(BoardView).set_edit_mode(edit_mode)
        self.query_one(StatusBar).set_edit_mode(edit_mode)
        self._update_statusbar()

    def _update_statusbar(self) -> None:
        bar = self.query_one(StatusBar)
        focused = self.app.focused
        if isinstance(focused, CardWidget):
            bar.set_context_card(self.edit_mode)
        elif isinstance(focused, LaneWidget):
            bar.set_context_lane(self.edit_mode)
        else:
            bar.set_context_global(self.edit_mode)

    # --- focus tracking for statusbar ---

    def on_focus(self, event) -> None:
        self._update_statusbar()

    # --- mutations ---

    def _mutate(self, fn, *args) -> None:
        self.undo_stack.push(self.workspace)
        fn(self.workspace, *args)
        store.save(self.workspace)
        self.query_one(BoardView).refresh_board(self.workspace)

    # --- actions ---

    def action_add_card(self) -> None:
        lane_idx = self.query_one(BoardView).focused_lane_index() or 0

        def on_result(result: tuple | None) -> None:
            if result:
                idx, name, severity = result
                self._mutate(actions.add_card, idx, name, severity)

        self.app.push_screen(AddCardScreen(self.workspace, default_lane_index=lane_idx), on_result)

    def action_add_lane(self) -> None:
        if not self.edit_mode:
            return

        def on_result(name: str | None) -> None:
            if name:
                self._mutate(actions.add_lane, name)

        self.app.push_screen(AddLaneScreen(), on_result)

    def action_delete_card(self) -> None:
        card_id = self.query_one(BoardView).focused_card_id()
        if card_id is None:
            return

        def on_confirm(ok: bool | None) -> None:
            if ok:
                self._mutate(actions.delete_card, card_id)

        self.app.push_screen(ConfirmScreen("Card löschen?"), on_confirm)

    def action_delete_lane(self) -> None:
        if not self.edit_mode:
            return
        lane_idx = self.query_one(BoardView).focused_lane_index()
        if lane_idx is None:
            return

        def on_confirm(ok: bool | None) -> None:
            if ok:
                self._mutate(actions.delete_lane, lane_idx)

        self.app.push_screen(ConfirmScreen("Lane löschen?"), on_confirm)

    def action_move_next(self) -> None:
        card_id = self.query_one(BoardView).focused_card_id()
        if card_id is not None:
            self._mutate(actions.move_card_next, card_id)

    def action_move_prev(self) -> None:
        card_id = self.query_one(BoardView).focused_card_id()
        if card_id is not None:
            self._mutate(actions.move_card_prev, card_id)

    def action_move_card(self) -> None:
        board = self.query_one(BoardView)
        card_id = board.focused_card_id()
        lane_idx = board.focused_lane_index()
        if card_id is None or lane_idx is None:
            return
        card = next((c for lane in self.workspace.Lanes for c in lane.Items if c.ID == card_id), None)
        if card is None:
            return

        def on_result(target: int | None) -> None:
            if target is not None and target != lane_idx:
                self._mutate(actions.move_card_to, card_id, target)

        self.app.push_screen(MoveCardScreen(self.workspace, card, lane_idx), on_result)

    def action_rename_card(self) -> None:
        card_id = self.query_one(BoardView).focused_card_id()
        if card_id is None:
            return
        card = next((c for lane in self.workspace.Lanes for c in lane.Items if c.ID == card_id), None)
        if card is None:
            return

        # Inline rename via a modal-less Input overlay
        # Reuse AddLaneScreen with prefilled value via a simple inline approach
        self._start_inline_rename(card_id, card.Name)

    def _start_inline_rename(self, card_id: int, current_name: str) -> None:
        from textual.widgets import Input as _Input

        class RenameScreen(ModalScreen[str | None]):  # type: ignore[misc]
            from textual.app import ComposeResult as _CR
            from textual.widgets import Button as _Btn, Label as _Lbl, Input as _Inp
            from textual.containers import Vertical as _V, Horizontal as _H

            def compose(self) -> ComposeResult:  # type: ignore[override]
                from textual.widgets import Button, Label, Input
                from textual.containers import Vertical, Horizontal
                with Vertical(classes="modal-container"):
                    yield Label("Card umbenennen", classes="modal-title")
                    yield Input(value=current_name, max_length=20, id="rename-input")
                    yield Label("", id="rename-error", classes="modal-error")
                    with Horizontal(classes="modal-buttons"):
                        yield Button("Abbrechen", id="cancel")
                        yield Button("Speichern", id="confirm", variant="primary")

            def on_mount(self) -> None:
                inp = self.query_one("#rename-input", _Input)
                inp.focus()
                inp.cursor_position = len(inp.value)

            def on_button_pressed(self, event) -> None:
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
                name = self.query_one("#rename-input", _Input).value.strip()
                if len(name) < 2:
                    self.query_one("#rename-error", Label).update("Mindestens 2 Zeichen.")
                    return
                self.dismiss(name)

        def on_result(new_name: str | None) -> None:
            if new_name:
                self._mutate(actions.rename_card, card_id, new_name)

        self.app.push_screen(RenameScreen(), on_result)

    def action_cycle_sev(self) -> None:
        card_id = self.query_one(BoardView).focused_card_id()
        if card_id is not None:
            self._mutate(actions.cycle_severity, card_id)

    def action_undo(self) -> None:
        prev = self.undo_stack.pop()
        if prev:
            self.workspace = prev
            store.save(self.workspace)
            self.query_one(BoardView).refresh_board(self.workspace)

    def action_focus_next(self) -> None:
        self.screen.focus_next(CardWidget)

    def action_focus_prev(self) -> None:
        self.screen.focus_previous(CardWidget)

    def action_search(self) -> None:
        bar = self.query_one("#search-bar", Input)
        bar.toggle_class("visible")
        if "visible" in bar.classes:
            bar.focus()
        else:
            bar.clear()
            self.query_one(BoardView).filter_cards("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-bar":
            self.query_one(BoardView).filter_cards(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-bar":
            self.action_search()

    # --- button click handlers from board ---

    def on_button_pressed(self, event) -> None:
        btn_id: str = event.button.id or ""
        if btn_id == "add-lane-btn":
            self.action_add_lane()
        elif btn_id.startswith("add-card-"):
            lane_idx = int(btn_id.split("-")[2])
            self.app.push_screen(
                AddCardScreen(self.workspace, default_lane_index=lane_idx),
                lambda r: self._mutate(actions.add_card, r[0], r[1], r[2]) if r else None,
            )
        elif btn_id.startswith("delete-lane-") and self.edit_mode:
            lane_idx = int(btn_id.split("-")[2])
            self.app.push_screen(
                ConfirmScreen("Lane löschen?"),
                lambda ok: self._mutate(actions.delete_lane, lane_idx) if ok else None,
            )
