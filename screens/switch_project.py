import re
from pathlib import Path

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ListItem, ListView, Static
from textual.containers import Vertical, Horizontal

import store
from model import ProjectEntry, Workspace

ARCHIVE_SENTINEL = "__archive__"


class NewProjectScreen(ModalScreen[tuple[str, str] | None]):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container"):
            yield Label("Neues Projekt", classes="modal-title")
            yield Input(placeholder="Projektname", max_length=30, id="new-proj-name")
            yield Label("", id="new-proj-error", classes="modal-error")
            with Horizontal(classes="modal-buttons"):
                yield Button("Abbrechen", id="cancel")
                yield Button("Erstellen", id="confirm", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#new-proj-name", Input).focus()

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
        name = self.query_one("#new-proj-name", Input).value.strip()
        if len(name) < 2:
            self.query_one("#new-proj-error", Label).update("Mindestens 2 Zeichen.")
            return
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower())
        path = str(Path.home() / f".kanbantabs_{safe}")
        self.dismiss((name, path))


class SwitchProjectScreen(ModalScreen[str | None]):
    def __init__(self, current_path: str) -> None:
        super().__init__()
        self.current_path = current_path

    def compose(self) -> ComposeResult:
        projects = store.load_projects()
        with Vertical(classes="modal-container project-switcher"):
            yield Label("Projekt wechseln", classes="modal-title")
            with ListView(id="project-list"):
                for i, p in enumerate(projects):
                    marker = " ●" if p.path == self.current_path else ""
                    yield ListItem(Static(p.name + marker), id=f"proj-{i}")
                yield ListItem(Static("Archiv  [readonly]"), id="proj-archive", classes="archive-entry")
            yield Label("", id="proj-switcher-error", classes="modal-error")
            with Vertical(classes="proj-buttons"):
                with Horizontal(classes="modal-buttons"):
                    yield Button("Abbrechen", id="cancel")
                    yield Button("Öffnen", id="open-project", variant="primary")
                with Horizontal(classes="modal-buttons"):
                    yield Button("Neu", id="new-project")
                    yield Button("Löschen", id="delete-project", variant="error")
                

    def on_mount(self) -> None:
        lv = self.query_one("#project-list", ListView)
        projects = store.load_projects()
        for i, p in enumerate(projects):
            if p.path == self.current_path:
                lv.index = i
                break
        lv.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self._open_selected()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "cancel":
            self.dismiss(None)
        elif btn == "open-project":
            self._open_selected()
        elif btn == "new-project":
            self._start_new_project()
        elif btn == "delete-project":
            self._delete_selected()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)

    def _open_selected(self) -> None:
        lv = self.query_one("#project-list", ListView)
        idx = lv.index
        if idx is None:
            return
        projects = store.load_projects()
        if idx == len(projects):
            self.dismiss(ARCHIVE_SENTINEL)
        elif 0 <= idx < len(projects):
            self.dismiss(projects[idx].path)

    def _start_new_project(self) -> None:
        def on_result(result: tuple[str, str] | None) -> None:
            if not result:
                return
            name, path = result
            projects = store.load_projects()
            if any(p.path == path for p in projects):
                self.query_one("#proj-switcher-error", Label).update(
                    f"Projekt '{name}' existiert bereits."
                )
                return
            new_ws = Workspace(Name=name)
            store.save_to(new_ws, path)
            projects.append(ProjectEntry(name=name, path=path))
            store.save_projects(projects)
            self.dismiss(path)

        self.app.push_screen(NewProjectScreen(), on_result)

    def _delete_selected(self) -> None:
        lv = self.query_one("#project-list", ListView)
        idx = lv.index
        if idx is None:
            return
        projects = store.load_projects()
        err = self.query_one("#proj-switcher-error", Label)
        if idx >= len(projects):
            err.update("Das Archiv kann nicht gelöscht werden.")
            return
        if len(projects) <= 1:
            err.update("Mindestens ein Projekt muss verbleiben.")
            return
        if projects[idx].path == self.current_path:
            err.update("Das aktuelle Projekt kann nicht gelöscht werden.")
            return
        projects.pop(idx)
        store.save_projects(projects)
        self._rebuild_list(projects)
        err.update("")

    def _rebuild_list(self, projects: list[ProjectEntry]) -> None:
        lv = self.query_one("#project-list", ListView)
        lv.clear()
        for i, p in enumerate(projects):
            marker = " ●" if p.path == self.current_path else ""
            lv.append(ListItem(Static(p.name + marker), id=f"proj-{i}"))
        lv.append(ListItem(Static("Archiv  [readonly]"), id="proj-archive", classes="archive-entry"))
