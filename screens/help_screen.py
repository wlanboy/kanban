from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown
from textual.containers import Vertical

HELP_TEXT = """
# KanbanTabs — Tastatur-Referenz

## Navigation
| Taste | Aktion |
|---|---|
| `j` / `↓` | Nächste Card fokussieren |
| `k` / `↑` | Vorherige Card fokussieren |
| `Tab` | Nächste Lane |
| `Shift+Tab` | Vorherige Lane |

## Cards
| Taste | Aktion |
|---|---|
| `n` | Neue Card anlegen |
| `d` | Fokussierte Card löschen |
| `r` | Card umbenennen |
| `o` | Beschreibung bearbeiten |
| `s` | Priorität ändern |
| `→` / `l` | Card in nächste Lane |
| `←` / `h` | Card in vorherige Lane |
| `↑` | Card in Lane nach oben |
| `↓` | Card in Lane nach unten |
| `m` | Card frei verschieben |

## Lanes
| Taste | Aktion |
|---|---|
| `a` | Neue Lane anlegen |
| `D` | Fokussierte Lane löschen |

## Allgemein
| Taste | Aktion |
|---|---|
| `u` | Undo |
| `/` | Suche/Filter |
| `?` | Diese Hilfe |
| `q` | Beenden |
"""


class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-container help-container"):
            yield Markdown(HELP_TEXT)
            yield Button("Schließen", id="close", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def on_key(self, event) -> None:
        if event.key in ("escape", "question_mark"):
            self.dismiss()
