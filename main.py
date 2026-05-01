from textual.app import App
from screens.main_screen import MainScreen
from screens.help_screen import HelpScreen


class KanbanApp(App):
    TITLE = "KanbanTabs"
    CSS_PATH = "app.tcss"
    SCREENS = {"help": HelpScreen}
    BINDINGS = [
        ("q", "quit", "Beenden"),
        ("question_mark", "push_screen('help')", "Hilfe"),
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def main() -> None:
    KanbanApp().run()


if __name__ == "__main__":
    main()
