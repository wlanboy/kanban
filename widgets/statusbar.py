from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import Horizontal


class StatusBar(Widget):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label("", id="statusbar-text")
            yield Label("ANSICHT", id="statusbar-mode")

    def set_context_card(self, edit_mode: bool = False) -> None:
        toggle = "[@b]e[/]Ansicht" if edit_mode else "[@b]e[/]Bearbeiten"
        self._set(f"[@b]n[/]Neu  [@b]d[/]Löschen  [@b]→/←[/]Lane  [@b]↑/↓[/]Sortieren  [@b]m[/]Verschieben  [@b]r[/]Umbenennen  [@b]o[/]Beschreibung  [@b]s[/]Priorität  [@b]u[/]Undo  [@b]/[/]Suche  {toggle}")

    def set_context_lane(self, edit_mode: bool = False) -> None:
        if edit_mode:
            self._set("[@b]a[/]Lane anlegen  [@b]D[/]Lane löschen  [@b]u[/]Undo  [@b]/[/]Suche  [@b]e[/]Ansicht  [@b]q[/]Beenden")
        else:
            self._set("[@b]n[/]Neu  [@b]e[/]Bearbeiten  [@b]/[/]Suche  [@b]q[/]Beenden")

    def set_context_global(self, edit_mode: bool = False) -> None:
        toggle = "[@b]e[/]Ansicht" if edit_mode else "[@b]e[/]Bearbeiten"
        self._set(f"[@b]n[/]Neu  [@b]u[/]Undo  [@b]/[/]Suche  {toggle}  [@b]q[/]Beenden")

    def set_edit_mode(self, edit_mode: bool) -> None:
        lbl = self.query_one("#statusbar-mode", Label)
        if edit_mode:
            lbl.update("[bold $green]BEARBEITEN[/bold $green]")
        else:
            lbl.update("ANSICHT")

    def _set(self, text: str) -> None:
        label = self.query_one("#statusbar-text", Label)
        label.update(text.replace("[@b]", "[bold $blue]").replace("[/]", "[/bold $blue] "))
