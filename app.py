from textual.app import App, ComposeResult
from textual.widgets import Static
from screens.session import Session


class Noni(App):
    
    # Session screen will always be the first screen on launch
    def on_mount(self) -> None:
        self.push_screen(Session())

if __name__ == "__main__":
    app = Noni()
    app.run()